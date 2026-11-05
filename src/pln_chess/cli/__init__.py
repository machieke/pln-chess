from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
from pln_chess.common import ROOT,read_json,write_json
from pln_chess.api import explain_move,infer_moves,train,compare_transforms,import_model
from pln_chess.pln import Runtime,NativeError
from pln_chess.learning import Model
from pln_chess.inference import Options
from pln_chess.domain import Position


def main(argv=None):
    parser=argparse.ArgumentParser(prog='pln-chess',description='Piece-relative native PLN research inspector')
    sub=parser.add_subparsers(dest='command',required=True)
    p=sub.add_parser('cycle3');p.add_argument('--action',choices=('train','evaluate','audit'),default='evaluate')
    p.add_argument('--dataset',default=str(ROOT/'artifacts/cycle3/dataset.json'));p.add_argument('--split',default='challenge')
    p.add_argument('--checkpoint',default=str(ROOT/'artifacts/cycle3/C3-full-model.json'));p.add_argument('--induction',action='store_true')
    p=sub.add_parser('counterfactual');p.add_argument('--fen',required=True);p.add_argument('--move',required=True)
    p.add_argument('--operation',required=True,choices=('add-blocker','remove-piece','move-piece','color-flip','remove-right'))
    p.add_argument('--square');p.add_argument('--target');p.add_argument('--right',default='K')
    p.add_argument('--checkpoint',default=str(ROOT/'artifacts/cycle3/C3-full-model.json'))
    p=sub.add_parser('cycle2'); p.add_argument('--dataset',default=str(ROOT/'artifacts/cycle2/dataset.json'))
    p.add_argument('--action',choices=('train','evaluate','audit'),default='evaluate'); p.add_argument('--split',default='heldout-transfer')
    p.add_argument('--induction',action='store_true'); p.add_argument('--checkpoint',default=str(ROOT/'artifacts/cycle2/B1-model.json'))
    audit=sub.add_parser('runtime-audit'); audit.add_argument('--output',default=str(ROOT/'artifacts/runtime-audit.json'))
    for name in ('infer','inspect'):
        p=sub.add_parser(name); p.add_argument('--fen',required=True); p.add_argument('--checkpoint',default=str(ROOT/'artifacts/model.json'))
        p.add_argument('--format',choices=('json','text'),default='json' if name=='infer' else 'text')
        p.add_argument('--max-invocations',type=int,default=20000); p.add_argument('--timeout',type=float,default=60)
        if name=='inspect': p.add_argument('--move',required=True)
    p=sub.add_parser('train'); p.add_argument('--config',default=str(ROOT/'configs/training.json'))
    p=sub.add_parser('evaluate'); p.add_argument('--split',default='heldout-transfer'); p.add_argument('--checkpoint',default=str(ROOT/'artifacts/model.json'))
    p=sub.add_parser('invariance'); p.add_argument('--fixture',default='transfer-source'); p.add_argument('--transform',choices=('translate',),default='translate')
    p.add_argument('--offset',default='1,0'); p.add_argument('--checkpoint',default=str(ROOT/'artifacts/model.json'))
    p=sub.add_parser('benchmark'); p.add_argument('--config',default=str(ROOT/'configs/benchmark.json'))
    p=sub.add_parser('report'); p.add_argument('--output',default=str(ROOT/'artifacts/final-report.md'))
    p=sub.add_parser('replay'); p.add_argument('--ledger',required=True); p.add_argument('--output',required=True); p.add_argument('--through',type=int)
    p.add_argument('--representation',choices=('full','hierarchical','C3-full'),default='full'); p.add_argument('--induction',action='store_true')
    p=sub.add_parser('hypothesis'); p.add_argument('id'); p.add_argument('--checkpoint',default=str(ROOT/'artifacts/model.json'))
    p=sub.add_parser('serve'); p.add_argument('--port',type=int,default=8765); p.add_argument('--checkpoint',default=str(ROOT/'artifacts/model.json'))
    args=parser.parse_args(argv)
    try:
        if args.command=='counterfactual':
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
            result=explain_move(args.fen,args.move,args.checkpoint,options) if args.command=='inspect' else infer_moves(args.fen,args.checkpoint,options)
            if args.format=='text':
                print(Position.from_fen(args.fen).board_text())
                items=[result['candidate']] if args.command=='inspect' else result['candidates']
                for item in items:
                    print(f"\n{item['move']}: {item['classification']} {item['legal_move_truth_value']}")
                    if args.command=='inspect':
                        print('Relative features:',json.dumps(item['observations']['context'],indent=2))
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
            from evaluation.experiments import evaluate
            runtime=Runtime(); result=evaluate(read_json(ROOT/'fixtures/dataset.json'),Model.load(args.checkpoint,runtime),args.split,runtime)
            write_json(ROOT/f'artifacts/evaluation-{args.split}.json',result)
            result={'split':result['split'],'metrics':result['metrics']}
        elif args.command=='benchmark':
            from evaluation.experiments import benchmark
            config=read_json(args.config); runtime=Runtime()
            result=benchmark(read_json(ROOT/config['dataset']),Model.load(ROOT/config['checkpoint'],runtime),runtime)
            write_json(ROOT/config['output'],result)
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
