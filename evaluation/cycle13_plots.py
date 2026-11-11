"""Standalone diagnostic figures from measured results; no inference imports.

Run with the analysis Python that provides matplotlib, independently of the
locked production environment. Input hashes and plotting versions are recorded.
"""
import argparse
import hashlib
import json
from pathlib import Path
import platform

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def run(out):
    out = Path(out).resolve()
    source = out / 'preferences/calibration.json'
    data = json.loads(source.read_text())
    shift_source = out / 'preferences/distribution-shift.json'
    shift = json.loads(shift_source.read_text())
    directory = out / 'figures'
    directory.mkdir(exist_ok=True)
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10,
        'axes.spines.top': False, 'axes.spines.right': False, 'svg.hashsalt': 'cycle13-preference-diagnostics'})
    outputs = []

    def save(figure, name):
        for extension in ('png', 'svg'):
            path = directory / (name + '.' + extension)
            metadata = {'Date': None} if extension == 'svg' else None
            figure.savefig(path, dpi=170, bbox_inches='tight', facecolor='white', metadata=metadata)
            outputs.append(dict(path=str(path.relative_to(out)), sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
        plt.close(figure)

    names = ['train', 'calibration', 'test', 'test-external-tactical']
    fig, axes = plt.subplots(2, 2, figsize=(10, 8.5), sharex=True, sharey=True)
    for axis, name in zip(axes.flat, names):
        record = data['panels'][name]
        bins = [b for b in record['reliability'] if b['n']]
        axis.plot([0, 1], [0, 1], '--', color='#a0a6ad', linewidth=1)
        if bins:
            axis.plot([b['mean_raw_strength'] for b in bins], [b['empirical_A_frequency'] for b in bins], color='#176f91')
            axis.scatter([b['mean_raw_strength'] for b in bins], [b['empirical_A_frequency'] for b in bins],
                s=[22 + min(100, b['n'] ** .5 * 8) for b in bins], color='#176f91')
        else:
            axis.text(.5, .5, 'No resolved directional labels', ha='center')
        score = record['brier_score']
        axis.set_title('{} · n={} · Brier {}'.format(name.replace('-', ' '), record['directional_examples'],
            'unavailable' if score is None else '{:.3f}'.format(score)))
        axis.set_xlim(-.03, 1.03)
        axis.set_ylim(-.03, 1.03)
        axis.set_xlabel('Raw A-channel PLN strength')
        axis.set_ylabel('Observed A-label frequency')
        axis.grid(alpha=.2)
    fig.suptitle('Preference reliability diagnostics; raw strength is not a calibrated probability', fontsize=12)
    fig.text(.02, -.02, 'Unknown and no-demonstrated labels are excluded from this binary diagnostic. Marker area indicates bin size.\nTraining is descriptive; held-out panels assess transfer. No calibration changes native inference.', fontsize=9)
    fig.tight_layout()
    save(fig, 'preference-reliability')

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.7))
    for name, color in zip(names[1:], ('#8057b3', '#176f91', '#b0681b')):
        records = data['panels'][name]['selective_risk']
        present = [r for r in records if r['accuracy'] is not None]
        axes[0].plot([r['min_confidence'] for r in records],
            [r['coverage'] if r['coverage'] is not None else float('nan') for r in records],
            marker='o', color=color, label=name.replace('-', ' '))
        axes[1].plot([r['coverage'] for r in present], [r['accuracy'] for r in present],
            marker='o', color=color, label=name.replace('-', ' '))
    for axis in axes:
        axis.set_xlim(-.03, 1.03)
        axis.set_ylim(-.03, 1.03)
        axis.grid(alpha=.2)
    axes[0].set_xlabel('Minimum raw confidence of an answered direction')
    axes[0].set_ylabel('Coverage of directionally labeled pairs')
    axes[1].set_xlabel('Coverage of directionally labeled pairs')
    axes[1].set_ylabel('Accuracy among answered directional pairs')
    axes[0].legend(frameon=False, fontsize=9)
    fig.suptitle('Selective preference accuracy and coverage; confidence is an evidence parameter', fontsize=12)
    fig.text(.02, -.03, 'Empty selections have undefined accuracy and are omitted. Small selected cohorts do not establish reliable move selection.', fontsize=9)
    fig.tight_layout()
    save(fig, 'preference-selective-coverage')

    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.7), sharex=True, sharey=True)
    pairs = (('independent-games','external-tactical'),('external-tactical','independent-games'))
    for axis, (training, target) in zip(axes, pairs):
        record = shift['studies'][training]['test_sources'][target]['calibration']
        bins = [b for b in record['reliability'] if b['n']]
        axis.plot([0,1],[0,1],'--',color='#a0a6ad',linewidth=1)
        axis.plot([b['mean_raw_strength'] for b in bins],[b['empirical_A_frequency'] for b in bins],
            marker='o',color='#8057b3')
        axis.set_title('{} training\n{} test · n={}'.format(training.replace('-', ' '),
            target.replace('-', ' '), record['directional_examples']))
        axis.set_xlim(-.03,1.03)
        axis.set_ylim(-.03,1.03)
        axis.set_xlabel('Raw A-channel PLN strength')
        axis.set_ylabel('Observed A-label frequency')
        axis.grid(alpha=.2)
    fig.suptitle('Source holdout: the test source family is absent from training',fontsize=12)
    fig.text(.02,-.03,'Fixed partitions and two curated source pools. This diagnostic does not establish reliability under arbitrary deployment shift.',fontsize=9)
    fig.tight_layout()
    save(fig,'preference-source-shift')
    (directory / 'manifest.json').write_text(json.dumps(dict(
        inputs={str(path.relative_to(out)): hashlib.sha256(path.read_bytes()).hexdigest() for path in (source,shift_source)},
        outputs=outputs, matplotlib=matplotlib.__version__, python=platform.python_version(),
        scope='Measured offline diagnostics only; no calibrated replacement for native truth values.'),
        sort_keys=True, indent=2) + '\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True)
    run(parser.parse_args().out)
