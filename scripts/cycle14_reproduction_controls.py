"""Run source-bound response comparison controls without replacing old receipts."""
import argparse
from pathlib import Path
import subprocess
import sys

from pln_chess.common import ROOT,write_json
from scripts.cycle9_baseline import sha


def run(out):
    out=Path(out).resolve()
    receipt=out/'response-comparison-controls-v2.json'
    assert not receipt.exists(),'Use a new control output directory; preserve prior evidence'
    out.mkdir(parents=True,exist_ok=True)
    test=ROOT/'tests/test_cycle14_response_comparison.py'
    log=out/'response-comparison-controls-v2.log'
    xml=out/'response-comparison-controls-v2.xml'
    argv=[sys.executable,'-m','pytest','-q',str(test),'--junitxml='+str(xml)]
    with log.open('x') as stream:
        result=subprocess.run(argv,cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT)
    write_json(receipt,dict(passed=result.returncode==0,returncode=result.returncode,
        argv=argv,log_sha256=sha(log),test_xml_sha256=sha(xml),test_source_sha256=sha(test),
        verifier_sha256=sha(ROOT/'scripts/cycle14_reproduce.py'),
        binding_verifier_sha256=sha(ROOT/'evaluation/cycle14_response_binding.py'),
        control_driver_sha256=sha(__file__),
        scope='Five synthetic host-verifier controls: valid changed clocks, roots and handles; rejected changes to truth values, handles, roots or request history. No native inference or empirical preference success is claimed.'))
    assert result.returncode==0,log
    print('C14 RESPONSE REPRODUCTION VERIFIER CONTROLS PASSED',flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',default='artifacts/cycle14/verification')
    run(parser.parse_args().out)
