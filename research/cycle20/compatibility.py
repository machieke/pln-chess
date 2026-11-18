"""Complete frozen-input comparison and targeted fresh legacy reruns."""
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict
from pathlib import Path
from pln_chess.common import ROOT, digest, read_json
from research.cycle15.native_reasoner import Budgets, NativeReasoner, Sentence
from research.cycle16.experiments import support_status
from research.cycle19.records import record,sha
from .native import derive,projection
from .state import Identity

KEYS=('query','contrary_query','answer','contrary','classification','incomplete','completion','selected','retained','remaining','support_status')
OBSERVABLE=('query','contrary_query','facts','rules','answer','contrary','classification','selected','retained','remaining')

def differences(a,b):
    return [k for k in KEYS if a[k]!=b[k]]

def old_pair(facts,rules,queries,budget):
    result=[]
    for query,contrary in ((queries[0],None),(queries[1],queries[2])):
        old=NativeReasoner().infer(facts,rules,query,contrary=contrary,budgets=budget)
        old['support_status']=support_status(old)
        result.append(old)
    return result

def projected(result,queries):
    return [projection(result,queries[0]),projection(result,queries[1],queries[2])]

def compare_all(destination,workers=4):
    dest=Path(destination)
    archive=Path(read_json(ROOT/'publication/cycle19/manifest.json')['original_local_root'])
    index=read_json(ROOT/'artifacts/cycle19/evaluation-index.json')
    rows={}
    for path in (archive/'study/evaluation/rows').glob('*.json'):
        row=read_json(path);rows[row['root'],row['variant'],row['arm']]=row
    assert len(index)==len(rows)==1256
    seen=set();work=[]
    for item in index:
        row=rows[item['root'],item['variant'],item['arm']]
        scope=row['native']['scope']
        path_cells=set(map(tuple,scope['relevant_ray_cells']))
        occupied={tuple(scope['cell_roles'][f['term'].split()[1]]) for f in scope['fact_origins'] if f['term'].startswith('(Occupied ')}
        group=(item['arm'],item['variant'],bool(path_cells&occupied))
        work.append((item,row,group not in seen));seen.add(group)
    def one(args):
        item,row,rerun=args
        key=digest([row['environment'],row['arm']]);path=dest/'rows'/(key+'.json')
        if path.exists():return read_json(path)
        examples=[];hashes=[]
        for name in ('Clear','Attack'):
            entry=item['stages'][name]['native'];source=archive/entry['path'].removeprefix('local-pack:')
            assert sha(source)==entry['sha256']==row['native']['stages'][name]['native']['sha256']
            old=read_json(source);hashes.append(entry['sha256']);examples.append(old)
            assert digest({k:old[k] for k in OBSERVABLE})==item['stages'][name]['observable_sha256']
        clear,attack=examples
        for k in ('facts','rules','budgets','marginals','api'):
            assert clear[k]==attack[k],k
        assert clear['api']=='derive' and not clear['marginals']
        facts=[Sentence(**s) for s in clear['facts']];rules=[Sentence(**s) for s in clear['rules']]
        budget=Budgets(**clear['budgets']);qs=[clear['query'],attack['query'],attack['contrary_query']]
        identity=Identity.create(row['native']['scope']['state_id'],row['environment'],row['native']['generation'] or row['native']['model'],'cycle19-local')
        result=derive(facts,rules,qs,identity,budget);parts=projected(result,qs)
        diffs=[differences(p,o) for p,o in zip(parts,examples)]
        extra=None
        if rerun or any(diffs):
            fresh=old_pair(facts,rules,qs,budget)
            extra=[differences(p,o) for p,o in zip(fresh,examples)]
        return record(path,dict(key=key,root=item['root'],variant=item['variant'],arm=item['arm'],
            identity=asdict(identity),input_hash=digest(result['state']['inputs']),baseline_proofs=hashes,
            snapshot=result['state']['snapshot'],receipt=result['state']['native_receipt'],readouts=result['readouts'],
            selected=len(result['selected']),retained=len(result['state']['queues'][1]),remaining=len(result['state']['queues'][0]),
            differences=diffs,fresh_legacy_differences=extra,derivations=result['derivations']))
    with ThreadPoolExecutor(max_workers=workers) as pool:results=list(pool.map(one,work))
    mismatches=[r['key'] for r in results if any(r['differences']) or any(r['fresh_legacy_differences'] or [])]
    return record(dest/'summary.json',dict(pairs=len(results),stages=len(results)*2,readouts=len(results)*3,
        fresh_old_pairs=sum(r['fresh_legacy_differences'] is not None for r in results),
        selected=sum(r['selected'] for r in results),retained=sum(r['retained'] for r in results),
        remaining=sum(r['remaining'] for r in results),mismatches=mismatches,passed=not mismatches))
