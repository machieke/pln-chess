"""Native conditional proofs with conservative, explicit presentation policy."""
from dataclasses import asdict
import time
from pathlib import Path
from pln_chess.common import digest
from pln_chess.domain import Position
from pln_chess.hypotheses import candidates
from pln_chess.pln import Runtime,TV,UNKNOWN,NativeError
from pln_chess.inference import Options,classify
from pln_chess.cycle2.descriptors import descriptors,relation
from pln_chess.cycle2.model import HierarchicalModel
from pln_chess.cycle2.native import NativeSession


def infer_moves(position,checkpoint,options=None,runtime=None,selected_moves=None,session=None,optimized=True):
    started=time.perf_counter();position=Position.from_fen(position) if isinstance(position,str) else position
    options=options or Options();runtime=runtime or Runtime(timeout=options.timeout_seconds)
    model=HierarchicalModel.load(checkpoint,runtime) if isinstance(checkpoint,(str,Path)) else checkpoint
    if model.runtime_version!=runtime.version: raise ValueError('Model/runtime mismatch')
    session=session or NativeSession(runtime,optimized);before_calls=session.calls;before_hits=session.hits
    nodes=[];traces=[];items=[];truncated=False
    def node(operator,expr,conclusion,premises,evidence,rule):
        if len(nodes)>=options.max_native_invocations: raise OverflowError('Native proof budget exhausted')
        name=f'n{len(nodes)}';nodes.append((name,expr))
        traces.append({'id':name,'operator':operator,'native_expression':expr,'conclusion':conclusion,
                       'premises':premises,'evidence_ids':sorted(set(evidence)),'matched_rule_ids':[rule],
                       'provenance':'native-derived'})
        return name
    def conditional(rel,origin='direct'):
        key=rel['id'];belief=model.hypotheses[key];ids=belief['evidence_ids']
        sensor=TV(1.,.99)
        if origin=='induction':
            induction=model.induction[key];tv=TV.from_json(induction['truth_value']);ids=induction['evidence_ids']
            p=node('Truth_ModusPonens',f'(Truth_ModusPonens {sensor.metta()} {tv.metta()})',rel['target'],
                   [{'sensor':rel,'truth_value':sensor.json()},{'induction':induction,'truth_value':tv.json()}],ids,key+':induction')
            return {'selected':p,'positive':p,'evidence_ids':ids,'id':key,'tier':rel['tier'],'origin':'native-induction'}
        p=node('Truth_ModusPonens',f'(Truth_ModusPonens {sensor.metta()} {TV.from_json(belief["positive"]).metta()})',rel['target'],
               [{'sensor':rel,'truth_value':sensor.json()},{'conditional':key+':positive','truth_value':belief['positive']}],ids,key+':positive')
        n=node('Truth_ModusPonens',f'(Truth_ModusPonens {sensor.metta()} {TV.from_json(belief["negative"]).metta()})','Not '+rel['target'],
               [{'sensor':rel,'truth_value':sensor.json()},{'conditional':key+':negative','truth_value':belief['negative']}],ids,key+':negative')
        q=node('Truth_Negation',f'(Truth_Negation ({n}))',rel['target'],[{'node':n}],ids,key+':negation')
        s=node('BestConfidenceCandidate',f'(let ($tv $e) (BestConfidenceCandidate ((({p}) (positive)) (({q}) (negative)))) $tv)',rel['target'],
               [{'node':p},{'node':q}],ids,key+':choice')
        return {'selected':s,'positive':p,'evidence_ids':ids,'id':key,'tier':rel['tier'],'origin':'direct-native-revision'}
    for move in selected_moves if selected_moves is not None else candidates(position):
        obs=descriptors(position,move,model.variant);start=len(nodes)
        item={'move':move.notation,'candidate_id':move.id,'piece':obs['piece'],'relative_pattern':obs['pattern'],'observations':obs,
              'proof_trace':[],'matched_hypotheses':[],'matched_rule_ids':[],'evidence_ids':[],'attack_beliefs':[],
              'movement_truth_value':UNKNOWN.json(),'legal_move_truth_value':UNKNOWN.json(),'classification':'unknown','status':'unknown',
              'gaps':['Local conditional evidence is native-partial; no joint movement AND king-safety theorem.'],
              'selection_policy':'Most specific reusable local relation; exact context only fallback. Dependent paths never revised together. Opposing decisive evidence abstains.'}
        if not obs['complete']:
            item['gaps'].append('Incomplete occupancy/history; no conditional proof scheduled.');items.append(item);continue
        try:
            matches=[r for r in obs['relations'] if r['id'] in model.hypotheses]
            movement=[conditional(r) for r in matches if r['target']=='MovementPatternSupported']
            legal=[conditional(r) for r in matches if r['target']=='LegalMove']
            induced=[conditional(r,'induction') for r in matches if r['id'] in model.induction]
            attacks=[]
            for attack in obs['attack_relations']:
                rel=attack['relation']
                if rel['id'] in model.hypotheses:
                    a={**conditional(rel),'attacker_id':attack['attacker_id'],'king_id':attack['king_id']}
                    prior=a['positive']
                    for edge,target in [('Attack-to-Exposure','WouldExposeOwnKing'),('Exposure-to-NotLegal','Not LegalMove')]:
                        bridge=relation(4,{'edge':edge},'Bridge')['id']
                        if bridge not in model.hypotheses:break
                        h=model.hypotheses[bridge]
                        prior=node('Truth_ModusPonens',f'(Truth_ModusPonens ({prior}) {TV.from_json(h["positive"]).metta()})',target,
                                   [{'node':prior},{'conditional':bridge,'truth_value':h['positive']}],a['evidence_ids']+h['evidence_ids'],bridge)
                        a['exposure' if target=='WouldExposeOwnKing' else 'negative_legality']=prior
                    if 'negative_legality' in a:
                        a['counter']=node('Truth_Negation',f'(Truth_Negation ({prior}))','LegalMove',[{'node':prior}],a['evidence_ids'],a['id']+':exposure-negation')
                    attacks.append(a)
                else: item['attack_beliefs'].append({'attacker_id':attack['attacker_id'],'truth_value':UNKNOWN.json(),'origin':'unlearned'})
            # Prefer reusable tiers. Exact-context remains fallback, never dominates it.
            reusable=[a for a in legal if a['tier']<6]
            primary=max(reusable or legal,key=lambda a:a['tier'],default=None)
            final=primary['selected'] if primary else None
            selected_inductions=[a for a in induced if primary and a['id']==primary['id']]
            if selected_inductions:
                a=selected_inductions[0]
                final=node('BestConfidenceCandidate',f'(let ($tv $e) (BestConfidenceCandidate ((({final}) (direct)) (({a["selected"]}) (induced)))) $tv)',
                           'LegalMove',[{'node':final},{'node':a['selected']}],primary['evidence_ids']+a['evidence_ids'],primary['id']+':origin-choice')
            counters=[a for a in attacks if 'counter' in a]
            if final and counters:
                choices=' '.join(f'(({a["counter"]}) (attack{i}))' for i,a in enumerate(counters))
                final=node('BestConfidenceCandidate',f'(let ($tv $e) (BestConfidenceCandidate ((({final}) (local)) {choices})) $tv)',
                           'LegalMove',[{'node':final}]+[{'node':a['counter']} for a in counters],
                           primary['evidence_ids']+[e for a in counters for e in a['evidence_ids']],primary['id']+':exposure-choice')
            item['_refs']={'movement':movement,'legal':legal,'induced':induced,'attacks':attacks,'primary':primary,'final':final,'start':start,'end':len(nodes)}
        except OverflowError as error:
            del nodes[start:];del traces[start:];item['classification']='incomplete';item['gaps'].append(str(error));truncated=True
        items.append(item)
    old_timeout=runtime.timeout;runtime.timeout=options.timeout_seconds;error=None
    try: values=session.batch(nodes)
    except NativeError as exc: values={};error=str(exc);truncated=True
    finally: runtime.timeout=old_timeout
    for item in items:
        refs=item.pop('_refs',None)
        if refs is None: continue
        if error: item['classification']='incomplete';item['gaps'].append(error);continue
        item['proof_trace']=[{**t,'truth_value':values[t['id']].json(),
                              'premises':[{**p,**({'truth_value':values[p['node']].json()} if 'node' in p else {})} for p in t['premises']]} for t in traces[refs['start']:refs['end']]]
        item['matched_hypotheses']=[{**a,'truth_value':values[a['selected']].json(),
                                      'belief':model.hypotheses[a['id']]} for a in refs['movement']+refs['legal']+refs['induced']]
        movement=max(refs['movement'],key=lambda a:a['tier'],default=None)
        if movement:
            item['movement_truth_value']=values[movement['selected']].json();item['movement_hypothesis_id']=movement['id']
        for a in refs['attacks']:
            item['attack_beliefs'].append({**a,'truth_value':values[a['selected']].json(),'positive_truth_value':values[a['positive']].json()})
        final=values[refs['final']] if refs['final'] else UNKNOWN
        item['legal_move_truth_value']=final.json();item['classification']=classify(final,options)
        item['chosen_hypothesis_id']=refs['primary']['id'] if refs['primary'] else None
        item['status']='native-partial' if refs['final'] else 'unknown'
        # Display abstention is not a native safety theorem or a replacement TV.
        conflicts=[a['id'] for a in refs['legal'] if classify(values[a['selected']],options) in ('supported','contradicted') and classify(values[a['selected']],options)!=item['classification'] and item['classification'] in ('supported','contradicted')]
        exposures=[a['id'] for a in refs['attacks'] if classify(values[a['selected']],options)=='supported']
        if conflicts or (exposures and item['classification']=='supported'):
            item['classification']='unknown';item['gaps'].append('Abstained: conflicting native conditionals or learned attack evidence. Raw TV retained.')
        item['conflicting_hypotheses']=conflicts;item['exposure_conflicts']=exposures
        item['matched_rule_ids']=sorted({r for t in item['proof_trace'] for r in t['matched_rule_ids']})
        item['evidence_ids']=sorted({e for t in item['proof_trace'] for e in t['evidence_ids']})
        item['dependence_overlap']='Alternatives share ledger evidence; choice/abstention only, no evidence fusion.'
    return {'schema':2,'position_id':position.id,'fen':position.fen(),'runtime_version':runtime.version,'model_version':model.version,
            'representation':model.variant,'budget':asdict(options),'truncated':truncated,'error':error,
            'native_invocations':session.calls-before_calls,'scheduled_invocations':len(nodes),'cache_hits':session.hits-before_hits,
            'grounded_atoms':sum(len(i['observations']['atoms'])+len(i['proof_trace']) for i in items),
            'elapsed_seconds':time.perf_counter()-started,'candidates':items,'coverage':'native-partial',
            'scheduler':'pure-native-expression-cache' if session.optimized else 'reference'}
