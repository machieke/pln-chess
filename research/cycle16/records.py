"""Immutable raw native records and compact inspectable indexes."""
from pathlib import Path
from pln_chess.common import write_json
from research.cycle15.native_reasoner import save_result


def compact(result,out):
    if 'stages' in result:
        return {**{k:v for k,v in result.items() if k not in ('stages','raw_observations')},
            'stages':{k:compact(v,out) for k,v in result['stages'].items()},
            'proof':save_result(result,Path(out)/'raw')}
    return {**{k:result[k] for k in ('query','answer','contrary','classification','incomplete',
        'usage','budgets','completion','proof_status')},
        'wall_seconds':result['receipt']['wall_seconds'],
        'peak_rss_kib':result['receipt']['peak_rss_kib'],
        'proof':save_result(result,Path(out)/'raw')}


def record(path,value):
    path=Path(path)
    if path.exists():raise ValueError('Refusing to overwrite experiment: '+str(path))
    write_json(path,value)
    return value
