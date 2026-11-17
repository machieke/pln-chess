"""Native matched arms; reference evaluation happens only after predictions."""
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from pln_chess.common import read_json
from research.cycle16.experiments import infer
from research.cycle16.records import compact,record
from research.cycle16.corpus import roots,variant,reference,groups


def metrics(rows,arm):
    result={}
    for stage in ('Clear','Attack','Exposure'):
        counts=Counter(r['arms'][arm]['stages'][stage]['classification'] for r in rows)
        result[stage]=dict(outcomes=dict(counts),endpoints=len(rows))
    correct=wrong=positive=positive_correct=0
    for row in rows:
        predicted=row['arms'][arm]['stages']['Attack']['classification'];label=row['reference']['label']
        positive+=label is True
        if label is not None and predicted in ('supported-positive','supported-negative'):
            ok=(predicted=='supported-positive')==label;correct+=ok;wrong+=not ok
            positive_correct+=label is True and ok
    result.update(correct=correct,incorrect=wrong,reference_positive=positive,
        positive_recall=positive_correct/positive if positive else None,roots=len({r['root'] for r in rows}))
    return result


def run(out,learning,workers=2,splits=('development','test')):
    out=Path(out);learning=Path(learning)
    models={name:read_json(learning/name/'model.json') for name in ('learned','prior','shared-chain')}
    def worker(root):
        rows=[]
        for name,state in [('original',root['state']),('EE',variant(root,'EE')),('OE',variant(root,'OE'))]:
            arms={}
            for arm,checkpoint in [('R',None),('F',None),('F-minus',None),('L',models['learned']),
                                   ('prior',models['prior']),('shared-chain',models['shared-chain'])]:
                arms[arm]=compact(infer(state,root['attacker'],root['target'],arm='L' if checkpoint else arm,
                    checkpoint=checkpoint),out)
            rows.append(dict(root=root['id'],split=root['split'],source_ancestry=root['source_ancestry'],
                coarse_geometry=root['coarse_geometry'],endpoint=name,state=state,
                query=dict(attacker=root['attacker'],target=root['target']),arms=arms,
                reference=reference(state,root['attacker'],root['target'])))
        record(out/'roots'/(root['id']+'.json'),rows)
        print('C16 EVALUATED',root['split'],root['id'],flush=True)
        return rows
    selected=[r for r in roots() if r['split'] in splits]
    with ThreadPoolExecutor(max_workers=workers) as pool:
        rows=[row for chunk in pool.map(worker,selected) for row in chunk]
    summary={split:{arm:metrics([r for r in rows if r['split']==split],arm)
        for arm in ('R','F','F-minus','L','prior','shared-chain')} for split in splits}
    summary['groups']=groups(roots());summary['model_versions']={n:m['version'] for n,m in models.items()}
    record(out/'results.json',rows);record(out/'summary.json',summary)
    return summary


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--learning',required=True)
    p.add_argument('--workers',type=int,default=2);a=p.parse_args();run(a.out,a.learning,a.workers)
