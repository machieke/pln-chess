"""Actual default API/CLI/inspector contracts after acceptance, no oracle."""
import json
import os
import subprocess
import sys
from pathlib import Path
from pln_chess.common import ROOT, read_json, write_json
from pln_chess.api import explain_move, analyze_batch
from pln_chess.learning import Model
from pln_chess.pln import Runtime
from pln_chess.cli.web import inspector_infer
from pln_chess.cycle7.api import compare_cycles

def run():
    out=Path(os.environ.get('C7_OUT',ROOT/'artifacts/cycle7'));rt=Runtime();path=out/'model/C7-default.json';model=Model.load(path,rt)
    fen='7k/8/8/8/8/8/2R5/2K5 w - - 0 1';move='c2e2'
    api=explain_move(fen,move,model,runtime=rt)
    ui=inspector_infer({'fen':fen,'move':move},model)
    cli=subprocess.run([sys.executable,'-m','pln_chess','inspect','--fen',fen,'--move',move,'--checkpoint',str(path),'--format','json'],capture_output=True,text=True)
    assert cli.returncode==0,cli.stderr;cli_result=json.loads(cli.stdout)
    for result in (api,ui,cli_result):
        assert result['mode']=='operational' and result['candidate']['classification']=='supported-legal'
        assert result['candidate']['proof_status']=='learned-conditional' and not result['candidate']['positive_proof_complete']
    strict=explain_move(fen,move,model,runtime=rt,mode='strict');assert strict['candidate']['classification']=='unknown'
    assert strict['candidate']['raw_stv']==api['candidate']['raw_stv']
    comparison=inspector_infer({'fen':fen,'move':move,'compare':True},model)
    assert set(comparison['comparisons'])=={'C6-operational','C7-operational'}
    batch=analyze_batch([{'fen':fen,'move':move,'mode':m} for m in ('operational','strict','experimental')],model,runtime=rt)
    assert [r['candidate']['classification'] for r in batch['results']]==['supported-legal','unknown','unknown']
    incomplete=inspector_infer({'fen':fen,'move':move,'max_invocations':0},model)
    assert incomplete['truncated'] and incomplete['candidate']['proof_status']=='incomplete'
    legacy=explain_move(fen,move,ROOT/'artifacts/cycle6/model/C6-full.json',runtime=rt)
    assert legacy['mode']=='operational' and legacy['candidate']['proof_status']=='native-conditional'
    from evaluation.cycle7_io import pack
    pack(out/'proofs/default-api-cli-inspector.json.xz',{'api':api,'cli':cli_result,'inspector':ui,'strict':strict,'comparison':comparison,'batch':batch,'incomplete':incomplete,'legacy':legacy})
    write_json(out/'default-smoke.json',{'passed':True,'mode':'operational','model_version':model.version,
        'API':True,'CLI':True,'inspector':True,'comparison_export':True,'batch_modes':True,'incomplete_preserved':True,'legacy_C6_default':True})

if __name__=='__main__':run()
