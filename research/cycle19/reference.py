"""A typed absence of a current-position probability model; no native bridge."""
def meaning(environment):
    return dict(schema='cycle19-current-position-meaning-v1',status='not_identified',
        event=dict(relation='Attack',attacker=environment['attacker'],target=environment['target'],state=environment['observed']['id']),
        conditioning='Available relative observations, supplied templates and admitted training evidence',
        probability=None,bounds=None,
        missing=['Observation error/missingness distribution','Representation and applicability error model',
            'Population for reusable-schema uncertainty','Relationship between bounded search and semantic truth',
            'Justified mapping from such uncertainty to native strength/confidence'],
        domain_truth='Offline audit of a fully specified reference state; distinct from native support',
        future_trial_probability_reused=False,native_confidence_conversion=None)
