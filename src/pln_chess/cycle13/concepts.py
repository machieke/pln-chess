"""Learned piece-independent fork packets with preserved starting conditionals."""
import copy
from dataclasses import dataclass, field, asdict
import time
from pln_chess.common import digest, digest_dataclass, canonical, read_json, write_json
from pln_chess.pln import Runtime, TV, UNKNOWN, NativeError
from pln_chess.inference import classify
from pln_chess.cycle3.native import NativeSession
from pln_chess.cycle11.fields.inference import FieldOptions
from pln_chess.cycle12.inference import ConceptSession, infer_concepts as starting_infer, _schedule, _empty_core

FORK_GRAMMAR='relative-fork-role-packet-v13'


def fork_key(descriptor):
    if not isinstance(descriptor,dict) or set(descriptor) != {'grammar','targets'} or descriptor['grammar'] != FORK_GRAMMAR:
        raise ValueError('Invalid fork role descriptor')
    targets=descriptor['targets']
    if not isinstance(targets,list) or len(targets)!=2 or targets != sorted(targets,key=canonical):
        raise ValueError('Fork role targets require a canonical unordered pair')
    for target in targets:
        if set(target) != {'occupancy','allegiance','attack'} or target['occupancy'] not in ('occupied','empty','unknown') or target['allegiance'] not in ('friendly','opponent','empty','unknown') or target['attack'] not in ('supported','contradicted','unknown','incomplete'):
            raise ValueError('Invalid fork role vocabulary')
    return 'fork-role-rule:'+digest(descriptor)


def fork_packet(result):
    if result['concept'] != 'Fork':
        raise ValueError('Fork role packet requires an explicit fork candidate')
    roles=result['observation']['roles'];attacker=roles['attacker']
    owner=attacker['piece']['owner'] if attacker['observed'] and attacker['piece'] else None
    targets=[];gaps=[]
    for name in ('target_a','target_b'):
        role=roles[name];piece=role['piece']
        allegiance='unknown' if not role['observed'] or owner is None else 'empty' if piece is None else 'friendly' if piece['owner']==owner else 'opponent'
        component=next((c for c in result['component_status'] if c['target_role']==name),None)
        status=component['classification'] if component else 'unknown'
        targets.append(dict(occupancy=role['occupancy'],allegiance=allegiance,attack=status))
        if allegiance=='unknown' or status in ('unknown','incomplete'):
            gaps.append('Unresolved occupancy, allegiance or independent attack field: '+name)
    descriptor=dict(grammar=FORK_GRAMMAR,targets=sorted(targets,key=canonical))
    rule=fork_key(descriptor)
    packet=dict(descriptor=descriptor,rule_id=rule,complete=not gaps and owner is not None,
        gaps=gaps,source_observation_id=result['observation_id'],
        component_proof_ids=[c['proof_id'] for c in result['component_status']],
        scope='Host grouping of role observations and separate field classifications; no native conjunction or fork verdict.')
    packet['id']='fork-role-observation:'+digest(packet)
    return packet


@dataclass
class ForkModel:
    runtime_version: str
    hypotheses: dict=field(default_factory=dict)
    training_report: dict=field(default_factory=dict)
    ledger_digest: str=''
    variant: str='C13-fork-role-experimental'
    schema: str='relative-fork-role-model-v13'
    grammar: str=FORK_GRAMMAR

    @property
    def version(self):
        return digest_dataclass(self)

    def validate(self,runtime=None):
        if self.schema!='relative-fork-role-model-v13' or self.grammar!=FORK_GRAMMAR:
            raise ValueError('Unsupported fork role model')
        if not isinstance(self.runtime_version,str) or not self.runtime_version or (runtime and self.runtime_version!=runtime.version):
            raise ValueError('Fork checkpoint/runtime mismatch')
        for identifier,h in self.hypotheses.items():
            if h['id']!=identifier or fork_key(h['descriptor'])!=identifier:
                raise ValueError('Invalid fork conditional identity')
            TV.from_json(h['positive']);TV.from_json(h['negative'])
            evidence=h['supporting_evidence']+h['contradicting_evidence']
            if not h['evidence_ids'] or not h['dependence_groups'] or len(set(evidence))!=len(evidence) or sorted(evidence)!=sorted(h['evidence_ids']):
                raise ValueError('Invalid fork evidence partition')
        return True

    def export(self,path):
        self.validate();write_json(path,{**asdict(self),'version':self.version})
        return dict(path=str(path),version=self.version,schema=self.schema)

    @classmethod
    def load(cls,path,runtime=None):
        data=read_json(path);expected=data.pop('version',None)
        try:
            model=cls(**data);model.validate(runtime)
        except (KeyError,TypeError) as error:
            raise ValueError('Malformed fork checkpoint') from error
        if expected!=model.version:
            raise ValueError('Fork checkpoint integrity mismatch')
        return model


class ForkSession:
    def __init__(self,runtime):
        self.runtime=runtime;self.starting=ConceptSession(runtime);self.native=NativeSession(runtime)


def infer_concepts(cases,starting_model,field_model,*,fork_model=None,options=None,runtime=None,session=None):
    started=time.perf_counter();options=options or FieldOptions();runtime=runtime or Runtime(timeout=options.timeout_seconds)
    fork_model=fork_model or ForkModel(runtime.version);fork_model.validate(runtime)
    session=session or ForkSession(runtime)
    if session.runtime is not runtime:
        raise ValueError('Fork session belongs to a different runtime instance')
    calls=runtime.invocations;hits=session.native.hits
    original=starting_infer(cases,starting_model,field_model,options=options,runtime=runtime,session=session.starting)
    version=fork_model.version;session.native.bind(digest([version,runtime.manifest,asdict(options)]))
    logical=original['execution']['logical_native_nodes'];jobs=[];plans={};generic=[]
    sensor=TV(1.,options.sensor_confidence);truncated=original['execution']['truncated'];error=original['execution']['error']
    for row in original['concepts']:
        if row['concept']!='Fork':
            generic.append(None);continue
        packet=fork_packet(row);observation=copy.deepcopy(row['observation'])
        observation.update(id=packet['id'],descriptor=packet['descriptor'],rule_id=packet['rule_id'],complete=packet['complete'],gaps=packet['gaps'])
        hypothesis=fork_model.hypotheses.get(packet['rule_id'])
        gaps=list(packet['gaps'])
        if hypothesis is None:
            gaps.append('No learned piece-independent fork conditional matches this packet.')
        result={**copy.deepcopy(row),**_empty_core(gaps), 'model_version':version,
            'rule_id':packet['rule_id'],'descriptor':packet['descriptor'],'observation':observation,
            'observation_id':packet['id'],'fork_role_packet':packet,
            'evidence_ids':list(hypothesis['evidence_ids']) if hypothesis else [],
            'dependence_groups':list(hypothesis['dependence_groups']) if hypothesis else []}
        viable=packet['complete'] and hypothesis is not None and sensor.confidence>0
        viable=viable and any(hypothesis[c]['confidence']>0 for c in ('positive','negative'))
        exhausted=viable and logical+4>options.max_native_invocations
        deadline=time.perf_counter()-started>=options.timeout_seconds
        if exhausted or deadline:
            result.update(classification='incomplete',proof_status='incomplete');truncated=True
            result['gaps'].append('Combined starting/fork proof-node or wall-time budget exhausted.')
        elif viable:
            logical+=4
            if packet['id'] not in plans:
                nodes,trace,selected=_schedule(observation,hypothesis,version,runtime.version,sensor)
                jobs.extend(nodes);plans[packet['id']]=dict(trace=trace,selected=selected,results=[])
            plans[packet['id']]['results'].append(result)
        generic.append(result)
    if jobs:
        previous=runtime.timeout
        try:
            remaining=options.timeout_seconds-(time.perf_counter()-started)
            if remaining<=0:
                raise NativeError('Fork deadline exhausted before native execution')
            runtime.timeout=min(previous,remaining);values=session.native.batch(jobs)
            for plan in plans.values():
                trace=[{**node,'truth_value':values[node['id']].json()} for node in plan['trace']]
                value=values[plan['selected']]
                for result in plan['results']:
                    result.update(raw_stv=value.json(),classification=classify(value,options),proof_trace=copy.deepcopy(trace),
                        proof_id=digest(trace),conditional_proof_complete=True,proof_status='native-packet-conditional',truth_value_origin='native')
        except NativeError as failure:
            truncated=True;error=str(failure)
            for plan in plans.values():
                for result in plan['results']:
                    result.update(classification='incomplete',proof_status='incomplete',planned_native_nodes=plan['trace'])
                    result['gaps'].append('Native failure without host fallback: '+error)
        finally:
            runtime.timeout=previous
    results=[]
    for old,new in zip(original['concepts'],generic):
        if new:
            new['concept_status']={'supported':'partial-concept-candidate','contradicted':'conditional-counterevidence',
                'unknown':'unverified-hypothesis','incomplete':'incomplete'}[new['classification']]
        effective=new if new is not None and old['classification']=='unknown' else old
        results.append({**copy.deepcopy(effective),'starting_conditional':copy.deepcopy(old),
            'fork_role_conditional':copy.deepcopy(new),'conditional_selection':'learned-fork-role' if effective is new and new is not None else 'preserved-starting-conditional'})
    return dict(schema='concept-comparison-v13',concepts=results,model_version=starting_model.version,
        fork_model_version=version,field_model_version=field_model.version,runtime_version=runtime.version,
        strategic_score=None,joint_native_composition=False,
        execution=dict(elapsed_seconds=time.perf_counter()-started,native_invocations=runtime.invocations-calls,
            scheduled_invocations=original['execution']['scheduled_invocations']+len(jobs),logical_native_nodes=logical,
            cache_hits=session.native.hits-hits+original['execution']['native_math_cache_hits']+original['execution']['field_relation_cache_hits'],
            proof_bytes=sum(len(canonical(r['proof_trace']).encode()) for r in results),
            grounded_atoms=logical,truncated=truncated,error=error,starting=original['execution']))
