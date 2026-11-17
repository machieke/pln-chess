"""Exact finite illustrative models, isolated from chess/native inference.

These are named reference cases, not a general inference engine. Fractions have
no conversion to native truth values, checkpoints, predictions or caches.
"""
from fractions import Fraction as F


def joint_cases():
    laws = {'independent': {(0, 0): F(1, 4), (0, 1): F(1, 4), (1, 0): F(1, 4), (1, 1): F(1, 4)},
        'positive_association': {(0, 0): F(1, 2), (1, 1): F(1, 2)},
        'negative_association': {(0, 1): F(1, 2), (1, 0): F(1, 2)}}
    return {name: dict(marginal_a=sum(p*a for (a, b), p in law.items()),
        marginal_b=sum(p*b for (a, b), p in law.items()), joint=sum(p*a*b for (a, b), p in law.items()),
        assumption='Explicit finite joint law: '+name) for name, law in laws.items()}


def bounds(a, b):
    if not 0 <= a <= 1 or not 0 <= b <= 1:
        raise ValueError('Expected probability marginals')
    return max(F(0), a+b-1), min(a, b)


def parameter_reuse():
    theta = (F(1, 4), F(3, 4))
    mean = sum(theta)/2
    return dict(mean=mean, shared_parameter=sum(t*t for t in theta)/2,
        independently_redrawn=mean*mean, same_event=mean,
        assumption='Two Bernoulli trials conditionally independent given shared theta; redrawing and same-event cases are distinct models')


def observations():
    # Uniform prior on theta={1/4,3/4}; one observed Bernoulli success.
    theta = (F(1, 4), F(3, 4))
    once = tuple(t/sum(theta) for t in theta)
    twice = tuple(t*t/sum(x*x for x in theta) for t in theta)
    predictive_once = sum(w*t for w, t in zip(once, theta))
    shared_two_predictions = sum(w*t*t for w, t in zip(once, theta))
    # Coupled shared datum Y=1 iff two independent fair latent bits are equal.
    # Posterior is 00/11 with equal probability. A factorized likelihood for a
    # vector record consisting of two local successes instead preserves product.
    factorized = {(a, b): once[i]*once[j] for i, a in enumerate(theta) for j, b in enumerate(theta)}
    equality_weights = {(a, b): F(1, 4)*int(a == b) for a in (0, 1) for b in (0, 1)}
    normalizer = sum(equality_weights.values())
    coupled = {pair: weight/normalizer for pair, weight in equality_weights.items()}
    return dict(posterior_once=once, duplicate_likelihood_posterior=twice,
        predictive_once=predictive_once, duplicate_likelihood_prediction=sum(w*t for w, t in zip(twice, theta)),
        two_predictions_after_one_update=shared_two_predictions,
        same_observation_replayed_posterior=once,
        coupled_shared_datum_joint=sum(p*a*b for (a, b), p in coupled.items()),
        coupled_shared_datum_marginals=(sum(p*a for (a, b), p in coupled.items()), sum(p*b for (a, b), p in coupled.items())),
        factorized_vector_record_joint=sum(p*a*b for (a, b), p in factorized.items()),
        assumptions=['Once: one Bernoulli likelihood; duplicate likelihood is an intentionally different two-event model',
            'Shared coupled datum: uniform latent bits conditioned on equality',
            'Factorized vector datum: independent theta priors and product of two local-success likelihoods',
            'Sharing a dataset label alone imposes none of these joint laws'])


def controls():
    event_law = {0: F(2, 3), 1: F(1, 3)}
    mean = sum(event*p for event, p in event_law.items())
    diamond_joint = sum(p*int(bool(event) and bool(event)) for event, p in event_law.items())
    # Both circular implications are deterministic identity maps.
    cycle_return = sum(p*int(bool(bool(event))) for event, p in event_law.items())
    prior = (F(1, 2), F(1, 2)); likelihood = (F(0), F(1))
    weights = tuple(p*l for p, l in zip(prior, likelihood))
    posterior = tuple(w/sum(weights) for w in weights)
    return dict(
        diamond=dict(source_probability=mean, joint=diamond_joint, incorrect_independent_product=mean*mean,
            assumption='Both deterministic branches equal the very same source event'),
        cycle=dict(before=mean, after=cycle_return,
            assumption='Deterministic A -> B -> A introduces no new observation or likelihood'),
        unequal=dict(marginals=(F(1, 4), F(3, 4)), bounds=bounds(F(1, 4), F(3, 4)),
            factorized_joint=F(3, 16), assumption='Product only under explicit independent-event model'),
        false_hypothesis=dict(prior=prior, likelihood=likelihood, posterior=posterior,
            assumption='Deterministic hypothesis H0 predicts no success; observe success without noise; alternative predicts success'),
        missing_dependence=dict(bounds=bounds(F(1, 2), F(1, 2)), point_estimate=None,
            status='not identified under marginal-only assumptions'))


def run():
    return dict(scope='Illustrative finite probability models, not native PLN semantics or measured chess probabilities',
        native_stv_interpretation='Unspecified; no Beta or full posterior interpretation assumed',
        equal_marginals=joint_cases(), parameter_reuse=parameter_reuse(), observations=observations(), controls=controls())
