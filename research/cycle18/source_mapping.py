"""Validate every Cycle 17 row and revision against immutable original artifacts.

This module has no reference-probability or native inference imports. State
reconstruction verifies the ledger's identities without asking an oracle.
"""
import copy
import json
from collections import Counter
from dataclasses import asdict
from pathlib import Path
from .contracts import Kind, Registry, observation, identity, sha, ParameterGeneration

ARMS = ('S-AA', 'S-BB', 'D-AB', 'D-BA', 'overlap-1', 'overlap-6')
RULES = ('clear-two', 'rook-attack')
EVIDENCE = 'artifacts/cycle17/learning/evidence.json'
CORPUS = 'artifacts/cycle17/corpus-registration.json'


def load(root, name):
    return json.loads((Path(root)/name).read_text())


def cells(root):
    p = {p['id']: p for p in root['state']['pieces']}
    a, b = p[root['attacker']]['cell'], p[root['target']]['cell']
    dx, dy = (b[0]-a[0])//3, (b[1]-a[1])//3
    assert abs(dx)+abs(dy) == 1
    return [(a[0]+i*dx, a[1]+i*dy) for i in (1,2)]


def state_for(root, occupancy):
    if occupancy == 'EE':
        return root['state']
    state = copy.deepcopy(root['state']); path = cells(root)
    state['pieces'] = [p for p in state['pieces'] if tuple(p['cell']) not in path]
    state['unknown'] = []
    state['id'] = 'variant_'+identity([root['id'],occupancy])[:24]
    state['history'] = 'hypothetical_'+identity([root['state']['history'],occupancy])[:24]
    for i, (cell, value) in enumerate(zip(path, occupancy)):
        if value == 'O':
            state['pieces'].append(dict(id=f'blocker_{i}_'+root['id'], kind='knight', owner=state['actor'],cell=list(cell)))
        if value == 'U':
            state['unknown'].append(list(cell))
    return state


def event_id(root_id, occupancy, role):
    return f'c17-event-v1:{root_id}:{occupancy}:{role}'


def map_sources(root):
    root = Path(root); registry = Registry()
    rows = load(root, EVIDENCE); corpus = load(root, CORPUS)
    assert len(rows) == 432 and sum(r['admitted'] for r in rows) == 48
    roots = {r['id']:r for r in corpus['roots'] if r['split'] in ('A','B')}
    assert len(roots) == 24
    hashes = {p:sha(root/p) for p in (EVIDENCE, CORPUS, 'training/cycle17_shared_evidence.py','research/cycle16/corpus.py','research/cycle17/corpus.py')}
    by_key = {(r['root'],r['occupancy'],r['rule']): (i,r) for i,r in enumerate(rows)}
    assert len(by_key) == len(rows)
    row_map = {}; vectors = {}
    for root_id, episode in roots.items():
        group = episode['source_ancestry']
        for occupancy in ('EE','EO','EU','OE','OO','OU','UE','UO','UU'):
            pairs = [by_key[(root_id,occupancy,r)] for r in RULES]
            row = pairs[0][1]; state = state_for(episode,occupancy)
            assert row['state_identity'] == identity(state)
            assert row['observation_identity'] == identity([state,episode['attacker'],episode['target']])
            assert pairs[1][1]['reference'] == row['reference']
            natural = occupancy == 'EE'
            environment = event_id(root_id,occupancy,'environment')
            vector = event_id(root_id,occupancy,'evaluation')
            registry.register(observation(environment, dict(state=state,attacker=episode['attacker'],target=episode['target']),
                episode=root_id, groups=[group], kind=Kind.ENVIRONMENT if natural else Kind.SYNTHETIC,
                method='Recorded PGN-derived state' if natural else 'Cycle16 deterministic occupancy intervention',
                parents=[] if natural else [event_id(root_id,'EE','environment')],
                source=(CORPUS,hashes[CORPUS]),locator=f"/roots/{corpus['roots'].index(episode)}",
                exclusion=None if natural else 'Dependent intervention, not additional experience',
                admission='context' if natural else 'excluded'))
            # One evaluation result, even though it has two rule-specific aliases.
            values = {rule:row['label'] for rule in RULES}
            registry.register(observation(vector,dict(labels=values,reference=row['reference'],
                    observation_identity=row['observation_identity'],occupancy=occupancy,
                    origin='mapped-external-evaluation',label_relationship='same-result-copied'),
                episode=root_id,groups=[group],kind=Kind.EVALUATION,
                method='One python-chess Board.attacks completion result copied into both rule rows',
                parents=[environment],admission='admitted' if natural else 'excluded',
                exclusion=None if natural else row['reason'],source=(EVIDENCE,hashes[EVIDENCE]),
                locator=f'/{pairs[0][0]}/reference'))
            vectors[(root_id,occupancy)] = vector
            for i, row in pairs:
                assert row['ancestry'] == group and row['split'] == episode['split']
                assert row['state_identity'] == identity(state)
                assert row['observation_identity'] == identity([state,episode['attacker'],episode['target']])
                assert row['admitted'] == natural and row['label'] is (True if natural else None)
                annotation = event_id(root_id,occupancy,row['rule'])
                registry.register(observation(annotation,row,episode=root_id,groups=[group],
                    kind=Kind.DERIVED if natural or 'U' not in occupancy else Kind.UNKNOWN,
                    method='Conditional admission annotation; label alias of evaluation event',parents=[vector],
                    admission='admitted' if natural else 'excluded',exclusion=None if natural else row['reason'],
                    source=(EVIDENCE,hashes[EVIDENCE]),locator=f'/{i}'))
                row_map[identity(row)] = dict(row_index=i,event_id=annotation,vector_event_id=vector,
                    environmental_event_id=environment,admitted=natural,rule=row['rule'],source_group=group)
    memberships = {}; generations = []; revisions = 0
    for arm in ARMS:
        directory = f'artifacts/cycle17/learning/{arm}'
        model = load(root,directory+'/model.json'); ledger = load(root,directory+'/ledger.json')
        assert len(ledger)==432
        assert {identity({k:r[k] for k in rows[0]}) for r in ledger}==set(row_map)
        assert identity({k:v for k,v in model.items() if k!='version'}) == model['version']
        assert model['ledger_hash'] == identity(ledger)
        assert model['corpus_hash'] == identity(corpus['roots'])
        hashes[directory+'/model.json'] = sha(root/directory/'model.json')
        hashes[directory+'/ledger.json'] = sha(root/directory/'ledger.json')
        selected = {}
        for rule in RULES:
            parameter = model['rules'][rule]
            admitted = [r for r in ledger if r['rule']==rule and r['action']=='native-revision']
            assert len(admitted) == 12
            assert parameter['ancestry'] == [r['ancestry'] for r in admitted]
            assert parameter['truth_value'] == dict(strength=1.0,confidence=0.923076923076923)
            admitted_ids = []
            previous = dict(strength=.5,confidence=0)
            for r in admitted:
                original = {k:r[k] for k in rows[0]}
                key = identity(original); mapped = row_map[key]
                assert mapped['admitted'] and mapped['rule']==rule and key in parameter['evidence']
                proof = root/directory/'raw'/(r['proof']['sha256']+'.json')
                assert sha(proof)==r['proof']['sha256'] and proof.stat().st_size==r['proof']['bytes']
                receipt = json.loads(proof.read_text())
                assert not receipt['incomplete'] and r['expression'] in receipt['program']
                assert r['before']==previous
                assert r['after']['strength']==1.0
                previous=r['after']
                hashes[str(proof.relative_to(root))] = sha(proof)
                admitted_ids.append(mapped['event_id']); revisions += 1
                selected.setdefault(mapped['vector_event_id'],[]).append(rule)
            assert len(set(parameter['evidence']))==12
            assert previous==parameter['truth_value']
            for r in ledger:
                if r['rule']!=rule:continue
                expected='unadmitted' if not r['admitted'] else 'native-revision' if r['ancestry'] in parameter['ancestry'] else 'outside-registered-arm'
                assert r['action']==expected
            excluded = [m['event_id'] for m in row_map.values() if m['rule']==rule and m['event_id'] not in admitted_ids]
            generations.append(asdict(ParameterGeneration.create(namespace='native-original',
                schema_id='rule_'+rule,events=admitted_ids,excluded=excluded,groups=parameter['ancestry'],
                learner='training.cycle17_shared_evidence.fit@'+hashes['training/cycle17_shared_evidence.py'],
                assumptions='C17 supplied structure / trust 0.5 / native revision / source-rule dedup',
                uncertainty=json.dumps(parameter['truth_value'],sort_keys=True),
                checkpoint=directory+'/model.json#'+rule)))
        memberships[arm] = {k:tuple(sorted(v)) for k,v in sorted(selected.items())}
    audit = dict(schema='cycle18-source-mapping-v1',preparation_records=len(rows),admitted_annotations=48,
        excluded_annotations=384,admitted_vector_events=24,source_games=24,
        mapped_events=len(registry.all()),revision_receipts_verified=revisions,
        unique_admitted_annotation_ids_across_arms=len({event_id(registry.get(v).source_episode_id,'EE',r)
            for arm in memberships.values() for v,rs in arm.items() for r in rs}),
        observation_kinds=dict(Counter(e.observation_kind for e in registry.all())),
        label_relationship='Both conditional labels copy the SAME reference call result; separate clearance measurement absent',
        missing_historical_fields=['measurement timestamp','independent clearance measurement','sensor/noise calibration','random sampling probability'],
        environment_scope='Registered PGN-derived state; reconstructed synthetic states, not direct sensor measurements',
        arm_counts={a:dict(vector_events=len(m),annotations=sum(map(len,m.values())),
            shared_vectors=sum(len(v)==2 for v in m.values())) for a,m in memberships.items()},
        source_hashes=hashes,record_mapping=row_map,native_parameter_generations=generations)
    return registry,memberships,audit
