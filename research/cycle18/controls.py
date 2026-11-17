"""Falsifiable source-bound contract controls; synthetic measurements quarantined."""
from dataclasses import replace
from fractions import Fraction as F
from .contracts import Kind, Registry, observation, identity, canonical
from .reference_joint import fit, result, Limits, encode
from .reference_bounds import posterior_bounds, unidentified
from .applications import ApplicationJournal
from .source_mapping import RULES


def expect_error(call):
    try:
        call()
    except (ValueError, TypeError) as error:
        return str(error)
    raise AssertionError('Expected rejection')


def measurement_noise(y1,y2,policy):
    """Two readings of one fair latent bit; complete finite declared noise model."""
    weights=[]
    for latent in (False,True):
        if policy=='noiseless-copy':
            likelihood=F(int(y1==latent and y2==latent))
        elif policy=='common-flip-1/10':
            likelihood=sum((p for flip,p in ((False,F(9,10)),(True,F(1,10)))
                if (latent!=flip)==y1 and (latent!=flip)==y2),F(0))
        elif policy=='independent-flips-1/10':
            likelihood=(F(9,10) if y1==latent else F(1,10))*(F(9,10) if y2==latent else F(1,10))
        else:
            raise ValueError('Unregistered noise policy')
        weights.append(likelihood/2)
    total=sum(weights)
    return dict(policy=policy,prior=['1/2','1/2'],readings=[y1,y2],unnormalized=list(map(str,weights)),
        status='point_under_declared_model' if total else 'inconsistent_evidence',
        latent_true_probability=str(weights[1]/total) if total else None)


def run(registry,memberships):
    measurements=[]
    def evaluate(*args,**kwargs):
        fitted=fit(*args,**kwargs)
        measurements.append(fitted.json()['resources'])
        return fitted
    selection=memberships['S-AA']; first=next(iter(selection));event=registry.get(first)
    before=registry.scientific_identity
    base=evaluate(registry,selection);d=base.json();bounds=posterior_bounds(base)
    duplicate=[registry.register(event) for _ in range(10)]
    assert not any(duplicate) and registry.scientific_identity==before
    assert evaluate(registry,selection)==base
    changed={**event.payload,'labels':{RULES[0]:False,RULES[1]:True}}
    changed_same_id=replace(event,observed_variables_json=canonical(changed),payload_hash=identity(changed))
    conflict=expect_error(lambda:registry.register(changed_same_id))
    assert registry.scientific_identity==before
    journals={}
    for count in (1,10,100):
        journal=ApplicationJournal()
        for _ in range(count):
            journal.apply(base,bindings={'attacker':'a','target':'t'},environment=[event.parent_event_ids[0]],
                state='s',history='h',query='two-distinct-trial-success')
        assert len(journal.records)==count and registry.scientific_identity==before
        assert evaluate(registry,selection)==base and posterior_bounds(base)==bounds
        journals[str(count)]=dict(applications=len(journal.records),generation=d['parameter_generation']['parameter_generation_id'],
            admitted_events=d['event_ids'],posterior_identity=d['posterior_identity'],bounds_identity=bounds.scientific_identity)
    journal=ApplicationJournal()
    def apply(parents=None,state='s',history='h'):
        return journal.apply(base,bindings={'a':'rook','t':'target'},environment=[event.parent_event_ids[0]],
            state=state,history=history,query='two-distinct-trial-success',parents=parents)
    origin=apply();oid=origin['application']['application_id']
    left=apply([oid]);right=apply([oid]);join=apply([left['application']['application_id'],right['application']['application_id']])
    cycle=[];parent=join['application']['application_id']
    for _ in range(10):
        record=apply([parent]);parent=record['application']['application_id'];cycle.append(record)
    assert {r['posterior_identity'] for r in journal.records}=={d['posterior_identity']}
    state_change=apply(state='new');history_change=apply(history='new')
    assert len({origin['context_identity'],state_change['context_identity'],history_change['context_identity']})==3
    self_training=expect_error(lambda:registry.register(base))
    fake_payload={**event.payload,'origin':'inference-prediction'}
    fake=observation('quarantine:prediction',fake_payload,episode='synthetic',groups=['quarantine:prediction'],
        kind=Kind.EVALUATION,method='Deliberate self-training attack',admission='admitted')
    registry.register(fake)
    inference_rejection=expect_error(lambda:fit(registry,{fake.event_id:RULES}))
    # Distinct event with identical measured payload retains distinct identity.
    new=observation('quarantine:new-measurement',event.payload,episode='quarantine:new-episode',groups=['quarantine:new-group'],
        kind=Kind.EVALUATION,method='Synthetic new external event; identical payload; independent group is an assumption',admission='admitted')
    registry.register(new)
    assert new.payload_hash==event.payload_hash and new.event_id!=event.event_id
    extended={**selection,new.event_id:RULES};updated=evaluate(registry,extended,prior_generation=d['parameter_generation']['parameter_generation_id'])
    assert updated.json()['posterior_identity']!=d['posterior_identity']
    removed=dict(selection);removed.pop(first)
    reduced=evaluate(registry,removed)
    assert reduced.json()['posterior_identity']!=d['posterior_identity']
    # Each incremental admission reconstructs from exact active IDs. No confidence subtraction.
    incremental={};prefixes=[];ingested=Registry()
    for eid,components in selection.items():
        current=registry.get(eid)
        for parent in current.parent_event_ids:
            ingested.register(registry.get(parent))
        ingested.register(current)
        incremental[eid]=components
        incremental_result=evaluate(ingested,incremental)
        reversed_result=evaluate(registry,dict(reversed(list(incremental.items()))))
        assert incremental_result==reversed_result
        prefixes.append(incremental_result.json()['posterior_identity'])
    assert incremental_result==base
    bad=observation('quarantine:conflicting-vector',changed,episode='quarantine:conflict',groups=['quarantine:conflict'],
        kind=Kind.EVALUATION,method='Synthetic corruption of an actual vector; not training evidence',admission='admitted')
    registry.register(bad)
    impossible=evaluate(registry,{bad.event_id:RULES})
    assert impossible.json()['status']=='inconsistent_evidence'
    noisy=[measurement_noise(True,True,p) for p in ('noiseless-copy','common-flip-1/10','independent-flips-1/10')]
    conflicts=[measurement_noise(True,False,p) for p in ('noiseless-copy','common-flip-1/10','independent-flips-1/10')]
    assert [r['latent_true_probability'] for r in noisy]==['1','9/10','81/82']
    assert [r['status'] for r in conflicts]==['inconsistent_evidence','inconsistent_evidence','point_under_declared_model']
    # Explicit supersession retains the original immutable version and changes active view.
    corrected=observation('quarantine:corrected-vector',event.payload,episode=bad.source_episode_id,groups=bad.ancestry_groups,
        kind=Kind.SUPERSEDED,method='Explicit synthetic correction',admission='admitted',supersedes=bad.event_id)
    registry.register(corrected)
    superseded_rejection=expect_error(lambda:fit(registry,{bad.event_id:RULES}))
    assert evaluate(registry,{corrected.event_id:RULES}).json()['status']=='point_under_declared_model'
    incomplete=[evaluate(registry,selection,limits=l).json() for l in (Limits(states=1),Limits(groups=1),
        Limits(likelihood_evaluations=1),Limits(rational_bits=1))]
    assert all(r['status']=='resource_incomplete' for r in incomplete)
    return encode(dict(schema='cycle18-contract-controls-v1',passed=True,source_event=event.json(),
        quarantine='All new measurements/corruptions exist only in this in-memory reference control registry',
        duplicate_deliveries=10,duplicate_added=0,changed_payload_rejection=conflict,
        application_repeats=journals,diamond=dict(origin=origin,left=left,right=right,join=join),
        cycle=cycle,cycle_evidence_added=0,state_change=state_change,history_change=history_change,
        self_training_rejections=[self_training,inference_rejection],new_equal_payload_event=new.json(),
        new_external_generation=updated.json(),source_removed_generation=reduced.json(),
        full_recomputation_order_parity=True,incremental_prefix_posteriors=prefixes,
        copy_conflict=impossible.json(),two_measurement_noise_cases=noisy,two_measurement_conflicts=conflicts,
        supersession=dict(original=bad.json(),replacement=corrected.json(),old_active_rejected=superseded_rejection),
        missing_dependence=unidentified().json(),bounded_dependence=bounds.json(),resource_failures=incomplete,
        resources=dict(fits=len(measurements),likelihood_evaluations=sum(r['likelihood_evaluations'] for r in measurements),
            max_states=max(r['states'] for r in measurements),max_rational_bits=max(r['max_rational_bits'] for r in measurements),
            measurement_noise_cases=6,measurement_noise_latent_states_per_case=2)))
