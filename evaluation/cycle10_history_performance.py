"""Temporal transport overhead and cache correctness under changing evidence."""
import argparse
from pathlib import Path
import time
from pln_chess.common import ROOT,read_json,write_json,digest
from pln_chess.pln import Runtime
from pln_chess.domain import Position
from pln_chess.api import find_move
from pln_chess.cycle8.model import PromotionModel
from pln_chess.cycle8.inference import infer_moves,Cycle8Options,Session
from pln_chess.cycle6.inference import production_code_hash
from evaluation.experiments import quantile
from evaluation.cycle7_io import pack


def run(out):
    from pln_chess.cycle10.temporal import replay,replay_game,native_options,verify,STANDARD_FEN
    out=Path(out);data=read_json(out/'datasets/dataset.json');rt=Runtime(timeout=180)
    model=PromotionModel.load(ROOT/'artifacts/cycle8/model/C8-promotion-relative.json',rt)
    cases=[]
    for source in sorted({g['source_collection'] for g in data['games']}):
        game=max((g for g in data['games'] if g['source_collection']==source),key=lambda g:len(g['moves']))
        cases.append((source,lambda game=game:replay_game(game,len(game['moves']),model.version,rt.version)))
    cases.extend([('empty-FEN',lambda:replay(STANDARD_FEN,[],source='benchmark-FEN')),
                  ('long-520-events',lambda:replay(STANDARD_FEN,['b1a3','b8a6','a3b1','a6b8']*130,
                    source='synthetic-structural-benchmark',initial_trust='attested-standard-start'))])
    overhead=[]
    for name,fn in cases:
        samples=[];ids=set()
        for _ in range(9):
            start=time.perf_counter();receipt=fn();elapsed=time.perf_counter()-start;ids.add(receipt['id'])
            start=time.perf_counter();assert verify(receipt);verification=time.perf_counter()-start
            samples.append(dict(replay_seconds=elapsed,verification_seconds=verification))
        assert len(ids)==1
        overhead.append(dict(case=name,events=len(receipt['events']),samples=samples,
            replay_seconds={f'p{int(q*100)}':quantile([s['replay_seconds'] for s in samples],q) for q in (.5,.95,.99)},
            legacy_window=receipt['legacy_window'],stable_receipt=True))
    initial='7k/5p2/8/6P1/8/8/8/K7 b - - 0 1'
    history=replay(initial,['f7f5'],source='cache/source-A',model_version=model.version,runtime_version=rt.version)
    position=Position.from_fen(history['resulting_fen']);move=find_move(position,'g5f6');session=Session(rt);comparisons=[]
    histories=[('base',history),('same-evidence',history),
        ('source-change',replay(initial,['f7f5'],source='cache/source-B',model_version=model.version,runtime_version=rt.version)),
        ('confidence-change',replay(initial,['f7f5'],source='cache/source-A',confidence=.8,model_version=model.version,runtime_version=rt.version)),
        ('missing-events',replay(position.fen(),[],source='cache/source-A',model_version=model.version,runtime_version=rt.version))]
    proofs=[]
    for name,receipt in histories:
        options=native_options(receipt,Cycle8Options(mode='operational',max_native_invocations=100000,timeout_seconds=180))
        reused=infer_moves(position,model,options,rt,[move],session=session)
        fresh=infer_moves(position,model,options,rt,[move],session=Session(rt))
        assert digest(reused['candidates'])==digest(fresh['candidates'])
        if name=='same-evidence':assert reused['native_invocations']==0
        candidate=reused['candidates'][0]
        comparisons.append(dict(case=name,transport_id=receipt['id'],native_invocations=reused['native_invocations'],
            cache_hits=reused['cache_hits'],exact_fresh_proof_parity=True,classification=candidate['classification'],
            truth_value=candidate['raw_stv'],proof_id=digest(candidate['proof_trace']),evidence_ids=candidate['evidence_ids']))
        proofs.append(dict(case=name,history=receipt,reused=reused,fresh=fresh))
    pack(out/'performance/temporal-cache-proofs.json.xz',proofs)
    write_json(out/'performance/temporal.json',dict(passed=True,production_code_hash=production_code_hash(),
        model_version=model.version,runtime_version=rt.version,replay_overhead=overhead,cache_controls=comparisons,
        scope='Transport measurements are separate from native inference latency. Repeated native expressions may be safely reused when inputs are equal; full candidate proofs must still match a fresh session after source, confidence or event changes.',
        quantile_limit='Nine descriptive repetitions; tail percentiles are sample maxima. Long synthetic sequence tests structural replay, not legal-game termination.'))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);run(p.parse_args().out)
