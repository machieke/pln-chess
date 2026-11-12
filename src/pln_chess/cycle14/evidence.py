"""Generation-aware, hash-chained evidence transactions and deterministic replay."""
import copy
import fcntl
import json
import os
from pathlib import Path
import tempfile

from pln_chess.common import canonical,digest
from pln_chess.pln import TV
from .ontology import key


class EvidenceLedger:
    def __init__(self,path):self.path=Path(path)

    def history(self):
        rows=[];previous=None
        if not self.path.exists():return rows
        for sequence,line in enumerate(self.path.read_text().splitlines(),1):
            row=json.loads(line);body={k:v for k,v in row.items() if k!='event_id'}
            if row['sequence']!=sequence or row['previous']!=previous or row['event_id']!='evidence-event:'+digest(body):
                raise ValueError('Corrupt evidence ledger chain')
            previous=row['event_id'];rows.append(row)
        return rows

    @staticmethod
    def validate(payload):
        required={'observation_id','source_position','candidate_moves','descriptor','packet','label','canonical_label',
            'source','source_game','dependence_group','transformation_lineage','temporal_context','model_versions',
            'runtime_version','dataset_hash','reference_evidence_id','observation_confidence','scope'}
        if not isinstance(payload,dict) or set(payload)!=required:raise ValueError('Missing or unsupported evidence fields')
        if payload['label'] not in ('A','B','no-demonstrated-preference','unknown'):raise ValueError('Invalid label')
        packet=payload['packet']
        if key(payload['descriptor'])!=packet['rule_id'] or payload['descriptor']!=packet['descriptor']:
            raise ValueError('Evidence descriptor identity mismatch')
        if packet['canonical_order'] not in (['A','B'],['B','A']):raise ValueError('Invalid pair orientation')
        expected=('first' if packet['canonical_order'][0]==payload['label'] else 'second') if payload['label'] in ('A','B') else payload['label']
        if payload['canonical_label']!=expected or payload['temporal_context'].get('horizon')!=payload['descriptor']['horizon']:
            raise ValueError('Label orientation or temporal scope mismatch')
        from pln_chess.domain import Position
        Position.from_fen(payload['source_position'])
        if not isinstance(payload['candidate_moves'],list) or len(payload['candidate_moves'])!=2 or len(set(payload['candidate_moves']))!=2:
            raise ValueError('Two distinct candidates required')
        for name in ('observation_id','source_game','dependence_group','runtime_version','reference_evidence_id','dataset_hash'):
            if not isinstance(payload[name],str) or not payload[name]:raise ValueError('Missing evidence provenance')
        if not isinstance(payload['transformation_lineage'],list) or any(not isinstance(v,str) or not v for v in payload['transformation_lineage']):
            raise ValueError('Invalid dependence ancestry')
        value=payload['observation_confidence']
        if isinstance(value,bool) or TV(1.,value).confidence>=1:raise ValueError('Finite observation confidence required')

    @staticmethod
    def replay(events):
        versions={};active={}
        for event in events:
            action=event['action'];generation=event['generation']
            if action=='ingest':
                for row in event['records']:
                    key_=(row['payload']['observation_id'],generation)
                    if key_ in versions and versions[key_]!=row:raise ValueError('Conflicting generation observation')
                    if row['evidence_id']!='preference-evidence-v14:'+digest([generation,row['payload']]):raise ValueError('Corrupt evidence identity')
                    EvidenceLedger.validate(row['payload']);versions[key_]=row
            elif action in ('activate','rollback'):
                for observation in event['observations']:
                    if (observation,generation) not in versions:raise ValueError('Activation references missing evidence')
                    active[observation]=generation
            else:raise ValueError('Unregistered evidence event')
        records=[versions[(observation,active[observation])] for observation in sorted(active)]
        return dict(records=records,active=active,versions=versions,
            active_digest=digest(records),chain_head=events[-1]['event_id'] if events else None)

    def snapshot(self):return self.replay(self.history())
    def records(self):return copy.deepcopy(self.snapshot()['records'])

    def transact(self,operations):
        """Validate the whole batch, then atomically replace one durable file.

        A stable separate lock survives rename. No timestamp enters a scientific
        identity. Failed batches and crashed temporary files change no history.
        """
        operations=copy.deepcopy(list(operations));self.path.parent.mkdir(parents=True,exist_ok=True)
        with self.path.with_suffix(self.path.suffix+'.lock').open('a+') as lock:
            fcntl.flock(lock,fcntl.LOCK_EX);events=self.history();snapshot=self.replay(events);pending=[]
            for operation in operations:
                generation=operation.get('generation');action=operation.get('action')
                if not isinstance(generation,str) or not generation or len(generation)>128:raise ValueError('Explicit label generation required')
                if action=='ingest':
                    if set(operation)!={'action','generation','payloads'}:raise ValueError('Invalid ingest fields')
                    records=[]
                    for payload in operation['payloads']:
                        self.validate(payload);key_=(payload['observation_id'],generation)
                        row=dict(generation=generation,evidence_id='preference-evidence-v14:'+digest([generation,payload]),payload=payload)
                        existing=snapshot['versions'].get(key_)
                        if existing:
                            if existing!=row:raise ValueError('Conflicting reuse within label generation')
                            continue
                        snapshot['versions'][key_]=row;records.append(row)
                    if not records:continue
                    body=dict(action=action,generation=generation,records=sorted(records,key=lambda r:r['payload']['observation_id']))
                elif action in ('activate','rollback'):
                    if set(operation)!={'action','generation','observations'}:raise ValueError('Invalid activation fields')
                    observations=sorted(set(operation['observations']))
                    if any((observation,generation) not in snapshot['versions'] for observation in observations):
                        raise ValueError('Activation references missing evidence')
                    observations=[o for o in observations if snapshot['active'].get(o)!=generation]
                    if not observations:continue
                    for observation in observations:snapshot['active'][observation]=generation
                    body=dict(action=action,generation=generation,observations=observations)
                else:raise ValueError('Unsupported ledger action')
                body.update(sequence=len(events)+len(pending)+1,previous=(pending[-1] if pending else events[-1])['event_id'] if pending or events else None)
                pending.append({**body,'event_id':'evidence-event:'+digest(body)})
            if not pending:return self.snapshot()
            combined=events+pending;result=self.replay(combined)
            descriptor,name=tempfile.mkstemp(prefix=self.path.name+'.',suffix='.partial',dir=self.path.parent)
            try:
                with os.fdopen(descriptor,'w') as stream:
                    for row in combined:stream.write(canonical(row)+'\n')
                    stream.flush();os.fsync(stream.fileno())
                os.replace(name,self.path)
                parent=os.open(self.path.parent,os.O_DIRECTORY)
                try:os.fsync(parent)
                finally:os.close(parent)
            finally:
                if os.path.exists(name):os.unlink(name)
            return result

    def append_many(self,payloads,*,generation='labels-g1',activate=True):
        payloads=list(payloads);operations=[dict(action='ingest',generation=generation,payloads=payloads)]
        if activate:operations.append(dict(action='activate',generation=generation,observations=[p['observation_id'] for p in payloads]))
        snapshot=self.transact(operations)
        return [copy.deepcopy(snapshot['versions'][(p['observation_id'],generation)]) for p in payloads]

    def activate(self,generation,observations,*,rollback=False):
        return self.transact([dict(action='rollback' if rollback else 'activate',generation=generation,observations=list(observations))])
