"""Host evaluation and diagnostic probabilities, separate from native TVs."""
from collections import defaultdict
import math
import random

from pln_chess.common import digest


def ratio(numerator,denominator):return numerator/denominator if denominator else None


def counts(rows):
    directional=[r for r in rows if r['label'] in ('A','B')]
    answered=[r for r in directional if r['prediction']['status'] in ('A-preferred','B-preferred')]
    correct=sum(r['prediction']['status']==r['label']+'-preferred' for r in answered)
    all_answers=sum(r['prediction']['status'] in ('A-preferred','B-preferred') for r in rows)
    nondirectional=[r for r in rows if r['label']=='no-demonstrated-preference']
    result=dict(N_all=len(rows),N_directional=len(directional),N_nondirectional=len(nondirectional),
        N_reference_unknown=sum(r['label']=='unknown' for r in rows),N_answered=len(answered),N_correct=correct,
        N_wrong=len(answered)-correct,N_model_answers_all=all_answers,N_model_abstentions_all=len(rows)-all_answers,
        N_directional_abstentions=len(directional)-len(answered),
        N_contradictions=sum(r['prediction'].get('contradiction',False) for r in rows),
        N_incomplete=sum(r['prediction']['status']=='incomplete' for r in rows),
        N_nondirectional_supported=sum(r['prediction'].get('no_preference_supported',False) and not r['prediction'].get('contradiction',False) for r in nondirectional),
        independent_ancestry_groups=len({r['dependence_group'] for r in rows}),
        answered_accuracy=ratio(correct,len(answered)),directional_coverage=ratio(len(answered),len(directional)),
        correct_answer_yield=ratio(correct,len(directional)),
        reference_resolution_rate=ratio(len(directional)+len(nondirectional),len(rows)),
        model_answer_rate_all=ratio(all_answers,len(rows)))
    assert result['N_all']==result['N_directional']+result['N_nondirectional']+result['N_reference_unknown']
    return result


def percentile(values,fraction):
    ordered=sorted(values)
    if not ordered:return None
    place=(len(ordered)-1)*fraction;left=int(place);right=min(left+1,len(ordered)-1)
    return ordered[left]+(place-left)*(ordered[right]-ordered[left])


def clustered_intervals(rows,*,repetitions=1000,seed=141414):
    grouped=defaultdict(list)
    for row in rows:grouped[row['dependence_group']].append(row)
    groups=sorted(grouped);randomizer=random.Random(seed)
    names=('answered_accuracy','directional_coverage','correct_answer_yield','reference_resolution_rate','model_answer_rate_all')
    samples={name:[] for name in names}
    for _ in range(repetitions if groups else 0):
        sample=[row for _ in groups for row in grouped[randomizer.choice(groups)]];measurement=counts(sample)
        for name in names:
            if measurement[name] is not None:samples[name].append(measurement[name])
    return dict(method='Percentile bootstrap resampling whole source-ancestry components with replacement',
        interval=.95,repetitions=repetitions,groups=len(groups),seed=seed,
        estimates={name:dict(low=percentile(values,.025),high=percentile(values,.975),defined_replicates=len(values)) for name,values in samples.items()},
        scope='Finite registered source groups; intervals do not establish universal transfer or eliminate source bias.')


EDGES=(0.,.2,.4,.6,.8,1.)


def bin_index(value):
    if not isinstance(value,(int,float)) or not 0<=value<=1:raise ValueError('Invalid diagnostic input')
    return min(4,int(value*5))


def raw_probability(row):return row['prediction']['channels']['A']['raw_stv']['strength']


def fit_calibration(rows):
    if any(r['split']!='calibration' for r in rows):raise ValueError('Calibration mappings require the reserved calibration split')
    bins=[dict(lower=EDGES[i],upper=EDGES[i+1],N=0,N_A=0) for i in range(5)]
    for row in rows:
        if row['label'] not in ('A','B'):continue
        target=bins[bin_index(raw_probability(row))];target['N']+=1;target['N_A']+=int(row['label']=='A')
    for target in bins:
        target['probability']=(target['N_A']+1)/(target['N']+2);target['empty']=target['N']==0
    result=dict(schema='c14-diagnostic-calibration-v1',event='Reference direction is displayed candidate A, conditional on a resolved A/B reference',
        bins=bins,fit_ids=sorted(r['id'] for r in rows if r['label'] in ('A','B')),
        fit_ancestry_groups=sorted({r['dependence_group'] for r in rows if r['label'] in ('A','B')}),
        input='Unnormalized native A-channel strength; confidence and B channel remain separate',
        method='Fixed equal-width bins with Laplace smoothing; empty bins map to 0.5',
        raw_native_values_modified=False,production_utility=False)
    result['hash']=digest(result);return result


def calibration_metrics(rows,mapping,*,repetitions=1000,seed=141414):
    if mapping['hash']!=digest({k:v for k,v in mapping.items() if k!='hash'}):raise ValueError('Calibration mapping integrity mismatch')
    rows=[r for r in rows if r['label'] in ('A','B')]
    def probabilities(row):
        raw=raw_probability(row);return raw,mapping['bins'][bin_index(raw)]['probability']
    def score(selected):
        result={}
        for arm,index in (('raw_A_strength',0),('calibrated',1)):
            squared=[];loss=[]
            for row in selected:
                p=probabilities(row)[index];y=int(row['label']=='A');clipped=min(1-1e-6,max(1e-6,p))
                squared.append((p-y)**2);loss.append(-y*math.log(clipped)-(1-y)*math.log1p(-clipped))
            result[arm]=dict(N=len(selected),brier=ratio(sum(squared),len(selected)),log_loss=ratio(sum(loss),len(selected)))
        return result
    result=score(rows);reliability=[]
    for arm,index in (('raw_A_strength',0),('calibrated',1)):
        for bin_ in range(5):
            selected=[r for r in rows if bin_index(probabilities(r)[index])==bin_]
            reliability.append(dict(arm=arm,bin=bin_,N=len(selected),
                mean_probability=ratio(sum(probabilities(r)[index] for r in selected),len(selected)),
                observed_A_fraction=ratio(sum(r['label']=='A' for r in selected),len(selected))))
    grouped=defaultdict(list)
    for row in rows:grouped[row['dependence_group']].append(row)
    groups=sorted(grouped);randomizer=random.Random(seed)
    boot={arm:{name:[] for name in ('brier','log_loss')} for arm in result}
    for _ in range(repetitions if groups else 0):
        sample=[row for _ in groups for row in grouped[randomizer.choice(groups)]];values=score(sample)
        for arm in boot:
            for name in boot[arm]:boot[arm][name].append(values[arm][name])
    intervals={arm:{name:dict(low=percentile(values,.025),high=percentile(values,.975)) for name,values in metrics.items()} for arm,metrics in boot.items()}
    selective=[]
    for threshold in (.5,.6,.7,.8,.9):
        selected=[r for r in rows if r['prediction']['status'] in ('A-preferred','B-preferred') and
            max(probabilities(r)[1],1-probabilities(r)[1])>=threshold]
        wrong=sum(r['prediction']['status']!=r['label']+'-preferred' for r in selected)
        selective.append(dict(diagnostic_certainty_threshold=threshold,N=len(selected),N_wrong=wrong,
            risk=ratio(wrong,len(selected)),coverage=ratio(len(selected),len(rows))))
    return dict(scores=result,reliability=reliability,clustered_95_intervals=intervals,bootstrap_groups=len(groups),
        bootstrap_repetitions=repetitions,selective_risk=selective,mapping_hash=mapping['hash'],
        log_loss_probability_clipping=[1e-6,1-1e-6],raw_channels_renormalized=False,
        scope='Host diagnostic scoring on resolved A/B references; unknown and nondirectional references excluded.')
