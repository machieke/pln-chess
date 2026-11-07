"""Separate raw native channels from acceptance policy; never fuse their TVs."""
from dataclasses import asdict,dataclass,replace
from pathlib import Path
import os,time
from pln_chess.common import ROOT,digest,read_json
from pln_chess.pln import Runtime,TV
from pln_chess.inference import classify
from pln_chess.cycle5.inference import Cycle5Options,Session as SourceSession,infer_moves as source_infer
from pln_chess.cycle6.model import ModeModel,POLICY
from pln_chess.cycle6.history import inspect as history_inspect,canonical_mode

MODES=('operational','strict','experimental')
REQUIRED_CHECKS=('baseline','frozen_utility','frozen_errors','new_adversarial_errors','negatives','strict_abstention','native_probes','provenance','cache_parity','tests','clean_bootstrap')

def production_code_hash():
    import hashlib
    return digest({str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src').rglob('*.py'))})
LABELS={'supported':'supported-legal','contradicted':'supported-illegal','unknown':'unknown','incomplete':'incomplete'}

@dataclass(frozen=True)
class Cycle6Options(Cycle5Options):
    mode:str|None=None
    def __post_init__(self):
        object.__setattr__(self,'temporal_mode',canonical_mode(self.temporal_mode))
        super().__post_init__()
        if self.mode is not None and self.mode not in MODES:raise ValueError('Unknown inference mode')

class Session:
    def __init__(self,runtime,optimized=True,max_entries=50000):
        self.runtime=runtime;self.optimized=optimized;self.max_entries=max_entries;self.scope=None
        self.source=SourceSession(runtime,optimized,max_entries)
    def bind(self,scope):
        if self.scope!=scope:
            self.source=SourceSession(self.runtime,self.optimized,self.max_entries);self.scope=scope

def default_mode(model):
    path=Path(os.environ.get('C6_OUT',ROOT/'artifacts/cycle6'))/'acceptance.json'
    if path.exists():
        receipt=read_json(path)
        if receipt.get('passed') is True and receipt.get('model_version')==model.version and receipt.get('runtime_version')==model.runtime_version and receipt.get('policy')==POLICY and receipt.get('all_required_checks_executed') is True and all(receipt.get('checks',{}).get(k) is True for k in REQUIRED_CHECKS) and receipt.get('production_code_hash')==production_code_hash() and receipt.get('registration_hash')==digest(read_json(ROOT/'configs/cycle6.json')):
            return 'operational'
    if 'C6_OUT' not in os.environ:
        from pln_chess.cycle7.inference import legacy_default_mode
        return legacy_default_mode(model)
    return 'strict'

def decision(legacy,strict,options,new_negative=True,history_conflict=False,premise_conflict=False):
    """Acceptance only. No TV construction, revision, or confidence competition."""
    if 'incomplete' in (legacy['classification'],strict['classification']):return 'incomplete','budget-incomplete'
    if history_conflict:return 'unknown','contradictory-temporal-evidence'
    if premise_conflict and legacy['classification']=='supported':return 'unknown','negative-premise-dependency-conflict; no defensible native bridge'
    positive=legacy['classification']=='supported' and classify(TV.from_json(legacy['truth_value']),options)=='supported'
    negative=strict['classification']=='contradicted'
    if positive and negative and new_negative:return 'unknown','opposing-global-channels; no defensible native dependency-aware choice'
    if options.mode!='operational':return ('contradicted','native-negative-chain') if negative else ('unknown','strict-positive-proof-gap' if options.mode=='strict' else 'experimental-composition-not-established')
    if negative and (new_negative or legacy['classification']=='contradicted'):return 'contradicted','native-negative-chain'
    if positive:return 'supported','C4-learned-conditional-projection'
    return 'unknown','insufficient-evidence'

def infer_moves(position,checkpoint,options=None,runtime=None,selected_moves=None,session=None,optimized=True):
    started=time.perf_counter();runtime=runtime or Runtime()
    model=ModeModel.load(checkpoint,runtime) if isinstance(checkpoint,(str,Path)) else checkpoint
    if getattr(model,'schema',None)!=6 or model.runtime_version!=runtime.version:raise ValueError('Cycle 6 checkpoint/runtime mismatch')
    version=model.version
    options=options if isinstance(options,Cycle6Options) else Cycle6Options(**(asdict(options) if options else {}))
    options=replace(options,mode=options.mode or default_mode(model))
    source=model.source_model()
    if model.variant=='C6-no-new-negatives':source.variant='C5-no-new-negatives'
    session=session or Session(runtime,optimized,options.max_cache_entries)
    if not isinstance(session,Session):raise ValueError('Cycle 6 requires a mode-scoped Session')
    scope=digest([runtime.manifest,version,options.mode,POLICY,'typed-premise-planner-v5','events-v6.1',asdict(options)])
    session.bind(scope)
    settings=asdict(options);settings.pop('mode')
    result=source_infer(position,source,Cycle5Options(**settings),runtime,selected_moves,session.source,optimized)
    temporal=history_inspect(result['fen'] if 'fen' in result else position,options.temporal_mode,options.temporal_evidence)
    for item in result['candidates']:
        legacy=item['legacy_projection'];strict={'classification':item['classification'],'truth_value':item['legal_move_truth_value'],'status':item['status']}
        new_negative=legacy['classification']!='contradicted' and strict['classification']=='contradicted'
        unsafe=[p for p in item.get('typed_premises',[]) if p['family'] in ('ray','destination','boundary','exposure') and classify(TV.from_json(p['truth_value']),Cycle5Options())=='supported' and ((p.get('bridge_overlap') and options.dependence_aware) or (p.get('supporting_evidence') and p.get('contradicting_evidence')))]
        cls,reason=decision(legacy,strict,options,new_negative,strict['status']=='temporal-conflict',bool(unsafe))
        # Selected diagnostic channel is identical across modes. An unknown
        # classification can therefore carry a strong local TV; policy is explicit.
        raw=strict['truth_value'] if strict['classification']=='contradicted' else legacy['truth_value']
        groups=sorted({g for n in item['proof_trace'] for g in n.get('dependence_groups',[])})
        positive_nodes=[n for n in item['proof_trace'] if n['conclusion']=='LocalAdmissibility']
        negative_nodes=[n for n in item['proof_trace'] if n['conclusion'] in ('LegalMove','Not LegalMove')]
        pg={g for n in positive_nodes for g in n.get('dependence_groups',[])};ng={g for n in negative_nodes for g in n.get('dependence_groups',[])}
        status='native-negative-chain' if cls=='contradicted' else 'native-conditional' if cls=='supported' else 'insufficient-native-proof'
        item.update(classification=LABELS[cls],legacy_classification=cls,mode=options.mode,raw_stv=raw,legal_move_truth_value=raw,
            proof_status=status,status='native-partial / evidence-supported' if cls=='supported' else 'incomplete' if cls=='incomplete' else status,
            proof_complete=cls=='contradicted',negative_proof_complete=cls=='contradicted',positive_proof_complete=False,dependence_groups=groups,
            native_rule_ids=sorted({n['operator'] for n in item['proof_trace']}),
            observation_sources={'geometry':'host piece-relative board sensor','destination':'host occupancy sensor','ray':'host relative ray scan','exposure':'host structural successor and opponent frames; learned native attack conditionals','temporal':'external observations; no historical legality theorem'},
            policy_version=POLICY,model_version=version,runtime_version=runtime.version,temporal_evidence=temporal,
            evidence_channels={'C4':legacy,'C5':strict,'local_native_stv':legacy['local_truth_value'],'new_negative':new_negative,'dependency_conflicts':unsafe,'overlap_groups':sorted(pg&ng),
                'positive_nodes':[n['id'] for n in positive_nodes],'negative_nodes':[n['id'] for n in negative_nodes]},
            mode_comparison={m:{'classification':LABELS[decision(legacy,strict,replace(options,mode=m),new_negative,strict['status']=='temporal-conflict',bool(unsafe))[0]],
                                'reason':decision(legacy,strict,replace(options,mode=m),new_negative,strict['status']=='temporal-conflict',bool(unsafe))[1]} for m in MODES},
            decision_policy=reason,decision_node={'id':digest([item['candidate_id'],POLICY,options.mode,reason]),'kind':'host acceptance policy','native':False,
                'positive_node':positive_nodes[-1]['id'] if positive_nodes else None,'negative_node':item.get('selected_negative_witness'),
                'C4_classification':legacy['classification'],'C5_classification':strict['classification'],'reason':reason})
        item['gaps']=list(dict.fromkeys(item['gaps']+item['proof_plan']['gaps']))
        item['abstention_reason']=item['gaps']+[reason] if cls in ('unknown','incomplete') else []
    result.update(schema=6,mode=options.mode,policy_version=POLICY,model_version=version,representation=model.variant,
        source_model_version=source.version,budget=asdict(options),cache_scope=digest([scope,result['cache_scope']]),temporal_evidence=temporal,
        elapsed_seconds=time.perf_counter()-started,coverage='Operational predictions are partial conditional evidence; strict and experimental require unavailable positive composition.')
    return result
