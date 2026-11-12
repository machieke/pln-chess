"""Freeze root selection before outcomes; bind disclosed offline PV branches."""
import argparse
from collections import Counter
from pathlib import Path

from pln_chess.common import ROOT,digest,read_json
from training.cycle14_labels import atomic_json
from training.cycle14_reference import board_from_history


def register(out):
    out=Path(out);data=read_json(out/'datasets/source-pairs.json');config=read_json(ROOT/'configs/cycle14.json')
    selected=[]
    for split,count in config['temporal_groups'].items():
        rows=sorted((r for r in data['records'] if r['split']==split and r['generation']=='new-c14'),
            key=lambda r:digest(['c14-temporal-selection',config['seed'],r['id']]))
        if len(rows)<count:raise ValueError('Insufficient registered independent root groups')
        selected.extend(dict(id=r['id'],split=split,source_game=r['source_game'],dependence_group=r['dependence_group']) for r in rows[:count])
    payload=dict(schema='c14-temporal-root-registration-v1',source_hash=data['hash'],records=selected,
        counts=dict(Counter(r['split'] for r in selected)),horizons=[2,3],
        selection='Hash order over new independent roots only, before labels or predictions; retain missing/short branches.',
        branches='First three plies of each separately restricted 80,000-node candidate search, including shorter terminal PVs.',
        source_groups=len({r['dependence_group'] for r in selected}),reference_or_prediction_filtering=False)
    payload['hash']=digest(payload);atomic_json(out/'datasets/temporal-registration.json',payload)
    return payload


def bind(out):
    out=Path(out);registration=register(out);data=read_json(out/'datasets/source-pairs.json')
    sources={r['id']:r for r in data['records']};plans=[];missing=[]
    for selected in registration['records']:
        row=sources[selected['id']];path=out/'labels/immediate-g1/records'/(row['id']+'.json')
        if not path.exists():missing.append(row['id']);continue
        label=read_json(path);branches={s:label['selected_pv'].get(s,[]) for s in ('A','B')}
        for side,line in branches.items():
            if line and line[0]!=row['moves'][('A','B').index(side)]:raise ValueError('Candidate/PV mismatch')
            board_from_history({**row['history'],'moves':row['history']['moves']+line})
        plans.append({**row,'branches':branches,'response_source_evidence':label['evidence_id'],
            'response_selection':'Offline teacher-assisted single-root PV at 80,000 nodes; no PLN prediction or reference-direction filtering.',
            'short_branches':[s for s,line in branches.items() if len(line)<3],
            'independent_of_pln_predictions':True,'reference_legal_replay':True})
    if missing:raise ValueError(f'{len(missing)} registered raw candidate searches are still pending')
    historical=read_json(ROOT/'artifacts/cycle13/datasets/temporal-plans.json')['records']
    for old in historical:
        row=sources[old['id']]
        plans.append({**row,'branches':old['branches'],'response_source_evidence':old['response_source_evidence'],
            'response_selection':old['response_selection'],'short_branches':[],
            'independent_of_pln_predictions':True,'reference_legal_replay':True})
    payload=dict(schema='c14-temporal-plans-v1',registration_hash=registration['hash'],source_hash=data['hash'],
        records=plans,new_groups=len(registration['records']),historical_diagnostic_groups=len(historical),
        counts=dict(Counter(p['split'] for p in plans)),horizons=[2,3],
        short_branch_groups=sum(bool(p['short_branches']) for p in plans),maximum_primary_responses_per_candidate=1,
        exhaustive_response_coverage=False,optimal_response_claim=False)
    payload['hash']=digest(payload);atomic_json(out/'datasets/temporal-plans.json',payload)
    comparisons=[{**p,'plan_id':p['id'],'id':p['id']+f'-ply{h}','horizon':h} for p in plans for h in (2,3)]
    value=dict(schema='c14-temporal-comparisons-v1',plan_hash=payload['hash'],records=comparisons)
    value['hash']=digest(value);atomic_json(out/'datasets/temporal-comparisons.json',value)
    return payload


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',default='artifacts/cycle14')
    parser.add_argument('stage',choices=('register','bind'));args=parser.parse_args()
    result=(register if args.stage=='register' else bind)(args.out)
    print(result.get('counts'),flush=True)
