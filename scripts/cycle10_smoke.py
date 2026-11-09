"""Actual public API, CLI, PGN import and diagnostic-presentation checks."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
import chess
import chess.pgn
from pln_chess.common import ROOT,read_json,write_json,digest
from pln_chess.pln import Runtime
from pln_chess.api import explain_move,external_report,compare_external_models,replay_recorded_game
from pln_chess.cycle8.model import PromotionModel
from pln_chess.cycle8.inference import default_mode
from pln_chess.cycle10.diagnostics import decorate_inspection
from pln_chess.cycle6.inference import production_code_hash


def run(out):
    out=Path(out);(out/'smoke').mkdir(exist_ok=True);rt=Runtime(timeout=180)
    model=PromotionModel.load(out/'model/C10-default.json',rt);assert default_mode(model)=='operational'
    for arm in ('small','large'):assert default_mode(PromotionModel.load(out/f'adaptation/model/{arm}.json',rt))=='strict'
    fen='7k/8/8/8/8/8/2R5/2K5 w - - 0 1';result=explain_move(fen,'c2e2',model,runtime=rt)
    assert result['candidate']['classification']=='supported-legal';before=digest(result);calls=rt.invocations;samples=[]
    for _ in range(7):
        start=time.perf_counter();decorated=decorate_inspection(result);elapsed=time.perf_counter()-start
        start=time.perf_counter();encoded=json.dumps(decorated);serialization=time.perf_counter()-start
        assert decorated['candidate']['external_diagnostics']['available'] and not decorated['candidate']['external_diagnostics']['native']
        assert digest(result)==before and rt.invocations==calls
        samples.append(dict(decoration_seconds=elapsed,json_seconds=serialization,bytes=len(encoded.encode())))
    commands=[]
    def cli(args,success=True):
        start=time.perf_counter();p=subprocess.run([sys.executable,'-m','pln_chess',*args],cwd=ROOT,capture_output=True,text=True)
        commands.append(dict(args=args,returncode=p.returncode,expected_success=success,seconds=time.perf_counter()-start,
            stdout_sha256=hashlib.sha256(p.stdout.encode()).hexdigest(),stderr=p.stderr))
        assert (p.returncode==0)==success,(args,p.stderr,p.stdout[:500])
        return json.loads(p.stdout) if success else p.stdout
    native=cli(['inspect','--fen',fen,'--move','c2e2','--format','json','--checkpoint',str(out/'model/C10-default.json')])
    assert native['candidate']==result['candidate']
    for section in ('summary','provenance','calibration','comparisons','temporal','identity'):
        target=out/f'smoke/{section}-cli.json';actual=cli(['external-report','--section',section,'--output',str(target)])
        assert actual==external_report(section) and read_json(target)==actual
    data=read_json(out/'datasets/dataset.json');record=data['games'][0]
    fixture=next(f for f in data['positions'] if f.get('source_game')==record['id'])
    history=replay_recorded_game(record['id'],fixture['ply']);assert history['resulting_fen']==fixture['fen']
    cli_history=cli(['history-replay','--game-id',record['id'],'--ply',str(fixture['ply'])]);assert cli_history==history
    game=chess.pgn.Game();game.setup(chess.Board(record['initial_fen']));game.headers.update(record['headers']);node=game
    for notation in record['moves']:node=node.add_variation(chess.Move.from_uci(notation))
    pgn=out/'smoke/published-game-export.pgn';pgn.write_text(str(game)+'\n',encoding='utf-8')
    prepared=out/'smoke/imported-game.json'
    imported=cli(['history-import-pgn','--input',str(pgn),'--source','smoke-export/'+record['source_collection'],'--output',str(prepared)])
    assert imported['games']==1
    replayed=cli(['history-replay','--input',str(prepared),'--ply',str(fixture['ply'])])
    assert replayed['resulting_fen']==fixture['fen'] and len(replayed['events'])==fixture['ply']
    compared=compare_external_models(fen,'c2e2',runtime=rt)
    cli_comparison=cli(['compare-external','--fen',fen,'--move','c2e2','--mode','operational'])
    for arm in ('frozen','small','large'):assert compared['comparisons'][arm]['candidate']==cli_comparison['comparisons'][arm]['candidate']
    cli(['history-replay','--game-id','missing-game','--ply','0'],success=False)
    write_json(out/'smoke/verified.json',dict(passed=True,production_code_hash=production_code_hash(),model_version=model.version,
        accepted_default_operational=True,adaptations_default_strict=True,API_CLI_native_candidates_equal=True,
        source_PGN_import_replayed=True,recorded_prefix_equal=True,external_report_export_equal=True,
        presentation_native_invocations=0,input_native_result_unmodified=True,presentation_samples=samples,
        commands=commands,scope='Reference chess library is used only to create this offline PGN export for importer verification, never by production replay or inference.'))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);run(p.parse_args().out)
