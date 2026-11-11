"""Execute the installed CLI and preserve complete transport proof identities."""
import argparse
import os
from pathlib import Path
import subprocess
import sys
import time
from pln_chess.common import ROOT,digest,read_json,write_json
from pln_chess.cycle6.inference import production_code_hash
from pln_chess.cycle12.graph import validate_graph
from evaluation.cycle7_io import pack
from scripts.cycle9_baseline import sha


def validate(result):
    graphs=0;proofs=set()
    def walk(value):
        nonlocal graphs
        if isinstance(value,dict):
            if 'graph' in value and isinstance(value['graph'],dict) and 'nodes' in value['graph']:
                assert validate_graph(value['graph']);graphs+=1
            if 'proof_trace' in value and 'proof_id' in value:
                assert digest(value['proof_trace'])==value['proof_id']
                proofs.add(value['proof_id'])
            for key,item in value.items():
                if key!='graph':walk(item)
        elif isinstance(value,list):
            for item in value:walk(item)
    walk(result)
    assert not result['execution']['truncated']
    return dict(graphs=graphs,proof_ids=len(proofs),all_valid=True)


def run(out):
    out=Path(out).resolve();code=production_code_hash();rows=[]
    pairs=read_json(out/'datasets/source-pairs.json')['records'];pair=min(pairs,key=lambda r:digest(['cli-smoke',r['id']]))
    plans=read_json(out/'datasets/temporal-plans.json')['records'];plan=min(plans,key=lambda r:digest(['cli-smoke',r['id']]))
    payloads=[('compare-moves',dict(fen=pair['fen'],move_a=pair['moves'][0],move_b=pair['moves'][1],
        history=pair['history'],preference_model='relational')),
        ('preference-continuations',dict(fen=plan['fen'],branches={k:[v] for k,v in plan['branches'].items()},
        history=plan['history'],preference_model='temporal',horizons=[2,3],selection_provenance=plan['response_selection']))]
    for name,payload in payloads:
        target=out/'cli-smoke';target.mkdir(parents=True,exist_ok=True)
        input_path=target/(name+'-input.json');output=target/(name+'-output.json');log=target/(name+'.txt')
        write_json(input_path,payload)
        argv=[str(Path(sys.executable).parent/'pln-chess'),name,'--input',str(input_path),'--output',str(output)]
        started=time.time()
        # CLI stdout is the same complete JSON; retain the single exact output
        # plus diagnostics instead of duplicating tens of MB in a text log.
        with log.open('w') as stream:
            subprocess.run(argv,cwd=ROOT,env=dict(os.environ,C13_OUT=str(out),TMPDIR='/dev/shm'),
                stdout=subprocess.DEVNULL,stderr=stream,check=True)
        result=read_json(output);validation=validate(result)
        assert result['inspector_model']['trained']
        archive=output.with_suffix('.json.xz');pack(archive,result)
        rows.append(dict(command=name,argv=argv,elapsed_seconds=time.time()-started,
            production_code_hash=code,validation=validation,artifact=str(archive.relative_to(out)),
            sha256=sha(archive),complete_json_sha256=sha(output),trained_model=result['inspector_model']))
        output.unlink()
    write_json(out/'cli-smoke/verified.json',dict(passed=True,production_code_hash=code,commands=rows,
        existing_api_tests='current/logs/tests.txt',api_migration_required=False,
        scope='Installed pair and continuation CLI commands with trained isolated checkpoints and complete JSON proof validation.'))
    print('TRAINED CLI SMOKE VERIFIED',flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',default='artifacts/cycle13');run(parser.parse_args().out)
