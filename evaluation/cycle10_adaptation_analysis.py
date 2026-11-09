"""Paired final-test changes and transfer diagnostics; no model selection."""
import argparse
from collections import defaultdict
from pathlib import Path
import random
from pln_chess.common import read_json,write_json
from evaluation.cycle3 import read_gzip
from evaluation.cycle9_analysis import metrics


def paired_intervals(before,after,positions_before,positions_after,draws=400):
    grouped=defaultdict(lambda:[0,0,0,0,0,0,0])
    for a,b in zip(before,after,strict=True):
        assert (a['fixture'],a['move'],a['label'])==(b['fixture'],b['move'],b['label'])
        v=grouped[a['source_game']];v[0]+=bool(a['label'])
        v[1]+=a['label'] and a['classification']=='supported-legal';v[2]+=b['label'] and b['classification']=='supported-legal'
        v[3]+=not a['label'] and a['classification']=='supported-legal';v[4]+=not b['label'] and b['classification']=='supported-legal'
    for a,b in zip(positions_before,positions_after,strict=True):
        assert a['fixture']==b['fixture'];v=grouped[a['source_game']];v[5]+=int(b['exact'])-int(a['exact']);v[6]+=1
    values=list(grouped.values());rng=random.Random(101012);samples={'recall_delta':[],'exact_set_accuracy_delta':[],'false_legal_count_delta':[]}
    for _ in range(draws):
        sums=[sum(v[i] for v in sample) for sample in [rng.choices(values,k=len(values))] for i in range(7)]
        samples['recall_delta'].append((sums[2]-sums[1])/sums[0] if sums[0] else 0)
        samples['exact_set_accuracy_delta'].append(sums[5]/sums[6]);samples['false_legal_count_delta'].append(sums[4]-sums[3])
    return dict(method='Paired percentile game bootstrap, 400 draws, identical game draws for each model. Residual opening/player dependence remains.',
        games=len(values),interval95={key:[sorted(v)[int(.025*draws)],sorted(v)[int(.975*draws)-1]] for key,v in samples.items()})


def run(out):
    out=Path(out);adapt=read_json(out/'adaptation/summary.json');data=read_json(out/'datasets/dataset.json')
    novelty=read_json(out/'datasets/relative-transfer-audit.json')['unseen_candidates_by_fixture']
    original=read_gzip(out/'analysis/frozen-rows.json.xz')
    rows=[r for r in original['rows'] if r['split']=='external-test'];positions=[p for p in original['positions'] if p['split']=='external-test']
    # Evaluation shards and all arms share a deterministic source/fixture ordering.
    order=lambda r:(r['fixture'],r['move']);rows.sort(key=order);positions.sort(key=lambda p:p['fixture'])
    train_positions={p['fen'] for p in data['positions'] if p['split']=='external-adaptation'}
    test_positions={p['fen'] for p in data['positions'] if p['split']=='external-test'};assert not train_positions&test_positions
    results={'frozen':dict(records=0,games=0,model_version=adapt['frozen_model'],metrics=metrics(rows,positions))}
    for arm in ('small','large'):
        stored=read_gzip(out/f'analysis/{arm}-rows.json.xz');current=sorted(stored['rows'],key=order);ps=sorted(stored['positions'],key=lambda p:p['fixture'])
        changes=[]
        for a,b in zip(rows,current,strict=True):
            assert order(a)==order(b)
            if a['classification']!=b['classification'] or a['truth_value']!=b['truth_value']:
                changes.append(dict(fixture=a['fixture'],move=a['move'],label=a['label'],before=a['classification'],after=b['classification'],
                    before_tv=a['truth_value'],after_tv=b['truth_value'],source_game=a['source_game'],
                    missing_exact_descriptor_in_frozen=a['move'] in novelty.get(a['fixture'],[])))
        unseen=[r for r in current if r['move'] in novelty.get(r['fixture'],[])];seen=[r for r in current if r['move'] not in novelty.get(r['fixture'],[])]
        results[arm]=dict(model_version=adapt['models'][arm]['model_version'],records=adapt['models'][arm]['training_report']['records'],
            games=adapt['models'][arm]['training_report']['source_games'],metrics=metrics(current,ps),
            frozen_unseen_descriptor_metrics=metrics(unseen,[]),frozen_known_descriptor_metrics=metrics(seen,[]),
            paired_uncertainty=paired_intervals(rows,current,positions,ps),
            changed_classifications=sum(c['before']!=c['after'] for c in changes),changed_native_truth_values=sum(c['before_tv']!=c['after_tv'] for c in changes),
            legal_abstentions_resolved=sum(c['label'] and c['before']=='unknown' and c['after']=='supported-legal' for c in changes),
            new_false_legal=sum(not c['label'] and c['before']!='supported-legal' and c['after']=='supported-legal' for c in changes),
            new_false_illegal=sum(c['label'] and c['before']!='supported-illegal' and c['after']=='supported-illegal' for c in changes),
            changes=changes)
    write_json(out/'adaptation/comparison.json',dict(models=results,new_learning_promoted=False,final_test_games=102,final_test_positions=1020,
        training_test_FEN_overlap=0,opening_family_partitioned=True,
        transfer_scope='Any changed test predictions occur in distinct source games and opening families, with no identical training FEN. Exact local descriptors can recur: this tests relational transfer, not universal unseen-structure coverage.',
        model_selection='No final-test selection, threshold tuning, acceptance promotion or update after inspecting these results.'))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);run(p.parse_args().out)
