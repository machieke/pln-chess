"""Registered orchestration; measurements stay outside native inference."""
from concurrent.futures import ThreadPoolExecutor
from itertools import product
from pathlib import Path
import time
import resource
from unittest.mock import patch
from pln_chess.common import ROOT,read_json,digest
from .corpus import roots
from .lifecycle import Journal
from .measurements import environment,measure,matrix,transformed
from .learning import fit
from .native import request
from .metrics import summarize
from .records import record
from .reference import meaning

ARMS=('H','F','D-AB','D-BA','S-AA','S-BB','P')


def prepare(selected=None,diagnostics=True):
    selected=selected or roots();journal=Journal();episodes=[];annotations=[]
    diagnostic=set(read_json(ROOT/'artifacts/cycle19/corpus-registration.json')['diagnostic_roots'])
    for root in selected:
        specs=[(environment(root),root['population'],root['split'],ARMS)]
        if diagnostics and root['id'] in diagnostic:
            for p in product('EOU',repeat=2):
                pattern=''.join(p);specs.append((matrix(root,pattern),'withheld-observations' if 'U' in pattern else 'occupancy-intervention','diagnostic',('F','D-AB','S-AA')))
            for kind in ('rename','rotate','reflect'):specs.append((transformed(root,kind),'representation-transform','diagnostic',('D-AB',)))
        for env,population,split,arms in specs:
            event=journal.add('environment',env);measured=measure(journal,event)
            episodes.append(dict(root=root['id'],game=root['game_identity'],variant=env['variant'],
                population=population,split=split,environment=event,measurement=measured,arms=arms))
            if population=='natural-training':annotations.extend(measured['annotations'].values())
    return journal,episodes,annotations


def measurement(out,selected=None,diagnostics=True):
    journal,episodes,annotations=prepare(selected,diagnostics)
    record(Path(out)/'episodes.json',episodes);record(Path(out)/'annotations.json',annotations)
    record(Path(out)/'snapshot.json',journal.snapshot())
    record(Path(out)/'query-meaning.json',meaning(journal.node(episodes[0]['environment'])['payload']))
    from .audits import fixtures,novelty
    fixtures(Path(out)/'manual-fixtures.json')
    if selected is None:novelty(roots(),Path(out)/'novelty.json')
    return journal,episodes,annotations


def training(journal,annotations,out):
    models={arm:fit(journal,annotations,Path(out)/arm,arm) for arm in ARMS if arm not in ('H','F')}
    record(Path(out)/'models.json',models)
    record(Path(out)/'snapshot.json',journal.snapshot())
    return models


def evaluate(journal,episodes,models,out,workers=4):
    out=Path(out);tasks=[(e,arm) for e in episodes for arm in e['arms']]
    def execute(task):
        episode,arm=task;generation=models[arm]['generation'] if arm in models else None
        native,execution=request(journal,episode['environment'],generation,arm=arm,out=out/'raw')
        row=dict(**{k:v for k,v in episode.items() if k!='arms'},arm=arm,native=native,execution=execution)
        record(out/'rows'/(digest([episode['environment'],arm])+'.json'),row)
        return row
    with patch('chess.Board.attacks',side_effect=AssertionError('Measurement oracle forbidden during native evaluation')):
        with ThreadPoolExecutor(max_workers=workers) as pool:rows=list(pool.map(execute,tasks))
    result=summarize(rows);record(out/'summary.json',result)
    record(out/'snapshot.json',journal.snapshot())
    return rows,result


def timed(name,fn,out):
    from .meter import reserved,phase
    started=time.perf_counter();before=resource.getrusage(resource.RUSAGE_SELF);children=resource.getrusage(resource.RUSAGE_CHILDREN)
    calls=reserved()
    with phase(name):result=fn()
    after=resource.getrusage(resource.RUSAGE_SELF);after_children=resource.getrusage(resource.RUSAGE_CHILDREN)
    record(Path(out)/(name+'-resources.json'),dict(category=name,wall_seconds=time.perf_counter()-started,
        native_calls=reserved()-calls,incomplete=False,
        host_cpu_seconds=after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime,
        child_cpu_seconds=after_children.ru_utime+after_children.ru_stime-children.ru_utime-children.ru_stime,
        host_peak_rss_kib=after.ru_maxrss,child_peak_rss_kib=after_children.ru_maxrss,
        memory_scope='Process high-water marks, not sum of concurrent RSS'))
    return result
