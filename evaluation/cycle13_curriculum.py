"""Describe actual relational coverage, without treating omitted domains as false."""
import argparse
from collections import Counter
from pathlib import Path
from pln_chess.common import digest,read_json,write_json
from evaluation.cycle3 import read_gzip


def summarize(out):
    out=Path(out);index=read_json(out/'features/index.json')
    sources={r['id']:r for r in read_json(out/'datasets/source-pairs.json')['records']}
    labels={r['id']:r['label'] for r in read_json(out/'datasets/reference-labels.json')['records']}
    rows=[]
    for receipt in index['records']:
        result=read_gzip(out/receipt['artifact']);changes=[c for side in result['changes'].values() for c in side]
        flags=dict(
            attack_counterevidence_to_support=any(c['predicate']=='OpensAttack' for c in changes),
            newly_queried_supported_attack=any(c['family']=='attack' and c['before'] is None and c['after']['classification']=='supported' for c in changes),
            supported_defense_persists=any(c['family']=='defense' and c['support_persists'] for c in changes),
            supported_defense_to_counterevidence=any(c['family']=='defense' and c['change_kind']=='support-to-counterevidence' for c in changes),
            supported_defense_domain_removed=any(c['family']=='defense' and c['change_kind']=='domain-removed' and c['before']['classification']=='supported' for c in changes),
            mobility_classification_changes=any(c['family']=='mobility' and c['before'] and c['after'] and c['before']['classification']!=c['after']['classification'] for c in changes),
            king_exposure_classification_changes=any(c['family']=='king-exposure' and c['before'] and c['after'] and c['before']['classification']!=c['after']['classification'] for c in changes))
        row=sources[receipt['id']]
        concepts=Counter(c['concept'] for state in result['states'].values() for c in state['concepts'])
        supported=Counter(c['concept'] for state in result['states'].values() for c in state['concepts'] if c['classification']=='supported')
        rows.append(dict(id=row['id'],split=row['split'],cohort=row['source']['cohort'],label=labels[row['id']],
            flags=flags,concept_candidate_families=sorted(concepts),supported_conditional_families=sorted(supported),
            quiet=row['offline_reference']['quiet_pair'],promotion=any(row['offline_reference']['promotions']),
            feature_artifact=receipt['artifact'],feature_semantic_sha256=receipt['semantic_sha256']))
    totals={name:sum(row['flags'][name] for row in rows) for name in rows[0]['flags']}
    families=sorted({name for row in rows for name in row['concept_candidate_families']})
    return dict(passed=True,source_hash=index['source_hash'],production_code_hash=index['production_code_hash'],
        pairs=len(rows),observed_change_coverage=totals,
        concept_candidate_pair_coverage={name:sum(name in r['concept_candidate_families'] for r in rows) for name in families},
        supported_concept_pair_coverage={name:sum(name in r['supported_conditional_families'] for r in rows) for name in families},
        quiet_pairs=sum(r['quiet'] for r in rows),promotion_pairs=sum(r['promotion'] for r in rows),
        ambiguous_reference_pairs=sum(r['label']=='no-demonstrated-preference' for r in rows),
        pair_details=rows,scope='Descriptive coverage of separately inferred endpoints. Domain creation/removal, candidate enumeration and conditional support remain distinct; no joint or causal strategic assertion.')


def run(out,compare=False):
    out=Path(out);result=summarize(out)
    if compare:
        replayed=summarize(out/'clean-research/run')
        assert digest(result)==digest(replayed),'Coverage changed in fresh native replay'
        result['fresh_replay_coverage_identical']=True
    write_json(out/'datasets/relational-coverage.json',result)
    print('CURRICULUM OBSERVATIONS',result['observed_change_coverage'],flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',default='artifacts/cycle13');parser.add_argument('--compare',action='store_true')
    args=parser.parse_args();run(args.out,args.compare)
