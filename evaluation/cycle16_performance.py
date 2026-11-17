"""Ten repeats per workload, independent stored lookup/proof expansion timings."""
import argparse
import json
from pathlib import Path
import statistics
import time
from pln_chess.common import canonical,digest,read_json
from pln_chess.cycle14.proofs import ProofStore
from research.cycle16.experiments import fixture,infer
from research.cycle16.records import compact,record


def run(out,checkpoint,repetitions=10):
    out=Path(out);model=read_json(checkpoint);rows=[];example=None
    cases=[('one-cell','E',2,'R',False),('two-recursive','EE',3,'R',False),
        ('two-finite','EE',3,'F',False),('two-learned','EE',3,'L',False),
        ('negative-obstruction','OE',3,'F',False),('unknown-occupancy','EU',3,'F',False),
        ('distractor-rich','EE',3,'F',True)]
    for name,occupancy,length,arm,full in cases:
        for i in range(repetitions):
            state,a,t=fixture(occupancy,length=length,tag='bench_'+str(i))
            if full:
                for j in range(8):state['pieces'].append(dict(id='distractor_'+str(j),kind='pawn',owner='white',cell=[j,6]))
            started=time.perf_counter();result=infer(state,a,t,arm=arm,checkpoint=model if arm=='L' else None,full_scope=full)
            elapsed=time.perf_counter()-started
            rows.append(dict(category=name,repetition=i,wall_seconds=elapsed,native_processes=3,
                selected_tasks=sum(r['usage']['selected_tasks'] for r in result['stages'].values()),
                retained_beliefs=sum(r['usage']['retained_beliefs'] for r in result['stages'].values()),
                cpu_seconds=sum(r['receipt']['cpu_seconds'] or 0 for r in result['stages'].values()),
                peak_rss_kib=max(r['receipt']['peak_rss_kib'] or 0 for r in result['stages'].values()),
                result=compact(result,out)))
            if name=='two-finite' and i==0:example=result
    document=json.loads(canonical(example))
    with ProofStore(out/'proofs.sqlite') as store:
        ref=store.put(document)
        identity=dict(state=example['observation_scope']['state_identity'],history=example['observation_scope']['history'],
            knowledge=example['knowledge_identity'],checkpoint=example['checkpoint_identity'],
            programs=[r['receipt']['program_sha256'] for r in example['stages'].values()],
            runtime=example['stages']['Attack']['receipt']['runtime'])
        summary={n:{k:r[k] for k in ('classification','answer','contrary')} for n,r in example['stages'].items()}
        handle=store.publish(ref,summary,identity)
        for i in range(repetitions):
            started=time.perf_counter();found=store.lookup(identity);elapsed=time.perf_counter()-started
            assert found['summary']==summary
            rows.append(dict(category='cached-answer',repetition=i,wall_seconds=elapsed,native_processes=0))
            started=time.perf_counter();expanded=store.expand(ref);elapsed=time.perf_counter()-started
            assert expanded==document and digest(expanded)==digest(example)
            rows.append(dict(category='full-proof-reconstruction',repetition=i,wall_seconds=elapsed,native_processes=0))
        assert store.lookup({**identity,'history':'different_history'}) is None
        assert store.lookup({**identity,'knowledge':'different_rules'}) is None
        archive=store.archive(ref)
        with ProofStore() as fresh:
            restored=fresh.import_archive(archive);assert fresh.expand(restored)==document
        integrity=dict(passed=True,exact_complete_json_roundtrip=True,fresh_archive_import=True,
            changed_history_misses=True,changed_knowledge_misses=True,census=store.census(),handle=handle,
            native_resident_atoms=0,archive_sha256=archive['manifest_sha256'],
            proof_status='Exact raw proof storage/reconstruction; no invented fired-rule tree')
    summary={name:dict(repetitions=len(selected:=[r for r in rows if r['category']==name]),
        median_seconds=statistics.median(r['wall_seconds'] for r in selected),
        min_seconds=min(r['wall_seconds'] for r in selected),max_seconds=max(r['wall_seconds'] for r in selected),
        native_processes_per_request=selected[0]['native_processes']) for name in sorted({r['category'] for r in rows})}
    record(out/'samples.json',rows);record(out/'summary.json',summary);record(out/'proof-integrity.json',integrity)
    return summary


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--checkpoint',required=True)
    a=p.parse_args();run(a.out,a.checkpoint)
