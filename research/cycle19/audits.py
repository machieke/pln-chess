"""Offline measurement fixtures and bounded novelty claims."""
from collections import Counter
import copy
from pln_chess.common import digest,ROOT,read_json
from research.cycle16.experiments import fixture
from .lifecycle import Journal
from .measurements import bindings,clearance,environment,measure
from .records import record


def fixtures(out):
    rows=[]
    for occupancy in ('EE','OE','EO','OO'):
        for friendly,reverse in ((False,False),(True,False),(False,True)):
            state,a,t=fixture(occupancy,tag='c19_hand')
            by={p['id']:p for p in state['pieces']}
            if friendly:by[t]['owner']=by[a]['owner']
            if reverse:
                for piece in state['pieces']:piece['cell']=[7-c for c in piece['cell']]
            root=dict(id=state['root'],state=state,attacker=a,target=t,source_collection='manual-fixture',
                game_identity='manual-fixture',source_ancestry='manual-fixture',split='diagnostic')
            j=Journal();env=j.add('environment',environment(root));m=measure(j,env);expected=occupancy=='EE'
            assert m['Clear']['value'] is expected and m['Attack']['value'] is expected
            rows.append(dict(occupancy=occupancy,friendly=friendly,reverse=reverse,expected=expected,environment=j.node(env),measurement=m))
    for fault in ('state','role'):
        j=Journal();env=environment(root)
        if fault=='role':env['attacker']='absent_attacker'
        event=j.add('environment',env);m=measure(j,event,expected_state='wrong_state' if fault=='state' else None)
        assert m['unresolved'];rows.append(dict(fault=fault,environment=env,measurement=m))
    return record(out,dict(passed=True,cases=rows,scope='Hand-declared expected targets, not stochastic reliability observations'))


def novelty(items,out):
    def axes(root):
        state=root['state'];bound,_=bindings(state,root['attacker'],root['target']);lookup={p['id']:p for p in state['pieces']}
        a=lookup[root['attacker']];t=lookup[root['target']]
        context=sorted((p['kind'],p['owner']==a['owner'],p['cell'][0]-a['cell'][0],p['cell'][1]-a['cell'][1]) for p in state['pieces'])
        return dict(source_game=root['game_identity'],endpoint_pair=digest(root['endpoint_locations']),direction=root['direction'],
            canonical_local_geometry=digest([t['cell'][0]-a['cell'][0],t['cell'][1]-a['cell'][1],2]),
            occupancy=''.join(clearance(state,bound)['occupancy']),context=digest(context),collection=root['source_collection'])
    training=[axes(r) for r in items if r['split'] in ('A','B')];result={}
    for split in ('A','B','development','test'):
        selected=[r for r in items if r['split']==split];values=[axes(r) for r in selected]
        result[split]=dict(roots=len(selected),directions=dict(Counter(r['direction'] for r in selected)),
            occupancy=dict(Counter(v['occupancy'] for v in values)),
            unseen_against_training={axis:sum(v[axis] not in {t[axis] for t in training} for v in values) for axis in training[0]},
            direction_fallbacks=sum(r['direction_fallback'] for r in selected))
    old={r['game_identity'] for c in (16,17) for r in read_json(ROOT/f'artifacts/cycle{c}/corpus-registration.json')['roots']}
    overlap=sorted(old&{r['game_identity'] for r in items});assert not overlap
    return record(out,dict(splits=result,prior_consequence_game_overlap=overlap,
        new_to_cycle=True,new_to_consequence_learner=True,new_to_project=False,
        earlier_project_exposure='All selected positions are derived from an already imported Cycle10 archive; no global-unseen claim',
        common_dependencies=['source collection','engines/opening families','supplied templates','position representation','measurement libraries'],
        unseen_path_length=False,representation_controls='Dependent renaming/rotation/reflection, not discovery of new structures'))
