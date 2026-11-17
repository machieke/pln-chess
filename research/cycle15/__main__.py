"""Small reproducible command-line inspection, with exact native evidence."""
import argparse
import json
from pathlib import Path
from pln_chess.common import write_json
from .native_reasoner import NativeReasoner,Sentence,save_result
from .queries import infer_consequence


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=('microcase','blocker'))
    parser.add_argument('--out',required=True)
    args=parser.parse_args();out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    if args.command=='microcase':
        result=NativeReasoner().infer([Sentence('(Present unfamiliar)',stamps=('observation',))],
            [Sentence('(Implication (Present $x) (Related $x))',1.,.95,('rule',),'supplied-domain-rule-template')],
            '(Related unfamiliar)')
        summary={k:result[k] for k in ('query','classification','answer','grounding_mode','usage')}
    else:
        state=dict(id='before',root='example',actor='white',history='observed',unknown=[],pieces=[
            dict(id='attacker',kind='rook',owner='black',cell=[0,0]),
            dict(id='blocker',kind='knight',owner='white',cell=[0,1]),
            dict(id='target',kind='king',owner='white',cell=[0,2])])
        result=infer_consequence(state,dict(id='supplied',piece='blocker',destination=[1,1]),
            dict(attacker='attacker',target='target',predicate='Attack'))
        summary=result['endpoint_comparison']
    summary['evidence']=save_result(result,out/'raw')
    write_json(out/'summary.json',summary);print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
