"""Native conditional preference application; no host truth-value arithmetic."""
import copy
from dataclasses import asdict
import time
from pln_chess.common import digest, canonical
from pln_chess.pln import Runtime, TV, UNKNOWN, NativeError
from pln_chess.inference import classify
from pln_chess.cycle3.native import NativeSession
from pln_chess.cycle11.fields.inference import FieldOptions
from .ontology import project, CHANNELS


class PreferenceNativeSession:
    def __init__(self,runtime):
        self.runtime=runtime
        self.native=NativeSession(runtime)


def infer_preferences(packets,model,*,runtime=None,options=None,session=None):
    started=time.perf_counter();options=options or FieldOptions()
    if not isinstance(packets,(list,tuple)) or len(packets)>64:
        raise ValueError('At most 64 explicit preference packets per native batch')
    observations=[project(packet,model.abstraction) for packet in packets]
    runtime=runtime or Runtime(timeout=options.timeout_seconds);model.validate(runtime)
    session=session or PreferenceNativeSession(runtime)
    if session.runtime is not runtime:
        raise ValueError('Preference session belongs to a different runtime instance')
    version=model.version;calls=runtime.invocations;hits=session.native.hits
    session.native.bind(digest([version,runtime.manifest,asdict(options)]))
    sensor=TV(1.,options.sensor_confidence)
    results=[];jobs=[];plans={};logical=0;truncated=False;error=None
    for packet,observation in zip(packets,observations):
        hypothesis=model.hypotheses.get(observation['rule_id'])
        result=dict(status='indeterminate',channels={side:dict(raw_stv=UNKNOWN.json(),classification='unknown')
            for side in ('A','B','no-demonstrated-preference')},rule_id=observation['rule_id'],
            descriptor=observation['descriptor'],observation=observation,observation_id=observation['id'],
            evidence_ids=list(hypothesis['evidence_ids']) if hypothesis else [],
            dependence_groups=list(hypothesis['dependence_groups']) if hypothesis else [],
            learned_conditional=copy.deepcopy(hypothesis),
            training_provenance=dict(dataset_hash=model.training_report.get('dataset_hash'),ledger_digest=model.ledger_digest,
                training_examples=model.training_report.get('training_examples',0)),
            opposing_training_labels=bool(hypothesis and sum(bool(hypothesis['supporting_evidence'][c]) for c in CHANNELS)>1),
            model_version=version,runtime_version=runtime.version,proof_trace=[],proof_id=digest([]),
            conditional_proof_complete=False,joint_proof_complete=False,proof_status='no-native-conditional-proof',
            contradiction=False,no_preference_supported=False,gaps=list(packet['gaps']),
            truth_value_origin='absence-prior',strategic_score=None,actionable_move=None,
            scope='Native conditional on an explicit host-assembled relative count packet; neither a joint strategic theorem nor a legal-move decision.')
        viable=(hypothesis is not None and observation['complete'] and sensor.confidence>0
            and any(value['confidence']>0 for value in hypothesis['channels'].values()))
        exhausted=viable and logical+3>options.max_native_invocations
        deadline=time.perf_counter()-started>=options.timeout_seconds
        if not observation['complete'] or exhausted or deadline:
            result.update(status='incomplete',proof_status='incomplete')
            result['gaps'].append('Required comparison observation or native work is incomplete.')
            truncated |= exhausted or deadline
        elif viable:
            logical+=3
            if observation['id'] not in plans:
                trace=[]
                for index,channel in enumerate(CHANNELS):
                    name='preference'+observation['id'].split(':')[1][:32]+str(index)
                    conditional=TV.from_json(hypothesis['channels'][channel])
                    expression=f'(Truth_ModusPonens {sensor.metta()} {conditional.metta()})'
                    jobs.append((name,expression))
                    trace.append(dict(id=name,operator='Truth_ModusPonens',native_expression=expression,
                        conclusion=dict(predicate='MovePreference',canonical_channel=channel),
                        premises=[dict(predicate='ObservedRelativeComparisonPacket',observation_id=observation['id'],
                            descriptor=observation['descriptor'],truth_value=sensor.json(),source_packet_id=packet['id'],
                            scope='Supplied sensor trust; no native conjunction of underlying field truths.'),
                            dict(rule_id=observation['rule_id'],channel=channel,truth_value=conditional.json())],
                        matched_rule_ids=[observation['rule_id']],evidence_ids=sorted(hypothesis['evidence_ids']+[observation['id']]),
                        dependence_groups=hypothesis['dependence_groups'],model_version=version,runtime_version=runtime.version,
                        proof_scope='Conditional application only; no complete strategic proof.'))
                plans[observation['id']]=dict(trace=trace,results=[])
            plans[observation['id']]['results'].append(result)
        elif hypothesis is None:
            result['gaps'].append('No learned conditional matches this relative packet.')
        else:
            result['gaps'].append('No positive-confidence packet or conditional evidence.')
        if not observation['distinguishable']:
            result['gaps'].append('The selected abstraction cannot distinguish the candidates directionally.')
        results.append(result)
    if jobs:
        previous_timeout=runtime.timeout
        try:
            remaining=options.timeout_seconds-(time.perf_counter()-started)
            if remaining<=0:
                raise NativeError('Preference deadline exhausted before native execution')
            runtime.timeout=min(previous_timeout,remaining)
            values=session.native.batch(jobs)
            for plan in plans.values():
                trace=[{**node,'truth_value':values[node['id']].json()} for node in plan['trace']]
                for result in plan['results']:
                    order=result['observation']['canonical_order']+['no-demonstrated-preference']
                    channels={side:dict(raw_stv=values[node['id']].json(),classification=classify(values[node['id']],options))
                        for side,node in zip(order,trace)}
                    a,b,n=(channels[side]['classification']=='supported' for side in ('A','B','no-demonstrated-preference'))
                    contradiction=(a and b) or (n and (a or b))
                    direction=result['observation']['distinguishable'] and not contradiction
                    result.update(channels=channels,status='A-preferred' if a and direction else 'B-preferred' if b and direction else 'indeterminate',
                        proof_trace=copy.deepcopy(trace),proof_id=digest(trace),conditional_proof_complete=True,
                        proof_status='native-packet-conditional',truth_value_origin='native',
                        contradiction=contradiction,no_preference_supported=n)
                    if contradiction:
                        result['gaps'].append('Opposing native channels are supported; no winner is selected.')
        except NativeError as failure:
            truncated=True;error=str(failure)
            for plan in plans.values():
                for result in plan['results']:
                    result.update(status='incomplete',proof_status='incomplete',planned_native_nodes=copy.deepcopy(plan['trace']))
                    result['gaps'].append('Native execution failed without host fallback: '+error)
        finally:
            runtime.timeout=previous_timeout
    for result in results:
        result['proof_graph']=dict(kind='conditional-preference',observation=result['observation'],
            native_nodes=copy.deepcopy(result['proof_trace']),proof_id=result['proof_id'],
            host_grouping_has_truth_value=False,joint_proof_complete=False)
    return dict(schema='preference-comparison-v13',comparisons=copy.deepcopy(results),
        model_version=version,runtime_version=runtime.version,
        execution=dict(elapsed_seconds=time.perf_counter()-started,native_invocations=runtime.invocations-calls,
            scheduled_invocations=len(jobs),logical_native_nodes=logical,cache_hits=session.native.hits-hits,
            proof_bytes=sum(len(canonical(r['proof_trace']).encode()) for r in results),
            grounded_atoms=logical+len(observations),truncated=truncated,error=error))
