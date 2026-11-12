"""Bounded relative role contrasts; identifiers bind evidence, never features."""
import copy
from collections import defaultdict

from pln_chess.common import canonical,digest
from pln_chess.cycle13 import ontology as previous

GRAMMAR='relative-role-preference-v14'
ABSTRACTIONS=('c13-relational','role-change-v1','shared-relation-v1')
CHANNELS=previous.CHANNELS
ROLES=('mover-attack','mover-defense','mover-mobility','king-exposure',
    'shared-attack-target','shared-defense-ward','supported-mover')


def counts(rows,*,available=True):
    return {**{status:sum(row['classification']==status for row in rows)
        for status in ('supported','contradicted','unknown','incomplete')},'queried':len(rows),'available':available}


def role_profile(state,mover):
    if state is None:return {name:counts([],available=False) for name in ROLES}
    field=state['field'];rows=field['relations'];present={p['id'] for p in field['pieces']}
    available=mover in present and not field['unknown_squares']
    result={}
    for name,family in (('mover-attack','attack'),('mover-defense','defense'),('mover-mobility','mobility'),('king-exposure','king-exposure')):
        selected=[r for r in rows if r['family']==family and (family=='king-exposure' or r['source_entity']==mover)]
        result[name]=counts(selected,available=available)
    # Set membership uses entity identity to bind a role within one observation.
    # Only bounded count contrasts and coverage categories enter learned keys.
    for name,family in (('shared-attack-target','attack'),('shared-defense-ward','defense')):
        grouped=defaultdict(list)
        for row in rows:
            if row['family']==family and row['target_entity']:grouped[row['target_entity']].append(row)
        selected=[]
        for target,relations in grouped.items():
            local=[r for r in relations if r['source_entity']==mover]
            if not local:continue
            supported={r['source_entity'] for r in relations if r['classification']=='supported'}
            unknown=any(r['classification'] in ('unknown','incomplete') for r in relations)
            status='supported' if mover in supported and len(supported)>=2 else 'unknown' if unknown else 'contradicted'
            selected.append(dict(classification=status))
        result[name]=counts(selected,available=available)
    result['supported-mover']=counts([r for r in rows if r['family']=='defense' and r['target_entity']==mover],available=available)
    return result


def seal(packet):
    packet=copy.deepcopy(packet);packet.pop('id',None);packet['id']='role-comparison:'+digest(packet);return packet


def enrich(base,states,movers):
    previous.validate_packet(base)
    return seal(dict(schema=GRAMMAR,base=base,role_profiles={
        'beforeA':role_profile(states['before'],movers['A']),
        'beforeB':role_profile(states['before'],movers['B']),
        'A':role_profile(states['A'],movers['A']),'B':role_profile(states['B'],movers['B'])},
        observation_kind='separate-native-endpoint-projections',
        scope='Host role binding and counts; shared relations do not assert a native conjunction.'))


def validate_packet(packet):
    if not isinstance(packet,dict) or set(packet)!={'id','schema','base','role_profiles','observation_kind','scope'} or packet['schema']!=GRAMMAR:
        raise ValueError('Invalid role packet; scores and labels are not production inputs')
    if seal(packet)['id']!=packet['id']:raise ValueError('Role packet integrity mismatch')
    previous.validate_packet(packet['base'])
    if set(packet['role_profiles'])!={'beforeA','beforeB','A','B'}:raise ValueError('Missing candidate-role profiles')
    for profile in packet['role_profiles'].values():
        if set(profile)!=set(ROLES):raise ValueError('Unregistered role features')
        for row in profile.values():
            if set(row)!=set(previous.COUNTS)|{'available'} or type(row['available']) is not bool:
                raise ValueError('Missing explicit role availability')
            if any(type(row[k]) is not int or not 0<=row[k]<=1000000 for k in previous.COUNTS):raise ValueError('Invalid role counts')
            if sum(row[k] for k in previous.COUNTS[:-1])!=row['queried']:raise ValueError('Unpartitioned role query domain')
    return True


def key(descriptor):
    if descriptor.get('grammar')==previous.GRAMMAR:return previous.key(descriptor)
    required={'grammar','abstraction','horizon','features','coverage','concept_scope'}
    if set(descriptor)!=required or descriptor['grammar']!=GRAMMAR or descriptor['abstraction'] not in ABSTRACTIONS[1:]:
        raise ValueError('Unregistered relative role descriptor')
    if type(descriptor['horizon']) is not int or descriptor['horizon'] not in (1,2,3):raise ValueError('Invalid horizon')
    names=set(previous.FIELDS)|{'role:'+r for r in (ROLES[:4] if descriptor['abstraction']=='role-change-v1' else ROLES)}
    if descriptor['concept_scope']=='bounded-role-candidates':names|={'concept:'+c for c in previous.CONCEPTS}
    elif descriptor['concept_scope']!='not-used':raise ValueError('Invalid concept scope')
    if set(descriptor['features'])!=names or set(descriptor['coverage'])!=names:raise ValueError('Unregistered feature vocabulary')
    if any(type(v) is not int or v not in (-1,0,1) for v in descriptor['features'].values()):raise ValueError('Only categorical contrasts are permitted')
    if any(v not in ('observed','partial','unqueried') for v in descriptor['coverage'].values()):raise ValueError('Invalid missing-context category')
    vector=tuple(descriptor['features'][n] for n in sorted(names))
    if vector<tuple(-v for v in vector):raise ValueError('Noncanonical pair orientation')
    return 'preference-rule:'+digest(descriptor)


def project(packet,abstraction='c13-relational',*,concepts=False):
    if abstraction not in ABSTRACTIONS:raise ValueError('Unregistered bounded descriptor')
    validate_packet(packet);base=packet['base']
    original=previous.project(base,'full' if concepts else 'relational')
    if abstraction=='c13-relational':return original
    direction=1 if original['canonical_order'][0]=='A' else -1
    features={k:v*direction for k,v in original['descriptor']['features'].items()}
    coverage=dict(original['descriptor']['coverage'])
    profiles=packet['role_profiles']
    for name in (ROLES[:4] if abstraction=='role-change-v1' else ROLES):
        before_a,before_b,a,b=[profiles[s][name] for s in ('beforeA','beforeB','A','B')]
        rows=(before_a,before_b,a,b)
        covered='unqueried' if any(not r['available'] or not r['queried'] for r in rows) else 'partial' if any(r['unknown'] or r['incomplete'] for r in rows) else 'observed'
        coverage['role:'+name]=covered
        features['role:'+name]=(previous.sign((a['supported']-before_a['supported'])-(b['supported']-before_b['supported']))
            if covered=='observed' else 0)
    vector=tuple(features[n] for n in sorted(features));direction=-1 if vector<tuple(-v for v in vector) else 1
    descriptor=dict(grammar=GRAMMAR,abstraction=abstraction,horizon=base['horizon'],
        features={n:v*direction for n,v in features.items()},coverage=coverage,
        concept_scope='bounded-role-candidates' if concepts else 'not-used')
    return dict(id='preference-observation:'+digest([packet['id'],descriptor]),descriptor=descriptor,
        rule_id=key(descriptor),canonical_order=['A','B'] if direction==1 else ['B','A'],
        distinguishable=any(vector),complete=base['complete'],source_packet_id=packet['id'],
        scope='Host role-bound endpoint contrasts; no native conjunction or strategic utility.')


def reverse_packet(packet):
    validate_packet(packet);result=copy.deepcopy(packet);result['base']=previous.reverse_packet(result['base'])
    for first,second in (('A','B'),('beforeA','beforeB')):
        result['role_profiles'][first],result['role_profiles'][second]=result['role_profiles'][second],result['role_profiles'][first]
    return seal(result)


def omit_context(packet):
    """A distinct missing-observation condition, never a zero-mobility claim."""
    validate_packet(packet);result=copy.deepcopy(packet)
    for side in ('A','B'):
        for group in ('fields','concepts'):
            for row in result['base']['profiles'][side][group].values():
                row.update(supported=0,contradicted=0,unknown=row['queried'],incomplete=0)
        for row in result['role_profiles'][side].values():
            row.update(supported=0,contradicted=0,unknown=row['queried'],incomplete=0,available=False)
    result['base']['gaps'].append('Endpoint observations deliberately omitted; queried contents are unknown.')
    result['base']=previous.seal(result['base']);return seal(result)
