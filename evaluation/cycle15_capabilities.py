"""Executable bounded capability matrix; no chess-specific inference code."""
import argparse
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import urllib.request

from pln_chess.common import ROOT, write_json
from research.cycle15.native_reasoner import Budgets, NativeReasoner, Sentence, save_result


def fact(term, stamp, strength=1., confidence=.99):
    return Sentence(term, strength, confidence, (stamp,), 'audit-input')


def rule(term, stamp, strength=1., confidence=.95):
    return Sentence(term, strength, confidence, (stamp,), 'supplied-domain-rule-template')


def cases():
    p = fact('(P alice)', 'p'); q = '(Q alice)'
    r = rule('(Implication (P $x) (Q $x))', 'r')
    s = rule('(Implication (Q $x) (R $x))', 's')
    rows = []
    def add(name, facts, rules, query=q, **kwargs):
        rows.append(dict(name=name, facts=facts, rules=rules, query=query, **kwargs))
    add('stored-fact', [p], [], '(P alice)')
    add('one-rule', [p], [r])
    add('two-rules', [p], [r, s], '(R alice)')
    add('missing-premise', [], [r])
    add('removed-rule', [p], [])
    add('changed-rule', [p], [rule('(Implication (P $x) (Other $x))', 'changed')])
    add('renamed', [fact('(P unfamiliar)', 'otherfact')], [r], '(Q unfamiliar)')
    add('unfamiliar-second-entity', [p, fact('(P zed)', 'zed')], [r], '(Q zed)')
    add('distractors', [p]+[fact(f'(Noise n{i})', f'n{i}') for i in range(8)],
        [r]+[rule(f'(Implication (Noise n{i}) (Unused n{i}))', f'd{i}') for i in range(4)])
    shared = rule('(Implication (Touches $a $t) (Implication (Owns $a $t) (Shared $a $t)))', 'shared')
    add('shared-role', [fact('(Touches a t)', 'touch'), fact('(Owns a t)', 'owner')], [shared], '(Shared a t)')
    add('swapped-role', [fact('(Touches a t)', 'touch'), fact('(Owns a u)', 'owner')], [shared], '(Shared a t)')
    add('missing-curried-premise', [fact('(Touches a t)', 'touch')], [shared], '(Shared a t)')
    add('overlap-chain', [p], [r, replace(s, stamps=('r',))], '(R alice)')
    add('independent-revision', [fact('Belief','one',1,.5),fact('Belief','two',0,.5)], [], 'Belief')
    add('shared-stamp-revision', [fact('Belief','one',1,.5),fact('Belief','one',0,.5)], [], 'Belief')
    add('duplicate-replay', [p, p], [r])
    add('opposing-channels', [p, fact('(NoQ alice)', 'opposing')], [r], contrary='(NoQ alice)')
    # Two supports descend from the same root fact; stamps must block their join.
    join=rule('(Implication (Q $x) (Implication (R $x) (Joined $x)))','join')
    add('shared-diamond', [p], [r,rule('(Implication (P $x) (R $x))','right'),join], '(Joined alice)')
    add('independent-join', [fact('(Q alice)','left'),fact('(R alice)','right')], [join], '(Joined alice)')
    add('reused-recursive-rule', [fact('(Edge a b)','ab'),fact('(Edge b c)','bc'),fact('(Edge c d)','cd')],
        [rule('(Implication (Edge $a $b) (Implication (Edge $b $c) (Edge $a $c)))','transitive')], '(Edge a d)')
    add('query-variable', [p], [r], '(Q $who)', mode='query')
    add('query-api', [p], [r], mode='query')
    add('query-is-not-backward', [], [r], tasks=[])
    add('inheritance-product', [fact('(Inheritance (Product a t) touches)','ip')],
        [rule('(Implication (Inheritance (Product $x $y) touches) (Inheritance (Product $x $y) related))','ir')],
        '(Inheritance (Product a t) related)')
    for steps in (0,1,2,3,8,64):
        add(f'steps-{steps}', [p], [r,s], '(R alice)', budgets=Budgets(steps,64,128,10))
    for size in (1,2,3,4,16):
        add(f'queue-{size}', [p], [r,s], '(R alice)', budgets=Budgets(24,size,size,10))
    for reversed_order in (False,True):
        tied=[fact('Tie','positive',1,.5),fact('Tie','negative',0,.5)]
        add(f'tie-order-{int(reversed_order)}',list(reversed(tied)) if reversed_order else tied,[], 'Tie',budgets=Budgets(0))
        add(f'eviction-order-{int(reversed_order)}',list(reversed([p,fact('Noise','noise')])) if reversed_order else [p,fact('Noise','noise')],
            [r,s], '(R alice)',budgets=Budgets(8,3,3))
    deduction=[rule('(Inheritance A B)','ab'),rule('(Inheritance B C)','bc')]
    add('missing-marginals',[],deduction,'(Inheritance A C)')
    add('explicit-synthetic-marginals',[],deduction,'(Inheritance A C)',marginals={t:(.5,.9) for t in 'ABC'})
    return rows


def run(out, selected=None):
    out=Path(out); out.mkdir(parents=True,exist_ok=True)
    reasoner=NativeReasoner(); summaries=[]
    for spec in cases():
        spec=dict(spec); name=spec.pop('name')
        if selected and name != selected: continue
        result=reasoner.infer(**spec)
        evidence=save_result(result,out/'raw')
        summary=dict(name=name,classification=result['classification'],answer=result['answer'],
            contrary=result['contrary'], completion=result['completion'],usage=result['usage'],
            absent_from_inputs=spec['query'] not in [s.term for s in spec['facts']+spec['rules']],
            wall_seconds=result['receipt']['wall_seconds'],peak_rss_kib=result['receipt']['peak_rss_kib'], evidence=evidence)
        summaries.append(summary)
        print(name,result['classification'],result['answer'],flush=True)
    write_json(out/'matrix.json',summaries)
    if selected:return summaries
    source_url='https://raw.githubusercontent.com/trueagi-io/PLN/4405956947c4b53c7ff01bd565aa3b114bc970a1/examples/Smokes.metta'
    source=out/'Smokes.original.metta'
    if not source.exists():source.write_bytes(urllib.request.urlopen(source_url,timeout=30).read())
    raw=source.read_text()
    # Only the three import declarations are adapted. All example rules,
    # assumptions, query and assertion remain byte-identical after line 3.
    adapted=f'!(import! &self "{reasoner.runtime.library}")\n'+''.join(raw.splitlines(keepends=True)[3:])
    (out/'Smokes.local.metta').write_text(adapted)
    receipt=reasoner.execute_program(adapted,30)
    receipt.update(original_url=source_url,original_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
        adaptation='Replace first three imports with one pinned local import; remaining bytes unchanged',
        scope='Final Edward cancerous assertion; does not establish friend-chain execution')
    write_json(out/'upstream-smoke.json',receipt)
    return summaries


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',required=True);parser.add_argument('--case')
    args=parser.parse_args();run(args.out,args.case)
