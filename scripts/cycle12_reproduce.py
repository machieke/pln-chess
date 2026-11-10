"""Complete clean-checkout Cycle 12 replay; no push or deployment."""
import argparse
import os
from pathlib import Path
import subprocess
import time
from pln_chess.common import ROOT, read_json, write_json
from scripts.cycle10_bootstrap import run as bootstrap
from scripts.cycle9_baseline import sha


def run(out,checkout,baseline,work,browser=True):
    out,checkout,baseline,work=(Path(p).resolve() for p in (out,checkout,baseline,work))
    for path in (out,checkout,baseline,work):
        if path.exists():raise ValueError('Use a new reproduction directory: '+str(path))
    if subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True):raise ValueError('Start from a committed, clean package')
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    out.mkdir(parents=True);bootstrap(out/'current-bootstrap',checkout,head)
    py=str(checkout/'.venv/bin/python');env=dict(os.environ,PLN_CHESS_ROOT=str(checkout),PYTHONPATH=f'{checkout}/src:{checkout}',TMPDIR='/dev/shm',C12_OUT=str(out))
    for key in ('C6_OUT','C7_OUT','C8_OUT','C9_OUT','C10_OUT','C11_OUT'):env.pop(key,None)
    commands=[]
    def command(name,args):
        log=out/'reproduction-logs'/f'{name}.txt';log.parent.mkdir(parents=True,exist_ok=True);started=time.time();argv=[py,*args]
        with log.open('w') as stream:result=subprocess.run(argv,cwd=checkout,env=env,stdout=stream,stderr=subprocess.STDOUT)
        commands.append(dict(name=name,argv=argv,cwd=str(checkout),source_head=head,started_unix=started,
            elapsed_seconds=time.time()-started,returncode=result.returncode,log=str(log.relative_to(out))))
        write_json(out/'reproduction-commands.json',commands)
        if result.returncode:raise RuntimeError(str(log))
        print('REPRODUCED',name,flush=True)
    command('unchanged-baseline',['-m','scripts.cycle12_baseline','--out',str(out/'baseline'),'--snapshot',str(baseline)])
    for name,module in [('concept-data','training.cycle12_data'),('concept-controls','training.cycle12_controls'),
        ('sequences','training.cycle12_sequences'),('dataset-audit','evaluation.cycle12_data_audit')]:
        command(name,['-m',module,'--out',str(out)])
    command('registered-studies',['-m','scripts.cycle12_studies','--out',str(out)])
    command('candidate-population',['-m','scripts.cycle12_legal_review','--out',str(out),'--source',str(checkout)])
    command('candidate-recoveries',['-m','evaluation.cycle12_legal_recovery','--out',str(out)])
    command('candidate-temporal-negative-controls',['-m','evaluation.cycle12_legal_controls','--out',str(out)])
    command('current-gates',['-m','scripts.cycle12_regression','--out',str(out),'--source',str(checkout)])
    command('native-boundary',['-m','evaluation.cycle12_delivery','boundary','--out',str(out)])
    command('fresh-research-replay',['-m','scripts.cycle12_research_replay','--out',str(out),'--source',str(checkout)])
    command('legal-promotion',['-m','evaluation.cycle12_delivery','acceptance','--out',str(out)])
    command('accepted-default-tests',['-m','scripts.cycle12_final_checks','--out',str(out)])
    command('new-cli-contracts',['-m','scripts.cycle12_cli_verify','--out',str(out)])
    command('performance',['-m','evaluation.cycle12_performance','--out',str(out)])
    if browser:command('browser',['-m','scripts.cycle12_ui_verify','--out',str(out),'--work',str(work)])
    else:write_json(out/'browser-not-executed.json',dict(executed=False,reason='Explicit --skip-browser option; complete delivery is not claimed.'))
    comparisons=[]
    for name in ('C12-concept-trained.json','C12-concept-empty.json','C12-default.json'):
        assert sha(out/'model'/name)==sha(checkout/'artifacts/cycle12/model'/name),name
        comparisons.append(dict(path='model/'+name,byte_identical=True,sha256=sha(out/'model'/name)))
    assert not subprocess.check_output(['git','status','--porcelain'],cwd=checkout,text=True)
    write_json(out/'reproduction-comparison.json',dict(passed=True,models=comparisons,
        native_research='clean-research/verified.json',native_legal='current/proof-parity.json'))
    write_json(out/'reproduction-execution.json',dict(source_head=head,starting_head=read_json(checkout/'configs/cycle12.json')['starting_head'],
        clean_checkout=True,end_to_end_reproduction_executed=True,browser_executed=browser,complete_delivery=browser,
        all_commands_passed=True,pushed=False,deployed=False,upstream_modified=False))
    if browser:
        command('consolidated-reports',['-m','scripts.cycle12_reports','--out',str(out),'--docs',str(out/'reports')])
        command('artifact-manifest',['-m','evaluation.cycle12_delivery','manifest','--out',str(out),'--docs',str(out/'reports')])
    print('CYCLE12 FULL REPRODUCTION COMPLETE',flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',required=True);parser.add_argument('--checkout',required=True)
    parser.add_argument('--baseline',required=True);parser.add_argument('--browser-work',required=True);parser.add_argument('--skip-browser',action='store_true')
    args=parser.parse_args();run(args.out,args.checkout,args.baseline,args.browser_work,not args.skip_browser)
