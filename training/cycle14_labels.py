"""Append-only offline label generations with separately reset raw UCI searches."""
import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
import lzma
from pathlib import Path

import chess

from pln_chess.common import ROOT,canonical,digest,read_json,write_json
from scripts.cycle9_baseline import sha
from training.cycle14_reference import RawEngine,board_from_history,classify_tier


def atomic_json(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():
        if read_json(path)!=value:raise ValueError('Immutable generation already exists: '+str(path))
        return
    temporary=path.with_suffix(path.suffix+'.partial')
    write_json(temporary,value);temporary.replace(path)


def semantic_search(raw):
    """Retain search evidence; omit only clock/nps text and derived wire hash.

    Exact wire bytes remain in the raw archive. Scientific identities include
    score/bound, depth, nodes, PV, candidate, options, history and termination.
    """
    result={k:v for k,v in raw.items() if k not in ('elapsed_seconds','transcript','transcript_sha256')}
    result['iterations']=[{k:v for k,v in row.items() if k!='time'} for row in raw['iterations']]
    result['candidates']={name:{k:v for k,v in row.items() if k!='time'} for name,row in raw['candidates'].items()}
    return result


def terminal_result(board,history,actor,nodes):
    outcome=board.outcome(claim_draw=True)
    if outcome is None:raise ValueError('A nonterminal endpoint requires a search')
    score=dict(kind='cp',value=0,mate_outcome=None,bound='unflagged') if outcome.winner is None else dict(
        kind='mate',value=0,mate_outcome='win' if outcome.winner==actor else 'loss',bound='unflagged')
    return dict(schema='c14-terminal-reference-v1',root_fen=board.fen(en_passant='fen'),history=history,
        original_actor='White' if actor else 'Black',node_budget=nodes,actual_reported_nodes=0,
        termination='completed',history_verified=True,score=score,pv=[],terminal_reason=outcome.termination.name,
        scope='Offline chess-library terminal adjudication; no search score or production inference.')


def worker(task):
    out,generation,row,source_hash,kind=task;out=Path(out)
    config=read_json(ROOT/'configs/cycle14.json')['reference']
    reference=read_json(ROOT/'artifacts/cycle13/sources/stockfish-source.json')
    binary=ROOT/reference['binary_path']
    assert sha(binary)==reference['binary_sha256']
    identity=dict(source_hash=source_hash,row_hash=digest(row),reference_manifest_sha256=sha(ROOT/'artifacts/cycle13/sources/stockfish-source.json'),
        config=config,adapter_sha256=sha(ROOT/'training/cycle14_reference.py'),driver_sha256=sha(__file__),kind=kind)
    base=out/'labels'/generation;path=base/'records'/(row['id']+'.json');raw_path=base/'raw'/(row['id']+'.json.xz')
    if path.exists():
        record=read_json(path)
        assert record['identity']==identity,'Preserve this label generation and choose a new name'
        assert record['raw_sha256']==sha(raw_path)
        return record
    actor=board_from_history(row['history'],row['fen']).turn
    raw_searches=[];semantic=[];tiers=[];selected_pv={};verdict='unknown';reason='unexecuted'
    with RawEngine(binary,threads=config['threads'],hash_mib=config['hash_mib']) as engine:
        initialization=engine.initialization
        for tier_index,budgets in enumerate(config['node_budget_ladder']):
            evaluations=[]
            for nodes in budgets:
                candidates={};terminations=[]
                for side,move in zip(('A','B'),row['moves']):
                    history=row['history'];board=board_from_history(history,row['fen'])
                    if kind=='temporal':
                        line=row['branches'][side][:row['horizon']]
                        if len(line)<row['horizon']:
                            candidates[side]=None;terminations.append('missing-endpoint');continue
                        history={**history,'moves':history['moves']+line};board=board_from_history(history)
                        roots=sorted(m.uci() for m in board.legal_moves)
                    else:roots=[move]
                    if kind=='temporal' and board.outcome(claim_draw=True) is not None:
                        raw=terminal_result(board,history,actor,nodes);candidate={k:raw[k] for k in ('score','pv')}
                        clean=raw
                    else:
                        raw=engine.analyze(history,roots=roots,nodes=nodes,actor=actor,expected_fen=board.fen(en_passant='fen'))
                        clean=semantic_search(raw);candidate=clean['candidates'].get(raw['bestmove'])
                    raw_searches.append(dict(tier=tier_index,side=side,analysis=raw))
                    semantic.append(dict(tier=tier_index,side=side,analysis=clean))
                    candidates[side]=candidate;terminations.append(raw['termination'])
                    if kind=='immediate' and tier_index==0 and nodes==budgets[-1] and candidate:
                        selected_pv[side]=candidate['pv'][:3]
                evaluation=dict(node_budget=nodes,candidates=candidates,
                    termination='completed' if all(t=='completed' for t in terminations) else 'incomplete',history_verified=True)
                evaluations.append(evaluation)
            verdict,reason=classify_tier(evaluations,config['preference_margin_cp'],config['nondirectional_margin_cp'])
            tiers.append(dict(tier=tier_index,budgets=budgets,label=verdict,reason=reason,evaluations=evaluations))
            if verdict!='unknown':break
    raw_payload=dict(identity=identity,initialization=initialization,searches=raw_searches)
    raw_path.parent.mkdir(parents=True,exist_ok=True)
    temporary=raw_path.with_suffix('.partial')
    with lzma.open(temporary,'wt',preset=1) as stream:stream.write(canonical(raw_payload))
    temporary.replace(raw_path)
    record=dict(schema='c14-reference-label-generation-v1',id=row['id'],generation=generation,identity=identity,
        label=verdict,reason=reason,tiers=tiers,analyses=semantic,selected_pv=selected_pv,
        split=row['split'],source_game=row['source_game'],dependence_group=row['dependence_group'],
        original_actor='White' if actor else 'Black',horizon=row.get('horizon',1),
        supersedes=row.get('previous_reference_evidence_id'),probability_of_correctness=None,
        actual_reported_nodes=sum(r['analysis']['actual_reported_nodes'] for r in raw_searches),
        reference_scope='Offline operational search agreement; no proven chess value or native PLN conclusion',
        inference_prediction_used=False)
    record['evidence_id']='c14-reference:'+digest(record)
    record.update(raw_artifact=str(raw_path.relative_to(out)),raw_sha256=sha(raw_path))
    atomic_json(path,record)
    print('C14 REFERENCE',generation,row['id'],verdict,reason,flush=True)
    return record


def run(out,generation='immediate-g1',workers=2,kind='immediate'):
    out=Path(out).resolve();data=read_json(out/'datasets'/('source-pairs.json' if kind=='immediate' else 'temporal-comparisons.json'))
    source_hash=data.get('hash') or digest(data);rows=data['records']
    old=read_json(ROOT/'artifacts/cycle13/datasets'/('reference-labels.json' if kind=='immediate' else 'temporal-labels.json'))
    previous={r['id']:r['evidence_id'] for r in old['records']}
    rows=[{**r,'previous_reference_evidence_id':previous.get(r['id'])} for r in rows]
    worst=len(rows)*2*sum(sum(t) for t in read_json(ROOT/'configs/cycle14.json')['reference']['node_budget_ladder'])
    assert worst<=read_json(ROOT/'configs/cycle14.json')['budgets']['reference_search_nodes']
    tasks=[(str(out),generation,row,source_hash,kind) for row in rows]
    with ProcessPoolExecutor(max_workers=workers) as pool:records=list(pool.map(worker,tasks))
    # Raw transcript hashes belong in the manifest, not reproducible evidence IDs.
    semantic_records=[{k:v for k,v in r.items() if k not in ('raw_artifact','raw_sha256')} for r in records]
    payload=dict(schema='c14-reference-dataset-v1',generation=generation,source_hash=source_hash,records=semantic_records,
        counts=dict(Counter(r['label'] for r in records)),actual_reported_nodes=sum(r['actual_reported_nodes'] for r in records),
        maximum_reserved_nodes=worst,no_production_reference_dependency=True,
        exclusions_from_scientific_identity=['elapsed_seconds','UCI time/nps fields','raw transcript and its hash'],
        raw_manifest={r['id']:dict(path=r['raw_artifact'],sha256=r['raw_sha256']) for r in records})
    payload['semantic_hash']=digest({k:v for k,v in payload.items() if k!='raw_manifest'})
    atomic_json(out/'labels'/generation/'index.json',payload)
    print('C14 REFERENCE COMPLETE',kind,payload['counts'],flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',default='artifacts/cycle14')
    parser.add_argument('--generation',default='immediate-g1');parser.add_argument('--workers',type=int,default=2)
    parser.add_argument('--kind',choices=('immediate','temporal'),default='immediate');args=parser.parse_args()
    run(args.out,args.generation,args.workers,args.kind)
