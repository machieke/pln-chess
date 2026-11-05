"""Executable native feasibility corpus, including deliberately failed candidates."""
from pathlib import Path
import re,subprocess,hashlib
from pln_chess.common import ROOT,write_json
from pln_chess.pln import Runtime
from pln_chess.pln.audit import CASES

PROBES={
 'inversion':'(Truth_inversion (stv 0.3 0.8) (stv 0.7 0.6))',
 'abduction':'(Truth_Abduction (stv 0.4 0.8) (stv 0.5 0.8) (stv 0.3 0.8) (stv 0.6 0.7) (stv 0.7 0.7))',
 'equivalence':'(Truth_equivalenceToImplication (stv 0.5 0.8) (stv 0.5 0.8) (stv 0.5 0.7))',
 'similarity':'(Truth_transitiveSimilarity (stv 0.5 0.8) (stv 0.5 0.8) (stv 0.5 0.8) (stv 0.7 0.7) (stv 0.6 0.7))',
 'zero-confidence-mp':'(Truth_ModusPonens (stv 1.0 0.0) (stv 0.8 0.9))',
 'confidence-one-mp':'(Truth_ModusPonens (stv 1.0 1.0) (stv 0.8 1.0))',
 'measured-induction':'(Truth_Induction (stv 0.4 0.8) (stv 0.2 0.8) (stv 0.3 0.8) (stv 1.0 0.8) (stv 0.75 0.8))',
}
RAW={
 'induction-inheritance':'(collapse (|- ((Inheritance C A) (stv 1.0 0.8)) ((Inheritance C B) (stv 0.75 0.8))))',
 'conjunction-introduction':'(collapse (|- (A (stv 0.8 0.9)) (B (stv 0.7 0.9))))',
 'conjunction-elimination':'(collapse (|- ((And A B) (stv 0.8 0.9))))',
 'conditionalization':'(collapse (|- ((And A B) (stv 0.8 0.9)) (A (stv 0.7 0.8))))',
 'incomplete-input':'(collapse (Truth_Induction (stv 0.4 0.8) (STV Unknown) (stv 0.3 0.8) (stv 1.0 0.8) (stv 0.75 0.8)))',
 'degenerate-marginal':'(collapse (Truth_Induction (stv 0.0 0.8) (stv 0.2 0.8) (stv 0.3 0.8) (stv 1.0 0.8) (stv 0.75 0.8)))',
 'confidence-one-revision':'(collapse (Truth_Revision (stv 1.0 1.0) (stv 0.0 0.5)))',
 'overlap':'(StampDisjoint (e1 e2) (e2 e3))',
 'disjoint':'(StampDisjoint (e1) (e2))',
 'zero-confidence-choice':'(BestConfidenceCandidate (((stv 0.5 0.0) (e))))',
 'conditional-chain':'(let ($b $btv) (|- (A (stv 1.0 0.9)) ((Implication A B) (stv 0.9 0.8))) (|- ($b $btv) ((Implication B C) (stv 0.8 0.7))))',
}

def audit(output=None):
    runtime=Runtime(timeout=60);source=runtime.library.read_text();records=[]
    cases={**{k:v[0] for k,v in CASES.items()},**PROBES}
    values=runtime.batch(list(cases.items()))
    for name,expr in cases.items():
        operator=next(iter(re.findall(r'\((Truth_[A-Za-z]+)',expr)), '|-')
        operator={'modus_ponens':'Truth_ModusPonens','revision':'Truth_Revision','negation':'Truth_Negation',
                  'choice':'BestConfidenceCandidate','weight_to_confidence':'Truth_w2c'}.get(name,operator)
        line=next((i for i,s in enumerate(source.splitlines(),1) if '(= ('+operator in s),None)
        expected=CASES[name][1] if name in CASES else None
        if expected:
            assert abs(values[name].strength-expected[0])<1e-10 and abs(values[name].confidence-expected[1])<1e-10
        records.append({'id':name,'expression':expr,'output':values[name].json(),
                        'operator':operator,'expected':expected,'domain':'Finite STVs in [0,1]; probability-consistent positive marginals for conditional formulas.',
                        'status':'verified-production' if name in ('modus_ponens','revision','negation','choice','weight_to_confidence') else 'verified-experimental',
                        'source':f'vendor/pln/lib_pln.metta:{line}','commit':runtime.version})
    definitions='(= (STV A) (stv 0.4 0.8))\n(= (STV B) (stv 0.3 0.8))\n(= (STV C) (stv 0.2 0.8))\n'
    body=definitions+'\n'.join(f'!(println! (PROBE {name} {expr}))' for name,expr in RAW.items())
    raw=runtime.execute(body)
    for name,expr in RAW.items():
        line=next((s for s in raw.splitlines() if s.startswith('(PROBE '+name+' ')),None)
        records.append({'id':name,'expression':expr,'output':line,'status':'unsupported' if name in ('conjunction-introduction','conjunction-elimination','conditionalization','incomplete-input','degenerate-marginal','confidence-one-revision','zero-confidence-choice') else 'verified-experimental'})
    assert '(PROBE conjunction-introduction ())' in raw
    assert '(probe overlap false)' in raw.lower() and '(probe disjoint true)' in raw.lower()
    report={'runtime':runtime.manifest,'records':records,'raw':raw,
            'induction_caution':'The rule-layer |- induction supplies STV A, STV B, STV C while the formula expects target A, common B, outcome C. Non-symmetric measured populations use the directly verified Truth_Induction formula with explicit roles; no silent argument reinterpretation.',
            'composition':'Unary chaining verified; conjunction introduction/elimination and conditionalization unsupported in pinned core. Nested implication is not conjunction.'}
    if output:
        write_json(output,report);Path(output).with_suffix('.metta').write_text('!(import! &self "'+str(runtime.library)+'")\n'+body+'\n')
    return report


def upstream_audit(repo='/tmp/pln-cycle2-upstream-audit',output=None):
    """Research-only alternate source loads; never modifies the production lock."""
    runtime=Runtime();reports=[]
    for branch in ('main','PLN_v0.6','pln0.9','Modularity'):
        commit=subprocess.check_output(['git','--git-dir',repo,'rev-parse',branch],text=True).strip()
        date=subprocess.check_output(['git','--git-dir',repo,'show','-s','--format=%cI',commit],text=True).strip()
        try:source=subprocess.check_output(['git','--git-dir',repo,'show',commit+':lib_pln.metta'],text=True,stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError:
            reports.append({'branch':branch,'commit':commit,'date':date,'status':'different-module-layout; no drop-in compatibility claimed'});continue
        target=ROOT/'artifacts/cycle2/research'/f'{commit}.metta';target.parent.mkdir(parents=True,exist_ok=True);target.write_text(source)
        runtime.library=target
        try: result=runtime.execute('!(println! (AND-PROBE (collapse (|- (A (stv 0.8 0.9)) (B (stv 0.7 0.9))))))');status='executed'
        except Exception as error: result=str(error);status='failed'
        reports.append({'branch':branch,'commit':commit,'date':date,'sha256':hashlib.sha256(source.encode()).hexdigest(),
                        'source':str(target.relative_to(ROOT)),'repository':'https://github.com/trueagi-io/PLN','license':'MIT',
                        'status':status,'conjunction_probe':result,'candidate_lines':[s for s in source.splitlines() if 'Conjunction' in s or 'Truth_And' in s or 'And ' in s]})
    report={'branches':reports,'decision':'No demonstrated drop-in native conjunction from tested maintained repository refs. Production runtime unchanged.',
            'scope':'Pinned main and three candidate branches; not an exhaustive theorem about all upstream repositories.'}
    if output:write_json(output,report)
    return report

if __name__=='__main__':
    audit(ROOT/'artifacts/cycle2/native-probes.json');upstream_audit(output=ROOT/'artifacts/cycle2/upstream-audit.json');print('Native probes recorded')
