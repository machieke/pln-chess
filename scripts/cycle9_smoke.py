"""Actual accepted API/CLI paths plus measured inspector presentation overhead."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
from pln_chess.common import ROOT,read_json,write_json,digest
from pln_chess.pln import Runtime
from pln_chess.api import explain_move,research_report,inspect_temporal_v9
from pln_chess.cycle8.model import PromotionModel
from pln_chess.cycle8.inference import default_mode
from pln_chess.cycle9.diagnostics import decorate_inspection
from pln_chess.cycle6.inference import production_code_hash


def run(out):
    out=Path(out);rt=Runtime(timeout=180);model=PromotionModel.load(out/'model/C9-default.json',rt)
    assert default_mode(model)=='operational'
    fen='7k/8/8/8/8/8/2R5/2K5 w - - 0 1';start=time.perf_counter()
    result=explain_move(fen,'c2e2',model,runtime=rt);native_seconds=time.perf_counter()-start
    assert result['candidate']['classification']=='supported-legal'
    before=digest(result);calls=rt.invocations;samples=[]
    for _ in range(7):
        start=time.perf_counter();decorated=decorate_inspection(result);decorate_seconds=time.perf_counter()-start
        start=time.perf_counter();encoded=json.dumps(decorated);serialization_seconds=time.perf_counter()-start
        assert decorated['candidate']['research_diagnostics']['calibrated']['native'] is False
        assert decorated['candidate']['research_diagnostics']['calibrated']['available']
        assert digest(result)==before and rt.invocations==calls
        samples.append(dict(decorate_seconds=decorate_seconds,json_serialization_seconds=serialization_seconds,bytes=len(encoded.encode())))
    commands=[]
    def cli(args):
        started=time.perf_counter();p=subprocess.run([sys.executable,'-m','pln_chess',*args],cwd=ROOT,capture_output=True,text=True)
        commands.append(dict(args=args,returncode=p.returncode,seconds=time.perf_counter()-started,stdout_sha256=hashlib.sha256(p.stdout.encode()).hexdigest(),stderr=p.stderr))
        assert p.returncode==0,(args,p.stderr,p.stdout[:500]);return json.loads(p.stdout)
    inferred=cli(['inspect','--fen',fen,'--move','c2e2','--format','json','--checkpoint',str(out/'model/C9-default.json')])
    assert inferred['candidate']==result['candidate']
    export=out/'smoke/calibration-cli.json'
    cli(['calibration-export','--output',str(export)])
    assert read_json(export)['data']==read_json(out/'calibration/results.json')
    cli(['research-report','--section','identity','--output',str(out/'smoke/identity-cli.json')])
    assert research_report('identity')['data']['production_code_hash']==production_code_hash()
    history=inspect_temporal_v9(fen,'trusted-metadata',dict(source='smoke-metadata',confidence=.8))
    assert history['epistemic_categories']['trusted_state_metadata'] and not history['epistemic_categories']['directly_observed_events']
    write_json(out/'smoke/verified.json',dict(passed=True,source_hash=production_code_hash(),model_version=model.version,
        native_seconds=native_seconds,presentation_samples=samples,presentation_native_invocations=0,
        native_input_unmodified=True,actual_cli_commands=commands,empirical_export_native=False))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);run(p.parse_args().out)
