"""Immutable Cycle 4/5 references and exactly matched, freshly executed baselines."""
import hashlib, platform, subprocess
from pathlib import Path
from pln_chess.common import ROOT, read_json, write_json
from pln_chess.pln import Runtime
from pln_chess.learning import Model
from evaluation.cycle4 import evaluate
from evaluation.cycle3 import read_gzip
from scripts.cycle4_baseline import pack
from scripts.cycle5_baseline import SPLITS as OLD_SPLITS

START='6c7538cedeb52fa4a921e3549ac57022ff7874d8'
SPLITS=OLD_SPLITS+[(f'cycle5-{s}','cycle5/datasets',s) for s in ('validation','combination-holdout','structural-holdout','independent-games')]

def lock(out):
    paths=subprocess.check_output(['git','ls-tree','-r','--name-only',START],text=True).splitlines()
    protected={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths if p.startswith(('artifacts/','fixtures/','vendor/','configs/','tests/')) or p.endswith('.lock')}
    value={'starting_head':START,'actual_head':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
           'working_tree':subprocess.check_output(['git','status','--short'],text=True),'tags':subprocess.check_output(['git','tag'],text=True).splitlines(),
           'C4_ancestor':subprocess.run(['git','merge-base','--is-ancestor','d5cfcb126acc9c3e5da669744d661e6895fb9303',START]).returncode==0,
           'runtime':Runtime().manifest,'python':platform.python_version(),'protected_files':protected,
           'immutable_snapshot':'All protected inputs are immutable git blobs reachable from starting_head; prior artifacts remain byte-identical.'}
    write_json(Path(out)/'baseline/start.json',value)
    selected=[p for p in protected if p in ['artifacts/cycle4/model/C4-full.json','artifacts/cycle5/model/C5-full.json','configs/cycle4.json','configs/cycle5.json'] or p in [f'artifacts/{s[1]}/dataset.json' for s in SPLITS]]
    pack(Path(out)/'baseline/inputs.json.xz',{p:read_json(ROOT/p) for p in selected})
    return value

def run(out):
    out=Path(out);rt=Runtime(timeout=180);results={}
    for name,path in [('C4','cycle4/model/C4-full.json'),('C5','cycle5/model/C5-full.json')]:
        model=Model.load(ROOT/f'artifacts/{path}',rt);results[name]={}
        for key,source,split in SPLITS:
            data=read_json(ROOT/f'artifacts/{source}/dataset.json')
            report=evaluate(data,model,split,rt,diagnostics=True)
            old=read_gzip(ROOT/f'artifacts/cycle5/evaluation/{"C5-full" if name=="C5" else name}-{key}.json.xz')
            fields=('fixture','move','classification','truth_value','proof_id','rule_ids','evidence_ids')
            assert [{k:r[k] for k in fields} for r in report['rows']]==[{k:r[k] for k in fields} for r in old['rows']],(name,key)
            assert [p['predicted'] for p in report['positions']]==[p['predicted'] for p in old['positions']]
            report['baseline_parity']=True;pack(out/f'baseline/{name}-{key}.json.xz',report)
            results[name][key]={'metrics':report['metrics'],'model_version':model.version,'dataset_hash':data['hash'],'proof_parity':True,
                'membership':[{'id':p['fixture'],'oracle_legal_count':len(p['expected'])} for p in report['positions']]}
            print('BASELINE',name,key,report['metrics']['recall'],flush=True)
    write_json(out/'baseline/comparison.json',results)
    return results

def reuse(out,source):
    """Reuse an executed baseline only when all frozen code and inputs match."""
    import shutil
    out,source=Path(out),Path(source)
    previous=read_json(source/'baseline/start.json');head=previous['actual_head']
    if previous['runtime']!=Runtime().manifest:raise ValueError('Baseline runtime changed')
    for path,expected in previous['protected_files'].items():
        if hashlib.sha256((ROOT/path).read_bytes()).hexdigest()!=expected:raise ValueError('Protected baseline input changed: '+path)
    paths=subprocess.check_output(['git','ls-tree','-r','--name-only',head],text=True).splitlines()
    checked={}
    for path in paths:
        if not path.endswith('.py') or not path.startswith(('src/','evaluation/','training/','scripts/')) or 'cycle6' in path:continue
        original=subprocess.check_output(['git','show',head+':'+path])
        actual=(ROOT/path).read_bytes()
        if actual!=original:raise ValueError('Frozen baseline source changed: '+path)
        checked[path]=hashlib.sha256(actual).hexdigest()
    if not checked:raise ValueError('No baseline sources verified')
    comparison=read_json(source/'baseline/comparison.json')
    if any(set(comparison[name])!={x[0] for x in SPLITS} or not all(v['proof_parity'] for v in comparison[name].values()) for name in ('C4','C5')):
        raise ValueError('Baseline comparison is incomplete or not proof matched')
    lock(out);(out/'baseline/start.json').rename(out/'baseline/current-checkout.json')
    copied={}
    for path in sorted((source/'baseline').iterdir()):
        if not path.is_file():continue
        destination=out/'baseline'/path.name;shutil.copy2(path,destination)
        sha=hashlib.sha256(path.read_bytes()).hexdigest()
        assert hashlib.sha256(destination.read_bytes()).hexdigest()==sha
        copied[path.name]=sha
    write_json(out/'baseline/reuse.json',{'executed_in_this_checkout':False,'executed_source_head':head,
        'current_head':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        'validated_unchanged_inputs':True,'frozen_source_hashes':checked,'copied_report_hashes':copied,
        'reason':'Freshly executed C4/C5 baselines reused after a Cycle 6-only optimization. Frozen inference/evaluation source, runtime, models, configs and datasets are byte-identical; no dataset or threshold substitution.'})
    return comparison

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--out',required=True);parser.add_argument('--lock-only',action='store_true');parser.add_argument('--reuse-from');a=parser.parse_args()
    if a.reuse_from:reuse(a.out,a.reuse_from)
    else:
        lock(a.out)
        if not a.lock_only:run(a.out)
