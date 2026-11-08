"""Grounded native rule scheduling and inspectable evidence choice."""
from __future__ import annotations
from dataclasses import dataclass,asdict
import time
from pln_chess.common import digest
from pln_chess.domain import Position
from pln_chess.hypotheses import candidates
from pln_chess.observations import observe
from pln_chess.learning import Model
from pln_chess.pln import Runtime,TV,UNKNOWN,NativeError

@dataclass(frozen=True)
class Options:
    max_native_invocations: int=20000
    timeout_seconds: float=60
    min_confidence: float=0.25
    supported_strength: float=0.8
    contradicted_strength: float=0.2

    def __post_init__(self):
        if self.max_native_invocations < 0 or self.timeout_seconds <= 0: raise ValueError('Invalid inference budget')
        if not 0 <= self.contradicted_strength < self.supported_strength <= 1: raise ValueError('Invalid display thresholds')
        if not 0 <= self.min_confidence <= 1: raise ValueError('Invalid display confidence')

class Schedule:
    def __init__(self,model,options):
        self.model=model; self.options=options; self.nodes=[]; self.traces=[]

    def node(self,operator,expression,conclusion,premises,rule_ids,evidence_ids):
        if len(self.nodes)>=self.options.max_native_invocations: raise OverflowError('Native invocation budget exhausted')
        name=f'n{len(self.nodes)}'
        self.nodes.append((name,expression))
        self.traces.append({'id':name,'operator':operator,'native_expression':expression,'conclusion':conclusion,
                            'premises':premises,'matched_rule_ids':rule_ids,'evidence_ids':sorted(set(evidence_ids))})
        return name

    def conditional(self,key,observation,conclusion,tv):
        belief=self.model.belief(key)
        pos=TV.from_json(belief['positive']); neg=TV.from_json(belief['negative'])
        evidence=belief['evidence_ids']
        common=[{'atom':observation,'truth_value':tv.json()},
                {'atom':f'(Implication {observation} {conclusion})','truth_value':pos.json(),'hypothesis_id':key}]
        p=self.node('modus-ponens',f'(let ($a $t) (|- ({observation} {tv.metta()}) ((Implication {observation} {conclusion}) {pos.metta()})) $t)',conclusion,common,[key+':positive'],evidence)
        negative=f'(Not {conclusion})'
        q=self.node('modus-ponens',f'(let ($a $t) (|- ({observation} {tv.metta()}) ((Implication {observation} {negative}) {neg.metta()})) $t)',negative,
                    [common[0],{'atom':f'(Implication {observation} {negative})','truth_value':neg.json(),'hypothesis_id':key}], [key+':negative'],evidence)
        n=self.node('negation-elimination',f'(let ($a $t) (|- ({negative} ({q}))) $t)',conclusion,[{'node':q}],[],evidence)
        selected=self.node('evidence-choice',f'(let ($tv $ev) (BestConfidenceCandidate ((({p}) (positive)) (({n}) (negative)))) $tv)',conclusion,[{'node':p},{'node':n}],[],evidence)
        return {'selected':selected,'positive':p,'negative':q,'evidence_ids':evidence,'hypothesis_id':key}

def classify(tv,options,incomplete=False):
    if incomplete: return 'incomplete'
    if tv.confidence < options.min_confidence: return 'unknown'
    if tv.strength >= options.supported_strength: return 'supported'
    if tv.strength <= options.contradicted_strength: return 'contradicted'
    return 'unknown'

def infer_moves(position,checkpoint=None,options=None,runtime=None,selected_moves=None,representation=None,mode=None):
    position=Position.from_fen(position) if isinstance(position,str) else position
    if mode is not None:
        from pln_chess.cycle6.inference import Cycle6Options
        settings=asdict(options) if options else {};settings['mode']=mode
        if 'promotion_training' in settings:
            from pln_chess.cycle8.inference import Cycle8Options
            options=Cycle8Options(**settings)
        elif any(k in settings for k in ('backoff','new_training','max_backoff_level')):
            from pln_chess.cycle7.inference import Cycle7Options
            options=Cycle7Options(**settings)
        else:options=Cycle6Options(**settings)
    options=options or Options(); runtime=runtime or Runtime(timeout=options.timeout_seconds)
    model=Model.load(checkpoint,runtime) if isinstance(checkpoint,(str,__import__('pathlib').Path)) else checkpoint or Model(runtime.version)
    if representation is not None and representation!=model.variant:
        raise ValueError('Requested representation does not match checkpoint')
    if model.schema==8:
        from pln_chess.cycle8.inference import infer_moves as cycle8_infer
        return cycle8_infer(position,model,options,runtime,selected_moves)
    if model.schema==7:
        from pln_chess.cycle7.inference import infer_moves as cycle7_infer
        return cycle7_infer(position,model,options,runtime,selected_moves)
    if model.schema==6:
        from pln_chess.cycle6.inference import infer_moves as mode_infer
        return mode_infer(position,model,options,runtime,selected_moves)
    if mode is not None:raise ValueError('Explicit proof modes require a Cycle 6 checkpoint; migrate schema 5 first')
    if model.schema==5:
        from pln_chess.cycle5.inference import infer_moves as premise_infer
        return premise_infer(position,model,options,runtime,selected_moves)
    if model.schema==4:
        from pln_chess.cycle4.inference import infer_moves as factored_infer
        return factored_infer(position,model,options,runtime,selected_moves)
    if model.schema==3:
        from pln_chess.cycle3.inference import infer_moves as relational_infer
        return relational_infer(position,model,options,runtime,selected_moves)
    if model.schema==2:
        from pln_chess.cycle2.inference import infer_moves as hierarchical_infer
        return hierarchical_infer(position,model,options,runtime,selected_moves)
    if model.runtime_version!=runtime.version: raise ValueError('Model/runtime mismatch')
    runtime.timeout=options.timeout_seconds
    schedule=Schedule(model,options); pending=[]; started=time.perf_counter(); truncated=False
    for move in (selected_moves if selected_moves is not None else candidates(position)):
        obs=observe(position,move,model.variant); begin=len(schedule.nodes)
        item={'move':move.notation,'candidate_id':move.id,'piece':obs['piece'],'relative_pattern':obs['pattern'],
              'observations':obs,'proof_trace':[],'evidence_ids':[],'matched_rule_ids':[],
              'movement_truth_value':UNKNOWN.json(),'attack_beliefs':[],'counterevidence_ids':[], 'status':'native-partial',
              'gaps':['No compositional conjunction proof; legality uses a learned joint observation category.'],
              'legal_move_truth_value':UNKNOWN.json(),'classification':'unknown'}
        if not obs['complete']:
            item['gaps'].append('Incomplete observation: joint sensor has zero confidence.')
            item['movement_truth_value']=UNKNOWN.json()
            item['matched_rule_ids']=[]
            item['attack_beliefs']=[]
            pending.append(item)
            continue
        try:
            sensor=TV.from_json(obs['tv'])
            legal=schedule.conditional(obs['key'],f'(RelativeObservation {position.id} {move.id})',f'(LegalMove {position.id} {move.id})',sensor)
            movement=schedule.conditional(obs['geometry_key'],f'(RelativePattern {move.id})',f'(MovementPatternSupported {move.id})',sensor)
            attacks=[]
            if model.variant not in ('no-exposure','geometry-only','weaker-prior'):
                for attack in obs['attacks']:
                    attack_atom=f'(Attack {attack["attacker_id"]} {attack["king_id"]} {move.id})'
                    belief=schedule.conditional(attack['key'],f'(OpponentFrame {attack["attacker_id"]} {move.id})',attack_atom,sensor)
                    # A learned positive attack supports exposure via an explicit weak prior.
                    # No safe-king conclusion is inferred from absence of attack evidence.
                    exposure=f'(WouldExposeOwnKing {position.id} {move.id})'
                    prior=TV(1.0,0.25)
                    e=schedule.node('modus-ponens',f'(let ($a $t) (|- ({attack_atom} ({belief["positive"]})) ((Implication {attack_atom} {exposure}) {prior.metta()})) $t)',exposure,
                                    [{'node':belief['positive']},{'atom':f'(Implication {attack_atom} {exposure})','truth_value':prior.json()}],['attack-to-exposure-prior'],belief['evidence_ids'])
                    negative_legal=f'(Not (LegalMove {position.id} {move.id}))'
                    veto=schedule.node('modus-ponens',f'(let ($a $t) (|- ({exposure} ({e})) ((Implication {exposure} {negative_legal}) {prior.metta()})) $t)',negative_legal,
                                       [{'node':e},{'atom':f'(Implication {exposure} {negative_legal})','truth_value':prior.json()}],['exposure-to-negative-legality-prior'],belief['evidence_ids'])
                    counter=schedule.node('negation-elimination',f'(let ($a $t) (|- ({negative_legal} ({veto}))) $t)',f'(LegalMove {position.id} {move.id})',[{'node':veto}],[],belief['evidence_ids'])
                    attacks.append({**belief,'exposure':e,'counter':counter,'attacker_id':attack['attacker_id']})
            final=legal['selected']
            if attacks:
                choices=' '.join(f'(({a["counter"]}) (attack{i}))' for i,a in enumerate(attacks))
                final=schedule.node('evidence-choice',f'(let ($tv $ev) (BestConfidenceCandidate ((({legal["selected"]}) (context)) {choices})) $tv)',f'(LegalMove {position.id} {move.id})',
                                    [{'node':legal['selected']}]+[{'node':a['counter']} for a in attacks],[],
                                    legal['evidence_ids']+[e for a in attacks for e in a['evidence_ids']])
            item['_refs']={'legal':legal,'final':final,'movement':movement,'attacks':attacks,'start':begin,'end':len(schedule.nodes)}
        except OverflowError:
            del schedule.nodes[begin:]; del schedule.traces[begin:]
            item['classification']='incomplete'; item['gaps'].append('Native invocation budget exhausted'); truncated=True
        pending.append(item)
    values={}; error=None
    try:
        # One batch preserves references across all candidate proofs.
        values=runtime.batch(schedule.nodes)
    except NativeError as exc:
        error=str(exc); truncated=True
    for item in pending:
        refs=item.pop('_refs',None)
        if refs is None: continue
        if error:
            item['classification']='incomplete'; item['gaps'].append(error); continue
        legal=values[refs['final']]
        item['context_only_truth_value']=values[refs['legal']['selected']].json()
        item['legal_move_truth_value']=legal.json(); item['classification']=classify(legal,options)
        item['movement_truth_value']=values[refs['movement']['selected']].json()
        item['evidence_ids']=sorted(set(refs['legal']['evidence_ids']+[e for a in refs['attacks'] for e in a['evidence_ids']]))
        item['counterevidence_ids']=sorted(set(e for a in refs['attacks'] for e in a['evidence_ids']))
        item['attack_beliefs']=[{'attacker_id':a['attacker_id'],'truth_value':values[a['selected']].json(),
                                'exposure_support':values[a['exposure']].json(),'evidence_ids':a['evidence_ids']} for a in refs['attacks']]
        item['matched_rule_ids']=sorted({r for t in schedule.traces[refs['start']:refs['end']] for r in t['matched_rule_ids']})
        for trace in schedule.traces[refs['start']:refs['end']]:
            trace={**trace,'truth_value':values[trace['id']].json()}
            trace['premises']=[{**p,**({'truth_value':values[p['node']].json()} if 'node' in p else {})} for p in trace['premises']]
            item['proof_trace'].append(trace)
    return {'schema':1,'position_id':position.id,'fen':position.fen(),'runtime_version':runtime.version,
            'model_version':model.version,'representation':model.variant,'budget':asdict(options),'truncated':truncated,
            'native_invocations':len(schedule.nodes) if not error else 0,'scheduled_invocations':len(schedule.nodes),
            'grounded_atoms':sum(len(x['observations']['atoms'])+len(x['proof_trace']) for x in pending),
            'elapsed_seconds':time.perf_counter()-started,'candidates':pending,
            'coverage':'native-partial','error':error}
