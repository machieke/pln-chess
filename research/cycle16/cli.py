"""Opt-in experiments and explicit observed-state requests."""
import argparse
import json
from pathlib import Path
from pln_chess.common import read_json
from research.cycle15.native_reasoner import Budgets
from .experiments import infer,fixture
from .records import compact,record


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('command',choices=('minimal','compare','occupancy','learned','infer','preservation'))
    p.add_argument('--out',required=True);p.add_argument('--state');p.add_argument('--attacker');p.add_argument('--target')
    p.add_argument('--arm',choices=('R','F','F-minus','L'),default='F');p.add_argument('--checkpoint')
    p.add_argument('--move',help='JSON file containing a supplied structural displacement')
    p.add_argument('--steps',type=int,default=64);p.add_argument('--tasks',type=int,default=128)
    p.add_argument('--beliefs',type=int,default=256);p.add_argument('--timeout',type=float,default=15)
    p.add_argument('--proof-mode',choices=('full','summary'),default='full')
    p.add_argument('--source');p.add_argument('--workers',type=int,default=4)
    a=p.parse_args();out=Path(a.out)
    if a.command=='minimal':
        from .evidence_audit import minimal
        result=minimal(out)
    elif a.command=='occupancy':
        from .panel import occupancy
        result=occupancy(out)
    elif a.command=='preservation':
        from scripts.cycle16_preservation import run
        if not a.source:p.error('--source is required')
        run(out,Path(a.source),a.workers);return
    else:
        state,attacker,target=fixture(tag='cli')
        if a.state:
            if not a.attacker or not a.target:p.error('--attacker and --target are required with --state')
            state,attacker,target=read_json(a.state),a.attacker,a.target
        if a.command=='learned' and not a.checkpoint:p.error('--checkpoint is required')
        results={}
        arms=('R','F','F-minus') if a.command=='compare' else ('L',) if a.command=='learned' else (a.arm,)
        for arm in arms:
            value=infer(state,attacker,target,arm=arm,checkpoint=a.checkpoint,
                budgets=Budgets(a.steps,a.tasks,a.beliefs,a.timeout),proof_mode='full',
                supplied_move=read_json(a.move) if a.move else None)
            if 'before' in value:
                results[arm]={**{k:v for k,v in value.items() if k not in ('before','after')},
                    'before':compact(value['before'],out),'after':compact(value['after'],out)}
            else:results[arm]=compact(value,out)
        result=record(out/'results.json',results)
    # Raw proofs always persist; the display never pretends a cache is inference.
    print(json.dumps(result if a.proof_mode=='full' else {'evidence_directory':str(out)},indent=2))


if __name__=='__main__':main()
