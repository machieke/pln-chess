"""Locked append-only preference evidence, distinct from legality supervision."""
import copy
from datetime import datetime, timezone
import fcntl
import json
import os
from pathlib import Path
from pln_chess.common import canonical, digest
from pln_chess.pln import TV
from pln_chess.domain import Position
from .ontology import key


class PreferenceLedger:
    def __init__(self,path):
        self.path=Path(path)

    def records(self):
        if not self.path.exists():
            return []
        rows=[]
        for sequence,line in enumerate(self.path.read_text().splitlines(),1):
            row=json.loads(line)
            if row['sequence'] != sequence or row['evidence_id'] != 'preference-evidence:'+digest(row['payload']):
                raise ValueError('Preference ledger identity or sequence mismatch')
            rows.append(row)
        return rows

    def append_many(self,payloads):
        payloads=copy.deepcopy(list(payloads))
        required={'observation_id','source_position','candidate_moves','descriptor','packet','label','canonical_label',
            'source','source_game','dependence_group','transformation_lineage','temporal_context','model_versions',
            'runtime_version','dataset_hash','reference_evidence_id','observation_confidence','scope'}
        for row in payloads:
            if not isinstance(row,dict) or set(row) != required:
                raise ValueError('Missing or unsupported preference evidence fields')
            if row['label'] not in ('A','B','no-demonstrated-preference','unknown') or row['canonical_label'] not in ('first','second','no-demonstrated-preference','unknown'):
                raise ValueError('Invalid four-way preference supervision')
            if any(not row[name] for name in ('observation_id','source_position','source','source_game','dependence_group','runtime_version','reference_evidence_id')):
                raise ValueError('Missing preference provenance')
            if len(row['candidate_moves']) != 2 or len(set(row['candidate_moves'])) != 2:
                raise ValueError('Preference evidence requires two distinct candidates')
            Position.from_fen(row['source_position'])
            if key(row['descriptor']) != row['packet']['rule_id'] or row['descriptor'] != row['packet']['descriptor']:
                raise ValueError('Evidence descriptor and packet differ')
            expected=('first' if row['packet']['canonical_order'][0]==row['label'] else 'second') if row['label'] in ('A','B') else row['label']
            if row['canonical_label']!=expected or row['temporal_context'].get('horizon')!=row['descriptor']['horizon']:
                raise ValueError('Preference label orientation or temporal scope mismatch')
            if not isinstance(row['transformation_lineage'],list) or any(not isinstance(v,str) or not v for v in row['transformation_lineage']):
                raise ValueError('Invalid preference ancestry')
            value=row['observation_confidence']
            if isinstance(value,bool) or TV(1.,value).confidence >= 1:
                raise ValueError('Finite preference observation confidence required')
        self.path.parent.mkdir(parents=True,exist_ok=True)
        with self.path.open('a+') as stream:
            fcntl.flock(stream,fcntl.LOCK_EX)
            rows=self.records();known={r['payload']['observation_id']:r for r in rows}
            pending=[];result=[]
            for payload in payloads:
                identifier='preference-evidence:'+digest(payload)
                existing=known.get(payload['observation_id'])
                if existing:
                    if existing['evidence_id'] != identifier:
                        raise ValueError('Conflicting reuse of a preference observation identity')
                    result.append(existing);continue
                row=dict(sequence=len(rows)+len(pending)+1,timestamp=datetime.now(timezone.utc).isoformat(),
                    evidence_id=identifier,payload=payload)
                known[payload['observation_id']]=row;pending.append(row);result.append(row)
            # Validate conflicts across the complete batch before the first write.
            for row in pending:
                stream.write(canonical(row)+'\n')
            stream.flush();os.fsync(stream.fileno())
        return copy.deepcopy(result)
