"""Select conditional evidence without inventing a joint native proof."""
import time
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from pln_chess.common import ROOT, read_json, digest
from pln_chess.domain import Position
from pln_chess.hypotheses import candidates
from pln_chess.pln import Runtime
from pln_chess.cycle4.ontology import descriptors
from pln_chess.cycle6.inference import Cycle6Options, Session as SourceSession, infer_moves as source_infer, production_code_hash
from pln_chess.cycle7.model import BackoffModel, key, LEVELS

PROOF_STATUSES=('native-compositional','native-unary/partial','learned-conditional','negative-supported','unknown','incomplete')

class Session:
    def __init__(self,runtime,optimized=True,max_entries=50000):
        self.frozen=SourceSession(runtime,optimized,max_entries)
        self.backoff=SourceSession(runtime,optimized,max_entries)

@dataclass(frozen=True)
class Cycle7Options(Cycle6Options):
    backoff:bool=True
    new_training:bool=True
    max_backoff_level:int=2
    def __post_init__(self):
        super().__post_init__()
        if type(self.backoff) is not bool or type(self.new_training) is not bool:raise ValueError('Invalid backoff options')
        if self.max_backoff_level not in range(3):raise ValueError('Invalid backoff level')

def accepted_receipt(model,legacy=False):
    import os
    p=Path(os.environ.get('C7_OUT',ROOT/'artifacts/cycle7'))/'acceptance.json'
    if p.exists():
        r=read_json(p)
        field='accepted_legacy_model_versions' if legacy else 'accepted_model_versions'
        if r.get('passed') is True and r.get('all_required_checks_executed') is True and all(r.get('checks',{}).get(k) is True for k in ('baseline','negatives','native','evaluation','parity','tests','clean_bootstrap')) and model.version in r.get(field,[]) and r.get('production_code_hash')==production_code_hash() and r.get('registration_hash')==digest(read_json(ROOT/'configs/cycle7.json')) and r.get('runtime_version')==model.runtime_version:
            return not legacy or r.get('legacy_registration_hash')==digest(read_json(ROOT/'configs/cycle6.json'))
    return False

def default_mode(model):return 'operational' if accepted_receipt(model) else 'strict'

def legacy_default_mode(model):return 'operational' if accepted_receipt(model,legacy=True) else 'strict'

def proof_category(item):
    # Positive composition is deliberately unreachable in this implementation.
    if item['classification']=='incomplete':return 'incomplete'
    if item['classification']=='supported-illegal' and item.get('negative_proof_complete'):return 'negative-supported'
    if item['classification']=='supported-legal' and any(n['conclusion']=='LocalAdmissibility' for n in item['proof_trace']):return 'learned-conditional'
    return 'unknown'

def infer_moves(position,checkpoint,options=None,runtime=None,selected_moves=None,session=None,optimized=True):
    started=time.perf_counter();runtime=runtime or Runtime()
    model=BackoffModel.load(checkpoint,runtime) if isinstance(checkpoint,(str,Path)) else checkpoint
    if model.schema!=7 or model.runtime_version!=runtime.version:raise ValueError('Cycle 7 checkpoint/runtime mismatch')
    options=options if isinstance(options,Cycle7Options) else Cycle7Options(**(asdict(options) if options else {}))
    options=replace(options,mode=options.mode or default_mode(model));version=model.version
    position=Position.from_fen(position) if isinstance(position,str) else position
    moves=list(selected_moves) if selected_moves is not None else list(candidates(position))
    source=model.source_model();base=source.source['base']['hypotheses'];frozen_keys=frozenset(base);selected={}
    settings=asdict(options)
    for k in ('backoff','new_training','max_backoff_level'):settings.pop(k)
    session=session or Session(runtime,optimized,options.max_cache_entries)
    if not isinstance(session,Session):raise ValueError('Cycle 7 requires its two-stage session')
    result=source_infer(position,source,Cycle6Options(**settings),runtime,moves,session.frozen,optimized)
    initial={i['candidate_id']:i for i in result['candidates']};affected=[]
    # Existing local hypotheses always win, including low-confidence or disputed
    # hypotheses. Coarse evidence cannot displace specific counterevidence.
    for move in moves if model.hypotheses else ():
        if initial[move.id]['classification']!='unknown':continue
        rel=next(r for r in descriptors(position,move)['relations'] if r['target']=='LocalAdmissibility')
        if rel['id'] in frozen_keys:
            selected[move.id]={'level':'frozen-exact','rule_id':rel['id'],'lineage':base[rel['id']]['evidence_ids']}
            continue
        levels=(range(options.max_backoff_level+1) if options.backoff else (0,)) if options.mode=='operational' else ()
        for level in levels:
            h=model.hypotheses.get(key(rel['descriptor'],level))
            if h is None or (not options.new_training and h.get('new_training')):continue
            # This is a host projection of a single learned conditional, explicitly
            # recorded. It does not combine independently learned premise TVs.
            base[rel['id']]={**h,**rel,'origin':'C7-host-projected-learned-conditional'}
            selected[move.id]={'level':LEVELS[level],'level_index':level,'rule_id':h['id'],
                'grounded_rule_id':rel['id'],'lineage':h['evidence_ids'],'dependence_groups':h['dependence_groups'],
                'projected_descriptor':h['descriptor'],'host_projection':True}
            affected.append(move)
            break
    if affected:
        remaining=max(0,options.max_native_invocations-result['scheduled_invocations'])
        # Use a stable configured timeout in the cache scope. Both stages check
        # the overall wall budget; a timeout is incomplete, never a negative.
        stage_options=replace(Cycle6Options(**settings),max_native_invocations=remaining,
            max_proof_bytes=max(1,options.max_proof_bytes-result['proof_bytes_estimate']))
        extra=source_infer(position,source,stage_options,runtime,affected,session.backoff,optimized)
        changed={i['candidate_id']:i for i in extra['candidates']}
        if time.perf_counter()-started>options.timeout_seconds:
            extra['truncated']=True;extra['error']='Combined Cycle 7 wall time budget exhausted'
            for item in changed.values():
                item.update(classification='incomplete',legacy_classification='incomplete',status='incomplete',proof_complete=False,
                    negative_proof_complete=False,abstention_reason=[extra['error']])
        result['candidates']=[changed.get(i['candidate_id'],i) for i in result['candidates']]
        for k in ('native_invocations','scheduled_invocations','cache_hits','cache_entries','grounded_atoms','proof_bytes_estimate'):
            result[k]+=extra[k]
        result['truncated']|=extra['truncated'];result['error']=extra['error'] or result['error']
        result['proof_dag']={digest(n):n for i in result['candidates'] for n in i['proof_trace']}
    for item in result['candidates']:
        if item['candidate_id'] not in selected and item.get('chosen_hypothesis_id'):
            k=item['chosen_hypothesis_id']
            selected[item['candidate_id']]={'level':'frozen-exact','rule_id':k,'lineage':base[k]['evidence_ids']}
        item['legacy_proof_status']=item['proof_status'];item['proof_status']=proof_category(item)
        item['proof_status_schema']='proof-status-v7';item['backoff']=selected.get(item['candidate_id'],{'level':'none','rule_id':None,'lineage':[]})
        item['partial_native_premises']=[p['id'] for p in item['typed_premises'] if p['status']=='learned-native-conditional']
        item['premise_proof_status']='native-unary/partial' if item['partial_native_premises'] else 'unknown'
        item['positive_proof_complete']=False
        frozen_comparison=initial[item['candidate_id']]['mode_comparison']
        item['mode_comparison']={**item['mode_comparison'],
            'strict':frozen_comparison['strict'],'experimental':frozen_comparison['experimental']}
        if options.mode!='operational' and model.hypotheses:
            item['mode_comparison']['operational']={'classification':None,'evaluated':False,
                'reason':'Run operational mode to evaluate optional backoff; strict inference does not execute it.'}
        item['model_version']=version
        item['decision_node']={**item['decision_node'],'backoff':item['backoff'],'C7_model_version':version}
        item['decision_node']['id']=digest(item['decision_node'])
    result.update(schema=7,model_version=version,source_model_version=source.version,representation=model.variant,
        budget=asdict(options),proof_status_schema='proof-status-v7',elapsed_seconds=time.perf_counter()-started)
    return result
