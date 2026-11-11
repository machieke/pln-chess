"""Typed relative count contrasts; host observations never synthesize a TV."""
import copy
from pln_chess.common import digest, canonical
from pln_chess.cycle12.ontology import CONCEPTS

GRAMMAR = 'relative-preference-contrasts-v13'
FIELDS = ('attack', 'defense', 'mobility', 'king-exposure')
CHANNELS = ('first', 'second', 'no-demonstrated-preference')
ABSTRACTIONS = ('relational','attack-only','defense-only','mobility-only','exposure-only',
                'without-concepts','weaker-relative','full')
COUNTS = ('supported','contradicted','unknown','incomplete','queried')


def sign(value):
    return int(value > 0) - int(value < 0)


def seal(packet):
    packet = copy.deepcopy(packet)
    packet.pop('id', None)
    packet['id'] = 'relative-comparison:' + digest(packet)
    return packet


def validate_packet(packet):
    allowed = {'id','schema','profiles','horizon','complete','gaps','source','provenance','candidate_descriptors'}
    if not isinstance(packet,dict) or set(packet) != allowed or packet['schema'] != GRAMMAR:
        raise ValueError('Invalid preference packet fields; labels and reference scores are not inference inputs')
    if seal(packet)['id'] != packet['id']:
        raise ValueError('Preference observation integrity mismatch')
    if type(packet['horizon']) is not int or packet['horizon'] not in (1,2,3):
        raise ValueError('Preference horizon must be one, two or three')
    if type(packet['complete']) is not bool or not isinstance(packet['gaps'],list):
        raise ValueError('Missing explicit comparison completeness')
    if not isinstance(packet['source'],str) or not packet['source'] or len(packet['source']) > 512:
        raise ValueError('Invalid comparison source')
    if set(packet['profiles']) != {'before','A','B'} or set(packet['candidate_descriptors']) != {'A','B'}:
        raise ValueError('Supply root and both candidate profiles')
    for profile in packet['profiles'].values():
        if set(profile) != {'fields','concepts','concept_scope'} or profile['concept_scope'] != 'bounded-role-candidates':
            raise ValueError('Invalid scoped relational profile')
        for name, families in (('fields',FIELDS),('concepts',tuple(CONCEPTS))):
            if set(profile[name]) != set(families):
                raise ValueError('Incomplete typed family profile')
            for counts in profile[name].values():
                if set(counts) != set(COUNTS) or any(type(v) is not int or v < 0 or v > 1000000 for v in counts.values()):
                    raise ValueError('Invalid observation counts')
                if sum(counts[k] for k in COUNTS[:-1]) != counts['queried']:
                    raise ValueError('Observation counts do not partition their query domain')
    return True


def families(abstraction):
    if abstraction not in ABSTRACTIONS:
        raise ValueError('Unknown preference abstraction')
    if abstraction.endswith('-only'):
        return ({'exposure-only':'king-exposure'}.get(abstraction,abstraction[:-5]),)
    if abstraction == 'weaker-relative':
        return ('attack','mobility')
    return FIELDS


def validate_descriptor(descriptor):
    if not isinstance(descriptor,dict) or set(descriptor) != {'grammar','abstraction','horizon','features','coverage','concept_scope'}:
        raise ValueError('Invalid relative preference descriptor')
    abstraction = descriptor['abstraction']
    selected = list(families(abstraction))
    if abstraction == 'full':
        selected += ['concept:' + name for name in CONCEPTS]
    if descriptor['grammar'] != GRAMMAR or type(descriptor['horizon']) is not int or descriptor['horizon'] not in (1,2,3):
        raise ValueError('Invalid preference grammar or horizon')
    if set(descriptor['features']) != set(selected) or set(descriptor['coverage']) != set(selected):
        raise ValueError('Invalid relative feature vocabulary')
    if any(type(v) is not int or v not in (-1,0,1) for v in descriptor['features'].values()):
        raise ValueError('Only categorical relative contrasts are learned')
    if any(v not in ('observed','partial') for v in descriptor['coverage'].values()):
        raise ValueError('Invalid unknown-state coverage category')
    if descriptor['concept_scope'] != ('bounded-role-candidates' if abstraction == 'full' else 'not-used'):
        raise ValueError('Invalid concept scope')
    vector = tuple(descriptor['features'][name] for name in sorted(selected))
    if vector < tuple(-v for v in vector):
        raise ValueError('Descriptor is not in canonical pair order')
    return True


def key(descriptor):
    validate_descriptor(descriptor)
    return 'preference-rule:' + digest(descriptor)


def project(packet, abstraction='relational'):
    validate_packet(packet)
    features, coverage = {}, {}
    before, a, b = (packet['profiles'][side] for side in ('before','A','B'))
    selected = [('fields',name,name) for name in families(abstraction)]
    if abstraction == 'full':
        selected += [('concepts',name,'concept:'+name) for name in CONCEPTS]
    for group, family, name in selected:
        base, first, second = (profile[group][family] for profile in (before,a,b))
        if abstraction == 'weaker-relative':
            features[name] = sign(int(first['supported'] > 0)-int(second['supported'] > 0))
        else:
            features[name] = sign((first['supported']-base['supported'])-(second['supported']-base['supported']))
        coverage[name] = 'partial' if any(c['unknown'] or c['incomplete'] for c in (base,first,second)) else 'observed'
    vector = tuple(features[name] for name in sorted(features))
    direction = -1 if vector < tuple(-v for v in vector) else 1
    descriptor = dict(grammar=GRAMMAR, abstraction=abstraction, horizon=packet['horizon'],
        features={name:direction*value for name,value in features.items()}, coverage=coverage,
        concept_scope='bounded-role-candidates' if abstraction == 'full' else 'not-used')
    return dict(id='preference-observation:'+digest([packet['id'],descriptor]), descriptor=descriptor,
        rule_id=key(descriptor), canonical_order=['A','B'] if direction == 1 else ['B','A'],
        distinguishable=any(vector), complete=packet['complete'], source_packet_id=packet['id'],
        scope='Host observation of separately supported records; no native conjunction or strategic utility.')


def reverse_packet(packet):
    validate_packet(packet)
    result = copy.deepcopy(packet)
    for name in ('profiles','candidate_descriptors'):
        result[name]['A'],result[name]['B'] = result[name]['B'],result[name]['A']
    return seal(result)
