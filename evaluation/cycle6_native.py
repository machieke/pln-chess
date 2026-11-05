"""Existing-operator inventory and independent-premise counterfactual laboratory."""
import re,subprocess
from pathlib import Path
from pln_chess.common import ROOT,digest,write_json
from pln_chess.pln import Runtime,TV
from evaluation.cycle5_native import audit as old_audit

DIRECT={
 'mp':'(Truth_ModusPonens (stv 0.9 0.8) (stv 0.95 0.8))',
 'deduction':'(Truth_Deduction (stv 0.2 0.8) (stv 0.4 0.8) (stv 0.5 0.8) (stv 0.9 0.8) (stv 0.8 0.8))',
 'induction':'(Truth_Induction (stv 0.2 0.8) (stv 0.1 0.8) (stv 0.5 0.8) (stv 1.0 0.8) (stv 0.8 0.8))',
 'abduction':'(Truth_Abduction (stv 0.2 0.8) (stv 0.4 0.8) (stv 0.3 0.8) (stv 0.8 0.8) (stv 0.7 0.8))',
 'revision':'(Truth_Revision (stv 1.0 0.8) (stv 0.0 0.8))',
 'negation':'(Truth_Negation (stv 0.9 0.8))',
 'inversion':'(Truth_inversion (stv 0.4 0.8) (stv 0.9 0.8))',
 'equivalence':'(Truth_equivalenceToImplication (stv 0.2 0.8) (stv 0.4 0.8) (stv 0.5 0.8))',
 'similarity':'(Truth_transitiveSimilarity (stv 0.4 0.8) (stv 0.4 0.8) (stv 0.4 0.8) (stv 0.7 0.8) (stv 0.7 0.8))',
 'evaluation':'(Truth_evaluationImplication (stv 0.4 0.8) (stv 0.2 0.8) (stv 0.5 0.8) (stv 0.9 0.8) (stv 0.8 0.8))',
 'symmetric-mp':'(Truth_SymmetricModusPonens (stv 0.9 0.8) (stv 0.95 0.8))',
 'choice':'(let ($tv $e) (BestConfidenceCandidate (((stv 0.9 0.7) (sourceA)) ((stv 0.1 0.8) (sourceB)))) $tv)'
}

def forms(source):
    lines=source.splitlines();out=[];start=None;depth=0;buf=[]
    for i,line in enumerate(lines,1):
        code=line.split(';',1)[0]
        if start is None and code.lstrip().startswith('(= ('):
            start=i;buf=[];depth=0
        if start is not None:
            buf.append(line);depth+=code.count('(')-code.count(')')
            if depth==0:
                raw='\n'.join(buf);symbol=re.match(r'\(= \(([^ ()]+)',raw.strip()).group(1)
                out.append({'symbol':symbol,'source':'vendor/pln/lib_pln.metta','line':start,'end_line':i,'definition':raw});start=None
    return out

def audit(out):
    out=Path(out);rt=Runtime(timeout=180);previous=old_audit();source=rt.library.read_text()
    learned={};ledger=[]
    for family in ('A','B'):
        tv=TV(.5,.05)
        for i in range(3):
            expr=f'(Truth_Revision {tv.metta()} (stv 1.0 0.5))';tv=rt.batch([('r',expr)])['r']
            ledger.append({'family':family,'group':f'learn-{family}-{i}','evidence_id':digest([family,i]),'expression':expr,'output':tv.json()})
        learned[family]=tv
    a,b=learned['A'].metta(),learned['B'].metta();tests={
      'independent':f'(collapse (|- (A {a}) (B {b})))',
      'missing-A':f'(collapse (|- (B {b})))',
      'missing-B':f'(collapse (|- (A {a})))',
      'swapped':f'(collapse (|- (B {b}) (A {a})))',
      'contradictory-B':f'(collapse (|- (A {a}) ((Not B) {b})))',
      'renamed':f'(collapse (|- (X {a}) (Y {b})))',
      'correlated':f'(collapse (if (StampDisjoint (source shared) (other shared)) (|- (A {a}) (B {b})) (empty)))',
      'compound-sensor-supplied':f'(collapse (|- ((And A B) {a}) ((Implication (And A B) C) {b})))',
      'compound-sensor-missing':f'(collapse (|- (A {a}) ((Implication (And A B) C) {b})))',
      'inheritance-chain':f'(collapse (|- ((Inheritance A B) {a}) ((Inheritance B C) {b})))',
      'implication-chain':f'(collapse (|- ((Implication A B) {a}) ((Implication B C) {b})))',
      'member-inheritance':f'(collapse (|- ((Member A B) {a}) ((Inheritance B C) {b})))',
      'inheritance-predicate-transfer':f'(collapse (|- ((Evaluation Safe B) {a}) ((Inheritance A B) {b})))',
      'similarity-wrapper':f'(collapse (|- ((Similarity A B) {a}) ((Similarity B C) {b})))',
      'equivalence-wrapper':f'(collapse (|- ((Equivalence A B) {a})))',
      'abduction-wrapper':f'(collapse (|- ((Implication A B) {a}) ((Implication C B) {b})))',
      'induction-wrapper':f'(collapse (|- ((Implication B A) {a}) ((Implication B C) {b})))'}
    # Supplied nesting is a positive mechanism control, never a learned C theorem.
    for name,aa,bb in [('nested-full',a,b),('nested-missing-A','(stv 0.5 0.0)',b),('nested-missing-B',a,'(stv 0.5 0.0)'),('nested-contradictory-B',a,'(stv 0.0 0.8)')]:
        tests[name]=f'(collapse (let ($rule $tv) (|- (A {aa}) ((Implication A (Implication B C)) (stv 0.95 0.8))) (|- (B {bb}) ($rule $tv))))'
    preamble='\n'.join(f'(= (STV {symbol}) (stv 0.4 0.8))' for symbol in ('A','B','C'))
    body=preamble+'\n'+'\n'.join(f'!(println! (C6PROBE {key} {expr}))' for key,expr in tests.items())
    raw=rt.execute(body);values=rt.batch(list(DIRECT.items()));records=[]
    for key,expr in tests.items():
        line=next(s for s in raw.splitlines() if s.startswith('(C6PROBE '+key+' '))
        records.append({'id':key,'expression':expr,'stdout':line,'stvs':[{'strength':float(x),'confidence':float(y)} for x,y in re.findall(r'\(stv ([\d.eE+-]+) ([\d.eE+-]+)\)',line)],
            'evidence_groups':[r['group'] for r in ledger],'proof_graph':{'inputs':['learned-A','learned-B'],'query':expr,'conclusion_is_supplied':key not in ('independent','missing-A','missing-B','swapped','contradictory-B','renamed','correlated')},
            'verdict':'No novel independent-premise C proof; successful structural derivations retain their supplied relational assumptions.'})
    for key in ('independent','missing-A','missing-B','swapped','contradictory-B','renamed','correlated','compound-sensor-missing','inheritance-predicate-transfer'):
        assert next(r for r in records if r['id']==key)['stdout']==f'(C6PROBE {key} ())',key
    inventory=[]
    for f in forms(source):
        if f['symbol'].startswith('Truth_') or f['symbol'] in ('|-','StampDisjoint','BestConfidenceCandidate'):
            verified=[k for k,e in DIRECT.items() if '('+f['symbol']+' ' in e]
            inventory.append({**f,'direct_probes':verified,'support':'directly-executed' if verified else 'wrapper-executed; inspect individual probe' if f['symbol']=='|-' else 'source-inspected',
                'assumptions':'Native truth functions do not enforce provenance independence; caller must gate shared evidence. Marginal TVs are population assumptions, not geometry sensors.'})
    history=[]
    for p in ('/tmp/pln-native-audit','/tmp/pln-experimental-audit','/tmp/pln-cycle2-upstream-audit'):
        if (Path(p)/'.git').exists():history.append({'path':p,'head':subprocess.check_output(['git','-C',p,'rev-parse','HEAD'],text=True).strip(),'log':subprocess.check_output(['git','-C',p,'log','-12','--format=%H %s'],text=True),
            'scope':'Locally available upstream history only; no claim that this is the latest remote HEAD.'})
    result={'runtime':rt.manifest,'inventory':inventory,'direct':[{'id':k,'expression':e,'output':values[k].json()} for k,e in DIRECT.items()],
        'training_evidence':ledger,'training_groups_disjoint':True,'learned':{k:v.json() for k,v in learned.items()},'records':records,'stdout':raw,
        'local_upstream_history':history,'inherited_audit':previous,'native_composition_achieved':False,
        'limitation':'The audited executable rule set derives chains, supplied nested implications and relational generalizations. It did not derive novel C from independent A and B without a supplied relation to C or a host joint observation. This is a scoped experimental result, not a theorem about all PLN implementations.'}
    write_json(out/'audit.json',result);(out/'audit.metta').write_text('!(import! &self "'+str(rt.library)+'")\n'+body+'\n'+'\n'.join(f'!(println! ({k} {e}))' for k,e in DIRECT.items()))
    return result

if __name__=='__main__':
    import sys
    audit(sys.argv[1])
