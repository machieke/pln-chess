"""Explicit external-model comparison and history transport application contracts."""
from dataclasses import replace
from pln_chess.common import ROOT,digest
from pln_chess.pln import Runtime
from pln_chess.api import explain_move
from pln_chess.cycle8.model import PromotionModel
from pln_chess.cycle8.inference import Cycle8Options
from .diagnostics import output_root
from .temporal import verify,replay,native_options


def compare_external(position,move,mode='operational',history=None,runtime=None,options=None):
    if mode not in ('operational','strict','experimental'):raise ValueError('Explicit inference mode required')
    runtime=runtime or Runtime(timeout=180);out=output_root();comparisons={}
    paths={'frozen':ROOT/'artifacts/cycle8/model/C8-promotion-relative.json',
           'small':out/'adaptation/model/small.json','large':out/'adaptation/model/large.json'}
    if history is not None:verify(history)
    for name,path in paths.items():
        model=PromotionModel.load(path,runtime);configured=replace(options,mode=mode) if options else Cycle8Options(mode=mode,timeout_seconds=180)
        transport=None
        if history is not None:
            transport=replay(**{**history['input'],'model_version':model.version,'runtime_version':runtime.version})
            configured=native_options(transport,configured)
        comparisons[name]=explain_move(position,move,model,configured,runtime)
        if transport:comparisons[name]['temporal_transport']=transport
    base=comparisons['frozen']['candidate'];differences={}
    for name,result in comparisons.items():
        c=result['candidate'];differences[name]=dict(classification_changed=c['classification']!=base['classification'],
            raw_stv_changed=c['raw_stv']!=base['raw_stv'],native_proof_equal=digest(c['proof_trace'])==digest(base['proof_trace']),
            evidence_added=sorted(set(c['evidence_ids'])-set(base['evidence_ids'])),
            evidence_removed=sorted(set(base['evidence_ids'])-set(c['evidence_ids'])))
    return dict(schema='external-comparison-v10',selected_key='frozen',selected_mode=mode,comparisons=comparisons,
        differences=differences,new_learning_promoted=False,
        scope='Small and large models are experimental. Comparison mode is explicit; the accepted operational checkpoint remains the frozen C8 model.')
