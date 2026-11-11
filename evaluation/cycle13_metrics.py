"""Preference diagnostics only; these numbers never participate in inference."""
from collections import Counter, defaultdict
import random
import statistics


def direction(row):
    return {'A-preferred':'A','B-preferred':'B'}.get(row['result']['status'])


def ratio(a,b):
    return a/b if b else None


def metrics(rows):
    labels=Counter(r['label'] for r in rows)
    directional=[r for r in rows if r['label'] in ('A','B')]
    answered=[r for r in directional if direction(r) is not None]
    correct=sum(direction(r)==r['label'] for r in answered)
    precision={};recall={};confusion={}
    for side in ('A','B'):
        tp=sum(r['label']==side and direction(r)==side for r in rows)
        fp=sum(r['label'] in ('A','B','no-demonstrated-preference') and r['label']!=side and direction(r)==side for r in rows)
        precision[side]=ratio(tp,tp+fp)
        recall[side]=ratio(tp,labels[side])
        confusion[side]=dict(true_positive=tp,false_positive=fp,missed_including_abstention=labels[side]-tp)
    none=[r for r in rows if r['label']=='no-demonstrated-preference']
    unknown=[r for r in rows if r['label']=='unknown']
    incomplete=sum(r['result']['status']=='incomplete' for r in rows)
    contradiction=sum(bool(r['result'].get('contradiction')) for r in rows)
    complete=sum(bool(r['result'].get('conditional_proof_complete')) for r in rows)
    return dict(examples=len(rows),independent_groups=len({r['dependence_group'] for r in rows}),
        label_counts=dict(labels),directional_examples=len(directional),directional_answers=len(answered),
        correct_directional_answers=correct,pairwise_accuracy=ratio(correct,len(answered)),
        accuracy_including_abstention=ratio(correct,len(directional)),directional_coverage=ratio(len(answered),len(directional)),
        directional_abstentions=len(directional)-len(answered),abstention_rate=ratio(len(directional)-len(answered),len(directional)),
        precision=precision,recall_including_abstention=recall,confusion=confusion,
        no_demonstrated_examples=len(none),unsupported_direction_on_ambiguous=sum(direction(r) is not None for r in none),
        correctly_supported_no_preference=sum(bool(r['result'].get('no_preference_supported')) for r in none),
        unknown_label_examples=len(unknown),directional_answers_without_resolved_reference=sum(direction(r) is not None for r in unknown),
        incomplete=incomplete,incomplete_rate=ratio(incomplete,len(rows)),contradictions=contradiction,
        contradiction_rate=ratio(contradiction,len(rows)),native_conditional_proofs=complete,
        conditional_proof_coverage=ratio(complete,len(rows)),
        complete_joint_strategic_proofs=sum(bool(r['result'].get('joint_proof_complete')) for r in rows),
        interpretation='Accuracy concerns answered, directionally labeled pairs; unknown teacher labels are excluded, and abstention-inclusive accuracy is separate. No-demonstrated preference is not a forced direction.')


def calibration(rows,bins=10):
    usable=[r for r in rows if r['label'] in ('A','B')]
    buckets=[[] for _ in range(bins)]
    squared=[]
    for row in usable:
        raw=row['result']['channels']['A']['raw_stv'];strength=raw['strength'];target=int(row['label']=='A')
        assert 0<=strength<=1
        buckets[min(bins-1,int(strength*bins))].append((strength,target,raw['confidence']))
        squared.append((strength-target)**2)
    reliability=[];weighted_error=0
    for index,bucket in enumerate(buckets):
        mean=statistics.mean(r[0] for r in bucket) if bucket else None
        empirical=statistics.mean(r[1] for r in bucket) if bucket else None
        if bucket:weighted_error+=len(bucket)*abs(mean-empirical)
        reliability.append(dict(lower=index/bins,upper=(index+1)/bins,n=len(bucket),
            mean_raw_strength=mean,empirical_A_frequency=empirical,
            mean_raw_confidence=statistics.mean(r[2] for r in bucket) if bucket else None))
    selective=[]
    for threshold in (0,.25,.5,.75,.9):
        selected=[r for r in usable if direction(r) and
            r['result']['channels'][direction(r)]['raw_stv']['confidence']>=threshold]
        correct=sum(direction(r)==r['label'] for r in selected)
        selective.append(dict(min_confidence=threshold,n=len(selected),coverage=ratio(len(selected),len(usable)),
            accuracy=ratio(correct,len(selected)),risk=ratio(len(selected)-correct,len(selected))))
    return dict(directional_examples=len(usable),brier_score=statistics.mean(squared) if squared else None,
        expected_calibration_error=ratio(weighted_error,len(usable)),reliability=reliability,selective_risk=selective,
        raw_confidence_is_probability=False,calibration_changes_inference=False,
        interpretation='Diagnostic comparison of raw A-channel strength with held-out directional labels. Channels are not normalized; confidence is shown only as an evidence/selection parameter. Unknown and no-demonstrated labels are excluded from this binary diagnostic.')


def bootstrap(rows,repetitions=1000,seed=131313):
    groups=defaultdict(list)
    for row in rows:groups[row['dependence_group']].append(row)
    if not groups:return dict(groups=0,repetitions=repetitions,intervals={})
    keys=sorted(groups);rng=random.Random(seed)
    values=defaultdict(list)
    for _ in range(repetitions):
        sampled=[row for _ in keys for row in groups[rng.choice(keys)]]
        result=metrics(sampled)
        for name in ('pairwise_accuracy','accuracy_including_abstention','directional_coverage','contradiction_rate'):
            if result[name] is not None:values[name].append(result[name])
    intervals={}
    for name,samples in values.items():
        samples.sort();n=len(samples)
        intervals[name]=dict(lower=samples[int(.025*(n-1))],upper=samples[int(.975*(n-1))],valid_replicates=n)
    return dict(groups=len(keys),repetitions=repetitions,seed=seed,intervals=intervals,
        method='Percentile 95% cluster bootstrap over connected ancestry components; all correlated rows travel together.',
        limitations='Small panels and selected tactical sources limit generalization; intervals do not capture teacher-label or source-selection uncertainty.')
