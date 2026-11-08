"""One application comparison contract for CLI and inspector exports."""
from dataclasses import asdict,replace
from pathlib import Path
import os
from pln_chess.common import ROOT,read_json,digest
from pln_chess.domain import Position
from pln_chess.api import find_move
from pln_chess.pln import Runtime
from pln_chess.cycle7.model import BackoffModel
from pln_chess.cycle7.inference import infer_moves as previous,Cycle7Options
from .model import PromotionModel
from .inference import infer_moves,Cycle8Options
from .ontology import observe


def compare_generations(position,move,checkpoint=None,mode='operational',runtime=None,options=None):
    if mode not in ('operational','strict','experimental'):raise ValueError('Comparison requires an explicit mode')
    runtime=runtime or Runtime(timeout=180)
    out=Path(os.environ.get('C8_OUT',ROOT/'artifacts/cycle8'))
    model=PromotionModel.load(checkpoint or out/'model/C8-promotion-relative.json',runtime) if checkpoint is None or isinstance(checkpoint,(str,Path)) else checkpoint
    if model.schema!=8:raise ValueError('Cycle 8 comparison requires a schema-8 candidate')
    position=Position.from_fen(position) if isinstance(position,str) else position;candidate=find_move(position,move)
    if candidate is None:raise ValueError('Move outside the seeded candidate grammar')
    options=replace(options,mode=mode) if options else Cycle8Options(mode=mode)
    old_settings=asdict(options);old_settings.pop('promotion_training')
    comparisons={}
    for label,name in [('C7-operational','C7-frozen'),('C7-learned-experimental','C7-learned-8')]:
        old=BackoffModel.load(ROOT/f'artifacts/cycle7/model/{name}.json',runtime)
        result=previous(position,old,Cycle7Options(**old_settings),runtime,[candidate])
        comparisons[label]={k:v for k,v in result.items() if k!='candidates'}|{'candidate':result['candidates'][0]}
    result=infer_moves(position,model,options,runtime,[candidate])
    comparisons['C8-experimental']={k:v for k,v in result.items() if k!='candidates'}|{'candidate':result['candidates'][0]}
    receipt=read_json(out/'acceptance.json') if (out/'acceptance.json').exists() else {}
    if receipt.get('new_learning_promoted') and (out/'model/C8-default.json').exists():
        accepted=PromotionModel.load(out/'model/C8-default.json',runtime)
        from .inference import accepted as valid_receipt
        if valid_receipt(accepted):
            result=infer_moves(position,accepted,options,runtime,[candidate])
            comparisons['C8-accepted']={k:v for k,v in result.items() if k!='candidates'}|{'candidate':result['candidates'][0]}
    before=comparisons['C7-operational']['candidate'];base_nodes={digest(n) for n in before['proof_trace']}
    differences={}
    for label,result in comparisons.items():
        c=result['candidate'];nodes={digest(n) for n in c['proof_trace']}
        differences[label]={'classification_changed':c['classification']!=before['classification'],
            'raw_stv_changed':c['raw_stv']!=before['raw_stv'],'native_nodes_added':sorted(nodes-base_nodes),
            'native_nodes_removed':sorted(base_nodes-nodes),'evidence_added':sorted(set(c['evidence_ids'])-set(before['evidence_ids'])),
            'evidence_removed':sorted(set(before['evidence_ids'])-set(c['evidence_ids'])),
            'promotion_selection':c.get('promotion_selection'),'proof_complete':c['proof_complete'],
            'positive_proof_complete':c['positive_proof_complete']}
    return {'schema':'cycle-comparison-v8','comparisons':comparisons,'selected_mode':mode,
        'selected_key':'C8-accepted' if 'C8-accepted' in comparisons else 'C8-experimental',
        'promotion_transition':observe(position,candidate),'differences':differences,
        'scope':'Experimental labels name research checkpoints. The requested inference mode is separate. Raw native STVs are not calibrated probabilities; positive conclusions remain partial learned conditionals.'}
