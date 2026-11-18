"""Denominator-explicit summaries and descriptive root-aware uncertainty."""
from collections import Counter,defaultdict
import math
import random


def ratio(n,d):return n/d if d else None


def wilson(n,d):
    if not d:return None
    z=1.959963984540054;p=n/d;den=1+z*z/d
    center=(p+z*z/(2*d))/den;half=z*math.sqrt(p*(1-p)/d+z*z/(4*d*d))/den
    return [max(0,center-half),min(1,center+half)]


def summarize(rows):
    groups=defaultdict(list)
    for row in rows:
        for target in ('Clear','Attack'):
            groups[(row['population'],row['split'],row['arm'],target)].append((row,target))
    output=[]
    for key,items in sorted(groups.items()):
        counts=Counter();tvs=[];clusters=defaultdict(list)
        for row,target in items:
            stage=row['native']['stages'][target];truth=row['measurement'][target]['value'];status=stage['classification']
            counts[status]+=1;counts['reference-unresolved' if truth is None else 'reference-positive' if truth else 'reference-negative']+=1
            positive=status=='supported-positive';negative=status=='supported-negative'
            counts['tp']+=positive and truth is True;counts['fp']+=positive and truth is False
            counts['tn']+=negative and truth is False;counts['fn']+=negative and truth is True
            counts['missed-reference-positive']+=truth is True and not positive
            counts['measurement-disagreement']+=row['measurement']['agreement']=='disagree'
            for channel in ('answer','contrary'):
                if stage[channel]:tvs.append(dict(channel=channel,strength=stage[channel]['strength'],confidence=stage[channel]['confidence']))
            clusters[row['root']].append(int(positive or negative))
        n=len(items);supported=counts['supported-positive']+counts['supported-negative']
        precision_den=counts['tp']+counts['fp'];recall_den=counts['reference-positive']
        natural=key[0].startswith('natural')
        uncertainty=dict(method='Wilson 95%, conditional exchangeable-game approximation' if natural else 'Root-cluster bootstrap, 1000 resamples, seed 19',
            caveat='Games may share engines/openings/publisher; intervals do not identify calibration or population independence')
        if natural:uncertainty.update(precision=wilson(counts['tp'],precision_den),recall=wilson(counts['tp'],recall_den),coverage=wilson(supported,n))
        else:
            rng=random.Random(19);keys=list(clusters);samples=[]
            for _ in range(1000):
                sample=[v for k in rng.choices(keys,k=len(keys)) for v in clusters[k]]
                samples.append(sum(sample)/len(sample))
            samples.sort();uncertainty['coverage']=[samples[24],samples[974]]
        for status in ('supported-positive','supported-negative','unknown','conflicting','incomplete','reference-positive','reference-negative','reference-unresolved','tp','fp','tn','fn','missed-reference-positive','measurement-disagreement'):counts.setdefault(status,0)
        output.append(dict(population=key[0],split=key[1],arm=key[2],target=key[3],roots=len(clusters),
            source_games=len({r['game'] for r,t in items}),queries=n,dependent_variants=0 if natural else n,
            counts=dict(counts),precision=ratio(counts['tp'],precision_den),precision_denominator=precision_den,
            recall=ratio(counts['tp'],recall_den),recall_denominator=recall_den,coverage=ratio(supported,n),
            coverage_denominator=n,uncertainty=uncertainty,truth_values=tvs,
            evidence=[dict(root=r['root'],variant=r['variant'],native=r['native']['stages'][t]['native']) for r,t in items]))
    return output
