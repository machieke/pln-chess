"""Research-only entry point, with exclusive output directories and dataflow fences."""
import argparse
import json
from pathlib import Path
import resource
import time
from dataclasses import asdict
from .contracts import sha
from .source_mapping import map_sources, ARMS


def output_directory(root,out):
    root=Path(root).resolve();out=Path(out).resolve()
    if out==root or out in root.parents:
        raise ValueError('Research output cannot replace a repository/ancestor')
    if out.is_relative_to(root) and not out.is_relative_to(root/'artifacts/cycle18'):
        raise ValueError('Reference output fenced from operational/native/historical paths')
    if out.exists():
        raise ValueError('Immutable output generation already exists')
    out.mkdir(parents=True)
    return out


def write(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x') as stream:
        json.dump(value,stream,indent=2,sort_keys=True,allow_nan=False);stream.write('\n')


def contract(root,out):
    from .reference_joint import fit, GRIDS, MODELS
    from .reference_bounds import posterior_bounds, unidentified
    from .controls import run as controls
    start=time.perf_counter();cpu=time.process_time()
    registry,memberships,audit=map_sources(root)
    write(out/'mappings/audit.json',audit)
    write(out/'mappings/events.json',[e.json() for e in registry.all()])
    write(out/'mappings/memberships.json',memberships)
    first=next(iter(memberships['S-AA']));event=registry.get(first)
    example=[registry.get(p).json() for p in event.parent_event_ids]+[event.json()]
    example += [e.json() for e in registry.all() if first in e.parent_event_ids]
    write(out/'mappings/decisive-example.json',dict(events=example,source_hashes=audit['source_hashes'],
        lesson='One evaluated vector parents two conditional annotations; 48 labels are 24 underlying evaluations'))
    summary={};total_evaluations=0;max_bits=0;max_states=0
    for grid in GRIDS:
        for arm in ARMS:
            for model in MODELS:
                fit_result=fit(registry,memberships[arm],model,grid);d=fit_result.json()
                assert d['status']=='point_under_declared_model'
                bound=posterior_bounds(fit_result).json()
                name=f'{grid}/{arm}/{model}'
                write(out/'reference_cases'/name/'result.json',d)
                write(out/'reference_cases'/name/'bounds.json',bound)
                summary[name]=dict(probability=d['predictive_probability'],posterior_identity=d['posterior_identity'],
                    bounds=bound['bounds'],events=len(d['event_ids']),source_groups=len(d['source_group_ids']),resources=d['resources'])
                total_evaluations+=d['resources']['likelihood_evaluations']
                max_bits=max(max_bits,d['resources']['max_rational_bits']);max_states=max(max_states,d['resources']['states'])
    write(out/'reference_cases/not-identified.json',unidentified().json())
    write(out/'reference_cases/summary.json',summary)
    # Quarantine controls mutate only their own local registry, after source outputs.
    control_results=controls(registry,memberships)
    write(out/'controls/results.json',control_results)
    write(out/'resources.json',dict(native_invocations=0,primary_fits=len(summary),likelihood_evaluations=total_evaluations,
        max_states=max_states,max_rational_bits=max_bits,wall_seconds=time.perf_counter()-start,
        cpu_seconds=time.process_time()-cpu,process_peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        output_bytes_before_resource_receipt=sum(p.stat().st_size for p in out.rglob('*') if p.is_file()),
        deliberate_budget_failures=4,unexpected_budget_failures=0,control_resources=control_results['resources'],
        total_likelihood_evaluations=total_evaluations+control_results['resources']['likelihood_evaluations'],
        scope='Registered fits plus separately itemized replay/control recomputations; six two-latent-state noise controls; no general scaling claim'))


def main():
    p=argparse.ArgumentParser();p.add_argument('command',choices=('contract','native'))
    p.add_argument('--out',required=True);p.add_argument('--root',default=None);a=p.parse_args()
    if a.root is None:
        from pln_chess.common import ROOT
        a.root=ROOT
    root=Path(a.root).resolve();out=output_directory(root,a.out)
    if a.command=='contract':
        contract(root,out)
    else:
        from .native_comparison import run
        run(root,out)


if __name__=='__main__':
    main()
