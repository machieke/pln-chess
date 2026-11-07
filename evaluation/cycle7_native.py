"""Bounded pinned-rule laboratory. No operator definitions or Python TV formulas."""
import re
from pathlib import Path
from pln_chess.common import ROOT, digest, write_json
from pln_chess.pln import Runtime, TV
from evaluation.cycle6_native import DIRECT, forms

DOMAINS = {
 'mp': 'Two STVs in [0,1]^2; native MP maps valid inputs to valid STVs; zero premise confidence gives zero output confidence.',
 'deduction': 'Five STVs; positive P,Q strengths and conditional-probability-consistency guards. Guard failure returns (stv 1 0); Q strength >.9999 uses R strength.',
 'induction': 'Five STVs; A strength>0, 0<B strength<1; returned strength must also lie in [0,1]. Native formula does not validate consistency or provenance.',
 'abduction': 'Five STVs; 0<B strength<1; returned strength must lie in [0,1]. Native formula does not validate consistency or provenance.',
 'revision': 'Two STVs; confidences in [0,1), at least one positive. Both zero or either one invokes empty safe division; no usable STV.',
 'negation': 'One STV in [0,1]^2; confidence preserved, involutive strength complement.',
 'inversion': 'Two STVs in [0,1]^2; uses B confidence, supplied link strength/confidence and native .6 penalty.',
 'equivalence': 'Three STVs; A strength>0 unless high-equivalence shortcut applies; output strength must lie in [0,1]. No unconditional domain validation.',
 'similarity': 'Five STVs; positive marginal strengths, all native division denominators nonzero, resulting strength in [0,1]. No blanket totality claim.',
 'evaluation': 'Five STVs; simpleDeductionStrength consistency guards and nonzero safe-division denominators; invalid case returns empty.',
 'symmetric-mp': 'Two STVs in [0,1]^2. Native hard-coded alternate conditional .2 is a model assumption; output lies in [0,1].',
 'choice': 'Tuple of (STV evidence) pairs; picks greatest confidence, first wins ties; empty tuple or all-zero confidence gives (). No fusion.',
}

class Recorder(Runtime):
    def __init__(self):
        self.transcripts=[]
        super().__init__(timeout=120)
    def execute(self, body):
        raw=super().execute(body)
        self.transcripts.append({'body':body,'stdout':raw})
        return raw

def probe(rt, name, expression, preamble=''):
    raw=rt.execute(preamble+'\n!(println! (C7PROBE '+name+' '+expression+'))')
    line=next(x for x in raw.splitlines() if x.startswith('(C7PROBE '+name+' '))
    return {'id':name,'expression':expression,'preamble':preamble,'stdout':raw,'result':line,
        'stvs':[{'strength':float(s),'confidence':float(c)} for s,c in re.findall(r'\(stv ([\d.eE+-]+) ([\d.eE+-]+)\)',line)]}

def inventory(rt):
    definitions=forms(rt.library.read_text())
    production='\n'.join(p.read_text() for p in (ROOT/'src').rglob('*.py'))
    records=[]
    for name, expr in DIRECT.items():
        rec=probe(rt,name,expr)
        assert len(rec['stvs'])==1
        TV.from_json(rec['stvs'][0])
        symbol=next(d['symbol'] for d in definitions if d['symbol'].startswith('Truth_') and '('+d['symbol']+' ' in expr) if name!='choice' else 'BestConfidenceCandidate'
        records.append({**rec,'source':[d for d in definitions if d['symbol']==symbol],
            'domain':DOMAINS[name],'source_present':True,'runtime_executable':True,'production_integrated':symbol in production})
    pre='\n'.join('(= (STV '+x+') (stv 0.4 0.8))' for x in ('A','B','C'))
    wrappers={
      'inheritance-deduction':'(collapse (|- ((Inheritance A B) (stv 0.9 0.8)) ((Inheritance B C) (stv 0.8 0.8))))',
      'inheritance-predicate':'(collapse (|- ((Evaluation (Predicate Eligible) (List (Concept B))) (stv 0.9 0.8)) ((Inheritance (Concept A) (Concept B)) (stv 0.95 0.8))))',
      'equivalence-wrapper':'(collapse (|- ((Equivalence A B) (stv 0.5 0.8))))',
      'unary-chain':'(collapse (let ($p $tv) (|- (A (stv 0.9 0.8)) ((Implication A B) (stv 0.95 0.8))) (|- ($p $tv) ((Implication B C) (stv 0.95 0.8)))))',
      'negative-wrapper':'(collapse (|- ((Not A) (stv 0.9 0.8))))',
      'revision-zero':'(collapse (Truth_Revision (stv 0.5 0.0) (stv 0.5 0.0)))',
      'revision-one':'(collapse (Truth_Revision (stv 1.0 1.0) (stv 1.0 0.5)))',
      'mp-zero':'(Truth_ModusPonens (stv 1.0 0.0) (stv 1.0 1.0))',
      'mp-one':'(Truth_ModusPonens (stv 1.0 1.0) (stv 1.0 1.0))',
      'choice-zero':'(BestConfidenceCandidate (((stv 1.0 0.0) (a)) ((stv 0.0 0.0) (b))))',
      'choice-tie':'(BestConfidenceCandidate (((stv 0.9 0.8) (a)) ((stv 0.1 0.8) (b))))',
      'symmetric-zero-strength':'(Truth_SymmetricModusPonens (stv 0.0 0.8) (stv 1.0 0.8))',
      'stamp-shared':'(StampDisjoint (a shared) (b shared))',
      'stamp-independent':'(StampDisjoint (a) (b))',
    }
    extra=[]
    for k,v in wrappers.items():
        record=probe(rt,k,v,pre)
        extra.append({**record,'source':[d for d in definitions if d['symbol'] in ('|-','StampDisjoint','BestConfidenceCandidate') or '('+d['symbol']+' ' in v],
            'source_present':True,'runtime_result_kind':'STV-returned' if record['stvs'] else 'empty' if record['result'].endswith(' ())') else 'non-STV-result',
            'production_integrated':False,'scope':'Exact wrapper/control probe; do not generalize a failing probe to every possible signature.'})
    return {'operators':records,'signature_and_edge_cases':extra,'native_definitions':definitions,
        'interpretation':'Native wrappers require exact Concept/Predicate/List types. Source-present predicate substitution returns empty in these exact runtime probes; source presence is not executable capability. All domains follow the pinned definitions; finite probes are not a proof of totality.'}

def learned_premises(rt):
    # Real relative board observations; the occupancy corpus contains no knight.
    from training.cycle5 import fixture
    from pln_chess.domain import Position
    from pln_chess.api import find_move
    from pln_chess.cycle5.ontology import descriptors
    import chess
    ledger=[];learned={}
    for family,kind,src,dst,occupancy in [('A',chess.KNIGHT,'d4','e6','Empty'),('B',chess.ROOK,'d4','d5','Opponent')]:
        tv=TV(.5,.05)
        for index in range(4):
            # Independent supervision sessions; repeated relative feature, unique source groups.
            a,b=[('d4','e6'),('c3','d5'),('e3','f5'),('b4','c6')][index] if family=='A' else [('d4','d5'),('c3','c4'),('e3','e4'),('b4','b5')][index]
            board=fixture(kind,a,b,occupancy);p=Position.from_fen(board.fen());m=find_move(p,a+b)
            before=tv;expr=f'(Truth_Revision {tv.metta()} (stv 1.0 0.5))';tv=rt.batch([('learn',expr)])['learn']
            row={'family':family,'fen':board.fen(),'move':a+b,'descriptor':descriptors(p,m),
                'source_group':f'C7-micro-{family}-{index}','observation':'knight relative (1,2) geometry' if family=='A' else 'opponent occupancy eligibility, independently supervised',
                'label':True,'prior':before.json(),'expression':expr,'output':tv.json()}
            row['evidence_id']=digest(row);ledger.append(row)
        learned[family]=tv
    a={r['source_group'] for r in ledger if r['family']=='A'};b={r['source_group'] for r in ledger if r['family']=='B'}
    assert not a&b
    return learned,ledger

def laboratory(rt):
    learned,ledger=learned_premises(rt);a,b=[learned[x].metta() for x in ('A','B')]
    conflict=rt.batch([('conflict',f'(Truth_Revision {b} (stv 0.0 0.8))')])['conflict'].metta()
    rule='(stv 0.95 0.8)';records=[]
    control_evidence={name:{'evidence_id':digest(['C7-control',name,tv]),'truth_value':tv,'origin':'supplied mechanism/control assumption, not learned joint evidence'}
        for name,tv in [('supplied-rule',{'strength':.95,'confidence':.8}),('negative-B',{'strength':0.,'confidence':.8}),('host-joint-sensor',learned['A'].json())]}
    # Exactly three encodings. Controls within an encoding are not new searches.
    encodings=[
      {'id':'nested-implication','rationale':'Existing MP can eliminate a supplied curried conditional; test whether independent facts alone provide it.',
       'missing_capability':'No rule introduces or learns A -> (B -> Eligible) from the two independent marginal curricula.',
       'origin':'supplied conditional axiom; not a learned joint theorem'},
      {'id':'product-antecedent','rationale':'An explicit product/And antecedent might be constructed by native matching; test independent inputs and host-built sensor control.',
       'missing_capability':'No pinned introduction rule constructs the joint antecedent.',
       'origin':'host-built product in positive mechanism control only'},
      {'id':'conditional-inheritance','rationale':'Typed predicate inheritance is source-present; test its exact runtime signature and whether independently learned geometry/occupancy shares a type.',
       'missing_capability':'No native rule identifies KnightStep with OpponentDestination or intersects these types.',
       'origin':'typed unary substitution; any successful type alignment is an extra supplied relation'},
    ]
    for enc in encodings:
        tests={}
        for variant,aa,bb in [('A-only',a,'(stv 0.5 0.0)'),('B-only','(stv 0.5 0.0)',b),('A+B',a,b),('negative-B',a,'(stv 0.0 0.8)'),('delete-A','(stv 0.5 0.0)',b),('delete-B',a,'(stv 0.5 0.0)'),('reverse',b,a),('contradict-B',a,conflict)]:
            if enc['id']=='nested-implication':
                expr=f'(collapse (let ($p $tv) (|- (A {aa}) ((Implication A (Implication B Eligible)) {rule})) (|- (B {bb}) ($p $tv))))'
            elif enc['id']=='product-antecedent':
                expr=f'(collapse (let ($p $tv) (|- (A {aa}) (B {bb})) (|- ($p $tv) ((Implication (Product A B) Eligible) {rule}))))'
            else:
                expr=f'(collapse (|- ((Inheritance (Concept Candidate) (Concept KnightStep)) {aa}) ((Evaluation (Predicate Eligible) (List (Concept OpponentDestination))) {bb})))'
            tests[variant]=expr
        if enc['id']=='nested-implication':
            tests['no-supplied-conditional']=f'(collapse (|- (A {a}) (B {b})))'
            tests['premise-reversal']=f'(collapse (let ($p $tv) (|- (B {b}) ((Implication A (Implication B Eligible)) {rule})) (|- (A {a}) ($p $tv))))'
        elif enc['id']=='product-antecedent':
            tests['host-joint-control']=f'(collapse (|- ((Product A B) {a}) ((Implication (Product A B) Eligible) {rule})))'
            tests['explicit-And-antecedent']=f'(collapse (|- (A {a}) ((Implication (And A B) Eligible) {rule})))'
            tests['premise-reversal']=f'(collapse (|- (B {b}) (A {a})))'
        else:
            tests['aligned-type-control']=f'(collapse (|- ((Evaluation (Predicate Eligible) (List (Concept KnightStep))) {b}) ((Inheritance (Concept Candidate) (Concept KnightStep)) {a})))'
            tests['premise-reversal']=f'(collapse (|- ((Evaluation (Predicate Eligible) (List (Concept OpponentDestination))) {b}) ((Inheritance (Concept Candidate) (Concept KnightStep)) {a})))'
        tests['correlated-duplicate']=f'(collapse (if (StampDisjoint (A shared) (B shared)) {tests["A+B"]} (empty)))'
        tests['duplicate-revision-unguarded']=f'(Truth_Revision {a} {a})'
        tests['duplicate-revision-guarded']=f'(collapse (if (StampDisjoint (A) (A)) (Truth_Revision {a} {a}) (empty)))'
        for variant,expr in tests.items():
            rec=probe(rt,enc['id']+'-'+variant,expr)
            families={'A','B'}
            if variant in ('A-only','delete-B','negative-B'):families.discard('B')
            if variant in ('B-only','delete-A'):families.discard('A')
            if variant.startswith('duplicate-revision'):families={'A'}
            ids=[r['evidence_id'] for r in ledger if r['family'] in families]
            if variant in ('negative-B','contradict-B'):ids.append(control_evidence['negative-B']['evidence_id'])
            if '(Implication ' in expr:
                ids.append(control_evidence['supplied-rule']['evidence_id'])
            if variant=='host-joint-control':ids=[control_evidence[x]['evidence_id'] for x in ('host-joint-sensor','supplied-rule')]
            records.append({**rec,'encoding':enc['id'],'condition':variant,
                'input_evidence_ids':ids,'dependency_ids':ids if rec['stvs'] else [],
                'dependency_kind':'Harness maps explicit input IDs; native-carried dependency stamps are independently tested by PLN.Query below.',
                'joint_origin':enc['origin'],'strict_success':False})
    # Native scheduler stamp outputs expose dependency provenance independently
    # of the Python diagnostic IDs; fixed step bound is recorded in the query.
    scheduler=[]
    for condition,kb in [
        ('independent-only',f'(Sentence (A {a}) (learn-A)) (Sentence (B {b}) (learn-B))'),
        ('supplied-nested',f'(Sentence (A {a}) (learn-A)) (Sentence (B {b}) (learn-B)) (Sentence ((Implication A (Implication B Eligible)) {rule}) (supplied-rule))'),
        ('deleted-A',f'(Sentence (B {b}) (learn-B)) (Sentence ((Implication A (Implication B Eligible)) {rule}) (supplied-rule))'),
        ('deleted-B',f'(Sentence (A {a}) (learn-A)) (Sentence ((Implication A (Implication B Eligible)) {rule}) (supplied-rule))'),
        ('shared-stamp',f'(Sentence (A {a}) (shared)) (Sentence (B {b}) (shared)) (Sentence ((Implication A (Implication B Eligible)) {rule}) (supplied-rule))')]:
        scheduler.append(probe(rt,'scheduler-'+condition,f'(PLN.Query ({kb}) Eligible 12 30 60)'))
    assert len(encodings)==3
    return {'experiment_budget':3,'encodings':encodings,'training':ledger,'training_groups_disjoint':True,
        'combined_training_examples':0,'heldout':{'fen':'2bk3K/8/5N2/7n/8/2B5/8/8 w - - 0 1','move':'f6h5','combined_configuration':'knight relative capture + opponent destination'},
        'records':records,'control_evidence':control_evidence,'native_scheduler_dependency_controls':scheduler,
        'native_stamp_map':{**{'learn-'+family:[r['evidence_id'] for r in ledger if r['family']==family] for family in ('A','B')},
            'supplied-rule':[control_evidence['supplied-rule']['evidence_id']],'shared':'Adversarial common-ancestor stamp assigned to both learned inputs for the correlation control.'},
        'native_positive_composition':'not demonstrated',
        'sampling_assumption':'A/B groups are disjoint synthetic supervision sessions. Their generated marginal examples are not a claim of empirical IID sampling; explicit shared-stamp controls test known dependence.',
        'stopped_after_budget':True,'additional_rook_and_pawn_witnesses':'Not attempted: primary witness failed; no additional encodings searched.',
        'limitation':'Nested MP depends on both input TVs but the required relation to Eligible is supplied, not learned or introduced from independent curricula. The host Product sensor control succeeds but cannot meet the research gate; even the aligned unary type control returns empty in this pinned runtime.'}

def run(out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True);rt=Recorder()
    inv=inventory(rt);lab=laboratory(rt)
    write_json(out/'inventory.json',{'runtime':rt.manifest,**inv});write_json(out/'laboratory.json',lab)
    write_json(out/'transcripts.json',rt.transcripts)
    for index,t in enumerate(rt.transcripts):
        (out/f'witness-{index:03}.metta').write_text('!(import! &self "'+str(rt.library)+'")\n'+t['body']+'\n')
    return lab

if __name__=='__main__':
    import sys
    run(sys.argv[1])
