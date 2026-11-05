"""Controlled activation experiment with declared finite training population."""
from pln_chess.common import ROOT,read_json,digest,write_json
from pln_chess.domain import Position,Move,parse_square
from pln_chess.api import find_move
from pln_chess.cycle4.ontology import descriptors,relation
from pln_chess.inference import classify,Options
from pln_chess.pln import TV,UNKNOWN


def experiment(dataset,model,runtime,output=None):
    import chess
    from pln_chess.learning import Model
    from evaluation.experiments import summarize
    legacy=[]
    for name,path in [('C2',ROOT/'artifacts/cycle2/B2-model.json'),('C3',ROOT/'artifacts/cycle3/C3-full-model.json')]:
        old=Model.load(path,runtime)
        for key,h in old.induction.items():
            ctv=runtime.batch([('c',f'(stv 1.0 (Truth_w2c {float(h["counts"]["B"])}))')])['c']
            expression='(Truth_Induction '+' '.join(TV(v,ctv.confidence).metta() for v in h['premises'])+')'
            actual=runtime.batch([('i',expression)])['i'].json()
            assert all(abs(actual[k]-h['truth_value'][k])<1e-12 for k in actual)
            legacy.append({'cycle':name,'hypothesis':key,'counts':h['counts'],'expression':expression,'tv':actual,'parity':True,
                           'evidence_ids':h['evidence_ids'],'dependence_groups':h['dependence_groups']})
    target={'piece':'Rook','motion':'orthogonal','effect':'ordinary','promotion':None,'destination':'Empty','ray_contents':[]}
    groups={}
    for r in dataset['examples']:
        p=Position.from_fen(r['fen']);m=find_move(p,r['move']);o=descriptors(p,m)
        groups.setdefault(r['dependence_group'],[]).append((r,o))
    population=[]
    for group,rows in sorted(groups.items()):
        r,o=next(((r,o) for r,o in rows if o['local_context']==target and o['pattern']['geometry']['distance']==1),rows[0])
        population.append({'group':group,'input':{'fen':r['fen'],'move':r['move']},'A':o['local_context']==target,
                           'B':o['local_context']==target and o['pattern']['geometry']['distance']==1,'C':r['movement_label'],
                           'source':r['source'],'evidence_fingerprint':digest(r)})
    n=len(population);a=sum(r['A'] for r in population);b=sum(r['B'] for r in population);c=sum(r['C'] for r in population)
    ba=sum(r['A'] and r['B'] for r in population);bc=sum(r['B'] and r['C'] for r in population)
    assert 0<a<=n and 0<b<n
    confidence=runtime.batch([('c',f'(stv 1.0 (Truth_w2c {float(b)}))')])['c'].confidence
    inputs=[TV(v,confidence) for v in (a/n,b/n,c/n,ba/b,bc/b)]
    expr='(Truth_Induction '+' '.join(tv.metta() for tv in inputs)+')'
    induced=runtime.batch([('i',expr)])['i']
    conditional=model.hypotheses[relation('LocalAdmissibility',target)['id']]['positive']
    outcomes=[]
    from pln_chess.domain import Piece
    from dataclasses import replace
    for src,dst in [('a2','d2'),('a2','h2'),('g3','b3'),('c1','c6'),('c7','c2')]:
        pieces=(Piece('wk','King','White',(1,0)),Piece('bk','King','Black',(7,7)),Piece('mover','Rook','White',parse_square(src)))
        p=Position(pieces,'White');move=Move(parse_square(src),parse_square(dst));o=descriptors(p,move)
        for control in ('held-out-distance','friendly-destination','wrong-geometry'):
            q=p;m=move
            if control=='friendly-destination':q=replace(p,pieces=p.pieces+(Piece('friendly','Pawn','White',move.end),))
            if control=='wrong-geometry':m=Move(move.start,(move.start[0]+1,move.start[1]+1))
            match=descriptors(q,m)['local_context']==target
            exprs=[('induced',f'(Truth_ModusPonens (stv 1.0 0.99) {induced.metta()})'),
                   ('abstraction',f'(Truth_ModusPonens (stv 1.0 0.99) {TV.from_json(conditional).metta()})')]
            values=runtime.batch(exprs) if match else {'induced':UNKNOWN,'abstraction':UNKNOWN}
            # Sparse direct-only arm has trained distance=1, deliberately no coarse projection.
            direct=UNKNOWN
            label=chess.Board(q.fen()).is_legal(chess.Move.from_uci(m.notation))
            outcomes.append({'fen':q.fen(),'move':m.notation,'control':control,'matched':match,'evaluation_label':label,
                'revision_only_distance_specific':{'tv':direct.json(),'class':classify(direct,Options())},
                'native_induction':{'tv':values['induced'].json(),'class':classify(values['induced'],Options())},
                'manually_seeded_abstraction':{'tv':values['abstraction'].json(),'class':classify(values['abstraction'],Options())}})
    actual=next(h for h in model.hypotheses.values() if h['target']=='LocalAdmissibility' and h['descriptor']==target)
    arm_metrics={}
    for arm in ('revision_only_distance_specific','native_induction','manually_seeded_abstraction'):
        scored=[{'label':r['evaluation_label'],'classification':r[arm]['class']} for r in outcomes]
        arm_metrics[arm]={**summarize(scored,[]),'raw_strength_squared_error':sum((r[arm]['tv']['strength']-int(r['evaluation_label']))**2 for r in outcomes)/len(outcomes),
                          'calibration_scope':'Descriptive raw-strength score on 15 synthetic probes; confidence is not treated as probability and no calibrator is fitted here.'}
    result={'legacy_reproduction':legacy,'legacy_diagnosis':read_json(ROOT/'artifacts/cycle3/induction.json')['diagnosis'],
        'population':population,'sampling':'One observation per source group, preferentially the declared rook distance-one stratum, otherwise first ledger row. This is stratified selection, not a random chess population.',
        'counts':{'N':n,'A':a,'B':b,'C':c,'BA':ba,'BC':bc},'marginals':[tv.json() for tv in inputs],
        'native_expression':expr,'native_truth_value':induced.json(),'runtime':runtime.manifest,
        'tasks':outcomes,'arm_metrics':arm_metrics,'production_direct_hypothesis':actual,
        'diagnosis':{'a_no_rule':False,'b_never_matched':False,'c_low_confidence':classify(induced,Options())!='supported',
            'd_suppressed':actual['positive']['confidence']>induced.confidence,'e_redundant_representation':True},
        'interpretation':'Native induction activates a deliberately withheld coarse conditional in the distance-specific control. The same generalization is already available through explicit host abstraction and native revision; no unique production benefit is established.',
        'production':'Experimental only, disabled. The C4-full and no-induction production configurations are identical in semantics.',
        'calibration':'Too few synthetic control cases for calibrated probabilities; raw strength/confidence reported separately. Production validation calibration is in calibration.json.'}
    if output:write_json(output,result)
    return result
