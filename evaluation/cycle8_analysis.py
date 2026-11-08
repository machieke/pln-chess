"""Offline paired evidence, calibration and curriculum audits; no inference policy."""
from collections import Counter,defaultdict
from pathlib import Path
import argparse
import random
from pln_chess.common import ROOT,read_json,write_json,digest
from pln_chess.domain import Position
from pln_chess.api import find_move
from pln_chess.cycle8.ontology import observe,key
from evaluation.cycle3 import read_gzip
from evaluation.cycle7_io import pack
from evaluation.cycle7_analysis import unknown_categories,example
from evaluation.experiments import fit_calibrator,score_calibration


def paired(before,after):
    assert before['dataset_hash']==after['dataset_hash']
    assert [(r['fixture'],r['move'],r['label']) for r in before['rows']]==[(r['fixture'],r['move'],r['label']) for r in after['rows']]
    a={p['fixture']:p for p in before['positions']};b={p['fixture']:p for p in after['positions']};assert a.keys()==b.keys()
    rows=[];clusters=defaultdict(list)
    for fid,p in a.items():
        q=b[fid];expected=set(p['expected']);assert expected==set(q['expected'])
        row={'fixture':fid,'family':p['family'],'source_game':p.get('source_game'),
            'before_exact':p['exact'],'after_exact':q['exact'],'legal_candidates':len(expected),
            'before_tp':len(expected&set(p['predicted'])),'after_tp':len(expected&set(q['predicted'])),
            'added_predictions':sorted(set(q['predicted'])-set(p['predicted'])),
            'removed_predictions':sorted(set(p['predicted'])-set(q['predicted']))}
        if p.get('source_game') is not None:kind,value='game',p['source_game']
        elif p.get('dependence_group') is not None:kind,value='source-group',p['dependence_group']
        else:kind,value='fixture',fid
        cluster=(kind,type(value).__name__,str(value));clusters[cluster].append(row);rows.append(row)
    rng=random.Random(808);keys=sorted(clusters);draws=[]
    for _ in range(1000):
        sample=[r for k in rng.choices(keys,k=len(keys)) for r in clusters[k]]
        total=sum(r['legal_candidates'] for r in sample)
        draws.append((sum(r['after_tp']-r['before_tp'] for r in sample)/total if total else 0,
            sum(int(r['after_exact'])-int(r['before_exact']) for r in sample)/len(sample)))
    def interval(index):
        v=sorted(d[index] for d in draws);return [v[25],v[974]]
    return {'positions':rows,'clusters':len(keys),'bootstrap_replicates':1000,'seed':808,
        'recall_delta_95_percentile_interval':interval(0),'exact_set_delta_95_percentile_interval':interval(1),
        'bootstrap_unit':'source game; otherwise source group (color mirrors together), otherwise historical fixture',
        'small_sample_caution':len(keys)<20,'scope':'Conditional on this synthetic corpus; no external-game guarantee.'}


def reference(out,split):
    return out/(f'evaluation/C7-frozen-{split}.json.xz' if split.startswith('cycle8-') else f'baseline/evaluation/C7-frozen-{split}.json.xz')


def dataset_audit(out):
    data=read_json(out/'datasets/dataset.json');counts={};training_keys=set()
    for r in data['examples']:
        if r['split']=='train':
            p=Position.from_fen(r['fen']);m=find_move(p,r['move']);o=observe(p,m)
            if o:training_keys.add(key(o['descriptor']))
    for split in data['counts']:
        fixtures=[p for p in data['positions'] if p['split']==split]
        examples=[r for r in data['examples'] if r['split']==split]
        counts[split]={'positions':len(fixtures),'source_groups':len({p['dependence_group'] for p in fixtures}),
            'source_games':len({p['source_game'] for p in fixtures if p.get('source_game') is not None}),
            'owners':dict(Counter(Position.from_fen(p['fen']).turn for p in fixtures)),
            'incomplete_observation_positions':sum(bool(p['unknown_squares']) for p in fixtures),
            'families':dict(Counter(p['family'] for p in fixtures)),
            'training_choices':dict(Counter(r['move'][-1] for r in examples)),
            'training_local_labels':dict(Counter(str(r['movement_label']) for r in examples)),
            'training_global_labels':dict(Counter(str(r['label']) for r in examples))}
        focus=[p for p in fixtures if p.get('focus_move')]
        counts[split]['focus_relative_keys_seen_in_training']=sum(key(observe(Position.from_fen(p['fen']),find_move(Position.from_fen(p['fen']),p['focus_move']))['descriptor']) in training_keys for p in focus)
        counts[split]['focus_positions']=len(focus)
    audit={'dataset_hash':data['hash'],'partitions':counts,'leakage':data['leakage_audit'],
        'balance':'Constructed complete scenarios have both owner orientations and all four promotion choices. Label counts and independent game outcomes are not forced to 50/50. Incomplete observations and game samples are reported separately.',
        'generalization_scope':'Complete interaction families are disjoint. Reusable atomic transition types deliberately recur; these are not unseen-type or arbitrary-context safety proofs.'}
    write_json(out/'datasets/audit.json',audit);return audit


def run(out):
    out=Path(out);summaries={p.name.removesuffix('-summary.json'):read_json(p) for p in sorted((out/'evaluation').glob('*-summary.json'))}
    regressions=[];representatives=[];calibration={};unknowns={};changes={}
    for arm,entries in summaries.items():
        validation=read_gzip(out/entries['cycle8-validation']['artifact']) if 'cycle8-validation' in entries else None
        calibrator=fit_calibrator(validation) if validation else None
        calibration[arm]={};changes[arm]={}
        for split,e in entries.items():
            report=read_gzip(out/e['artifact']);before=read_gzip(reference(out,split))
            delta=paired(before,report);write_json(out/f'paired/{arm}-{split}.json',delta)
            prior={(r['fixture'],r['move']):r for r in before['rows']};lost=0;wrong=0;added=0
            for row in report['rows']:
                old=prior[row['fixture'],row['move']]
                loss=old['classification'] in ('supported-legal','supported-illegal') and old['classification']!=row['classification']
                error=(row['classification']=='supported-legal' and not row['label']) or (row['classification']=='supported-illegal' and row['label'])
                lost+=loss;wrong+=error;added+=old['classification']=='unknown' and row['classification'] in ('supported-legal','supported-illegal')
                if loss or error:
                    regressions.append({'arm':arm,'split':split,'artifact':e['artifact'],'loss_of_prior_support':loss,'incorrect_supported_decision':error,
                        'before_classification':old['classification'],**{k:row[k] for k in ('fixture','fen','move','label','classification','truth_value','proof_id','proof_refs','decision_ref','evidence_ids','dependence_groups','root_cause','promotion_selection')}})
            changes[arm][split]={'lost_prior_supported_decisions':lost,'incorrect_supported_decisions':wrong,'new_supported_decisions':added,
                'recall_delta_95_percentile_interval':delta['recall_delta_95_percentile_interval'],'exact_set_delta_95_percentile_interval':delta['exact_set_delta_95_percentile_interval'],'clusters':delta['clusters']}
            if calibrator and split!='cycle8-validation':
                calibration[arm][split]={}
                for category,rows in [('all',report['rows']),('in-board',[r for r in report['rows'] if r['destination_exists']]),('promotion',[r for r in report['rows'] if r['promotion']])]:
                    scored={**report,'rows':rows};calibration[arm][split][category]={'candidates':len(rows),**score_calibration(scored,calibrator),
                        'raw_strength_brier':sum((r['truth_value']['strength']-r['label'])**2 for r in rows)/len(rows) if rows else None,
                        'confidence_bins':{str(i):{'n':len(g),'wrong_supported':sum((r['classification']=='supported-legal' and not r['label']) or (r['classification']=='supported-illegal' and r['label']) for r in g)} for i in range(10) if (g:=[r for r in rows if min(9,int(r['truth_value']['confidence']*10))==i])}}
            if arm in ('C8-promotion-relative','C8-no-promotion-training','C8-frozen'):
                unknown=[r for r in report['rows'] if r['classification']=='unknown']
                unknowns[arm+'-'+split]={'unknown':len(unknown),'legal_unknown':sum(r['label'] for r in unknown),'multi_label_categories':dict(Counter(c for r in unknown for c in unknown_categories(r)))}
                if split in ('cycle7-independent-games','cycle8-combination-holdout'):
                    for category,selected in [('success',[r for r in report['rows'] if r['label'] and r['classification']=='supported-legal'][:5]),('unresolved',[r for r in unknown if r['label']][:5])]:
                        representatives += [{'arm':arm,'split':split,'kind':category,**example(report,r)} for r in selected]
            print(arm,split,'analyzed',flush=True)
    write_json(out/'comparison.json',summaries);write_json(out/'paired-summary.json',changes)
    write_json(out/'calibration.json',{'scope':'Validation-only empirical mapping. No changes to native STVs, decisions, confidence or thresholds. Candidate-level diagnostics include correlated rows; no confidence interval or calibrated probability guarantee.', 'arms':calibration})
    write_json(out/'unknown-analysis.json',unknowns)
    pack(out/'proofs/all-regressions.json.xz',regressions);pack(out/'proofs/representative-examples.json.xz',representatives)
    write_json(out/'regression-summary.json',{'count':len(regressions),'by_arm':dict(Counter(r['arm'] for r in regressions)),
        'scope':'Includes research arms, intentionally destructive ablations and strict-mode abstentions; default eligibility is separate.'})
    dataset_audit(out)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',required=True);run(parser.parse_args().out)
