"""Research interfaces; every command uses a new external output generation."""
import argparse
from pathlib import Path
from pln_chess.common import ROOT,read_json
from .records import output,record
from .meter import metered
from .study import measurement,training,evaluate,timed
from .lifecycle import Journal
from .corpus import roots


def compact(out):
    """Two registered training games plus one held-out measured episode."""
    from .controls import run
    selected=[next(r for r in roots() if r['split']==split) for split in ('A','B','test')]
    j,episodes,annotations=measurement(out/'measurement',selected,False)
    from .learning import fit
    models={'D-AB':fit(j,annotations,out/'learning/D-AB','D-AB')}
    for e in episodes:e['arms']=('F','D-AB')
    rows,summary=evaluate(j,episodes,models,out/'evaluation',workers=1)
    controls=run(j,episodes,annotations,models,selected,out/'lifecycle',compact=True)
    return record(out/'verified.json',dict(passed=controls['passed'],measured_episodes=len(episodes),
        measurement_disagreements=sum(e['measurement']['agreement']=='disagree' for e in episodes),
        evaluated_queries=len(rows)*2,learning='Two measured games, native revisions; compact demonstration, not full-cohort fit',
        lifecycle='Actual leave-one and corrected-source refits; full/incremental parity; historical native replay'))


def main():
    p=argparse.ArgumentParser();p.add_argument('command',choices=('measure','fit','evaluate','lifecycle','study','compact','anchors','reference'))
    p.add_argument('--out',required=True);p.add_argument('--input');p.add_argument('--meter',required=True)
    p.add_argument('--workers',type=int,default=4);a=p.parse_args();out=output(a.out)
    if not 1<=a.workers<=8:raise ValueError('Research worker ceiling is eight')
    def run():
        if a.command=='measure':measurement(out);return
        if a.command=='compact':compact(out);return
        if a.command=='anchors':
            from .anchors import run as anchors
            anchors(ROOT,out);return
        if a.command=='reference':
            from .reference import meaning
            from .measurements import environment
            record(out/'query-meaning.json',meaning(environment(roots()[0])));return
        if a.command=='study':
            from .corpus import census,REGISTER
            from unittest.mock import patch
            def repeat_census():
                with patch('chess.Board.attacks',side_effect=AssertionError('Outcome oracle prohibited in census')):
                    value=census(out/'census-reproduction.json')
                assert value==read_json(REGISTER)
                return value
            timed('corpus-preparation',repeat_census,out)
            j,episodes,annotations=timed('measurement',lambda:measurement(out/'measurement'),out)
            models=timed('training',lambda:training(j,annotations,out/'learning'),out)
            rows,summary=timed('inference',lambda:evaluate(j,episodes,models,out/'evaluation',a.workers),out)
            from .controls import run as controls
            timed('lifecycle',lambda:controls(j,episodes,annotations,models,roots(),out/'lifecycle'),out)
            record(out/'verified.json',dict(passed=True,episodes=len(episodes),queries=len(rows)*2,
                incomplete=sum(v['counts']['incomplete'] for v in summary)))
            return
        if not a.input:raise ValueError('--input must name a study generation')
        source=Path(a.input);j=Journal.historical(read_json(source/'measurement/snapshot.json'))
        episodes=read_json(source/'measurement/episodes.json');annotations=read_json(source/'measurement/annotations.json')
        if a.command=='fit':training(j,annotations,out);return
        j=Journal.historical(read_json(source/'learning/snapshot.json'));models=read_json(source/'learning/models.json')
        if a.command=='evaluate':evaluate(j,episodes,models,out,a.workers)
        else:
            from .controls import run as controls
            controls(j,episodes,annotations,models,roots(),out)
    with metered(a.meter,a.command):timed(a.command,run,out)


if __name__=='__main__':main()
