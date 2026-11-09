"""Standalone research figures; run with a matplotlib environment."""
import argparse
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def run(out):
    out=Path(out);dest=out/'analysis/figures';dest.mkdir(parents=True,exist_ok=True)
    read=lambda path:json.loads((out/path).read_text())
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    def save(fig,name):
        fig.tight_layout()
        for suffix in ('png','svg','pdf'):fig.savefig(dest/(name+'.'+suffix),dpi=170,bbox_inches='tight')
        plt.close(fig)
    frozen=read('analysis/frozen-summary.json');temporal=read('analysis/temporal-summary.json')
    names=[n for n in frozen if n.startswith('external-test/')];labels=[n.split('/',1)[1].replace('lichess-','').replace('tcec-','') for n in names]
    fig,axes=plt.subplots(1,2,figsize=(12,4))
    for axis,metric,title in zip(axes,('recall','exact_move_set_accuracy'),('Legal-move recall','Exact legal-move sets')):
        for offset,report,label,color in [(-.18,frozen,'Frozen FEN-only','#4267ac'),(.18,temporal,'Same model + recorded history','#169b81')]:
            values=[report[n]['complete'][metric]*100 for n in names]
            axis.bar([i+offset for i in range(len(names))],values,width=.35,label=label,color=color)
            for i,name in enumerate(names):
                low,high=report[name]['intervals']['interval95'][metric]
                x=i+offset;axis.vlines(x,100*low,100*high,color='#172335',linewidth=1.2)
                axis.hlines([100*low,100*high],x-.035,x+.035,color='#172335',linewidth=1.2)
        axis.set_xticks(range(len(names)),labels,rotation=15,ha='right');axis.set_ylim(0,105);axis.set_ylabel('Percent');axis.set_title(title)
    axes[0].legend(fontsize=8);fig.suptitle('External final test: identical accepted C8 model, different supplied evidence\n95% game-cluster bootstrap intervals; residual opening/player dependence remains',fontsize=11)
    save(fig,'external-generalization')
    calibration=read('calibration/results.json');fig,axis=plt.subplots(figsize=(10,4))
    for offset,key,label,color in [(-.25,'raw-strength','Raw strength diagnostic','#b8714c'),(0,'frozen-C9','Frozen C9 map','#4267ac'),(.25,'external-validation-fit','External validation map','#169b81')]:
        values=[calibration['results']['in-board/'+n]['measurements'][key]['brier'] for n in names]
        axis.bar([i+offset for i in range(len(names))],values,width=.24,label=label,color=color)
    axis.set_xticks(range(len(names)),labels,rotation=15,ha='right');axis.set_yscale('log');axis.set_ylabel('Brier score (log scale; lower is better)')
    axis.set_title('Distribution shift: in-board diagnostics; no effect on native classification');axis.legend(fontsize=8);save(fig,'calibration-shift')
    before=read('performance/C9-external.json');after=read('performance/C10-current.json');fig,axes=plt.subplots(1,2,figsize=(13,4))
    labels=[r['fixture']['id'].replace('dense-','').replace('lichess-','').replace('tcec-','') for r in before['records']]
    for axis,mode in zip(axes,('cold','warm')):
        for offset,report,label,color in [(-.18,before,'C9 source','#4267ac'),(.18,after,'C10 source','#169b81')]:
            values=[r['aggregates'][mode]['latency_seconds']['p50'] for r in report['records']]
            axis.bar([i+offset for i in range(len(values))],values,width=.35,label=label,color=color)
        axis.set_xticks(range(len(labels)),labels,rotation=35,ha='right');axis.set_ylabel('Median seconds');axis.set_title(mode.title()+' inference');axis.legend(fontsize=8)
    fig.suptitle('Nine serial repetitions per source/mode; full candidate and native proof parity')
    save(fig,'performance')
    small=read('analysis/small-summary.json');large=read('analysis/large-summary.json');adapt=read('adaptation/summary.json')
    x=[0,adapt['models']['small']['training_report']['records'],adapt['models']['large']['training_report']['records']]
    fig,axis=plt.subplots(figsize=(8,4))
    for metric,label,color in [('recall','Recall','#4267ac'),('exact_move_set_accuracy','Exact sets','#169b81')]:
        values=[r['external-test']['complete'][metric]*100 for r in (frozen,small,large)]
        axis.plot(x,values,'o-',label=label,color=color)
        for at,report in zip(x,(frozen,small,large)):
            low,high=report['external-test']['intervals']['interval95'][metric]
            axis.vlines(at,100*low,100*high,color=color,linewidth=1.3)
            axis.hlines([100*low,100*high],at-4,at+4,color=color,linewidth=1.3)
    axis.set_xlabel('Additional external observations (nested 6 / 24 games)');axis.set_ylabel('Percent');axis.set_ylim(0,105)
    axis.set_title('Controlled adaptation on untouched opening-family test holdouts\n95% game-cluster bootstrap intervals',fontsize=11);axis.legend();save(fig,'sample-efficiency')
    failures=read('analysis/frozen-failure-index.json');counts=failures['categories'];fig,axis=plt.subplots(figsize=(10,6))
    ordered=sorted(counts,key=lambda k:counts[k]['candidates']);axis.barh(ordered,[counts[k]['candidates'] for k in ordered],color='#4267ac')
    axis.set_xlabel('Affected candidates (categories can overlap)');axis.set_title('Frozen failure census: structural triage, not automatic causal proof');save(fig,'failure-taxonomy')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);run(p.parse_args().out)
