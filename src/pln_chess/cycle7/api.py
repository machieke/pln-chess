"""Versioned comparison exports, preserving complete native proofs."""
from pathlib import Path
from pln_chess.domain import Position
from pln_chess.pln import Runtime
from pln_chess.api import find_move
from pln_chess.cycle6.inference import infer_moves as previous, Cycle6Options
from pln_chess.cycle7.model import BackoffModel
from pln_chess.cycle7.inference import infer_moves, Cycle7Options

def compare_cycles(position,move,checkpoint,mode='operational',runtime=None,options=None):
    if mode not in ('operational','strict','experimental'):raise ValueError('Comparison requires an explicit inference mode')
    runtime=runtime or Runtime(timeout=120)
    model=BackoffModel.load(checkpoint,runtime) if isinstance(checkpoint,(str,Path)) else checkpoint
    position=Position.from_fen(position) if isinstance(position,str) else position
    candidate=find_move(position,move)
    if candidate is None:raise ValueError('Move outside the seeded candidate grammar')
    from dataclasses import asdict,replace
    options=replace(options,mode=mode) if options else Cycle7Options(mode=mode)
    old={k:v for k,v in asdict(options).items() if k not in ('backoff','new_training','max_backoff_level')}
    a=previous(position,model.source_model(),Cycle6Options(**old),runtime,[candidate])
    b=infer_moves(position,model,options,runtime,[candidate])
    def single(r):return {k:v for k,v in r.items() if k!='candidates'}|{'candidate':r['candidates'][0]}
    return {'schema':'cycle-comparison-v7','comparisons':{'C6-'+mode:single(a),'C7-'+mode:single(b)},'selected_mode':mode,
        'native_proof_equal':a['candidates'][0]['proof_trace']==b['candidates'][0]['proof_trace'],
        'scope':'Raw TVs are native truth values, not calibrated legality probabilities. C7 proof labels use proof-status-v7; legacy labels are retained.'}
