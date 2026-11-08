"""Bounded learned transition projection; no new native operator or oracle."""
from collections import defaultdict
from dataclasses import dataclass, asdict, replace
from pathlib import Path
import os
import time
from pln_chess.common import ROOT, digest, read_json
from pln_chess.domain import Position
from pln_chess.hypotheses import candidates
from pln_chess.pln import Runtime
from pln_chess.cycle6.inference import Cycle6Options, Session as NativeSourceSession, infer_moves as native_source_infer, production_code_hash
from pln_chess.cycle7.inference import Cycle7Options, Session as SourceSession, infer_moves as source_infer, proof_category
from .model import PromotionModel
from .ontology import observe, key

CHECKS=('baseline','evaluation','negatives','native_boundary','cache_parity','tests','clean_bootstrap','provenance')


@dataclass(frozen=True)
class Cycle8Options(Cycle7Options):
    promotion_training: bool = True

    def __post_init__(self):
        super().__post_init__()
        if type(self.promotion_training) is not bool:raise ValueError('Invalid promotion option')


class Session:
    def __init__(self, runtime, optimized=True, max_entries=50000):
        self.source=SourceSession(runtime,optimized,max_entries)
        self.projections={}
        self.runtime=runtime;self.optimized=optimized;self.max_entries=max_entries

    def projection(self, identifier):
        if identifier not in self.projections:
            # Bound distinct projection sessions as well as each native cache.
            if len(self.projections)>=128:self.projections.pop(next(iter(self.projections)))
            self.projections[identifier]=NativeSourceSession(self.runtime,self.optimized,self.max_entries)
        return self.projections[identifier]


def accepted(model, legacy=False):
    path=Path(os.environ.get('C8_OUT',ROOT/'artifacts/cycle8'))/'acceptance.json'
    if not path.exists():return False
    receipt=read_json(path)
    field='accepted_legacy_model_versions' if legacy else 'accepted_model_versions'
    return (receipt.get('passed') is True and receipt.get('all_required_checks_executed') is True
        and all(receipt.get('checks',{}).get(k) is True for k in CHECKS)
        and model.version in receipt.get(field,[]) and receipt.get('runtime_version')==model.runtime_version
        and receipt.get('production_code_hash')==production_code_hash()
        and receipt.get('registration_hash')==digest(read_json(ROOT/'configs/cycle8.json'))
        and receipt.get('legacy_registrations')=={str(i):digest(read_json(ROOT/f'configs/cycle{i}.json')) for i in (6,7)})


def default_mode(model):return 'operational' if accepted(model) else 'strict'


def infer_moves(position, checkpoint, options=None, runtime=None, selected_moves=None, session=None, optimized=True):
    started=time.perf_counter();runtime=runtime or Runtime()
    model=PromotionModel.load(checkpoint,runtime) if isinstance(checkpoint,(str,Path)) else checkpoint
    if model.schema!=8 or model.runtime_version!=runtime.version:raise ValueError('Cycle 8 checkpoint/runtime mismatch')
    options=options if isinstance(options,Cycle8Options) else Cycle8Options(**(asdict(options) if options else {}))
    options=replace(options,mode=options.mode or default_mode(model))
    position=Position.from_fen(position) if isinstance(position,str) else position
    moves=list(selected_moves) if selected_moves is not None else list(candidates(position))
    session=session or Session(runtime,optimized,options.max_cache_entries)
    if not isinstance(session,Session):raise ValueError('Cycle 8 requires a projection-scoped Session')
    version=model.version;source=model.source_model();settings=asdict(options);settings.pop('promotion_training')
    # The registered candidate never masks destination or ray context in C7.
    source_options=replace(Cycle7Options(**settings),backoff=False,max_backoff_level=0)
    result=source_infer(position,source,source_options,runtime,moves,session.source,optimized)
    initial={i['candidate_id']:i for i in result['candidates']}
    original_base=source.source['source']['base']['hypotheses']
    observations={m.id:observe(position,m) for m in moves if m.promotion}
    selected={};groups=defaultdict(list)
    if options.mode=='operational' and options.promotion_training and model.hypotheses:
        for move in moves:
            obs=observations.get(move.id);item=initial[move.id]
            if obs is None or not obs['complete'] or item['classification']!='unknown':continue
            identifier=key(obs['descriptor'],model.projection_variant)
            h=model.hypotheses.get(identifier)
            if h is None:continue
            # Preserve any existing local counterevidence; selection is not a confidence contest.
            legacy_key=obs['legacy_local_relation']['id']
            existing=original_base.get(legacy_key)
            if existing and existing.get('contradicting_evidence'):continue
            groups[identifier].append(move)
            selected[move.id]={'rule_id':identifier,'grounded_rule_id':legacy_key,'level':'promotion-relative',
                'descriptor':h['descriptor'],'evidence_ids':h['evidence_ids'],'dependence_groups':h['dependence_groups'],
                'host_projection':True,'scope':'Learned local transition, not independent-premise composition'}
    changed={}
    for identifier,affected in sorted(groups.items()):
        if time.perf_counter()-started>=options.timeout_seconds:
            result['truncated']=True;result['error']='Combined Cycle 8 wall budget exhausted'
            for move in affected:
                item=dict(initial[move.id]);item.update(classification='incomplete',legacy_classification='incomplete',status='incomplete',proof_complete=False,negative_proof_complete=False)
                changed[move.id]=item
            continue
        native=source.source_model();base=native.source['base']['hypotheses'];h=model.hypotheses[identifier]
        for move in affected:
            relation=observations[move.id]['legacy_local_relation']
            base[relation['id']]={**h,**relation,'origin':'C8-host-projected-native-learned-transition',
                'promotion_transition_descriptor':h['descriptor'],'promotion_hypothesis_id':identifier}
        native_settings={k:v for k,v in settings.items() if k not in ('backoff','new_training','max_backoff_level')}
        native_settings['max_native_invocations']=max(0,options.max_native_invocations-result['scheduled_invocations'])
        native_settings['max_proof_bytes']=max(1,options.max_proof_bytes-result['proof_bytes_estimate'])
        extra=native_source_infer(position,native,Cycle6Options(**native_settings),runtime,affected,session.projection(identifier),optimized)
        for item in extra['candidates']:
            item['legacy_proof_status']=item['proof_status'];item['proof_status']=proof_category(item)
            item['backoff']=selected[item['candidate_id']]
            item.setdefault('typed_premises',[])
            item['partial_native_premises']=[p['id'] for p in item['typed_premises'] if p['status']=='learned-native-conditional']
            item['premise_proof_status']='native-unary/partial' if item['partial_native_premises'] else 'unknown'
            changed[item['candidate_id']]=item
        for field in ('native_invocations','scheduled_invocations','cache_hits','cache_entries','grounded_atoms','proof_bytes_estimate'):
            result[field]+=extra[field]
        result['truncated']|=extra['truncated'];result['error']=extra['error'] or result['error']
    result['candidates']=[changed.get(i['candidate_id'],i) for i in result['candidates']]
    if time.perf_counter()-started>options.timeout_seconds:
        result['truncated']=True;result['error']='Combined Cycle 8 wall budget exhausted'
        for item in result['candidates']:
            item.update(classification='incomplete',legacy_classification='incomplete',status='incomplete',proof_complete=False,negative_proof_complete=False)
    for item in result['candidates']:
        obs=observations.get(item['candidate_id']);item['promotion_transition']=obs
        item['promotion_selection']=selected.get(item['candidate_id'])
        item['proof_status']=proof_category(item);item['proof_status_schema']='proof-status-v8'
        item['positive_proof_complete']=False;item['model_version']=version
        item['evidence_state']={'supported-legal':'supported','supported-illegal':'contradicted','unknown':'unknown','incomplete':'incomplete'}[item['classification']]
        before=initial[item['candidate_id']]['mode_comparison']
        item['mode_comparison']={**item['mode_comparison'],'strict':before['strict'],'experimental':before['experimental']}
        if options.mode!='operational' and (model.hypotheses or source.hypotheses):
            item['mode_comparison']['operational']={'classification':None,'evaluated':False,'reason':'Operational learned transitions were not executed in this mode.'}
        item['decision_node']={**item['decision_node'],'C8_model_version':version,'promotion_selection':item['promotion_selection']}
        item['decision_node']['id']=digest(item['decision_node'])
    result['proof_dag']={digest(n):n for item in result['candidates'] for n in item['proof_trace']}
    result.update(schema=8,model_version=version,source_model_version=source.version,representation=model.variant,
        proof_status_schema='proof-status-v8',budget=asdict(options),elapsed_seconds=time.perf_counter()-started,
        coverage='Partial learned transition evidence; no new native composition operator.')
    return result
