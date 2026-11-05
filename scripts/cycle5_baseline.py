"""Versioned C4 rerun; never writes to earlier evidence directories."""
import hashlib, os, platform, subprocess
from pathlib import Path
from pln_chess.common import ROOT, read_json, write_json
from pln_chess.pln import Runtime
from pln_chess.learning import Model
from evaluation.cycle4 import evaluate
from evaluation.cycle3 import read_gzip
from evaluation.experiments import summarize, fit_calibrator, score_calibration
from scripts.cycle4_baseline import pack

START = 'd5cfcb126acc9c3e5da669744d661e6895fb9303'
SPLITS = [('frozen-heldout-transfer','cycle2','heldout-transfer'),
          ('frozen-adversarial','cycle2','adversarial'),
          ('cycle3-independent-games','cycle3','independent-games'),
          ('cycle4-independent-games','cycle4/datasets','independent-games')]

def lock(out):
    runtime = Runtime(timeout=180)
    paths = subprocess.check_output(['git','ls-tree','-r','--name-only',START],text=True).splitlines()
    protected = {p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths
                 if p.startswith(('artifacts/','fixtures/','vendor/','configs/','tests/')) or p.endswith('.lock')}
    value = {'reference_head':START,'actual_head':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
             'working_tree':subprocess.check_output(['git','status','--short'],text=True),
             'runtime':runtime.manifest,'python':platform.python_version(),'platform':platform.uname()._asdict(),
             'protected_files':protected,'command':'TMPDIR=/dev/shm .venv/bin/python -m scripts.cycle5_baseline'}
    write_json(Path(out)/'baseline-start.json',value)
    return value

def main(out=None):
    out=Path(out or os.environ.get('C5_OUT',ROOT/'artifacts/cycle5'));out.mkdir(parents=True,exist_ok=True)
    receipt=lock(out);rt=Runtime(timeout=180);model=Model.load(ROOT/'artifacts/cycle4/model/C4-full.json',rt)
    calibration=fit_calibrator(read_gzip(ROOT/'artifacts/cycle4/evaluation/C4-full-cycle4-validation.json.xz'))
    results={}
    for name,path,split in SPLITS:
        data=read_json(ROOT/f'artifacts/{path}/dataset.json')
        report=evaluate(data,model,split,rt,diagnostics=True)
        previous=read_gzip(ROOT/f'artifacts/cycle4/evaluation/C4-full-{name}.json.xz')
        keys=lambda r:{(x['fixture'],x['move']):(x['classification'],x['truth_value'],x['proof_id']) for x in r['rows']}
        assert keys(report)==keys(previous),name
        report['metrics']['in_board_only']=summarize([r for r in report['rows'] if r['destination_exists']],report['positions'])
        report['metrics']['per_family']={f:summarize([r for r in report['rows'] if r['family']==f],[]) for f in sorted({r['family'] for r in report['rows']})}
        report['calibration']=score_calibration(report,calibration)
        pack(out/f'baseline/{name}.json.xz',report)
        results[name]={'metrics':report['metrics'],'model_version':model.version,'dataset_hash':data['hash'],'full_proof_parity':True}
        print('C4 BASELINE',name,report['metrics']['recall'],report['metrics']['unknown'],flush=True)
    pack(out/'baseline/original-49-errors.json.xz',read_gzip(ROOT/'artifacts/cycle4/proofs/original-49-errors.json.xz'))
    write_json(out/'baseline.json',{'lock':receipt,'results':results})
    print('C5 BASELINE COMPLETE',flush=True)

if __name__=='__main__':main()
