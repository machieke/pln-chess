"""Offline reference panel and separate native supplied-branch results."""
import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from pln_chess.common import ROOT,digest,read_json
from pln_chess.pln import Runtime
from pln_chess.cycle13.api import PreferenceOptions,PreferenceSession
from pln_chess.cycle14.api import preference_summary
from pln_chess.cycle14.temporal import analyze_continuations
from evaluation.cycle14_archive import OfflineAuditStore as ProofStore, archive_census
from training.cycle14_labels import worker,atomic_json
from evaluation.cycle14_profile import models
from evaluation.cycle14_preferences import load_model
from evaluation.cycle14_metrics import counts,clustered_intervals
from evaluation.cycle7_io import pack
from scripts.cycle9_baseline import sha


def labels(out,workers=1):
    out=Path(out).resolve();data=read_json(out/'datasets/response-plans.json');generation='responses-g1'
    rows=[r for r in data['comparisons'] if r['primary_label_reuse'] is None]
    tasks=[(str(out),generation,r,data['hash'],'temporal') for r in rows]
    with ProcessPoolExecutor(max_workers=workers) as pool:records=list(pool.map(worker,tasks))
    previous={r['id']:r for r in read_json(out/'labels/temporal-g1/index.json')['records']}
    records.extend(dict(previous[r['primary_label_reuse']],id=r['id'],reused_observation_id=r['primary_label_reuse'])
        for r in data['comparisons'] if r['primary_label_reuse'])
    atomic_json(out/'labels'/generation/'index.json',dict(passed=True,source_hash=data['hash'],records=records,
        N_new_analyses=len(rows),N_reused=len(records)-len(rows),counts=dict(Counter(r['label'] for r in records)),
        actual_additional_reported_nodes=sum(r['actual_reported_nodes'] for r in records if not r.get('reused_observation_id')),
        independent_groups=data['independent_groups'],branch_crossproducts_are_dependent=True))


def run(out):
    out=Path(out);runtime=Runtime(timeout=900);registry=read_json(out/'model/registry.json')
    loaded=models(runtime);loaded['preference_model']=load_model(out,registry['models'][registry['primary_temporal']],runtime)
    plans=read_json(out/'datasets/response-plans.json');labels={r['id']:r for r in read_json(out/'labels/responses-g1/index.json')['records']}
    options=PreferenceOptions(timeout_seconds=900);results=[]
    for plan in plans['records']:
        target=out/'responses'/plan['id'];receipt=target/'result.json'
        identity=dict(plan_hash=digest(plan),models={k:m.version for k,m in loaded.items()},driver_sha256=sha(__file__),
            archive_policy_sha256=sha(ROOT/'evaluation/cycle14_archive.py'))
        if receipt.exists():
            row=read_json(receipt);assert row['identity']==identity;results.append(row);continue
        with ProofStore() as store:
            result=analyze_continuations(plan['fen'],plan['branches'],**loaded,runtime=runtime,
                options=options,session=PreferenceSession(runtime),store=store,history=plan['history'],
                source='cycle14-registered-response/'+plan['id'],horizons=(2,3),selection_provenance=plan['response_selection'])
            archive=store.archive(result['proof_root']);pack(target/'archive.json.xz',archive)
        assert result['global_robust_preference'] is None and not result['automatic_move_selection']
        comparisons=[]
        for c in result['comparisons']:
            a,b=c['branches']['A'],c['branches']['B'];identifier=plan['id']+f"-response-A{a}-B{b}-ply{c['horizon']}"
            comparisons.append(dict(id=identifier,horizon=c['horizon'],label=labels[identifier]['label'],
                reference_evidence_id=labels[identifier]['evidence_id'],prediction=c['preference'],
                dependence_group=plan['dependence_group'],branch_indices=c['branches']))
        by_horizon={h:{r['prediction']['status'] for r in comparisons if r['horizon']==h} for h in (2,3)}
        row=dict(identity=identity,id=plan['id'],summary=result,comparisons=comparisons,coverage=plan['coverage'],
            opposed_supported_branches={str(h):{'A-preferred','B-preferred'}<=states for h,states in by_horizon.items()},
            archive_sha256=sha(target/'archive.json.xz'),archive_audit=archive_census(archive),independent_groups=1,global_preference=None)
        atomic_json(receipt,row);results.append(row);print('C14 RESPONSE PANEL',plan['id'],flush=True)
    diagnostics=[]
    for case in read_json(out/'datasets/response-panel-registration.json')['diagnostic_cases']:
        with ProofStore() as store:
            result=analyze_continuations(case['fen'],case['branches'],**loaded,runtime=runtime,options=options,
                session=PreferenceSession(runtime),store=store,horizons=(2,3),source=case['id'],selection_provenance='Controlled diagnostic')
            archive=store.archive(result['proof_root']);pack(out/'responses/diagnostics'/(case['id']+'.json.xz'),archive)
            diagnostics.append(dict(case=case,summary=result,archive_audit=archive_census(archive)))
    assert diagnostics[0]['summary']['branch_coverage']['A'][0]['diagnostic_only']
    assert all(row['missing_horizons'] for rows in diagnostics[1]['summary']['branch_coverage'].values() for row in rows)
    # Three branches are a hard configurable interface bound, not a search tree.
    case=read_json(out/'datasets/response-panel-registration.json')['diagnostic_cases'][1]
    try:
        with ProofStore() as store:analyze_continuations(case['fen'],{'A':case['branches']['A']*4,'B':case['branches']['B']},**loaded,runtime=runtime,options=options,store=store)
    except ValueError:rejected_four=True
    else:rejected_four=False
    assert rejected_four
    pack(out/'responses/diagnostics.json.xz',diagnostics)
    all_rows=[r for result in results for r in result['comparisons']]
    atomic_json(out/'responses/summary.json',dict(passed=True,independent_groups=len(results),branch_comparisons=len(all_rows),
        counts=counts(all_rows),intervals=clustered_intervals(all_rows),
        opposed_supported_panels=sum(any(r['opposed_supported_branches'].values()) for r in results),
        incomplete_endpoint_comparisons=sum(r['prediction']['status']=='incomplete' for r in all_rows),
        diagnostic_branch_occurrences=sum(row['diagnostic_only'] for r in results for rows in r['summary']['branch_coverage'].values() for row in rows),
        unknown_legality_branch_occurrences=sum(row['legality_unknown'] for r in results for rows in r['summary']['branch_coverage'].values() for row in rows),
        supported_illegal_branch_occurrences=sum(row['supported_illegal'] for r in results for rows in r['summary']['branch_coverage'].values() for row in rows),
        known_unexamined_replies=sum(v['unexamined_legal_replies'] for r in results for v in r['coverage'].values()),
        diagnostics=[dict(id=r['case']['id'],coverage=r['summary']['branch_coverage']) for r in diagnostics],
        more_than_three_responses_rejected=rejected_four,global_robust_preference=None,
        offline_archive_policy_sha256=sha(ROOT/'evaluation/cycle14_archive.py'),
        panels_exceeding_interactive_archive_budget=sum(not r['archive_audit']['within_interactive_default_limit'] for r in results),
        selection_policy=plans['records'][0]['response_selection'],
        scope='Separate conditional predictions on supplied teacher and hash-sampled branches. No average, product, worst-case robust native conclusion, or exhaustive-response assertion.'))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('stage',choices=('labels','run'));parser.add_argument('--out',default='artifacts/cycle14');parser.add_argument('--workers',type=int,default=1)
    args=parser.parse_args();labels(args.out,args.workers) if args.stage=='labels' else run(args.out)
