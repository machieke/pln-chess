"""Existing native TV rules on explicit host-observed concept packets."""
import copy
from dataclasses import asdict, replace
import time

from pln_chess.common import digest, canonical
from pln_chess.inference import classify
from pln_chess.pln import Runtime, TV, UNKNOWN, NativeError
from pln_chess.cycle3.native import NativeSession
from pln_chess.cycle11.fields.inference import FieldOptions, FieldSession, infer_queries
from .ontology import CONCEPTS, observe_concept, component_queries


class ConceptSession:
    def __init__(self,runtime,max_entries=4096):
        if type(max_entries) is not int or max_entries<0:raise ValueError('Invalid concept cache capacity')
        self.runtime=runtime;self.native=NativeSession(runtime);self.fields=FieldSession(runtime)
        self.scope=None;self.cache={};self.max_entries=max_entries

    def bind(self,scope):
        if scope!=self.scope:self.cache.clear();self.scope=scope
        self.native.bind(scope)

    def put(self,identifier,record):
        if self.max_entries:
            self.cache[identifier]=copy.deepcopy(record)
            while len(self.cache)>self.max_entries:self.cache.pop(next(iter(self.cache)))


def _schedule(observation,hypothesis,model_version,runtime_version,sensor):
    stem='concept'+observation['id'].split(':')[1][:32]
    names=[stem+suffix for suffix in ('p','n','x','s')]
    positive,negative=TV.from_json(hypothesis['positive']),TV.from_json(hypothesis['negative'])
    expressions=[f'(Truth_ModusPonens {sensor.metta()} {positive.metta()})',
        f'(Truth_ModusPonens {sensor.metta()} {negative.metta()})',
        f'(Truth_Negation ({names[1]}))',
        f'(let ($tv $ev) (BestConfidenceCandidate ((({names[0]}) (positive)) (({names[2]}) (negative)))) $tv)']
    packet=dict(predicate='ObservedStructuralRolePacket',observation_id=observation['id'],truth_value=sensor.json(),
        descriptor=observation['descriptor'],roles=observation['roles'],source=observation['source'],
        component_observation_ids=[c['observation']['id'] for c in observation['components'] if c['observation']],
        grouping='Host-supplied composite observation; no native conjunction and no fusion of component field TVs.')
    premises=[[packet,dict(hypothesis=observation['rule_id'],channel='positive',truth_value=positive.json())],
        [packet,dict(hypothesis=observation['rule_id'],channel='negative',truth_value=negative.json())],
        [dict(node=names[1])],[dict(node=names[0]),dict(node=names[2])]]
    traces=[]
    for index,(name,expression,operator,premise) in enumerate(zip(names,expressions,
        ('Truth_ModusPonens','Truth_ModusPonens','Truth_Negation','BestConfidenceCandidate'),premises)):
        traces.append(dict(id=name,operator=operator,native_expression=expression,
            conclusion=dict(predicate=observation['target'],concept=observation['concept'],negated=index==1),
            premises=premise,matched_rule_ids=[observation['rule_id']],
            evidence_ids=sorted(set(hypothesis['evidence_ids']+[observation['id']])),
            dependence_groups=hypothesis['dependence_groups'],model_version=model_version,runtime_version=runtime_version,
            observation_id=observation['id'],
            proof_scope='Native conditional on a host-observed structural packet. No joint uncertain-field proof or complete strategic concept.'))
    return list(zip(names,expressions)),traces,names[-1]


def _empty_core(gaps):
    return dict(raw_stv=UNKNOWN.json(),classification='unknown',conditional_proof_complete=False,
        proof_trace=[],proof_id=digest([]),proof_status='no-native-conditional-proof',truth_value_origin='absence-prior',gaps=list(gaps))


def infer_concepts(cases,model,field_model,*,options=None,runtime=None,session=None):
    started=time.perf_counter();options=options or FieldOptions()
    if not isinstance(cases,(list,tuple)) or len(cases)>64:raise ValueError('At most 64 explicit concept candidates per batch')
    runtime=runtime or Runtime(timeout=options.timeout_seconds);model.validate(runtime);field_model.validate(runtime)
    version=model.version;session=session or ConceptSession(runtime)
    if session.runtime is not runtime:raise ValueError('Concept session belongs to another runtime instance')
    calls=runtime.invocations;native_hits=session.native.hits
    session.bind(digest([version,runtime.manifest,asdict(options)]))
    observations=[observe_concept(case) for case in cases]
    field_queries=[q for observation in observations for q in component_queries(observation)]
    if field_queries:
        remaining=options.timeout_seconds-(time.perf_counter()-started)
        previous_timeout=runtime.timeout
        try:
            runtime.timeout=min(previous_timeout,max(.001,remaining))
            # Keep the caller's option identity stable across cache lookups;
            # remaining wall time is an execution limit, not a new hypothesis.
            field_result=infer_queries(field_queries,field_model,options,runtime,session.fields)
        finally:runtime.timeout=previous_timeout
    else:
        field_result=dict(relations=[],logical_native_nodes=0,scheduled_invocations=0,native_invocations=0,
            truncated=False,error=None,relation_cache_hits=0)
    relations={r['query_id']:r for r in field_result['relations']}
    logical_nodes=field_result['logical_native_nodes'];jobs=[];pending={};cores=[];cache_hits=0
    truncated=field_result['truncated'];error=field_result['error'];sensor=TV(1.,options.sensor_confidence)
    for observation in observations:
        hypothesis=model.hypotheses.get(observation['rule_id']);gaps=list(observation['gaps'])
        if hypothesis is None:gaps.append('No learned conditional matches this role packet.')
        if sensor.confidence==0:gaps.append('The supplied packet has zero observation confidence.')
        viable=observation['complete'] and hypothesis is not None and sensor.confidence>0
        if viable and not any(hypothesis[channel]['confidence']>0 for channel in ('positive','negative')):
            viable=False;gaps.append('The learned conditional has no positive-confidence evidence.')
        core=_empty_core(gaps)
        exhausted=viable and logical_nodes+4>options.max_native_invocations
        deadline=time.perf_counter()-started>=options.timeout_seconds
        if exhausted or deadline:
            truncated=True;core.update(classification='incomplete',proof_status='incomplete')
            core['gaps'].append('Combined field/concept proof-node budget exhausted.' if exhausted else 'Concept inference deadline exhausted.')
        elif viable:
            logical_nodes+=4
            if observation['id'] in session.cache:
                core=copy.deepcopy(session.cache[observation['id']]);cache_hits+=1
            elif observation['id'] in pending:
                core=pending[observation['id']]['core']
            else:
                nodes,trace,selected=_schedule(observation,hypothesis,version,runtime.version,sensor)
                jobs.extend(nodes);pending[observation['id']]=dict(core=core,trace=trace,selected=selected)
        cores.append(core)
    if jobs:
        previous_timeout=runtime.timeout
        try:
            remaining=options.timeout_seconds-(time.perf_counter()-started)
            if remaining<=0:raise NativeError('Concept deadline exhausted before native execution')
            runtime.timeout=min(previous_timeout,remaining);values=session.native.batch(jobs)
            for identifier,plan in pending.items():
                trace=[{**node,'truth_value':values[node['id']].json()} for node in plan['trace']]
                tv=values[plan['selected']];core=plan['core']
                core.update(raw_stv=tv.json(),classification=classify(tv,options),conditional_proof_complete=True,
                    proof_trace=trace,proof_id=digest(trace),proof_status='native-packet-conditional',truth_value_origin='native')
                if core['classification']=='unknown':core['gaps'].append('Conditional evidence is below the registered thresholds.')
                session.put(identifier,core)
        except NativeError as failure:
            truncated=True;error=str(failure)
            for plan in pending.values():
                plan['core'].update(classification='incomplete',proof_status='incomplete',planned_native_nodes=plan['trace'])
                plan['core']['gaps'].append('Native execution failed; no host inference fallback: '+error)
        finally:runtime.timeout=previous_timeout
    results=[]
    for index,(case,observation,core) in enumerate(zip(cases,observations,cores)):
        hypothesis=model.hypotheses.get(observation['rule_id']);fields=[];component_status=[]
        for i,component in enumerate(observation['components']):
            record=relations.get(observation['id']+':component:'+str(i))
            if record is not None:
                record=copy.deepcopy(record)
                record['concept_component']=dict(stage=component['stage'],source_role=component['source_role'],
                    target_role=component['target_role'],expected_polarity=component['expected_polarity'])
                fields.append(record)
            component_status.append(dict(stage=component['stage'],source_role=component['source_role'],target_role=component['target_role'],
                expected_polarity=component['expected_polarity'],classification=record['classification'] if record else 'unknown',
                proof_id=record['proof_id'] if record else None,absent_source=component['absent_source']))
        concept=observation['concept'];spec=CONCEPTS[concept]
        diagnostics=dict(strategic_value=None,complete_concept_truth_value=None,legal_restriction_proved=False)
        if concept=='Pin':
            target=observation['roles']['target']
            diagnostics['target_role']='unobserved' if not target['observed'] else 'absent' if not target['piece'] else 'absolute-pin-target' if target['piece']['kind']=='King' else 'relative-pin-target'
        if concept=='OverloadedDefender':
            diagnostics.update(strategically_overloaded=None,obligations=component_status,
                consequence_scope='Local obligations are retained separately. Supplied counterfactual responses require separate before/after field comparisons; no exhaustive response search is performed.')
        if concept=='TrappedPiece':
            diagnostics.update(geometric_candidate_cells=len(observation['components']),
                locally_supported_ordinary_exits=[r['target_square'] for r in fields if r['classification']=='supported'],
                contradicted_ordinary_exits=[r['target_square'] for r in fields if r['classification']=='contradicted'],
                unknown_ordinary_exits=[r['target_square'] for r in fields if r['classification'] in ('unknown','incomplete')],
                supported_legal_exits=None,unfavorable_exits=None,strategically_trapped=None)
        result=dict(case_id=case.get('id','concept-case:'+digest(case)),concept=concept,target=spec['target'],
            rule_id=observation['rule_id'],descriptor=observation['descriptor'],observation=observation,
            observation_id=observation['id'],model_version=version,field_model_version=field_model.version,runtime_version=runtime.version,
            evidence_ids=list(hypothesis['evidence_ids']) if hypothesis else [],
            dependence_groups=list(hypothesis['dependence_groups']) if hypothesis else [],
            structural_candidate=True,joint_proof_complete=False,field_relations=fields,component_status=component_status,
            missing_capabilities=list(spec['gaps'])+['No native conjunction is supplied by the host dependency graph.'],
            diagnostics=diagnostics,**copy.deepcopy(core))
        result['concept_status']={'supported':'partial-concept-candidate','contradicted':'conditional-counterevidence',
            'unknown':'unverified-hypothesis','incomplete':'incomplete'}[core['classification']]
        results.append(result)
    return dict(schema='relative-concept-result-v12',concepts=results,model_version=version,field_model_version=field_model.version,
        runtime_version=runtime.version,strategic_score=None,move_ranking=None,joint_native_composition=False,
        execution=dict(native_invocations=runtime.invocations-calls,scheduled_invocations=len(jobs)+field_result['scheduled_invocations'],
            logical_native_nodes=logical_nodes,concept_cache_hits=cache_hits,native_math_cache_hits=session.native.hits-native_hits,
            field_relation_cache_hits=field_result['relation_cache_hits'],elapsed_seconds=time.perf_counter()-started,
            proof_bytes=sum(len(canonical(r['proof_trace']).encode()) for r in results),truncated=truncated,error=error),
        scope='Independent native fields plus native conditionals on explicitly host-grouped structural packets. Complete strategic interpretations remain partial.')
