"""Post-hoc coarser ancestry audit; never changes splits, models or predictions."""
import argparse
from collections import defaultdict
from pathlib import Path
import random
from pln_chess.common import digest,read_json,write_json
from evaluation.cycle15_corpus import registration
from evaluation.cycle15_consequences import metrics


def geometry(root):
    return digest({k:v for k,v in root['family'].items() if k!='kind'})


def run(results,out):
    roots=registration();byid={r['id']:r for r in roots};groups=defaultdict(list)
    for root in roots:groups[geometry(root)].append(root)
    overlaps=[dict(geometry=key,roots=[r['id'] for r in members],splits=sorted({r['split'] for r in members}))
              for key,members in groups.items() if len({r['split'] for r in members})>1]
    test=[r for r in read_json(results) if r['split']=='test']
    novel={r['id'] for r in roots if r['split']=='test' and all(x['split']=='test' for x in groups[geometry(r)])}
    subset=[r for r in test if r['root'] in novel]
    blocks=defaultdict(list)
    for row in test:blocks[geometry(byid[row['root']])].append(row)
    rng=random.Random(15);keys=sorted(blocks);draws=[]
    for _ in range(1000):
        sample=[row for key in rng.choices(keys,k=len(keys)) for row in blocks[key]]
        m=metrics(sample,'D');draws.append(m['positive_recall_including_abstention'])
    draws.sort()
    report=dict(exact_registered_typed_splits_disjoint=True,
        registered_definition='direction, length, blocker index and attacker kind',
        coarser_definition='direction, length and blocker index; kinds grouped as dependent variants',
        typed_families={s:sum(r['split']==s for r in roots) for s in ('train','development','test')},
        geometry_groups={s:sum(any(r['split']==s for r in g) for g in groups.values()) for s in ('train','development','test')},
        cross_split_geometry_overlaps=overlaps,test_roots_with_unseen_geometry=len(novel),
        strictly_unseen_test_geometry_groups=len({geometry(byid[r]) for r in novel}),
        unseen_geometry_results={arm:metrics(subset,arm) for arm in 'ABCD'},
        geometry_cluster_positive_recall_95=[draws[25],draws[975]],
        prior_predictions_or_splits_changed=False,
        conclusion='The nominal 48 typed test families are not 48 independent unseen geometry groups. Positive transfer is demonstrated for held-out kind/geometry combinations and identities, not for independently unseen ray geometry.',
        scope='Post-hoc structural dependence sensitivity audit; synthetic panel, not independent natural games')
    write_json(out,report)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--results',required=True);p.add_argument('--out',required=True)
    a=p.parse_args();run(a.results,a.out)
