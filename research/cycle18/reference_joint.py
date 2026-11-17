"""Exact, bounded two-parameter reference hypotheses. Never native truth values."""
from dataclasses import asdict, dataclass
from fractions import Fraction as F
from itertools import product
from .contracts import Kind, ParameterGeneration, canonical, identity
from .source_mapping import RULES

SCHEMA = 'reference-semantics-v18'
GRIDS = {'primary':(F(1,4),F(1,2),F(3,4)), 'two':(F(1,4),F(3,4)),
         'five':tuple(F(i,10) for i in (1,3,5,7,9))}
MODELS = ('M-F', 'M-J-copy', 'M-J-upper', 'M-J-lower')
QUERY = ('Two distinct future antecedent-qualified episode/channel trials with conditionally '
         'independent outcomes given one shared parameter pair; q(a,b)=a*b. '
         'This future-trial assumption is separate from within-training-vector dependence.')


@dataclass(frozen=True)
class Limits:
    states: int = 25
    groups: int = 100
    likelihood_evaluations: int = 2500
    rational_bits: int = 16384


@dataclass(frozen=True)
class ReferenceResult:
    """Immutable serialized payload; returned dictionaries cannot mutate a generation."""
    content: str

    def json(self):
        import json
        return json.loads(self.content)

    @property
    def scientific_identity(self):
        return identity(self.json())


def encode(value):
    if isinstance(value,F):
        return str(value)
    if isinstance(value,dict):
        return {k:encode(v) for k,v in value.items()}
    if isinstance(value,(tuple,list)):
        return [encode(v) for v in value]
    return value


def result(value):
    return ReferenceResult(canonical(encode(value)))


def table(a,b,model):
    """Complete joint Bernoulli table; every model has the stated marginals."""
    if model == 'M-F':
        both = a*b
    elif model in ('M-J-copy','M-J-upper'):
        if model == 'M-J-copy' and a != b:
            raise ValueError('Copy model requires equal parameter support')
        both = min(a,b)
    elif model == 'M-J-lower':
        both = max(F(0),a+b-1)
    else:
        raise ValueError('Unregistered model')
    return {(1,1):both,(1,0):a-both,(0,1):b-both,(0,0):1-a-b+both}


def likelihood(a,b,labels,model):
    if set(labels) == set(RULES):
        return table(a,b,model)[tuple(int(labels[r]) for r in RULES)]
    if len(labels)==1:
        rule,y = next(iter(labels.items())); p=a if rule==RULES[0] else b
        return p if y else 1-p
    raise ValueError('Expected one or two observed channels')


def groups_for(registry, selection):
    """One vector event per registered game. Aliases cannot add factors."""
    groups = {}
    for event_id, components in sorted(selection.items()):
        event = registry.get(event_id)
        if event not in registry.active():
            raise ValueError('Superseded evidence cannot update active generation')
        if event.observation_kind not in (Kind.EVALUATION,Kind.SUPERSEDED) or event.admission_status != 'admitted':
            raise ValueError('Only admitted external evaluation vectors are update inputs')
        payload=event.payload
        if payload.get('origin') not in ('mapped-external-evaluation','quarantined-external-measurement'):
            raise ValueError('Inference/prediction self-training is prohibited')
        components=tuple(sorted(set(components)))
        if not components or not set(components)<=set(RULES):
            raise ValueError('Unknown or empty component selection')
        labels={r:payload['labels'][r] for r in components}
        if not all(type(v) is bool for v in labels.values()):
            raise ValueError('Unknown values are not negative observations')
        if len(event.ancestry_groups)!=1:
            raise ValueError('Multi-source dependence needs an unimplemented likelihood contract')
        group=event.ancestry_groups[0]
        if group in groups:
            raise ValueError('Multiple measurements in one group require a joint observation contract')
        groups[group]=dict(event_id=event_id,components=components,labels=labels,
            payload_hash=event.payload_hash,source_episode_id=event.source_episode_id,
            label_relationship=payload.get('label_relationship'))
    return groups


def fit(registry, selection, model='M-J-copy', grid='primary', *, limits=Limits(), prior_generation=None):
    if any(v<0 for v in asdict(limits).values()):
        raise ValueError('Resource limits must be nonnegative')
    if model not in MODELS or grid not in GRIDS:
        raise ValueError('Model/grid not preregistered')
    support=GRIDS[grid]
    states=[(a,b) for a,b in product(support,repeat=2) if model!='M-J-copy' or a==b]
    groups=groups_for(registry,selection)
    assumptions=dict(model=model,grid=grid,parameter_support=support,
        prior='Uniform diagonal, equal parameters' if model=='M-J-copy' else 'Uniform product prior',
        observation_model='Copy one Bernoulli outcome into both annotations' if model=='M-J-copy'
            else 'Joint Bernoulli vector; P(11)='+{'M-F':'a*b','M-J-upper':'min(a,b)','M-J-lower':'max(0,a+b-1)'}[model],
        across_groups='Conditionally independent given parameters; supplied and unverified for TCEC games',
        observation_identity='A vector enters once; selected components share its one group likelihood',
        empirical_status='Hypothetical stochastic pipeline, not calibrated from selected deterministic positives',
        faithful_to_copy_operation=model=='M-J-copy',query=QUERY,
        selection='Conditional on natural EE antecedent qualification; no blocked paths counted as failures')
    base=dict(schema=SCHEMA,model_family='M-F' if model=='M-F' else 'M-J',model=model,
        assumptions=assumptions,assumptions_id=identity(encode(assumptions)),event_ids=sorted(selection),
        source_group_ids=sorted(groups),event_to_likelihood=groups,query=QUERY,
        native_strength=None,native_confidence=None,empirical_evaluation_uncertainty=None,
        confidence_mapping='unresolved; no conversion to native confidence',
        resources=dict(states=len(states),source_groups=len(groups),likelihood_evaluations=0,max_rational_bits=0),
        limits=asdict(limits))
    if len(states)>limits.states or len(groups)>limits.groups:
        return result(dict(base,status='resource_incomplete',reason='state/group limit',predictive_probability=None))
    weights=[]; traces=[]; evaluations=0; bits=0
    for a,b in states:
        weight=F(1,len(states)); prior=weight; factors=[]
        for group,datum in groups.items():
            evaluations+=1
            if evaluations>limits.likelihood_evaluations:
                return result(dict(base,status='resource_incomplete',reason='likelihood evaluation limit',predictive_probability=None,
                    resources=dict(states=len(states),source_groups=len(groups),likelihood_evaluations=evaluations-1,max_rational_bits=bits)))
            factor=likelihood(a,b,datum['labels'],model)
            weight*=factor
            bits=max(bits,weight.numerator.bit_length(),weight.denominator.bit_length())
            if bits>limits.rational_bits:
                return result(dict(base,status='resource_incomplete',reason='rational arithmetic limit',predictive_probability=None,
                    resources=dict(states=len(states),source_groups=len(groups),likelihood_evaluations=evaluations,max_rational_bits=bits)))
            factors.append(dict(source_group=group,likelihood=factor))
        weights.append(weight)
        traces.append(dict(theta_clear=a,theta_attack=b,prior=prior,group_likelihoods=factors,unnormalized=weight,
            within_source_table={str(k):v for k,v in table(a,b,model).items()}))
    normalizer=sum(weights,F(0))
    base['resources'].update(likelihood_evaluations=evaluations,max_rational_bits=bits)
    base.update(prior_and_likelihoods=traces,normalizer=normalizer)
    if normalizer==0:
        return result(dict(base,status='inconsistent_evidence',predictive_probability=None,
            reason='Zero evidence probability under the declared model; no epsilon or silent noise repair'))
    posterior=[dict(theta_clear=a,theta_attack=b,probability=w/normalizer) for (a,b),w in zip(states,weights)]
    bits=max(bits,*(max(p['probability'].numerator.bit_length(),p['probability'].denominator.bit_length()) for p in posterior))
    if bits>limits.rational_bits:
        return result(dict(base,status='resource_incomplete',reason='posterior rational limit',predictive_probability=None))
    predictive=sum((p['probability']*p['theta_clear']*p['theta_attack'] for p in posterior),F(0))
    marginals={}
    for name in ('theta_clear','theta_attack'):
        law={v:sum((p['probability'] for p in posterior if p[name]==v),F(0)) for v in support}
        mean=sum((v*w for v,w in law.items()),F(0))
        marginals[name]=dict(distribution=[dict(value=v,probability=w) for v,w in law.items()],mean=mean,
            variance=sum((w*(v-mean)**2 for v,w in law.items()),F(0)))
    generation=ParameterGeneration.create(namespace='reference-only',schema_id='pipeline-label-pair-v18',
        events=selection,excluded=[],groups=groups,learner='cycle18-exact-enumeration-v1',
        assumptions=base['assumptions_id'],uncertainty=canonical(encode(posterior)),prior=prior_generation)
    def rational_growth(value):
        if isinstance(value,F):return max(value.numerator.bit_length(),value.denominator.bit_length())
        if isinstance(value,dict):return max((rational_growth(v) for v in value.values()),default=0)
        if isinstance(value,(list,tuple)):return max((rational_growth(v) for v in value),default=0)
        return 0
    bits=max(bits,rational_growth([normalizer,posterior,predictive,marginals]))
    base['resources']['max_rational_bits']=bits
    if bits>limits.rational_bits:
        return result(dict(base,status='resource_incomplete',reason='predictive/moment rational limit',predictive_probability=None))
    return result(dict(base,status='point_under_declared_model',predictive_probability=predictive,
        posterior=posterior,posterior_identity=identity(encode(posterior)),parameter_uncertainty=marginals,
        parameter_generation=asdict(generation),
        repeated_same_event_probability=marginals['theta_clear']['mean'] if model=='M-J-copy' else None))
