"""Actual accepted-default application contracts and complete comparison exports."""
import argparse
import json
import subprocess
import sys
from pathlib import Path
from pln_chess.common import ROOT,read_json,write_json
from pln_chess.api import explain_move,analyze_batch
from pln_chess.learning import Model
from pln_chess.pln import Runtime
from pln_chess.cli.web import inspector_infer
from evaluation.cycle7_io import pack


def run(out):
    out=Path(out);rt=Runtime(timeout=180);path=out/'model/C8-default.json';model=Model.load(path,rt)
    fen='7k/8/8/8/8/8/2R5/2K5 w - - 0 1';move='c2e2'
    api=explain_move(fen,move,model,runtime=rt);ui=inspector_infer({'fen':fen,'move':move},model)
    def cli(*args):
        result=subprocess.run([sys.executable,'-m','pln_chess',*args],capture_output=True,text=True)
        assert result.returncode==0,result.stderr;return json.loads(result.stdout)
    result=cli('inspect','--fen',fen,'--move',move,'--format','json')
    for r in (api,ui,result):
        assert r['model_version']==model.version and r['mode']=='operational'
        assert r['candidate']['classification']=='supported-legal' and not r['candidate']['positive_proof_complete']
    strict=explain_move(fen,move,model,runtime=rt,mode='strict');assert strict['candidate']['classification']=='unknown'
    batch=analyze_batch([{'fen':fen,'move':move,'mode':m} for m in ('operational','strict','experimental')],model,runtime=rt)
    assert [r['candidate']['classification'] for r in batch['results']]==['supported-legal','unknown','unknown']
    incomplete=inspector_infer({'fen':fen,'move':move,'max_invocations':0},model)
    assert incomplete['truncated'] and incomplete['candidate']['classification']=='incomplete'
    promotion='r1b1nk1r/pp3P2/nbp3pp/1N2P3/1P1P2P1/2Q5/P1K1N2P/R3R3 w - - 3 29'
    comparisons=[]
    for move in ('f7e8n','f7f8q'):
        web=inspector_infer({'fen':promotion,'move':move,'model':'C8-default','mode':'operational','compare':True},model)
        command=cli('compare-generations','--fen',promotion,'--move',move)
        assert web['differences']==command['differences']
        for label in web['comparisons']:
            assert web['comparisons'][label]['candidate']==command['comparisons'][label]['candidate']
        comparisons.append({'inspector':web,'CLI':command})
    legacy={}
    for key,path in [('C7',ROOT/'artifacts/cycle7/model/C7-default.json'),('C6',ROOT/'artifacts/cycle6/model/C6-full.json')]:
        legacy[key]=explain_move(fen,'c2e2',path,runtime=rt)
        assert legacy[key]['mode']=='operational'
    pack(out/'proofs/default-api-cli-inspector.json.xz',{'api':api,'CLI':result,'inspector':ui,'strict':strict,'batch':batch,'incomplete':incomplete,'comparisons':comparisons,'legacy':legacy})
    write_json(out/'default-smoke.json',{'passed':True,'model_version':model.version,'API':True,'CLI_default':True,
        'inspector':True,'comparison_export':True,'batch_modes':True,'incomplete_preserved':True,'legacy_C6_C7_defaults':True})


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',required=True);run(parser.parse_args().out)
