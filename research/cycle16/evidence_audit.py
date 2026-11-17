"""Separate native admissibility diagnostics; these never supply query answers."""
from dataclasses import asdict
from pathlib import Path
from pln_chess.common import ROOT, read_json
from research.cycle15.native_reasoner import NativeReasoner, Sentence, Budgets, parse, render, alpha_key
from .experiments import infer, fixture, observations, knowledge, GENEROUS, MEDIUM
from .records import compact, record


def replay_baseline(out):
    out=Path(out);reasoner=NativeReasoner();rows={}
    for name in ('one-rule','two-rules','shared-role','swapped-role','reused-recursive-rule',
                 'learned-baseline','stage-b-exposure','long-path-generous'):
        source=ROOT/'artifacts/cycle15/representative'/(name+'.json');old=read_json(source)
        new=reasoner.infer([Sentence(**r) for r in old['facts']], [Sentence(**r) for r in old['rules']],
            old['query'],contrary=old['contrary_query'],budgets=Budgets(**old['budgets']),
            marginals=old['marginals'],mode=old['api'])
        exact=all(new[k]==old[k] for k in ('answer','contrary','classification'))
        rows[name]=dict(source=str(source),exact_answer_parity=exact,result=compact(new,out))
        assert exact,(name,new['classification'])
    for name,occ in [('obstruction','OE'),('unknown','EU')]:
        state,a,t=fixture(occ,tag='baseline_'+name)
        rows[name]=compact(infer(state,a,t,arm='R',reasoner=reasoner),out)
    return record(out/'baseline-replay.json',dict(passed=True,rows=rows))


def pair_diagnostic(left,right,out,reasoner=None):
    reasoner=reasoner or NativeReasoner()
    def statement(row):return f'({row["term"]} (stv {row["strength"]} {row["confidence"]}))'
    program=f'!(import! &self "{reasoner.runtime.library}")\n'
    program+=f'!(println! (C16DISJOINT (StampDisjoint {render(left["stamps"])} {render(right["stamps"])})))\n'
    program+=f'!(println! (C16STRUCTURAL (collapse (|- {statement(left)} {statement(right)}))))\n'
    program+=f'!(println! (C16STRUCTURAL_REVERSE (collapse (|- {statement(right)} {statement(left)}))))\n'
    receipt=reasoner.execute_program(program,15)
    from research.cycle15.native_reasoner import save_result
    markers=[parse(line) for line in receipt['stdout'].splitlines() if line.startswith('(C16')]
    return dict(left=left,right=right,overlap=sorted(set(left['stamps'])&set(right['stamps'])),
        markers=markers,incomplete=receipt['incomplete'],proof=save_result(receipt,Path(out)/'raw'),
        scope='Admissibility and structural witness only; no claim the scheduler attempted this pair')


def minimal(out):
    out=Path(out);reasoner=NativeReasoner()
    facts=[Sentence('(State audit_state)',stamps=('obs_audit_state',)),
        Sentence('(Empty audit_c1 audit_state)',stamps=('obs_audit_c1',)),
        Sentence('(Empty audit_c2 audit_state)',stamps=('obs_audit_c2',))]
    rules=[r for r in knowledge('R') if r.stamps[0] in ('rule_empty-tail','rule_extend-empty')]
    symbolic=reasoner.infer(facts,rules,'(PathEmpty (Cons audit_c1 (Cons audit_c2 Nil)) audit_state)',budgets=GENEROUS)
    initial=next(r for r in symbolic['retained'] if r['term']=='(PathEmpty Nil audit_state)')
    extension=next(r for r in symbolic['retained'] if r['term']=='(PathEmpty (Cons audit_c2 Nil) audit_state)')
    partial=next(r for r in symbolic['retained'] if alpha_key(r['term'])==alpha_key(
        '(Implication (PathEmpty $tail audit_state) (PathEmpty (Cons audit_c1 $tail) audit_state))'))
    diagnostic=pair_diagnostic(partial,extension,out,reasoner)
    state,a,t=fixture(tag='minimal');arms={}
    for arm in ('R','F','F-minus'):
        arms[arm]=compact(infer(state,a,t,arm=arm,budgets=GENEROUS,reasoner=reasoner),out)
    return record(out/'minimal.json',dict(symbolic=compact(symbolic,out),initial_empty_tail=initial,
        first_extension=extension,partial_other_cell=partial,diagnostic=diagnostic,arms=arms,
        gate='Minimal comparison executed before corpus expansion; success is reported separately'))


def dependencies(out):
    out=Path(out);reasoner=NativeReasoner();rows={}
    def sentence(term,*stamps):return Sentence(term,stamps=stamps,origin='audit-input')
    for name,shared in [('shared-rule-only','rule_audit_reuse'),('shared-environment','obs_audit_common'),
                        ('shared-training','train_audit_common'),('truly-disjoint',None)]:
        left=sentence('(Implication AuditB AuditC)','rule_audit_next',*([shared] if shared else []))
        right=sentence('AuditB','obs_audit_branch',*([shared] if shared else []))
        result=reasoner.infer([right],[left],'AuditC')
        rows[name]=dict(result=compact(result,out),diagnostic=pair_diagnostic(asdict(left),asdict(right),out,reasoner),
            assumption='Explicit synthetic stamp arrangement, not replacement provenance for real observations')
    rules=[sentence('(Implication AuditA AuditB)','rule_audit_ab'),
           sentence('(Implication AuditA AuditC)','rule_audit_ac'),
           sentence('(Implication AuditB (Implication AuditC AuditD))','rule_audit_join')]
    base=sentence('AuditA','obs_audit_origin')
    rows['diamond']=compact(reasoner.infer([base],rules,'AuditD',budgets=GENEROUS),out)
    rows['diamond-disjoint-inputs']=compact(reasoner.infer(
        [sentence('AuditB','obs_audit_b'),sentence('AuditC','obs_audit_c')],rules,'AuditD',budgets=GENEROUS),out)
    for name,facts in [('single-delivery',[base]),('replayed-input',[base,base])]:
        rows[name]=compact(reasoner.infer(facts,rules[:1],'AuditB',budgets=GENEROUS),out)
    cycle=[sentence('(Implication AuditA AuditB)','rule_cycle_ab'),sentence('(Implication AuditB AuditA)','rule_cycle_ba')]
    rows['circular-chain']=compact(reasoner.infer([base],cycle,'AuditA',budgets=GENEROUS),out)
    return record(out/'dependencies.json',rows)
