"""Append-only evidence with explicit correlation, idempotency, and ordering."""
from __future__ import annotations
from datetime import datetime, timezone
import fcntl
import json
from pathlib import Path
from pln_chess.common import canonical, digest
from pln_chess.pln import TV

class Ledger:
    def __init__(self,path): self.path=Path(path)

    def append_many(self,payloads):
        """One locked transaction for bulk ingestion, with the same payload hashes.

        Validate all inputs before writing; a crash can leave a valid prefix, and
        retry is idempotent. Each payload retains its own evidence identity.
        """
        payloads=list(payloads)
        for payload in payloads:
            required=('position_id','candidate_id','relative_feature_fingerprint','label','source','dependence_group','observation_tv','targets','runtime_version','model_version','transformation_lineage')
            if any(k not in payload for k in required): raise ValueError('Missing evidence field')
            if not payload['source'] or not payload['dependence_group'] or type(payload['label']) is not bool: raise ValueError('Invalid evidence identity/label')
            if TV.from_json(payload['observation_tv']).confidence>=1: raise ValueError('Finite revision confidence required')
        self.path.parent.mkdir(parents=True,exist_ok=True)
        with self.path.open('a+') as file:
            fcntl.flock(file,fcntl.LOCK_EX);records=self.records();known={r['evidence_id']:r['sequence'] for r in records};sequence=len(records);results=[]
            for payload in payloads:
                eid=digest(payload)
                if eid in known:
                    results.append({'evidence_id':eid,'sequence':known[eid],'status':'duplicate'});continue
                sequence+=1;known[eid]=sequence
                record={'sequence':sequence,'timestamp':datetime.now(timezone.utc).isoformat(),'evidence_id':eid,'idempotency_key':eid,'payload':payload}
                file.write(canonical(record)+'\n');results.append({'evidence_id':eid,'sequence':sequence,'status':'appended'})
            file.flush()
            import os
            os.fsync(file.fileno())
        return results

    def records(self):
        if not self.path.exists(): return []
        records=[]
        for number,line in enumerate(self.path.read_text().splitlines(),1):
            if not line: continue
            record=json.loads(line)
            if record['sequence'] != number: raise ValueError('Ledger sequence discontinuity')
            if record['evidence_id'] != digest(record['payload']): raise ValueError('Ledger evidence hash mismatch')
            records.append(record)
        return records

    def append(self,payload,idempotency_key=None):
        for field in ('position_id','candidate_id','relative_feature_fingerprint','label','source','dependence_group','observation_tv','targets','runtime_version','model_version','transformation_lineage'):
            if field not in payload: raise ValueError(f'Missing evidence field: {field}')
        if not payload['source'] or not payload['dependence_group']: raise ValueError('Source and dependence group are required')
        if type(payload['label']) is not bool: raise ValueError('Legal/illegal label must be Boolean')
        tv=TV.from_json(payload['observation_tv'])
        if tv.confidence >= 1: raise ValueError('Finite native revision evidence requires confidence < 1')
        evidence_id=digest(payload); key=idempotency_key or evidence_id
        self.path.parent.mkdir(parents=True,exist_ok=True)
        with self.path.open('a+') as file:
            fcntl.flock(file,fcntl.LOCK_EX)
            records=self.records()
            for old in records:
                if old['idempotency_key']==key or old['evidence_id']==evidence_id:
                    if old['evidence_id'] != evidence_id: raise ValueError('Idempotency key reused for different evidence')
                    return {'evidence_id':old['evidence_id'],'sequence':old['sequence'],'status':'duplicate'}
            record={'sequence':len(records)+1,'timestamp':datetime.now(timezone.utc).isoformat(),
                    'evidence_id':evidence_id,'idempotency_key':key,'payload':payload}
            file.write(canonical(record)+'\n'); file.flush()
            import os
            os.fsync(file.fileno())
            return {'evidence_id':evidence_id,'sequence':record['sequence'],'status':'appended'}
