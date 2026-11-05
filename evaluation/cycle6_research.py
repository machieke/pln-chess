"""Causal regressions, disjoint primitive curricula, temporal and locality audits."""
import copy,re,tempfile
from dataclasses import replace,asdict
from pathlib import Path
import chess
from pln_chess.common import ROOT,read_json,write_json,digest
from pln_chess.pln import TV,UNKNOWN
from pln_chess.learning import Model,PRIOR
from pln_chess.domain import Position,Piece,Move
from pln_chess.api import explain_move,find_move
from pln_chess.cycle6.inference import Cycle6Options
from pln_chess.cycle6.history import inspect
from pln_chess.cycle5.model import train
from pln_chess.cycle5.ontology import descriptors
from evaluation.cycle3 import read_gzip
from scripts.cycle4_baseline import pack
from training.cycle5 import fixture,payload
from training.cycle4 import enrich4

def curriculum(data,model,runtime,out):
    rows=[]
    def add(family,board,move,supervised):
        row=enrich4({'fen':board.fen(),'move':move,'label':chess.Move.from_uci(move) in board.legal_moves,
                     'source':'C6-primitive-'+family,'dependence_group':'C6-primitive-'+family,'split':'train','confidence':.5})
        row['geometry_label']=True;rows.append({**row,'supervised_families':supervised})
    geometry=[(chess.KNIGHT,'d4','e6','Empty'),(chess.ROOK,'c3','c4','Friendly'),(chess.BISHOP,'d3','e4','Friendly'),
              (chess.QUEEN,'c3','c4','Empty'),(chess.PAWN,'d4','e5','Friendly'),(chess.PAWN,'d4','d5','Friendly'),(chess.KING,'d3','e4','Friendly')]
    for i,(kind,a,b,d) in enumerate(geometry):add('geometry-'+str(i),fixture(kind,a,b,d),a+b,['geometry'])
    for d in ('Empty','Opponent','Friendly'):add('destination-'+d,fixture(chess.PAWN,'d3','d5',d),'d3d5',['destination','boundary'])
    for kind in (chess.ROOK,chess.BISHOP,chess.QUEEN):
        a,b,cell=('d4','f6','e5') if kind==chess.BISHOP else ('d4','f4','e4')
        for d in ('Friendly','Opponent'):add(f'ray-{kind}-{d}',fixture(kind,a,b,'Friendly',(cell,d)),a+b,['ray'])
    test_keys={t['descriptor']['abstract_combination'] for t in data['factorial_tasks']}
    examples=[payload(r,runtime,r['supervised_families']) for r in rows]
    overlaps=sorted({p['abstract_combination'] for p in examples}&test_keys)
    assert not overlaps,[(r["source"],p["abstract_combination"]) for r,p in zip(rows,examples) if p["abstract_combination"] in overlaps]
    bridge=model.source_model().base_model();bridge.hypotheses={k:v for k,v in bridge.hypotheses.items() if v['target']=='Bridge'}
    with tempfile.TemporaryDirectory() as tmp:isolated=train(examples,bridge,runtime,Path(tmp)/'evidence.jsonl')
    isolated.export(out/'model/C6-factorial-primitives.json')
    write_json(out/'factorial-curriculum.json',{'rows':rows,'evidence':examples,'model_version':isolated.version,
        'abstract_combination_overlap':overlaps,'train_groups':sorted({p['dependence_group'] for p in examples}),
        'joint_targets':0,'scope':'Actual board supervision for geometry/destination/ray/boundary; temporal and attack exposure are evaluated as missing families, not invented learned primitive rules.'})
    return isolated

def factorial(data,model,runtime,out):
    isolated=curriculum(data,model,runtime,out);results=[];controls=[]
    for t in data['factorial_tasks']:
        fields=dict(t['position']);fields['pieces']=tuple(Piece(**{**p,'square':tuple(p['square'])}) for p in fields['pieces']);fields['unknown_squares']=tuple(map(tuple,fields['unknown_squares']));fields['ep']=tuple(fields['ep']) if fields['ep'] else None
        p=Position(**fields);m=Move(**{**t['move_object'],'start':tuple(t['move_object']['start']),'end':tuple(t['move_object']['end'])})
        operational=explain_move(p,m,model,Cycle6Options(mode='operational'),runtime)['candidate']
        primitive=explain_move(p,m,isolated,runtime=runtime)['candidate']
        results.append({'id':t['id'],'base_id':t['base_id'],'family':t['family'],'variant':t['variant'],'fen':t['fen'],'move':t['move'],'oracle_legal':t['label'],
            'operational':operational,'independent_primitive_model':primitive,
            'native_composed':False,'native_conditional_transfer':[x['id'] for x in primitive['typed_premises'] if x['status']=='learned-native-conditional'],
            'host_joint_category':operational['legacy_projection'],'combination_absent_from_primitive_training':True})
        if t['variant']!='original':continue
        by={x['family']:x for x in primitive['typed_premises'] if x['status']=='learned-native-conditional'}
        for variant in ('both','missing-A','missing-B','uncertain-B','contradictory-B','overlap','swapped','renamed'):
            aa=TV.from_json(by.get('geometry',{}).get('truth_value',UNKNOWN.json()));bb=TV.from_json(by.get('destination',{}).get('truth_value',UNKNOWN.json()))
            # Raw independent properties retain their actual polarity. No host
            # multiplication, renaming of predicates into conjunction, or C rule.
            if variant=='missing-A':aa=UNKNOWN
            if variant in ('missing-B','uncertain-B'):bb=TV(bb.strength,0 if variant=='missing-B' else .05)
            if variant=='contradictory-B':bb=runtime.batch([('n',f'(Truth_Negation {bb.metta()})')])['n']
            left,right=('B','A') if variant=='swapped' else ('X','Y') if variant=='renamed' else ('A','B')
            expr=f'(collapse (|- ({left} {aa.metta()}) ({right} {bb.metta()})))'
            if variant=='overlap':expr=f'(collapse (if (StampDisjoint (a shared) (b shared)) (|- (A {aa.metta()}) (B {bb.metta()})) (empty)))'
            raw=runtime.execute(f'!(println! (CONTROL {expr}))');assert '(CONTROL ())' in raw
            controls.append({'case':t['id'],'variant':variant,'expression':expr,'stdout':raw,'raw_stvs':[aa.json(),bb.json()],
                'independence_groups':{k:v['dependence_groups'] for k,v in by.items()},'conclusion':'unknown; native composition not achieved'})
    pack(out/'factorial.json.xz',{'tasks':results,'controls':controls,'native_composition_achieved':False,
        'families_without_isolated_learned_primitives':['temporal history','attack exposure'],
        'limitation':'These families have structural/external observations and operational C4 chains, but no new jointly learned positive native theorem.'})
    locality=[]
    for item in results:
        base=next(r for r in results if r['base_id']==item['base_id'] and r['variant']=='original')
        def primitive_map(c):return {r['id']:r['truth_value'] for r in c['typed_premises']}
        a,b=base['operational'],item['operational']
        locality.append({'id':item['id'],'variant':item['variant'],'primitive_keys_and_tvs_equal':primitive_map(a)==primitive_map(b),
            'C4_local_descriptor_equal':a['observations']['local_context']==b['observations']['local_context'],
            'global_classification_equal':a['classification']==b['classification'],'global_tv_equal':a['raw_stv']==b['raw_stv'],
            'before':{'class':a['classification'],'raw_stv':a['raw_stv']},'after':{'class':b['classification'],'raw_stv':b['raw_stv']},
            'scope':'Local rule invariance is distinct from globally relevant king-exposure changes.'})
    inspected=[]
    for name,hyp in [('C4',model.source_model().base_model().hypotheses),('C5',model.hypotheses)]:
        for key,h in hyp.items():
            desc=h.get('descriptor');text=__import__('json').dumps(desc,sort_keys=True)
            inspected.append({'model':name,'id':key,'target':h['target'],'descriptor':desc,'absolute_square_tokens':re.findall(r'"[a-h][1-8]"',text),
                'position_or_global_keys':[x for x in ('position_id','postmove_opponents','opponent_frames','full_board','fen') if x in text],
                'scope':'global learned attack frame' if h['target']=='Attack' else 'historical/boundary context' if any(k in text for k in ('castle','ep_offset','edge_distance')) else 'local primitive or joint category'})
    write_json(out/'locality.json',{'hypotheses':inspected,'transforms':locality,'counterexamples':[r for r in locality if not all(r[k] for k in ('primitive_keys_and_tvs_equal','C4_local_descriptor_equal','global_classification_equal','global_tv_equal'))],
        'absolute_key_findings':[r for r in inspected if r['absolute_square_tokens'] or r['position_or_global_keys']]})
    return results

def regressions(model,runtime,out):
    from pln_chess.cycle6.inference import infer_moves,Session
    sessions={}
    def explain(fen,move,options):
        key=digest(asdict(options));session=sessions.setdefault(key,Session(runtime));position=Position.from_fen(fen)
        result=infer_moves(position,model,options,runtime,[find_move(position,move)],session)
        return result['candidates'][0]
    historical=read_gzip(ROOT/'artifacts/cycle5/proofs/original-49-errors.json.xz');a=[]
    for r in historical:
        c=explain(r['fen'],r['move'],Cycle6Options(mode='operational'))
        removed=explain(r['fen'],r['move'],Cycle6Options(mode='operational',suppress_families=('ray','boundary','destination','exposure')))
        a.append({'fen':r['fen'],'move':r['move'],'C2_C5_transition':r['transition'],'C6':c,'removed_families':['ray','boundary','destination','exposure'],'without':removed})
    pack(out/'proofs/original-49.json.xz',a);assert len(a)==49 and all(r['C6']['classification']=='supported-illegal' for r in a)
    old=read_gzip(ROOT/'artifacts/cycle5/proofs/new-negative-counterfactuals.json.xz');b=[]
    for r in old:
        row=r['row'];c=explain(row['fen'],row['move'],Cycle6Options(mode='operational'))
        removed=explain(row['fen'],row['move'],Cycle6Options(mode='operational',suppress_families=tuple(r['removed_families'])))
        b.append({'split':r['split'],'fixture':row['fixture'],'fen':row['fen'],'move':row['move'],'oracle_legal':row['label'],'C6':c,'removed_families':r['removed_families'],'without':removed,
            'C5_proof_parity':c['proof_trace']==r['native_proof']['proof_trace']})
    pack(out/'proofs/new-238.json.xz',b)
    assert len(b)==238 and all(r['C6']['classification']=='supported-illegal' and r['without']['classification']=='unknown' and not r['oracle_legal'] and r['C5_proof_parity'] for r in b)
    summary={'historical_count':len(a),'historical_preserved':sum(r['C6']['classification']=='supported-illegal' for r in a),'historical_removal_changes':sum(r['without']['classification']!='supported-illegal' for r in a),
        'new_count':len(b),'new_preserved':sum(r['C6']['classification']=='supported-illegal' for r in b),'new_removal_changes':sum(r['without']['classification']=='unknown' for r in b),'new_proof_parity':all(r['C5_proof_parity'] for r in b),'false_illegal':0}
    write_json(out/'negative-regressions.json',summary);return summary

def temporal(runtime,out):
    cases=[]
    starts=[('double-step','7k/1p6/8/2P5/8/8/8/2K5 b - - 0 1',['b7b5']),
        ('rook-right','6k1/8/8/8/8/8/8/4K2R w K - 0 1',['h1h2']),
        ('king-right','6k1/8/8/8/8/8/8/4K2R w K - 0 1',['e1e2']),
        ('castle','6k1/8/8/8/8/8/8/4K2R w K - 0 1',['e1g1']),
        ('promotion','7k/P7/8/8/8/8/8/2K5 w - - 0 1',['a7a8q']),
        ('capture-right','4k2r/8/8/8/8/8/8/4K2R b Kk - 0 1',['h8h1']),
        ('en-passant','7k/8/8/1pP5/8/8/8/2K5 w - b6 0 1',['c5b6'])]
    for name,fen,moves in starts:
        p=Position.from_fen(fen)
        for m in moves:p=p.successor(find_move(p,m))
        e={'initial_fen':fen,'moves':moves,'source':'C6-observed-events-'+name,'confidence':.99,'castling_history_attested':True}
        cases.append({'id':name,'modes':{mode:inspect(p,mode,None if mode=='unknown' else e) for mode in ('unknown','trusted-fen','observed-events')},
            'contradictory':inspect(fen,'observed-events',e),'incomplete':inspect(fen,'observed-events',{**e,'moves':[]}),
            'rights_edit_conflict':inspect(replace(p,rights='K' if p.rights=='-' else '-'),'observed-events',e)})
    assert all(c['modes']['observed-events']['status']=='structurally-consistent' and c['contradictory']['status']=='conflicting' and c['rights_edit_conflict']['status']=='conflicting' for c in cases)
    write_json(out/'temporal.json',{'cases':cases,'no_legal_play_theorem':True})

def induction(data,model,runtime,out):
    from evaluation.cycle5_research import induction as previous
    olddata=read_json(ROOT/'artifacts/cycle5/datasets/dataset.json');base=previous(olddata,runtime,model.source_model());arms=[]
    for h in base['rules']:
        for name,inputs in [('enabled',h['inputs']),('disabled',[UNKNOWN.json()]*5),('sham',h['inputs']),
            ('marginal-half',[{**v,'strength':v['strength']*.5} if i<3 else v for i,v in enumerate(h['inputs'])]),
            ('marginal-confidence-zero',[{**v,'confidence':0} if i<3 else v for i,v in enumerate(h['inputs'])])]:
            expr='(Truth_Induction '+' '.join(TV.from_json(v).metta() for v in inputs)+')'
            raw=runtime.execute(f'!(println! (INDUCTION {expr}))')
            arms.append({'rule':h['id'],'arm':name,'expression':expr,'stdout':raw,'evidence_ids':h['evidence_ids'],'dependence_groups':h['dependence_groups']})
        expr=f'(collapse (if (StampDisjoint (population source) (source application)) (Truth_Revision {TV.from_json(h["truth_value"]).metta()} {TV.from_json(h["truth_value"]).metta()}) (empty)))'
        raw=runtime.execute(f'!(println! (INDUCTION {expr}))');assert '(INDUCTION ())' in raw
        arms.append({'rule':h['id'],'arm':'dependence-overlap','expression':expr,'stdout':raw})
    transfer=[]
    for task in data['factorial_tasks']:
        if task['variant']!='original':continue
        h=next((r for r in base['rules'] if r['descriptor']==next(x['descriptor'] for x in task['descriptor']['typed_relations'] if x['family']=='geometry')),None)
        c=explain_move(task['fen'],task['move'],model,Cycle6Options(mode='operational'),runtime)['candidate']
        expr=f'(Truth_ModusPonens (stv 1.0 0.99) {TV.from_json(h["truth_value"]).metta() if h else UNKNOWN.metta()})';tv=runtime.batch([('a',expr)])['a']
        transfer.append({'case':task['id'],'matching_rule':h['id'] if h else None,'native_expression':expr,'output':tv.json(),'global_before':c['classification'],'global_after':c['classification'],
            'reason':'Candidate rule concerns geometry only; no defensible global rule injection or classification gain.','global_proof_refs':[digest(n) for n in c['proof_trace']]})
    write_json(out/'induction.json',{'C5_reexecuted':base,'ablations':arms,'unseen_combinations':transfer,'global_classification_changes':0,'enabled_in_operational':False,
        'C2_C4_audit':'Existing C2-C4 probes reexecuted by native audit; measured-population assumptions and C4 zero-confidence marginal caveat remain visible.'})

def research(data,model,runtime,out):
    out=Path(out)
    from evaluation.cycle6_native import audit
    audit(out/'native-probes');print('NATIVE COMPLETE',flush=True)
    factorial(data,model,runtime,out);print('FACTORIAL COMPLETE',flush=True)
    regressions(model,runtime,out);print('REGRESSIONS COMPLETE',flush=True)
    temporal(runtime,out);print('TEMPORAL COMPLETE',flush=True)
    induction(data,model,runtime,out);print('INDUCTION COMPLETE',flush=True)
    examples(model,runtime,out);print('EXAMPLES COMPLETE',flush=True)

def conflicting_model(model,runtime):
    """Isolated synthetic counterevidence; never exported as production beliefs."""
    from pln_chess.cycle5.ontology import relation
    m=copy.deepcopy(model);rel=relation('ray',{'piece':'Rook','effect':'ordinary','occupancy':'Empty'},'RayObstruction')
    # Learn the deliberately contradictory antecedent through native revision.
    # This tests opposing scopes, not a claim that an empty ray is obstructed.
    positive=PRIOR;negative=PRIOR;ids=[];groups=[]
    for i in range(3):
        values=runtime.batch([('p',f'(Truth_Revision {positive.metta()} (stv 1.0 0.8))'),('n',f'(Truth_Revision {negative.metta()} (stv 0.0 0.8))')])
        positive,negative=values['p'],values['n'];ids.append(digest(['contradictory-lab',i]));groups.append('contradictory-lab-'+str(i))
    m.source['hypotheses'][rel['id']]={**rel,'positive':positive.json(),'negative':negative.json(),'evidence_ids':ids,'dependence_groups':groups,'supporting_evidence':ids,'contradicting_evidence':[]}
    return m

def examples(model,runtime,out):
    cases=[('rook-obstruction','7k/8/8/8/8/8/2RP4/2K5 w - - 0 1','c2h2'),
           ('king-into-attack','3r3k/8/8/8/8/8/2K5/8 w - - 0 1','c2d3'),
           ('unresolved-knight','2bk3K/8/5N2/7n/8/2B5/8/8 w - - 0 1','f6h5'),
           ('unverified-castle','6k1/8/8/8/8/8/8/4K2R w K - 0 1','e1g1'),
           ('operational-positive','7k/8/8/8/8/8/2R5/2K5 w - - 0 1','c2e2')]
    rows=[]
    for name,fen,move in cases:
        rows.append({'id':name,'fen':fen,'move':move,'C4':explain_move(fen,move,model.source_model().base_model(),runtime=runtime),
            'C5':explain_move(fen,move,model.source_model(),runtime=runtime),'C6':{mode:explain_move(fen,move,model,runtime=runtime,mode=mode) for mode in ('operational','strict','experimental')}})
    changed=conflicting_model(model,runtime);fen=cases[-1][1];move=cases[-1][2]
    rows.append({'id':'contradictory-evidence','fen':fen,'move':move,'scope':'Synthetic separately learned ray counterevidence; isolated, never part of operational checkpoint.',
        'model_version':changed.version,'C6':{mode:explain_move(fen,move,changed,runtime=runtime,mode=mode) for mode in ('operational','strict','experimental')}})
    pack(Path(out)/'proofs/examples.json.xz',rows)
    return rows
