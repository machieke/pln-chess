"""Standalone publication artifacts from measured Cycle 11 summaries."""
import argparse
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

FAMILIES = ('attack', 'defense', 'mobility', 'king-exposure')
COLORS = ('#147d92', '#8057b3', '#cb7b1b', '#b64c60')


def run(out):
    out = Path(out).resolve()
    files = ('field-evaluation/summary.json', 'field-evaluation/calibration.json', 'performance/summary.json')
    data = [json.loads((out / name).read_text()) for name in files]
    fields, calibration, performance = data
    directory = out / 'figures'
    directory.mkdir(exist_ok=True)
    plt.rcParams.update({'font.family':'DejaVu Sans', 'font.size':10, 'axes.spines.top':False, 'axes.spines.right':False})
    outputs = []

    def save(figure, name):
        for extension in ('png', 'svg'):
            path = directory / f'{name}.{extension}'
            figure.savefig(path, dpi=170, bbox_inches='tight', facecolor='white')
            outputs.append(dict(path=str(path.relative_to(out)), sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
        plt.close(figure)

    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.8), sharey=True)
    for axis, population, title in zip(axes, ('all', 'external-game-panel'), ('Registered mixed test panel', 'Published-game subpanel')):
        for index, (metric, color) in enumerate((('precision','#147d92'), ('recall','#8057b3'), ('abstention_rate','#cb7b1b'))):
            values = [fields['summaries']['trained'][population][family]['metrics'][metric] for family in FAMILIES]
            axis.bar(np.arange(4)+(index-1)*.24, [value if value is not None else 0 for value in values], width=.22,
                color=color, label=metric.replace('_', ' ').capitalize())
        axis.set_xticks(range(4), ['Attack', 'Defense', 'Mobility', 'King\nexposure'])
        axis.set_ylim(0, 1.08)
        axis.set_title(title)
        axis.grid(axis='y', alpha=.2)
        axis.set_axisbelow(True)
    axes[0].set_ylabel('Measured relation rate')
    axes[1].legend(loc='lower right', framealpha=.95)
    fig.suptitle('Cycle 11: local conditional influence, separate from legal play', fontsize=13)
    fig.text(.02, -.025, 'Structured populations; unknowns remain abstentions. Confidence intervals and error counts are in the linked report. No strategic-success claim.', fontsize=9)
    fig.tight_layout()
    save(fig, 'relation-results')

    fig, axes = plt.subplots(2, 2, figsize=(9.5, 8), sharex=True, sharey=True)
    for axis, family, color in zip(axes.flat, FAMILIES, COLORS):
        record = calibration['families'][family]
        bins = [b for b in record['raw_all']['bins'] if b['count']]
        axis.plot([0,1], [0,1], color='#999999', linestyle='--', linewidth=1)
        axis.plot([b['mean_strength'] for b in bins], [b['observed_frequency'] for b in bins], color=color)
        axis.scatter([b['mean_strength'] for b in bins], [b['observed_frequency'] for b in bins],
            s=[25+min(100, b['count']**.5) for b in bins], color=color)
        axis.set_title(f"{family.replace('-', ' ').title()} · raw Brier {record['raw_all']['brier']:.4f}")
        axis.set_xlim(-.03, 1.03)
        axis.set_ylim(-.03, 1.03)
        axis.grid(alpha=.2)
        axis.set_xlabel('Raw PLN strength used as a diagnostic score')
        axis.set_ylabel('Observed positive-label frequency')
    fig.suptitle('Held-out reliability diagnostics; confidence is not a probability', fontsize=13)
    fig.tight_layout()
    save(fig, 'relation-reliability')

    names = list(performance['workloads'])
    fig, axis = plt.subplots(figsize=(11.5, 5.6))
    for index, (condition, label, color) in enumerate((
        ('full-cold','Cold field','#8057b3'), ('full-warm','Warm field','#cb7b1b'),
        ('successor-full-cold','Full successor','#147d92'), ('successor-incremental','Incremental successor','#b64c60'))):
        records = [performance['workloads'][name][condition] for name in names]
        values = [r['median_seconds'] for r in records]
        axis.bar(np.arange(len(names))+(index-1.5)*.2, values, width=.19, color=color, label=label)
        axis.errorbar(np.arange(len(names))+(index-1.5)*.2, values,
            yerr=[[m-r['minimum_seconds'] for m,r in zip(values,records)], [r['maximum_seconds']-m for m,r in zip(values,records)]],
            fmt='none', ecolor='#333333', linewidth=.7, capsize=2)
    axis.set_xticks(range(len(names)), [name.replace('-', '\n') for name in names])
    axis.set_ylabel('Wall seconds (log scale)')
    axis.set_yscale('log')
    axis.set_title('Exact field-cache parity: medians and measured min–max ranges')
    axis.legend(ncol=2, loc='upper left', fontsize=9)
    axis.grid(axis='y', alpha=.2)
    axis.set_axisbelow(True)
    fig.text(.02, -.02, f"{performance['repetitions']} repetitions in isolated workers; Python allocation tracking adds overhead. Native proof identities match full recomputation.", fontsize=9)
    fig.tight_layout()
    save(fig, 'field-performance')
    (directory / 'manifest.json').write_text(json.dumps(dict(inputs={name:hashlib.sha256((out/name).read_bytes()).hexdigest() for name in files},
        outputs=outputs, matplotlib=matplotlib.__version__, numpy=np.__version__, labels='Measured diagnostics; no inferred strategic values or calibrated native confidence.'), indent=2, sort_keys=True)+'\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True)
    run(parser.parse_args().out)
