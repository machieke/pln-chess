"""Pre-registered occupancy, structural, rule and bounded-execution controls."""
import copy
from dataclasses import replace,asdict
from pathlib import Path
from pln_chess.common import read_json
from research.cycle15.native_reasoner import NativeReasoner,Sentence,parse,alpha_key
from research.cycle15.observations import successor,ray
from .corpus import OCCUPANCIES,reference,roots,variant
from .experiments import fixture,infer,observations,knowledge,SMALL,MEDIUM,GENEROUS
from .records import compact,record
from .evidence_audit import pair_diagnostic


def occupancy(out):
    out=Path(out);rows=[]
    for kind in ('rook','bishop','queen'):
        for value in OCCUPANCIES:
            state,a,t=fixture(value,kind,tag=kind+'_'+value)
            result=infer(state,a,t)
            rows.append(dict(kind=kind,occupancy=value,result=compact(result,out),reference=reference(state,a,t)))
    return record(out/'occupancy.json',rows)


def interventions(out):
    out=Path(out);reasoner=NativeReasoner();state,a,t=fixture(tag='intervention')
    facts,scope=observations(state,a,t);rules=knowledge('F');sid=state['id']
    query=f'(Attack {a} {t} {sid})';contrary=f'(NoAttack {a} {t} {sid})'
    empty=[f for f in facts if f.term.startswith('(Empty ')]
    assert len(empty)==2
    cases={'base':(facts,rules), 'remove-clear-two':(facts,knowledge('F-minus'))}
    for i,item in enumerate(empty):
        cases['remove-empty-'+str(i)]=([f for f in facts if f!=item],rules)
    cases['wrong-state']=([replace(f,term=f.term.replace(sid,'state_unrelated')) if f==empty[0] else f for f in facts],rules)
    cases['wrong-ray-role']=([replace(f,term=f.term.replace(a,'unrelated_attacker')) if f.term.startswith('(RayPath ') else f for f in facts],rules)
    cases['lower-rule-tv']=(facts,[replace(r,confidence=.2) if r.stamps[0]=='rule_clear-two' else r for r in rules])
    cases['reverse-input-order']=(list(reversed(facts)),list(reversed(rules)))
    for i in (0,1):
        cases['confidence-cell-'+str(i)]=([replace(f,confidence=.5) if f==empty[i] else f for f in facts],rules)
    cases['competing-occupancy-audit']=(facts+[Sentence(empty[0].term.replace('Empty','Occupied'),
        stamps=('obs_competing_occupancy',),origin='audit-input',ancestry=(state['root'],))],rules)
    other,oa,ot=fixture('OO',tag='stale');stale,_=observations(other,oa,ot)
    cases['indexed-stale-before-facts']=(facts+stale,rules)
    results={name:compact(reasoner.infer(fs,rs,query,contrary=contrary,budgets=GENEROUS),out) for name,(fs,rs) in cases.items()}
    # Chess-path witness uses actual returned beliefs, with the same stable stamps.
    recursive=reasoner.infer(facts,knowledge('R'),query,budgets=GENEROUS)
    cells=scope['relevant_ray_cells'];roles={tuple(v):k for k,v in scope['cell_roles'].items()}
    c1,c2=[roles[tuple(c)] for c in cells]
    extension=next(r for r in recursive['retained'] if r['term']==f'(PathEmpty (Cons {c2} Nil) {sid})')
    partial=next(r for r in recursive['retained'] if alpha_key(r['term'])==alpha_key(
        f'(Implication (PathEmpty $tail {sid}) (PathEmpty (Cons {c1} $tail) {sid}))'))
    results['chess-recursive-witness']=dict(result=compact(recursive,out),diagnostic=pair_diagnostic(partial,extension,out))
    return record(out/'interventions.json',results)


def structural(out):
    out=Path(out);rows={};state,a,t=fixture('OE',tag='structural')
    blocker=next(p for p in state['pieces'] if p['id'].startswith('blocker'))
    move=dict(id='move_structural',piece=blocker['id'],destination=[0,0])
    rows['sole-blocker-leaves']=infer(state,a,t,supplied_move=move)
    along=successor(state,{**move,'destination':[3,1]})
    rows['blocker-moves-along']=infer(along,a,t)
    second=copy.deepcopy(state);second['id']+='second';second['pieces'].append(dict(id='second_blocker',kind='pawn',owner='white',cell=[3,1]))
    rows['second-blocker-remains']=infer(successor(second,move),a,t)
    unrelated=copy.deepcopy(state);unrelated['id']+='unrelated';unrelated['pieces'].append(dict(id='unrelated_piece',kind='pawn',owner='black',cell=[7,7]))
    rows['unrelated-move']=infer(successor(unrelated,dict(id='move_unrelated',piece='unrelated_piece',destination=[6,7])),a,t)
    clear,a,t=fixture(tag='roles')
    for name,change in [('attacker-removed','remove-a'),('target-removed','remove-t'),('target-replaced','replace'),
                        ('ordinary-target','ordinary'),('friendly-target','friendly'),('wrong-actor','actor')]:
        current=copy.deepcopy(clear);current['id']+=name
        if change.startswith('remove'):current['pieces']=[p for p in current['pieces'] if p['id']!=(a if change=='remove-a' else t)]
        elif change=='replace':current['pieces'][1]['id']='replacement_target'
        elif change=='ordinary':current['pieces'][1]['kind']='knight'
        elif change=='friendly':current['pieces'][1]['owner']='black'
        else:current['actor']='black'
        rows[name]=infer(current,a,t)
    for name in ('renamed','reflected','owner-swapped','translated'):
        current=copy.deepcopy(clear);current['id']+=name;aa,tt=a,t
        if name=='renamed':
            for p in current['pieces']:p['id']='unfamiliar_'+p['id']
            aa,tt='unfamiliar_'+a,'unfamiliar_'+t
        elif name=='owner-swapped':
            current['actor']='black'
            for p in current['pieces']:p['owner']='white' if p['owner']=='black' else 'black'
        else:
            for p in current['pieces']:p['cell']=[7-p['cell'][0],p['cell'][1]] if name=='reflected' else [p['cell'][0]+1,p['cell'][1]+1]
        rows[name]=infer(current,aa,tt)
    for length in (1,2,4):
        s,aa,tt=fixture('E'*(length-1),length=length,tag='length_'+str(length))
        rows['intervening-'+str(length-1)]=infer(s,aa,tt,budgets=GENEROUS)
    def shrink(value):
        if 'before' in value:return {**{k:v for k,v in value.items() if k not in ('before','after')},'before':compact(value['before'],out),'after':compact(value['after'],out)}
        return compact(value,out)
    return record(out/'structural.json',{name:shrink(value) for name,value in rows.items()})


def budgets(out,learning):
    out=Path(out);rows={};state,a,t=fixture(tag='budgets')
    for arm in ('R','F'):
        for name,budget in [('small',SMALL),('medium',MEDIUM),('generous',GENEROUS)]:
            rows[arm+'-'+name]=compact(infer(state,a,t,arm=arm,budgets=budget),out)
    root=next(r for r in roots() if r['split']=='development');state=variant(root,'EE')
    for name in ('learned','prior','shared-chain','leave-one'):
        model=read_json(Path(learning)/name/'model.json')
        rows[name]=compact(infer(state,root['attacker'],root['target'],arm='L',checkpoint=model,budgets=GENEROUS),out)
    # Actual learned-chain overlap from returned clearance and terminal partial.
    full=infer(state,root['attacker'],root['target'],arm='L',checkpoint=read_json(Path(learning)/'shared-chain/model.json'),budgets=GENEROUS)
    clear=full['stages']['Clear']['query'];attack=full['stages']['Attack']['query']
    retained=full['stages']['Attack']['retained']
    clearance=next((r for r in retained if r['term']==clear),None)
    target=next((r for r in retained if r['term']==f'(Implication {clear} {attack})'),None)
    rows['shared-chain-witness']=dict(clearance=clearance,terminal_partial=target,
        diagnostic=pair_diagnostic(target,clearance,out) if target and clearance else None,
        result=compact(full,out))
    reasoner=NativeReasoner()
    from research.cycle15.native_reasoner import save_result
    program=f'!(import! &self "{reasoner.runtime.library}")\n'
    program+='!(println! (C16LIMIT (LimitSize ((Sentence (AuditA (stv 1 0.9)) (obs_limit_a)) (Sentence (AuditB (stv 1 0.8)) (obs_limit_b))) 2)))\n'
    receipt=reasoner.execute_program(program)
    rows['effective-capacity']=dict(receipt=save_result(receipt,out/'raw'),stdout=receipt['stdout'])
    return record(out/'budgets-learning.json',rows)
