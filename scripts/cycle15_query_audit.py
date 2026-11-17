"""Separate retrieval from inference when Query receives no active tasks."""
import argparse
from pathlib import Path
from pln_chess.common import write_json
from research.cycle15.native_reasoner import NativeReasoner,Sentence
from evaluation.cycle15_consequences import compact


def run(out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True);reasoner=NativeReasoner()
    facts=[Sentence('(P entity)',stamps=('premise',))]
    rules=[Sentence('(Implication (P $x) (Q $x))',1.,.95,('rule',),'supplied-domain-rule-template')]
    rows=[]
    for name,query,tasks in [('query-retrieval-with-empty-tasks','(P entity)',[]),
                             ('query-absent-conclusion-with-empty-tasks','(Q entity)',[]),
                             ('query-absent-conclusion-with-active-tasks','(Q entity)',None)]:
        result=reasoner.infer(facts,rules,query,tasks=tasks,mode='query')
        rows.append(dict(name=name,result=compact(result,out)))
    assert [r['result']['classification'] for r in rows]==['supported-positive','unknown','supported-positive']
    write_json(out/'query-boundary.json',dict(passed=True,rows=rows,
        conclusion='With the same fact and rule already in beliefs, empty tasks permit retrieval but not an absent conclusion; Query does not initiate backward chaining',
        earlier_probe_scope='The original query-is-not-backward matrix row had no fact and was insufficient alone to distinguish chaining direction'))


def chain(out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True);reasoner=NativeReasoner()
    facts=[Sentence('(P entity)',stamps=('premise',))]
    first=Sentence('(Implication (P $x) (Q $x))',1.,.95,('chain_first',),'supplied-domain-rule-template')
    second=Sentence('(Implication (Q $x) (R $x))',1.,.95,('chain_second',),'supplied-domain-rule-template')
    rows=[]
    for name,observed,rules in [('full-chain',facts,[first,second]),('remove-first-rule',facts,[second]),
                                ('remove-second-rule',facts,[first]),('remove-premise',[],[first,second])]:
        result=reasoner.infer(observed,rules,'(R entity)')
        rows.append(dict(name=name,result=compact(result,out)))
    assert [r['result']['classification'] for r in rows]==['supported-positive','unknown','unknown','unknown']
    write_json(out/'chain-interventions.json',dict(passed=True,rows=rows,
        conclusion='The absent two-rule conclusion requires both reusable rules and the sole initial fact'))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--part',choices=('query','chain'),default='query')
    a=p.parse_args();(run if a.part=='query' else chain)(a.out)
