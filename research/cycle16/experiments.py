"""Whole-knowledge native requests over raw structural observations."""
from dataclasses import asdict
from pathlib import Path
from pln_chess.common import ROOT, digest, read_json
from research.cycle15.knowledge import load_rules, templates
from research.cycle15.native_reasoner import Budgets, NativeReasoner, Sentence, parse
from research.cycle15.observations import observe, successor, validate_state, coordinate

SMALL=Budgets(24,64,128,15)
MEDIUM=Budgets(64,128,256,15)
GENEROUS=Budgets(128,256,512,30)
SEMANTICS='Occupancy-constrained sliding influence, including friendly destination; not legal capture or move legality'


def knowledge(arm='F', checkpoint=None):
    if arm not in ('R','F','F-minus','L'):
        raise ValueError('Expected R, F, F-minus or L')
    if arm=='L' and checkpoint is None:
        raise ValueError('L requires an explicit finite checkpoint')
    if arm in ('R','F-minus') and checkpoint is not None:
        raise ValueError('Recursive controls use the frozen supplied parameters')
    path=ROOT/'knowledge/cycle16'/('recursive.metta' if arm=='R' else 'finite_two.metta')
    return load_rules(checkpoint,path=path,remove=('clear-two',) if arm=='F-minus' else ())


def observations(state, attacker, target, **kwargs):
    validate_state(state)
    unknown=[coordinate(cell) for cell in state['unknown']]
    if len(set(unknown))!=len(unknown):
        raise ValueError('Duplicate unknown structural cell')
    return observe(state,attacker,target,**kwargs)


def channel(value):
    return value is not None and value['strength']>=.6 and value['confidence']>=.1


def support_status(result):
    if result['incomplete']: return 'incomplete execution'
    if result['classification']=='conflicting': return 'positive and contrary support'
    if result['classification']!='unknown': return 'supported at registered display thresholds'
    if result['answer'] or result['contrary']: return 'native support below display threshold'
    return 'no matching support returned within budget'


def infer(state,attacker,target,*,arm='F',checkpoint=None,budgets=None,proof_mode='full',
          supplied_move=None,full_scope=False,reasoner=None):
    if proof_mode not in ('full','summary'):raise ValueError('Expected full or summary proof')
    if supplied_move is not None:
        observations(state,attacker,target)
        after=successor(state,supplied_move)
        return dict(supplied_move=supplied_move,transition='structural hypothetical; no legality decision',
            before=infer(state,attacker,target,arm=arm,checkpoint=checkpoint,budgets=budgets,
                         proof_mode=proof_mode,full_scope=full_scope,reasoner=reasoner),
            after=infer(after,attacker,target,arm=arm,checkpoint=checkpoint,budgets=budgets,
                        proof_mode=proof_mode,full_scope=full_scope,reasoner=reasoner))
    facts,scope=observations(state,attacker,target,full_scope=full_scope)
    rules=knowledge(arm,checkpoint)
    reasoner=reasoner or NativeReasoner()
    sid=state['id'];shape=scope['shape'] or 'unaligned'
    queries={'Clear':(f'(Clear {attacker} {target} {shape} {sid})',None),
             'Attack':(f'(Attack {attacker} {target} {sid})',f'(NoAttack {attacker} {target} {sid})'),
             'Exposure':(f'(KingExposed {target} {state["actor"]} {sid})',
                         f'(NotKingExposed {target} {state["actor"]} {sid})')}
    stages={}
    # Each stage is a fresh, fully disclosed call. No stage's answer is injected
    # into another, and no rule is selected by host-side path length.
    for name,(query,contrary) in queries.items():
        result=reasoner.infer(facts,rules,query,contrary=contrary,budgets=budgets or MEDIUM)
        result['support_status']=support_status(result)
        stages[name]=result
    if isinstance(checkpoint,(str,Path)):checkpoint=read_json(checkpoint)
    result=dict(target_semantics=SEMANTICS,observation_scope=scope,arm=arm,
        query_domain_valid=scope['attacker_present'] and scope['target_present'],
        domain_reason=None if scope['attacker_present'] and scope['target_present'] else 'query entity absent; not negative evidence',
        knowledge_identity=digest([s.metta() for s in rules]),
        checkpoint_identity=checkpoint['version'] if checkpoint else None,
        raw_observations=[asdict(s) for s in facts],stages=stages,
        inference_boundary='raw facts and entire registered knowledge; no label or clearance oracle',
        proof_status='native selected tasks, returned beliefs/stamps; no complete fired-rule tree')
    if proof_mode=='summary':
        result['stages']={n:{k:r[k] for k in ('query','answer','contrary','classification','incomplete',
            'support_status','usage','budgets','proof_status')} for n,r in stages.items()}
    return result


def fixture(occupancy='EE',kind='rook',length=3,tag='pilot'):
    if len(occupancy)!=length-1 or set(occupancy)-set('EOU'):raise ValueError('Invalid fixture occupancy')
    diagonal=kind=='bishop';start=[1,1];end=[1+length,1+length if diagonal else 1]
    if max(end)>7:raise ValueError('Out-of-board fixture')
    state=dict(id='state_'+tag,root='root_'+tag,actor='white',history='history_'+tag,unknown=[],pieces=[
        dict(id='attacker_'+tag,kind=kind,owner='black',cell=start),
        dict(id='target_'+tag,kind='king',owner='white',cell=end)])
    for i,status in enumerate(occupancy,1):
        cell=[1+i,1+i if diagonal else 1]
        if status=='O':state['pieces'].append(dict(id=f'blocker_{i}_{tag}',kind='knight',owner='white',cell=cell))
        if status=='U':state['unknown'].append(cell)
    return state,state['pieces'][0]['id'],state['pieces'][1]['id']
