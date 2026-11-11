"""Pinned reference-engine supervision, isolated from production inference."""
import argparse
from collections import Counter
import json
from pathlib import Path
import time

import chess
import chess.engine

from pln_chess.common import ROOT, digest, read_json, write_json
from scripts.cycle9_baseline import sha


def score_value(score):
    return dict(cp=score.score(),mate=score.mate())


def order(a,b,margin):
    """Offline label policy only. Never converted into a model utility."""
    if a['mate'] is None and b['mate'] is None:
        difference=a['cp']-b['cp']
        return 1 if difference>=margin else -1 if difference<=-margin else 0
    def category(value):
        return 0 if value['mate'] is None else 1 if value['mate']>0 else -1
    first,second=category(a),category(b)
    if first!=second:return 1 if first>second else -1
    if a['mate']==b['mate']:return 0
    # With both scores mate-valued, lower signed distance is preferable:
    # mate in 2 rather than 4; being mated in 4 rather than 2.
    return 1 if a['mate']<b['mate'] else -1


def label(evaluations,config):
    if len(evaluations)!=2 or any(len(e['candidates'])!=2 for e in evaluations):return 'unknown','Missing comparison output.'
    directions=[];ambiguous=[]
    for evaluation in evaluations:
        rows=evaluation['candidates']
        if any(r['lowerbound'] or r['upperbound'] for r in rows):return 'unknown','Unresolved score bound.'
        a,b=[r['score'] for r in rows]
        directions.append(order(a,b,config['preference_margin_cp']))
        ambiguous.append(a['mate'] is None and b['mate'] is None and abs(a['cp']-b['cp'])<=config['ambiguous_margin_cp'])
    if directions==[1,1]:return 'A','Same directional margin at both registered node budgets.'
    if directions==[-1,-1]:return 'B','Same directional margin at both registered node budgets.'
    if all(ambiguous):return 'no-demonstrated-preference','Both comparisons fall within the registered ambiguity margin.'
    return 'unknown','Budgets disagree, margin is intermediate, or mate distinction remains unresolved.'


def run(out,binary=None):
    out=Path(out).resolve()
    # Preparing this driver is allowed during baseline replay; fitting or
    # generating preference labels waits for the verified baseline.
    assert read_json(out/'baseline/reproduction-receipt.json')['passed']
    config=read_json(ROOT/'configs/cycle13.json')['reference_engine']
    reference=read_json(out/'sources/stockfish-source.json')
    binary=Path(binary or ROOT/reference['binary_path']).resolve()
    assert sha(binary)==reference['binary_sha256'],'Unregistered reference binary'
    data=read_json(out/'datasets/source-pairs.json');expected=data.pop('hash');assert digest(data)==expected
    records=[]
    engine=chess.engine.SimpleEngine.popen_uci(str(binary),timeout=120)
    try:
        engine.configure({'Threads':config['threads'],'Hash':config['hash_mib'],'UCI_ShowWDL':True})
        for row in data['records']:
            path=out/'labels'/f"{row['id']}.json"
            identity=dict(source_hash=expected,row_hash=digest(row),reference_binary_sha256=sha(binary),
                config=config,driver_sha256=sha(__file__))
            if path.exists():
                record=read_json(path);assert record['identity']==identity,'Use a new label generation directory'
                records.append(record);continue
            history=row['history'];board=chess.Board(history['initial_fen'])
            for move in history['moves']:board.push_uci(move)
            assert board.fen(en_passant='fen')==row['fen']
            roots=[chess.Move.from_uci(m) for m in row['moves']]
            evaluations=[]
            for nodes in config['node_budgets']:
                engine.configure({'Clear Hash':None})
                started=time.perf_counter()
                infos=engine.analyse(board,chess.engine.Limit(nodes=nodes),multipv=2,
                    root_moves=sorted(roots,key=lambda m:m.uci()),game=object(),info=chess.engine.INFO_ALL)
                indexed={info['pv'][0].uci():info for info in infos if info.get('pv')}
                candidates=[]
                for move in row['moves']:
                    if move not in indexed:continue
                    info=indexed[move];pv=[m.uci() for m in info['pv']]
                    check=board.copy()
                    for uci in pv:check.push_uci(uci)
                    candidates.append(dict(move=move,score=score_value(info['score'].pov(board.turn)),
                        pv=pv,depth=info.get('depth'),seldepth=info.get('seldepth'),nodes=info.get('nodes'),
                        engine_seconds=info.get('time'),lowerbound=bool(info.get('lowerbound')),
                        upperbound=bool(info.get('upperbound')),wdl=list(info['wdl'].pov(board.turn)) if 'wdl' in info else None,
                        scope='Offline reference-engine output, not a native PLN conclusion.'))
                evaluations.append(dict(node_budget=nodes,candidates=candidates,elapsed_seconds=time.perf_counter()-started))
            verdict,reason=label(evaluations,config)
            record=dict(id=row['id'],identity=identity,label=verdict,reason=reason,evaluations=evaluations,
                source='Stockfish 18 fixed-node two-root comparisons',source_game=row['source_game'],
                dependence_group=row['dependence_group'],split=row['split'],temporal_context=row['history'],
                probability_of_correctness=None,reference_selection_only=True)
            record['evidence_id']='reference-preference:'+digest(record)
            write_json(path,record);records.append(record)
            print('REFERENCE',row['id'],verdict,flush=True)
    finally:engine.quit()
    payload=dict(schema='c13-offline-preference-labels-v1',source_hash=expected,records=records,
        counts=dict(Counter(r['label'] for r in records)),reference_manifest_sha256=sha(out/'sources/stockfish-source.json'),
        no_production_reference_dependency=True)
    payload['hash']=digest(payload)
    write_json(out/'datasets/reference-labels.json',payload)
    print('REFERENCE LABELS COMPLETE',payload['counts'],flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',default='artifacts/cycle13');parser.add_argument('--binary')
    args=parser.parse_args();run(args.out,args.binary)
