from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
import os
from pln_chess.common import ROOT,read_json,write_json
from pln_chess.api import explain_move,infer_moves,train,compare_transforms,import_model
from pln_chess.pln import Runtime,NativeError
from pln_chess.learning import Model
from pln_chess.inference import Options
from pln_chess.domain import Position


def main(argv=None):
    cycle8_out=Path(os.environ.get('C8_OUT',ROOT/'artifacts/cycle8'))
    latest=cycle8_out/'model/C8-default.json'
    if not latest.exists():latest=ROOT/'artifacts/cycle7/model/C7-default.json'
    if not latest.exists():latest=ROOT/'artifacts/cycle6/model/C6-full.json'
    default_checkpoint=latest if latest.exists() else ROOT/'artifacts/model.json'
    from pln_chess.cycle12.acceptance import default_checkpoint as verified_default
    default_checkpoint=verified_default(default_checkpoint)
    parser=argparse.ArgumentParser(prog='pln-chess',description='Piece-relative native PLN research inspector')
    sub=parser.add_subparsers(dest='command',required=True)
    p=sub.add_parser('concept-inspect');p.add_argument('--input',required=True);p.add_argument('--output')
    p=sub.add_parser('field-evolution');p.add_argument('--input',required=True);p.add_argument('--output')
    p=sub.add_parser('field-inspect');p.add_argument('--fen',required=True);p.add_argument('--field-checkpoint');p.add_argument('--piece')
    p.add_argument('--family',choices=('all','geometry','attack','defense','mobility','king-exposure'),default='all');p.add_argument('--move');p.add_argument('--history')
    p.add_argument('--legal-mode',choices=('operational','strict','experimental'),default='operational')
    p.add_argument('--max-invocations',type=int,default=100000);p.add_argument('--timeout',type=float,default=180);p.add_argument('--output')
    p=sub.add_parser('history-claims');p.add_argument('--input',required=True);p.add_argument('--output')
    p=sub.add_parser('external-report');p.add_argument('--section',choices=('summary','provenance','failures','calibration','comparisons','dependence','temporal','performance','identity','architecture'),default='summary')
    p.add_argument('--arm',choices=('frozen','small','large','temporal'),default='frozen');p.add_argument('--output')
    p=sub.add_parser('history-import-pgn');p.add_argument('--input',required=True);p.add_argument('--source',required=True);p.add_argument('--limit',type=int,default=1000);p.add_argument('--output',required=True)
    p=sub.add_parser('history-replay');p.add_argument('--input');p.add_argument('--game-id');p.add_argument('--ply',type=int);p.add_argument('--output')
    p=sub.add_parser('compare-external');p.add_argument('--fen',required=True);p.add_argument('--move',required=True);p.add_argument('--mode',choices=('operational','strict','experimental'),default='operational');p.add_argument('--history');p.add_argument('--output')
    p=sub.add_parser('research-report');p.add_argument('--section',choices=('summary','calibration','failures','performance','temporal','identity'),default='summary');p.add_argument('--output')
    p=sub.add_parser('calibration-export');p.add_argument('--output',required=True)
    p=sub.add_parser('temporal-inspect-v9');p.add_argument('--fen',required=True);p.add_argument('--mode',choices=('fen-only','trusted-metadata','event-backed'),default='fen-only');p.add_argument('--history')
    p=sub.add_parser('migrate-model');p.add_argument('--checkpoint',default=str(ROOT/'artifacts/cycle5/model/C5-full.json'));p.add_argument('--output',required=True)
    p=sub.add_parser('composition-audit');p.add_argument('--output',default=str(ROOT/'artifacts/cycle5/native-probes/cli-audit.json'))
    p=sub.add_parser('temporal-inspect');p.add_argument('--fen',required=True);p.add_argument('--mode',choices=('fen-only','trusted-metadata','event-backed'),default='fen-only');p.add_argument('--history')
    p=sub.add_parser('compare-models');p.add_argument('--fen',required=True);p.add_argument('--move',required=True)
    p.add_argument('--before',default=str(ROOT/'artifacts/cycle4/model/C4-full.json'));p.add_argument('--after',default=str(ROOT/'artifacts/cycle5/model/C5-full.json'))
    p=sub.add_parser('compare-cycles');p.add_argument('--fen',required=True);p.add_argument('--move',required=True);p.add_argument('--checkpoint',default=str(ROOT/'artifacts/cycle7/model/C7-default.json'));p.add_argument('--mode',choices=('operational','strict','experimental'),default='operational')
    p=sub.add_parser('compare-generations');p.add_argument('--fen',required=True);p.add_argument('--move',required=True);p.add_argument('--checkpoint',default=str(cycle8_out/'model/C8-promotion-relative.json'));p.add_argument('--mode',choices=('operational','strict','experimental'),default='operational')
    p=sub.add_parser('cycle4');p.add_argument('--action',choices=('train','evaluate','diagnose','audit'),default='evaluate')
    p.add_argument('--dataset',default=str(ROOT/'artifacts/cycle4/datasets/dataset.json'));p.add_argument('--split',default='structural-combination')
    p.add_argument('--checkpoint',default=str(ROOT/'artifacts/cycle4/model/C4-full.json'));p.add_argument('--output')
    p=sub.add_parser('analyze-batch');p.add_argument('--input',required=True);p.add_argument('--output',required=True)
    p.add_argument('--checkpoint',default=str(ROOT/'artifacts/cycle4/model/C4-full.json'))
    p=sub.add_parser('cycle3');p.add_argument('--action',choices=('train','evaluate','audit'),default='evaluate')
    p.add_argument('--dataset',default=str(ROOT/'artifacts/cycle3/dataset.json'));p.add_argument('--split',default='challenge')
    p.add_argument('--checkpoint',default=str(ROOT/'artifacts/cycle3/C3-full-model.json'));p.add_argument('--induction',action='store_true')
    p=sub.add_parser('counterfactual');p.add_argument('--fen',required=True);p.add_argument('--move',required=True)
    p.add_argument('--operation',choices=('add-blocker','remove-piece','move-piece','color-flip','remove-right'))
    p.add_argument('--family',choices=('all','geometry','destination','ray','boundary','exposure','temporal'))
    p.add_argument('--square');p.add_argument('--target');p.add_argument('--right',default='K')
    p.add_argument('--checkpoint',default=str(ROOT/'artifacts/cycle3/C3-full-model.json'))
    p=sub.add_parser('cycle2'); p.add_argument('--dataset',default=str(ROOT/'artifacts/cycle2/dataset.json'))
    p.add_argument('--action',choices=('train','evaluate','audit'),default='evaluate'); p.add_argument('--split',default='heldout-transfer')
    p.add_argument('--induction',action='store_true'); p.add_argument('--checkpoint',default=str(ROOT/'artifacts/cycle2/B1-model.json'))
    audit=sub.add_parser('runtime-audit'); audit.add_argument('--output',default=str(ROOT/'artifacts/runtime-audit.json'))
    for name in ('infer','inspect'):
        p=sub.add_parser(name); p.add_argument('--fen',required=True); p.add_argument('--checkpoint',default=str(default_checkpoint))
        p.add_argument('--format',choices=('json','text'),default='json' if name=='infer' else 'text')
        p.add_argument('--mode',choices=('operational','strict','experimental'))
        p.add_argument('--max-invocations',type=int,default=20000); p.add_argument('--timeout',type=float,default=60)
        p.add_argument('--temporal-mode',choices=('fen-only','trusted-metadata','event-backed'),default='fen-only')
        if name=='inspect':p.add_argument('--move',required=True);p.add_argument('--history')
    p=sub.add_parser('train'); p.add_argument('--config',default=str(ROOT/'configs/training.json'))
    p=sub.add_parser('evaluate'); p.add_argument('--split',default='heldout-transfer'); p.add_argument('--checkpoint',default=str(default_checkpoint))
    p.add_argument('--mode',choices=('operational','strict','experimental'));p.add_argument('--dataset');p.add_argument('--output');p.add_argument('--variant',choices=('C5-full','C5-abstract-only','C5-no-new-negatives'))
    p=sub.add_parser('invariance'); p.add_argument('--fixture',default='transfer-source'); p.add_argument('--transform',choices=('translate',),default='translate')
    p.add_argument('--offset',default='1,0'); p.add_argument('--checkpoint',default=str(default_checkpoint))
    p=sub.add_parser('benchmark'); p.add_argument('--config',default=str(ROOT/'configs/benchmark.json'));p.add_argument('--mode',choices=('operational','strict','experimental'));p.add_argument('--checkpoint');p.add_argument('--positions');p.add_argument('--output')
    p=sub.add_parser('report'); p.add_argument('--output',default=str(ROOT/'artifacts/final-report.md'))
    p=sub.add_parser('replay'); p.add_argument('--ledger',required=True); p.add_argument('--output',required=True); p.add_argument('--through',type=int)
    p.add_argument('--representation',choices=('full','hierarchical','C3-full','C4-full','C5-full'),default='full'); p.add_argument('--induction',action='store_true')
    p=sub.add_parser('hypothesis'); p.add_argument('id'); p.add_argument('--checkpoint',default=str(default_checkpoint))
    p=sub.add_parser('serve'); p.add_argument('--port',type=int,default=8765); p.add_argument('--checkpoint',default=str(default_checkpoint))
    args=parser.parse_args(argv)
    try:
        if args.command in ('concept-inspect','field-evolution'):
            from pln_chess.cycle12.api import inspector_fields, inspector_evolution
            supplied=read_json(args.input)
            result=inspector_fields(supplied) if args.command=='concept-inspect' else inspector_evolution(supplied)
            if args.output:write_json(args.output,result)
        elif args.command=='field-inspect':
            from pln_chess.api import inspect_fields
            from pln_chess.cycle11.fields.inference import FieldOptions
            result=inspect_fields(args.fen,args.field_checkpoint,family=args.family,piece=args.piece,candidate=args.move,
                history=read_json(args.history) if args.history else None,legal_mode=args.legal_mode,
                options=FieldOptions(max_native_invocations=args.max_invocations,timeout_seconds=args.timeout))
            if args.output:write_json(args.output,result)
        elif args.command=='history-claims':
            from pln_chess.api import replay_history_claims
            supplied=read_json(args.input)
            result=replay_history_claims(**(supplied['input'] if supplied.get('schema')=='temporal-transport-v11' else supplied))
            if args.output:write_json(args.output,result)
        elif args.command=='external-report':
            from pln_chess.cycle10.diagnostics import report
            result=report(args.section,args.arm)
            if args.output:write_json(args.output,result)
        elif args.command=='history-import-pgn':
            from training.cycle10_import import import_pgn
            result=import_pgn(args.input,args.source,args.limit);write_json(args.output,result)
            result=dict(output=args.output,games=len(result['games']),complete_games=result['complete_games'],oracle_scope=result['oracle_scope'])
        elif args.command=='history-replay':
            from pln_chess.cycle10.temporal import replay,replay_game
            from pln_chess.cycle10.diagnostics import recorded_history
            if args.input:
                payload=read_json(args.input)
                if 'games' in payload:
                    games=payload['games']
                    if args.game_id:game=next((g for g in games if g['id']==args.game_id),None)
                    elif len(games)==1:game=games[0]
                    else:raise ValueError('Select a game ID when the prepared file contains multiple games')
                    if game is None:raise ValueError('Unknown prepared game ID')
                    from pln_chess.cycle8.model import PromotionModel
                    runtime=Runtime();model=PromotionModel.load(cycle8_out/'model/C8-promotion-relative.json',runtime)
                    result=replay_game(game,len(game['moves']) if args.ply is None else args.ply,model.version,runtime.version)
                else:
                    supplied=payload['input'] if payload.get('schema')=='temporal-transport-v10' else payload
                    if args.ply is not None:
                        if not 0<=args.ply<=len(supplied['moves']):raise ValueError('Ply is outside the supplied history')
                        supplied={**supplied,'moves':supplied['moves'][:args.ply],'complete':False,'expected_fen':None}
                    result=replay(**supplied)
            elif args.game_id:result=recorded_history(args.game_id,args.ply)
            else:raise ValueError('Supply an event JSON file or a recorded game ID')
            if args.output:write_json(args.output,result)
        elif args.command=='compare-external':
            from pln_chess.cycle10.api import compare_external
            result=compare_external(args.fen,args.move,args.mode,read_json(args.history) if args.history else None)
            if args.output:write_json(args.output,result)
        elif args.command in ('research-report','calibration-export'):
            from pln_chess.cycle9.diagnostics import report
            result=report('calibration' if args.command=='calibration-export' else args.section)
            if args.output:
                write_json(args.output,result);result={'output':args.output,'section':result['section'],'available':result['available']}
        elif args.command=='temporal-inspect-v9':
            from pln_chess.cycle9.temporal import inspect
            result=inspect(args.fen,args.mode,read_json(args.history) if args.history else None)
        elif args.command=='migrate-model':
            from pln_chess.cycle6.model import ModeModel
            result=ModeModel.migrate(Model.load(args.checkpoint,Runtime())).export(args.output)
        elif args.command=='composition-audit':
            from evaluation.cycle5_native import audit
            result=audit(args.output)
        elif args.command=='temporal-inspect':
            from pln_chess.cycle5.history import inspect
            result=inspect(args.fen,args.mode,read_json(args.history) if args.history else None)
        elif args.command=='compare-models':
            runtime=Runtime();result={'C4':explain_move(args.fen,args.move,args.before,runtime=runtime),'C5':explain_move(args.fen,args.move,args.after,runtime=runtime)}
        elif args.command=='compare-cycles':
            from pln_chess.cycle7.api import compare_cycles
            result=compare_cycles(args.fen,args.move,args.checkpoint,args.mode)
        elif args.command=='compare-generations':
            from pln_chess.cycle8.api import compare_generations
            result=compare_generations(args.fen,args.move,args.checkpoint,args.mode)
        elif args.command=='cycle4':
            if args.action=='audit':
                from evaluation.cycle4_native import audit
                result=audit(Path(args.output) if args.output else ROOT/'artifacts/cycle4/native-probes/cli-audit.json')
            elif args.action=='train':
                from pln_chess.cycle4.model import train as factored_train
                data=read_json(args.dataset)
                model=factored_train([r for r in data['examples'] if r['split']=='train'],args.checkpoint,
                                    ledger_path=ROOT/'artifacts/cycle4/cli-evidence.jsonl')
                result={'version':model.version,'hypotheses':len(model.hypotheses)}
            else:
                from evaluation.cycle4 import evaluate
                runtime=Runtime();path=Path(args.output) if args.output else ROOT/f'artifacts/cycle4/evaluation/cli-{args.split}.json.xz'
                report=evaluate(read_json(args.dataset),Model.load(args.checkpoint,runtime),args.split,runtime,path,diagnostics=args.action=='diagnose')
                result={'metrics':report['metrics'],'artifact':str(path),'oracle_scope':'Evaluation only'}
        elif args.command=='analyze-batch':
            from pln_chess.api import analyze_batch
            result=analyze_batch(read_json(args.input),args.checkpoint);write_json(args.output,result)
            result={'output':args.output,'candidates':len(result['results']),'unresolved':len(result['unresolved'])}
        elif args.command=='counterfactual':
            if args.family:
                from pln_chess.cycle5.inference import counterfactual
                runtime=Runtime();result=counterfactual(args.fen,args.move,Model.load(args.checkpoint,runtime),runtime=runtime)
                if args.family!='all':result['without']={args.family:result['without'][args.family]}
            else:
                if not args.operation:raise ValueError('Specify --operation or --family')
                from pln_chess.cycle3.counterfactual import compare
                result=compare(args.fen,args.move,args.checkpoint,args.operation,args.square,args.target,right=args.right)
        elif args.command=='cycle3':
            if args.action=='audit':
                from evaluation.cycle3_native import audit
                result=audit(ROOT/'artifacts/cycle3/native-probes.json')
            elif args.action=='train':
                from pln_chess.cycle3.model import train as relational_train
                data=read_json(args.dataset)
                model=relational_train([r for r in data['examples'] if r['split']=='train'],args.checkpoint,
                                       {'induction':args.induction},ledger_path=ROOT/'artifacts/cycle3/cli-evidence.jsonl')
                result={'version':model.version,'hypotheses':len(model.hypotheses),'induced':len(model.induction)}
            else:
                from evaluation.cycle3 import evaluate
                runtime=Runtime();report=evaluate(read_json(args.dataset),Model.load(args.checkpoint,runtime),args.split,runtime,
                                                 ROOT/f'artifacts/cycle3/cli-{args.split}.json.gz')
                result=report['metrics']
        elif args.command=='cycle2':
            if args.action=='audit':
                from evaluation.cycle2_native import audit
                result=audit(ROOT/'artifacts/cycle2/native-probes.json')
            elif args.action=='train':
                from pln_chess.cycle2.model import train as train_hierarchy
                data=read_json(args.dataset)
                model=train_hierarchy([r for r in data['examples'] if r['split']=='train' and r.get('training_eligible',True)],args.checkpoint,
                                      {'induction':args.induction},ledger_path=ROOT/'artifacts/cycle2/cli-evidence.jsonl')
                result={'version':model.version,'hypotheses':len(model.hypotheses),'induced':len(model.induction)}
            else:
                from evaluation.cycle2 import evaluate as evaluate_hierarchy
                runtime=Runtime();result=evaluate_hierarchy(read_json(args.dataset),Model.load(args.checkpoint,runtime),args.split,runtime)
                write_json(ROOT/f'artifacts/cycle2/cli-{args.split}.json',result);result=result['metrics']
        elif args.command=='runtime-audit':
            from pln_chess.pln.audit import runtime_audit
            r=runtime_audit(args.output)
            result={'passed':r['passed'],'runtime':r['runtime']['pln'],'tests':r['tests'],'blockers':r['blockers']}
        elif args.command in ('infer','inspect'):
            options=Options(max_native_invocations=args.max_invocations,timeout_seconds=args.timeout)
            if read_json(args.checkpoint).get('schema')==8:
                from pln_chess.cycle8.inference import Cycle8Options
                options=Cycle8Options(mode=args.mode,max_native_invocations=args.max_invocations,timeout_seconds=args.timeout,temporal_mode=args.temporal_mode)
            elif read_json(args.checkpoint).get('schema')==7:
                from pln_chess.cycle7.inference import Cycle7Options
                options=Cycle7Options(mode=args.mode,max_native_invocations=args.max_invocations,timeout_seconds=args.timeout,temporal_mode=args.temporal_mode)
            elif read_json(args.checkpoint).get('schema')==6:
                from pln_chess.cycle6.inference import Cycle6Options
                options=Cycle6Options(mode=args.mode,max_native_invocations=args.max_invocations,timeout_seconds=args.timeout,temporal_mode=args.temporal_mode)
            elif args.mode is not None:raise ValueError('--mode requires a Cycle 6 checkpoint; use migrate-model')
            elif read_json(args.checkpoint).get('schema')==5:
                from pln_chess.cycle5.inference import Cycle5Options
                options=Cycle5Options(max_native_invocations=args.max_invocations,timeout_seconds=args.timeout,temporal_mode=args.temporal_mode)
            result=explain_move(args.fen,args.move,args.checkpoint,options,temporal_evidence=read_json(args.history) if args.history else None) if args.command=='inspect' else infer_moves(args.fen,args.checkpoint,options)
            if args.format=='text':
                if result.get('mode'):print(f"Mode {result['mode']}; policy {result['policy_version']}")
                print(Position.from_fen(args.fen).board_text())
                items=[result['candidate']] if args.command=='inspect' else result['candidates']
                for item in items:
                    print(f"\n{item['move']}: {item['classification']} {item['legal_move_truth_value']}")
                    if item.get('proof_status'):print('Proof status:',item['proof_status'])
                    if args.command=='inspect':
                        print('Relative features:',json.dumps(item['observations']['context'],indent=2))
                        if item.get('factored_premises'):
                            print('Factored premises:',json.dumps(item['factored_premises'],indent=2))
                            print('Decision policy:',item.get('decision_policy'))
                        for step in item['proof_trace']:
                            print(f"{step['id']}: {step['operator']} -> {step['conclusion']} {step['truth_value']}")
                        print('Evidence IDs:',', '.join(item['evidence_ids']))
                        print('Coverage:',item['status'],'; '.join(item['gaps']))
                print(f"Runtime {result['runtime_version']}; model {result['model_version']}; truncated={result['truncated']}")
                return 2 if result['truncated'] else 0
        elif args.command=='train':
            config=read_json(args.config); data=read_json(ROOT/config['dataset'])
            rows=[r for r in data['examples'] if r['split']==config['split']]
            model=train(rows,ROOT/config['checkpoint'],config,ledger_path=ROOT/config['ledger'])
            result={'version':model.version,'hypotheses':len(model.hypotheses),'records':model.training_report['records'],
                    'native_invocations':model.training_report['native_invocations']}
        elif args.command=='replay':
            from pln_chess.evidence import Ledger
            model=train(Ledger(args.ledger),args.output,{'through_sequence':args.through,'variant':args.representation,'induction':args.induction})
            result={'version':model.version,'through_sequence':args.through,'hypotheses':len(model.hypotheses)}
        elif args.command=='hypothesis': result=import_model(args.checkpoint).inspect_hypothesis(args.id)
        elif args.command=='invariance':
            fixture=next(p for p in read_json(ROOT/'fixtures/dataset.json')['positions'] if p['id']==args.fixture)
            result=compare_transforms(fixture['fen'],tuple(map(int,args.offset.split(','))),args.checkpoint,fixture['focus_move'])
        elif args.command=='evaluate':
            # Development command lazily accesses the isolated evaluation package.
            runtime=Runtime();model=Model.load(args.checkpoint,runtime)
            if model.schema==8:
                from evaluation.cycle8 import evaluate
                from pln_chess.cycle8.inference import Cycle8Options,default_mode
                result=evaluate(read_json(args.dataset or cycle8_out/'datasets/dataset.json'),model,args.split,runtime,Cycle8Options(mode=args.mode or default_mode(model)),Path(args.output) if args.output else cycle8_out/f'evaluation/cli-{args.split}.json.xz')
            elif model.schema==7:
                from evaluation.cycle7 import evaluate
                from pln_chess.cycle7.inference import Cycle7Options,default_mode
                result=evaluate(read_json(args.dataset or ROOT/'artifacts/cycle7/datasets/dataset.json'),model,args.split,runtime,Path(args.output) if args.output else ROOT/f'artifacts/cycle7/evaluation/cli-{args.split}.json.xz',Cycle7Options(mode=args.mode or default_mode(model)))
            elif model.schema==6:
                from evaluation.cycle6 import evaluate
                from pln_chess.cycle6.inference import Cycle6Options,default_mode
                result=evaluate(read_json(args.dataset or ROOT/'artifacts/cycle6/datasets/dataset.json'),model,args.split,runtime,Path(args.output) if args.output else ROOT/f'artifacts/cycle6/evaluation/cli-{args.split}.json.xz',Cycle6Options(mode=args.mode or default_mode(model)))
            elif args.mode is not None:raise ValueError('--mode requires a Cycle 6 checkpoint')
            elif model.schema==5:
                from evaluation.cycle4 import evaluate
                if args.variant:model.variant=args.variant
                result=evaluate(read_json(args.dataset or ROOT/'artifacts/cycle5/datasets/dataset.json'),model,args.split,runtime,Path(args.output) if args.output else ROOT/f'artifacts/cycle5/evaluation/cli-{args.split}.json.xz',diagnostics=True)
            else:
                from evaluation.experiments import evaluate
                result=evaluate(read_json(args.dataset or ROOT/'fixtures/dataset.json'),model,args.split,runtime)
                write_json(args.output or ROOT/f'artifacts/evaluation-{args.split}.json',result)
            result={'split':result['split'],'metrics':result['metrics'],**({k:result[k] for k in ('mode','model_version','runtime_version')} if model.schema in (6,7,8) else {})}
        elif args.command=='benchmark':
            from evaluation.experiments import benchmark
            config=read_json(args.config); runtime=Runtime()
            checkpoint=args.checkpoint or (str(default_checkpoint) if args.mode else ROOT/config['checkpoint'])
            model=Model.load(checkpoint,runtime)
            if model.schema==8:
                from evaluation.cycle8_benchmark import run
                from pln_chess.cycle8.inference import default_mode
                result={'records':run(cycle8_out,model.variant,checkpoint=checkpoint,fixtures=read_json(args.positions) if args.positions else None,mode=args.mode or default_mode(model))}
                if args.output:write_json(args.output,result)
            elif model.schema==7:
                from evaluation.cycle7_cli import benchmark
                result=benchmark(model,args.positions,args.output,args.mode)
            elif model.schema==6:
                from evaluation.cycle6_benchmark import benchmark as mode_benchmark
                from pln_chess.cycle6.inference import default_mode
                result=mode_benchmark(checkpoint,read_json(args.positions or ROOT/'artifacts/cycle5/benchmarks/positions.json'),args.output or ROOT/'artifacts/cycle6/benchmarks/cli.json',args.mode or default_mode(model))
            elif args.mode is not None:raise ValueError('--mode requires a Cycle 6 checkpoint')
            else:
                result=benchmark(read_json(ROOT/config['dataset']),model,runtime)
                write_json(args.output or ROOT/config['output'],result)
        elif args.command=='report':
            from evaluation.reporting import final_report
            result={'output':str(final_report(args.output))}
        elif args.command=='serve':
            from pln_chess.cli.web import serve
            serve(args.port,args.checkpoint); return 0
        print(json.dumps(result,indent=2,sort_keys=True))
        return 2 if isinstance(result,dict) and result.get('truncated') else 0
    except (ValueError,NativeError,FileNotFoundError,StopIteration) as error:
        print(f'pln-chess: {error}',file=sys.stderr); return 2

if __name__=='__main__': raise SystemExit(main())
