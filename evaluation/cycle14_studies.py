"""Registered representation, matched factorial and reversal diagnostics."""
import argparse
import copy
from collections import Counter,defaultdict
from pathlib import Path
import random

from pln_chess.common import ROOT,canonical,digest,read_json
from pln_chess.pln import Runtime
from pln_chess.cycle14.ontology import ABSTRACTIONS,project,omit_context,reverse_packet
from pln_chess.cycle14.model import PreferenceModel
from pln_chess.cycle14.evidence import EvidenceLedger
from training.cycle14_features import training_records
from training.cycle14_learning import train
from training.cycle14_labels import atomic_json
from evaluation.cycle14_preferences import predict,load_model,data_identity
from evaluation.cycle14_metrics import counts,clustered_intervals,percentile
from evaluation.cycle3 import read_gzip
from evaluation.cycle7_io import pack
from scripts.cycle9_baseline import sha


def register_reversals(out):
    """Read observation packets only; never labels or preference predictions."""
    out=Path(out);generations=read_json(out/'features/selected-generations.json')
    indexes={kind:read_json(out/'features'/generation/'index.json') for kind,generation in generations.items()
        if kind in ('immediate','temporal')}
    immediate={r['id']:r['observations'][0]['packet'] for r in indexes['immediate']['records']}
    temporal={r['id']:r for r in indexes['temporal']['records']}
    plans=read_json(out/'datasets/temporal-registration.json');rows=[]
    for plan in plans['records']:
        if plan['split']!='test':continue
        root=immediate[plan['id']];end=temporal[plan['id']]['observations'][-1]['packet']
        changes=[]
        for side in ('A','B'):
            for family in ('attack','defense','mobility'):
                before=root['base']['profiles'][side]['fields'][family]
                after=end['base']['profiles'][side]['fields'][family]
                if before['supported']!=after['supported']:changes.append(dict(side=side,family=family,before=before,after=after))
        rows.append(dict(id=plan['id'],dependence_group=plan['dependence_group'],source_game=plan['source_game'],
            complete=root['base']['complete'] and end['base']['complete'],changes=changes,
            initial_packet_id=root['id'],endpoint_packet_id=end['id'],horizon=3))
    rows.sort(key=lambda r:digest(['c14-reversal-panel',r['id']]))
    selected=[];used=set()
    for arm,want_change in (('reversal-opportunity',True),('persistence-control',False)):
        candidates=[r for r in rows if r['id'] not in used]
        candidates.sort(key=lambda r:(not(r['complete'] and bool(r['changes'])==want_change),digest(['c14-reversal-panel',r['id']])))
        for row in candidates[:10]:
            selected.append({**row,'arm':arm,'structural_criterion_met':row['complete'] and bool(row['changes'])==want_change})
            used.add(row['id'])
    assert len(selected)==len(used)==20
    payload=dict(schema='c14-reversal-registration-v1',records=selected,primary_horizon=3,secondary_horizon=2,
        policy='Complete native endpoint attack/defense/mobility support changes prioritize opportunities; unchanged support prioritizes persistence controls. Hash order resolves ties and preserves deterministic fallback cases.',
        reference_labels_read=False,model_predictions_read=False,source_temporal_registration=plans['hash'],
        effective_independent_groups=20,already_in_primary_test=True,
        interpretation='Structural opportunities do not promise reference reversals; all outcomes and fallback failures remain in the denominator.')
    payload['hash']=digest(payload);atomic_json(out/'datasets/reversal-registration.json',payload)


def representation(out):
    out=Path(out);records=[r for r in training_records(out,temporal=True) if r['split'] in ('train','development')]
    summaries={};tables={}
    for abstraction in ABSTRACTIONS:
        groups=defaultdict(list)
        for row in records:
            p=project(row['packet'],abstraction)
            label=('first' if p['canonical_order'][0]==row['label'] else 'second') if row['label'] in ('A','B') else row['label']
            groups[p['rule_id']].append(dict(id=row['id'],label=label,split=row['split'],dependence_group=row['dependence_group'],
                descriptor=p['descriptor'],complete=p['complete'],distinguishable=p['distinguishable']))
        census=[]
        for key,rows in sorted(groups.items()):
            directions={r['label'] for r in rows if r['label'] in ('first','second')}
            census.append(dict(rule_id=key,descriptor=rows[0]['descriptor'],observations=len(rows),
                independent_groups=len({r['dependence_group'] for r in rows}),label_counts=dict(Counter(r['label'] for r in rows)),
                conflicting_directions=len(directions)==2,incomplete=sum(not r['complete'] for r in rows),
                nondistinguishable=sum(not r['distinguishable'] for r in rows),observation_ids=[r['id'] for r in rows]))
        tables[abstraction]=census
        summaries[abstraction]=dict(N=len(records),keys=len(census),conflicting_keys=sum(r['conflicting_directions'] for r in census),
            examples_in_conflicting_keys=sum(r['observations'] for r in census if r['conflicting_directions']),
            distinguishable_directional=sum(r['label'] in ('A','B') and project(r['packet'],abstraction)['distinguishable'] for r in records))
    # Metadata, pair orientation and declared unobserved context are tested over
    # the complete permitted representation-development population.
    invariance=[]
    for row in records:
        for abstraction in ABSTRACTIONS:
            original=project(row['packet'],abstraction);reversed_=project(reverse_packet(row['packet']),abstraction)
            assert original['rule_id']==reversed_['rule_id']
            if original['distinguishable']:assert original['canonical_order']==list(reversed(reversed_['canonical_order']))
            assert not any(x in canonical(original['descriptor']) for x in ('source_game','proof_id','reference_evidence_id','cp_score'))
            omitted=project(omit_context(row['packet']),abstraction)
            invariance.append(dict(id=row['id'],abstraction=abstraction,pair_rule_invariant=True,
                omitted_distinguishable=omitted['distinguishable'],omitted_coverage=omitted['descriptor']['coverage']))
    pack(out/'representation/collisions.json.xz',tables);pack(out/'representation/packet-controls.json.xz',invariance)
    atomic_json(out/'representation/census.json',dict(passed=True,cohorts=['train','development'],summaries=summaries,
        inspected_final_reference_labels=False,model_outcomes_used=False,orientation_checks=len(invariance),
        supplied_abstraction='Fixed coarse contrasts, explicit missingness and mover/shared-role counts; native revision learns channel TVs on these supplied keys.',
        limitation='Opposing labels can share a coarse key; refinement can reduce sharing while reducing support. Counts alone do not establish strategic sufficiency.'))


def paired_effect(left,right,repetitions=1000):
    a={r['id']:r for r in left};b={r['id']:r for r in right};assert set(a)==set(b)
    ids=sorted(a);assert all(a[i]['label']==b[i]['label'] and a[i]['dependence_group']==b[i]['dependence_group'] for i in ids)
    groups=defaultdict(list)
    for i in ids:groups[a[i]['dependence_group']].append(i)
    names=('answered_accuracy','directional_coverage','correct_answer_yield');rand=random.Random(141414)
    def differences(selected):
        first=counts([a[i] for i in selected]);second=counts([b[i] for i in selected])
        return {name:None if first[name] is None or second[name] is None else second[name]-first[name] for name in names}
    samples={name:[] for name in names};keys=sorted(groups)
    for _ in range(repetitions if keys else 0):
        sampled=[i for _ in keys for i in groups[rand.choice(keys)]]
        for name,value in differences(sampled).items():
            if value is not None:samples[name].append(value)
    return dict(N=len(ids),ancestry_groups=len(groups),right_minus_left=differences(ids),
        clustered_95_intervals={name:dict(low=percentile(v,.025),high=percentile(v,.975),defined_replicates=len(v)) for name,v in samples.items()},
        bootstrap_repetitions=repetitions,method='Paired source-ancestry percentile bootstrap; missing accuracy stays undefined')


def factorial(out):
    out=Path(out);runtime=Runtime();registry=read_json(out/'model/registry.json');freeze=read_json(out/'evaluation-freeze.json')
    assert sha(out/'model/registry.json')==freeze['registry_sha256']
    all_records=training_records(out,temporal=True);test=[r for r in all_records if r['split'] in ('test','source-holdout')]
    by_id={r['id']:r for r in test};primary=registry['primary_immediate'];models={name:load_model(out,entry,runtime) for name,entry in registry['models'].items()}
    saved={name:read_gzip(out/'evaluation'/name/'native-predictions.json.xz') for name in models}
    pairs=[('old-labels-old-descriptor','revised-labels-historical-only','supervision-matched-historical'),
        ('revised-labels-historical-only','immediate-c13-relational','additional-independent-evidence'),
        ('immediate-c13-relational',primary,'descriptor-matched-supervision'),
        (primary,'immediate-selected-concepts','concept-evidence'),
        ('revised-labels-historical-only','historical-dependent-repeat','dependent-repeated-labels'),
        ('historical-dependent-repeat','historical-unsafe-repeat','unsafe-dependence'),
        ('temporal-old-labels','temporal-revised-historical','temporal-supervision'),
        ('temporal-old-descriptor','temporal-selected','temporal-descriptor'),
        ('temporal-selected','temporal-selected-concepts','temporal-concepts')]
    effects=[]
    for left,right,factor in pairs:
        for split in ('test','source-holdout'):
            for h in (1,2,3):
                a=[r for r in saved[left] if r['split']==split and r['horizon']==h]
                b=[r for r in saved[right] if r['split']==split and r['horizon']==h]
                if not a or not b:continue
                effects.append(dict(factor=factor,left=left,right=right,split=split,horizon=h,
                    left_counts=counts(a),right_counts=counts(b),effect=paired_effect(a,b)))
    temporal=[]
    for split in ('test','source-holdout'):
        for horizon in (2,3):
            endpoints=[r for r in test if r['split']==split and r['temporal_context']['horizon']==horizon]
            roots=[dict(by_id[r['id'].rsplit('-ply',1)[0]],id=r['id'],label=r['label'],reference_evidence_id=r['reference_evidence_id']) for r in endpoints]
            omitted=[dict(r,packet=omit_context(r['packet'])) for r in endpoints]
            arms={}
            for checkpoint in (primary,'temporal-selected','temporal-omission-robust'):
                for context,rows in (('immediate',roots),('continued',endpoints),('omitted',omitted)):
                    name=checkpoint+'/'+context;arms[name]=predict(rows,models[checkpoint],runtime)
            pack(out/'temporal'/f'{split}-h{horizon}-factorial.json.xz',arms)
            comparisons=[(primary+'/immediate','temporal-selected/continued','combined-primary'),
                (primary+'/immediate','temporal-selected/immediate','temporal-training-with-immediate-input'),
                (primary+'/continued','temporal-selected/continued','temporal-training-with-same-continuation'),
                ('temporal-selected/immediate','temporal-selected/continued','same-checkpoint-observation-context'),
                ('temporal-selected/omitted','temporal-selected/continued','same-checkpoint-explicit-missingness'),
                ('temporal-omission-robust/omitted','temporal-omission-robust/continued','omission-robust-same-checkpoint')]
            temporal.append(dict(split=split,horizon=horizon,counts={name:counts(rows) for name,rows in arms.items()},
                paired=[dict(factor=factor,left=a,right=b,effect=paired_effect(arms[a],arms[b])) for a,b,factor in comparisons],
                root_endpoint_reference_changes=sum(by_id[r['id'].rsplit('-ply',1)[0]]['label']!=r['label'] for r in endpoints)))
    train_rows=[r for r in all_records if r['split']=='train' and r['temporal_context']['horizon']==1 and r['label'] in ('A','B')]
    majority=Counter(r['label'] for r in train_rows).most_common(1)[0][0]
    baselines=[]
    for split in ('test','source-holdout'):
        rows=[dict(id=r['id'],label=r['label'],dependence_group=r['dependence_group'],prediction={'status':majority+'-preferred'}) for r in test if r['split']==split and r['temporal_context']['horizon']==1]
        baselines.append(dict(split=split,majority_class=majority,training_only=True,counts=counts(rows),intervals=clustered_intervals(rows)))
    atomic_json(out/'ablations/summary.json',dict(passed=True,effects=effects,temporal=temporal,evaluation_only_majority=baselines,
        independent_channels_not_normalized=True,causal_scope='Controlled differences within registered finite cohorts; no strategic strength claim. Horizon-specific keys can make immediate-only models abstain on unseen horizon keys.'))
    atomic_json(out/'temporal/summary.json',dict(passed=True,panels=temporal,test_groups_each_horizon=50,
        same_roots_at_two_horizons=True,endpoint_targets_matched=True,original_actor_fixed=True,
        omission_is_valid_unknown_observation=True,exhaustive_responses=False))


def dependence(out):
    out=Path(out);runtime=Runtime();registry=read_json(out/'model/registry.json')
    records=training_records(out,temporal=True);training=[r for r in records if r['split']=='train'];selected=registry['selected_descriptor']
    original=load_model(out,registry['models']['temporal-selected'],runtime)
    temporal=[r for r in training if r['temporal_context']['horizon']>1]
    repeated=training+[dict(r,id=r['id']+'/repeated-reference-analysis') for r in temporal]+[dict(r,id=r['id']+'/repeated-continuation') for r in temporal]
    fits={}
    for name,handling in (('temporal-repeat-handled',True),('temporal-repeat-unsafe',False)):
        fits[name]=train(repeated,runtime,out/'dependence'/name,dataset_hash=data_identity(repeated),abstraction=selected,
            dependence=handling,baseline_root=out,variant='C14-'+name)
    channels=lambda m:{k:v['channels'] for k,v in m.hypotheses.items()}
    assert channels(original)==channels(fits['temporal-repeat-handled'])
    unsafe=fits['temporal-repeat-unsafe'];inflated=[key for key,h in original.hypotheses.items() if any(unsafe.hypotheses[key]['channels'][c]['confidence']>v['confidence'] for c,v in h['channels'].items())]
    primary=registry['primary_immediate'];immediate=[r for r in training if r['temporal_context']['horizon']==1]
    replay=train(immediate,runtime,out/'dependence/primary-replay',dataset_hash=data_identity(immediate),abstraction=selected,
        baseline_root=out,variant='C14-'+primary)
    assert sha(out/'dependence/primary-replay/checkpoint.json')==registry['models'][primary]['sha256']
    assert (out/'dependence/primary-replay/ledger.jsonl').read_bytes()==(out/'learning'/primary/'ledger.jsonl').read_bytes()
    old=EvidenceLedger(out/'learning/old-labels-old-descriptor/ledger.jsonl').records()
    new=EvidenceLedger(out/'learning/revised-labels-historical-only/ledger.jsonl').records()
    ledger=EvidenceLedger(out/'dependence/supersession/ledger.jsonl')
    for entries in (old,new):
        grouped=defaultdict(list)
        for entry in entries:grouped[entry['generation']].append(entry['payload'])
        for gen,payloads in sorted(grouped.items()):ledger.append_many(payloads,generation=gen)
    for gen in sorted({r['generation'] for r in old}):ledger.activate(gen,[r['payload']['observation_id'] for r in old if r['generation']==gen],rollback=True)
    assert ledger.records()==sorted(old,key=lambda r:r['payload']['observation_id'])
    old_rows=[r for r in training_records(out,labels='old') if r['split']=='train']
    rollback=train(old_rows,runtime,out/'dependence/rollback-fit',dataset_hash=data_identity(old_rows),baseline_root=out,variant='C14-old-labels-old-descriptor')
    assert sha(out/'dependence/rollback-fit/checkpoint.json')==registry['models']['old-labels-old-descriptor']['sha256']
    target=next(r for r in training if r['label'] in ('A','B') and project(r['packet'],selected)['distinguishable'] and project(r['packet'],selected)['complete'])
    conflict=dict(target,id=target['id']+'/conflicting-dependent-label',label='B' if target['label']=='A' else 'A')
    conflicted=train(training+[conflict],runtime,out/'dependence/conflict',dataset_hash=data_identity(training+[conflict]),abstraction=selected,baseline_root=out,variant='C14-conflict-control')
    withheld=[r for r in read_gzip(out/'dependence/conflict/native-training.json.xz')['excluded'] if r['reason']=='contradictory-dependent-component']
    assert any(target['dependence_group'] in r['dependence_groups'] for r in withheld)
    atomic_json(out/'dependence/summary.json',dict(passed=True,training_rows=len(training),repeated_rows=len(repeated),
        additional_independent_groups=0,handled_native_tvs_identical=True,unsafe_inflated_rules=inflated,
        primary_checkpoint_replayed_byte_identically=True,primary_ledger_replayed_byte_identically=True,
        superseded_versions_preserved=len(ledger.snapshot()['versions']),active_after_rollback=len(ledger.records()),
        rollback_checkpoint_byte_identical=True,conflicting_components_withheld=withheld,
        models={name:m.version for name,m in fits.items()},unsafe_counting_is_default=False))


def reversals(out):
    out=Path(out);runtime=Runtime();registration=read_json(out/'datasets/reversal-registration.json')
    freeze=read_json(out/'evaluation-freeze.json');assert sha(out/'datasets/reversal-registration.json')==freeze['reversal_registration_sha256']
    registry=read_json(out/'model/registry.json');model=load_model(out,registry['models']['primary-temporal'] if 'primary-temporal' in registry['models'] else registry['models'][registry['primary_temporal']],runtime)
    records={r['id']:r for r in training_records(out,temporal=True)};results=[]
    for registered in registration['records']:
        root=records[registered['id']]
        for horizon in (2,3):
            endpoint=records[root['id']+f'-ply{horizon}'];before=predict([root],model,runtime)[0]['prediction'];after=predict([endpoint],model,runtime)[0]['prediction']
            no_premise=predict([dict(endpoint,packet=omit_context(endpoint['packet']))],model,runtime)[0]['prediction']
            reduced=copy.deepcopy(model);key=project(endpoint['packet'],model.abstraction,concepts=model.use_concepts)['rule_id']
            removed=reduced.hypotheses.pop(key,None);reduced.variant='C14-counterfactual-conditional-removed'
            no_rule=predict([endpoint],reduced,runtime)[0]['prediction']
            supporting=set(removed['dependence_groups']) if removed else set()
            training=[r for r in records.values() if r['split']=='train' and r['dependence_group'] not in supporting]
            removal=train(training,runtime,out/'reversals/removal-fits'/f"{root['id']}-h{horizon}",dataset_hash=data_identity(training),
                abstraction=model.abstraction,concepts=model.use_concepts,baseline_root=out,variant='C14-supporting-ancestry-removed')
            no_evidence=predict([endpoint],removal,runtime)[0]['prediction']
            resolved=root['label'] in ('A','B') and endpoint['label'] in ('A','B');reference_flip=resolved and root['label']!=endpoint['label']
            model_flip=before['status'] in ('A-preferred','B-preferred') and after['status'] in ('A-preferred','B-preferred') and before['status']!=after['status']
            correct_before=before['status']==root['label']+'-preferred';correct_after=after['status']==endpoint['label']+'-preferred'
            success=resolved and correct_before and correct_after and (reference_flip if registered['arm']=='reversal-opportunity' else not reference_flip)
            results.append(dict(registered,horizon=horizon,initial_label=root['label'],endpoint_label=endpoint['label'],
                initial_reference=root['reference_evidence_id'],endpoint_reference=endpoint['reference_evidence_id'],
                before=before,after=after,premise_omitted=no_premise,conditional_removed=no_rule,evidence_ancestry_removed=no_evidence,
                removed_groups=sorted(supporting),removal_model_version=removal.version,resolved_both=resolved,
                reference_reversal=reference_flip,model_reversal=model_flip,successful_registered_outcome=success,
                failed_reasons=[reason for reason,failed in (('structural-criterion-unmet',not registered['structural_criterion_met']),
                    ('unresolved-reference',not resolved),('initial-answer-not-correct',not correct_before),('endpoint-answer-not-correct',not correct_after),
                    ('registered-target-pattern-not-observed',resolved and (reference_flip!=(registered['arm']=='reversal-opportunity')))) if failed],
                target_change='Root search versus supplied-branch endpoint search, always original actor; no optimal-play claim.'))
    pack(out/'reversals/panel.json.xz',results)
    summary=[]
    for arm in ('reversal-opportunity','persistence-control'):
        for horizon in (2,3):
            rows=[r for r in results if r['arm']==arm and r['horizon']==horizon]
            summary.append(dict(arm=arm,horizon=horizon,N=len(rows),structural_criteria_met=sum(r['structural_criterion_met'] for r in rows),
                N_resolved_both=sum(r['resolved_both'] for r in rows),reference_reversals=sum(r['reference_reversal'] for r in rows),
                model_reversals=sum(r['model_reversal'] for r in rows),successes=sum(r['successful_registered_outcome'] for r in rows),
                failures=[r['id'] for r in rows if not r['successful_registered_outcome']]))
    atomic_json(out/'reversals/summary.json',dict(passed=True,registration_hash=registration['hash'],panels=summary,
        independent_groups=20,primary_horizon=3,all_registered_cases_reported=True,proofs_and_removals_retained=True,
        interpretation='Engineering execution passed; successful_registered_outcome is the empirical research outcome. Structural change alone is not a validated preference reversal.'))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('stage',choices=('register_reversals','representation','factorial','dependence','reversals'));parser.add_argument('--out',default='artifacts/cycle14')
    args=parser.parse_args();globals()[args.stage](args.out)
