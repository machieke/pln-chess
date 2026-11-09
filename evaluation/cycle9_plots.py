"""Standalone publication/export figures from measured diagnostics (matplotlib)."""
import argparse
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def run(out):
    out=Path(out);data=json.loads((out/'calibration/results.json').read_text())
    cohorts=('independent-games','adversarial','special-moves')
    fig,axes=plt.subplots(1,3,figsize=(13,4),constrained_layout=True)
    for ax,cohort in zip(axes,cohorts):
        scores=data['evaluations'][cohort]['in-board']
        ax.plot([0,1],[0,1],color='0.6',linestyle='--',label='identity reference')
        for name,label in [('raw-strength','Raw native strength'),('empirical-calibrated','Empirical diagnostic')]:
            bins=scores[name]['bins']
            ax.plot([b['mean_score'] for b in bins],[b['observed_legal_frequency'] for b in bins],marker='o',label=label)
        ax.set(xlim=(0,1),ylim=(0,1),title=cohort,xlabel='Score / diagnostic estimate',ylabel='Observed legal frequency')
        ax.grid(alpha=.2)
    axes[0].legend(fontsize=8);fig.suptitle('Cycle 9 reliability · in-board candidates · calibration fit on separate games')
    target=out/'calibration';target.mkdir(exist_ok=True)
    for suffix in ('svg','png','pdf'):fig.savefig(target/f'reliability.{suffix}',dpi=160)
    plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(10,4),constrained_layout=True)
    for cohort in cohorts:
        curve=data['evaluations'][cohort]['in-board']['selective_risk_coverage'];nonempty=[x for x in curve if x['n']]
        axes[0].plot([x['coverage'] for x in nonempty],[x['risk'] for x in nonempty],marker='o',label=cohort)
        axes[1].plot([x['min_native_confidence'] for x in curve],[x['coverage'] for x in curve],marker='o',label=cohort)
    axes[0].set(xlabel='Coverage',ylabel='Observed selective error rate',title='Selective risk')
    axes[1].set(xlabel='Minimum native confidence',ylabel='Coverage',title='Confidence filtering')
    for ax in axes:ax.grid(alpha=.2);ax.legend(fontsize=8)
    fig.suptitle('Diagnostic filtering only · native classifications are unchanged')
    for suffix in ('svg','png','pdf'):fig.savefig(target/f'selective-risk.{suffix}',dpi=160)
    plt.close(fig)
    (target/'plot-environment.json').write_text(json.dumps(dict(matplotlib=matplotlib.__version__,backend='Agg',source='evaluation/cycle9_plots.py'),indent=2)+'\n')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);run(p.parse_args().out)
