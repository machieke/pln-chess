"""Run the full suite and inspect the actual source-bound accepted default."""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

from pln_chess.common import ROOT, read_json, write_json
from pln_chess.cycle6.inference import production_code_hash
from scripts.cycle9_baseline import sha


def run(out):
    from pln_chess.pln import Runtime
    from pln_chess.learning import Model
    from pln_chess.cycle12.acceptance import accepted_model, default_checkpoint
    from pln_chess.cycle12.model import ConceptModel
    from pln_chess.cycle11.fields.model import FieldModel
    out=Path(out).resolve();receipt=read_json(out/'acceptance.json')
    assert receipt['passed'] and receipt['production_code_hash']==production_code_hash()
    for key in ('C6_OUT','C7_OUT','C8_OUT','C9_OUT','C10_OUT','C11_OUT'):
        if key in os.environ:raise ValueError('Remove legacy override before default verification: '+key)
    os.environ['C12_OUT']=str(out)
    runtime=Runtime();path=out/'model/C12-default.json';model=Model.load(path,runtime)
    assert default_checkpoint(ROOT/'artifacts/cycle10/model/C10-default.json')==path
    assert model.version==receipt['default_model_version'] and accepted_model(model)
    assert not accepted_model(ConceptModel.load(out/'model/C12-concept-trained.json',runtime))
    assert not accepted_model(FieldModel.load(ROOT/'artifacts/cycle11/model/C11-field-trained.json',runtime))
    target=out/'final-tests';target.mkdir(parents=True,exist_ok=True)
    argv=[sys.executable,'-m','pytest','-q'];started=time.time();code=production_code_hash()
    with (target/'pytest.txt').open('w') as stream:
        result=subprocess.run(argv,cwd=ROOT,env=dict(os.environ,TMPDIR='/dev/shm'),stdout=stream,stderr=subprocess.STDOUT)
    record=dict(argv=argv,returncode=result.returncode,elapsed_seconds=time.time()-started,
        source_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        production_code_hash=code,acceptance_sha256=sha(out/'acceptance.json'))
    write_json(target/'command.json',record)
    assert result.returncode==0,(target/'pytest.txt')
    count=re.search(r'(\d+) passed',(target/'pytest.txt').read_text());assert count
    assert int(count[1])==read_json(out/'current/verified.json')['test_count']
    # Exercise the actual CLI default, without --checkpoint, as well as selection in Python.
    argv=[sys.executable,'-m','pln_chess','inspect','--fen','7k/8/8/8/R6p/8/8/6K1 w - - 0 1',
        '--move','a4h4','--mode','operational','--format','json']
    raw=subprocess.check_output(argv,cwd=ROOT,env=dict(os.environ,TMPDIR='/dev/shm'),text=True)
    inspected=json.loads(raw)
    assert inspected['candidate']['classification']=='supported-legal'
    assert inspected['model_version']==model.version and not inspected['truncated']
    assert inspected['candidate']['model_version']==model.version
    write_json(target/'cli-default-inspection.json',inspected)
    assert code==production_code_hash()
    write_json(target/'verified.json',dict(passed=True,test_count=int(count[1]),**record,
        default_checkpoint=str(path),default_model_version=model.version,
        concept_and_field_models_rejected=True,cli_default_argv=argv,cli_default_classification='supported-legal',
        model_sha256=sha(path),production_unchanged_during_tests=True))
    print('Accepted-default full suite and CLI verification passed',flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',required=True)
    run(parser.parse_args().out)
