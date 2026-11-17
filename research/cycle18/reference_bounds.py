"""Sharp finite posterior-marginal coupling bounds, not unspecified-prior Bayes."""
from fractions import Fraction as F
from .contracts import identity
from .reference_joint import result, SCHEMA, encode


def coupling(left,right,reverse=False):
    a=[[F(v['value']),F(v['probability'])] for v in left]
    b=[[F(v['value']),F(v['probability'])] for v in right]
    a.sort();b.sort(reverse=reverse)
    if any(w<0 or not 0<=v<=1 for v,w in a+b) or sum(w for v,w in a)!=1 or sum(w for v,w in b)!=1:
        raise ValueError('Expected normalized finite probability marginals')
    if len({v for v,w in a})!=len(a) or len({v for v,w in b})!=len(b):
        raise ValueError('Duplicate marginal support')
    i=j=0;plan=[]
    while i<len(a) and j<len(b):
        w=min(a[i][1],b[j][1])
        if w:
            plan.append(dict(theta_clear=a[i][0],theta_attack=b[j][0],probability=w))
        a[i][1]-=w;b[j][1]-=w
        if a[i][1]==0:i+=1
        if b[j][1]==0:j+=1
    return plan,sum((p['theta_clear']*p['theta_attack']*p['probability'] for p in plan),F(0))


def posterior_bounds(fitted):
    d=fitted.json()
    if d['status']!='point_under_declared_model':
        return result(dict(schema=SCHEMA,model_family='M-B',status='not_identified',reason='No supplied posterior marginals',predictive_probability=None))
    fixed={k:v['distribution'] for k,v in d['parameter_uncertainty'].items()}
    low,lo=coupling(fixed['theta_clear'],fixed['theta_attack'],True)
    high,hi=coupling(fixed['theta_clear'],fixed['theta_attack'])
    return result(dict(schema=SCHEMA,model_family='M-B',status='bounded_under_declared_constraints',
        event_ids=d['event_ids'],source_group_ids=d['source_group_ids'],source_model=d['model'],
        source_posterior_identity=d['posterior_identity'],fixed_information=fixed,
        feasible_set_identity=identity(fixed),constraints='Exactly supplied posterior marginals; every nonnegative coupling with these row/column sums',
        predictive_probability=None,bounds=[lo,hi],lower_witness=low,upper_witness=high,
        sharpness='Finite rearrangement: moving mass from crossed to aligned pairs changes E[a*b] by mass*(a2-a1)*(b2-b1)>=0; quantile/antiquantile couplings attain endpoints',
        limits='Does not condition an unspecified prior coupling. Does not identify the actual empirical pipeline population.',
        query=d['query'],native_confidence=None))


def unidentified():
    return result(dict(schema=SCHEMA,model_family='M-B',status='not_identified',predictive_probability=None,
        fixed_information='Actual all-positive, antecedent-selected deterministic labels; no independently measured error/noise process or population sampling model',
        reason='No posterior parameter marginals or joint prior/likelihood identified by recorded labels or native TVs',
        bounds=None,confidence_mapping='unresolved'))
