"""Run the preregistered clean-reference strata before full feature closure."""
import argparse
from pathlib import Path
import subprocess

from pln_chess.common import ROOT,digest,read_json,write_json
from scripts.cycle9_baseline import sha
from training.cycle14_labels import worker


def run(source,out):
    source,out=Path(source).resolve(),Path(out).resolve();records=[]
    assert ROOT.resolve()!=source.parent.parent
    assert not subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True)
    for kind,filename,oldname in (('immediate','source-pairs.json','reference-labels.json'),
            ('temporal','temporal-comparisons.json','temporal-labels.json')):
        data=read_json(source/'datasets'/filename);sources={r['id']:r for r in data['records']}
        previous={r['id']:r['evidence_id'] for r in read_json(ROOT/'artifacts/cycle13/datasets'/oldname)['records']}
        generation=read_json(source/f'labels/{kind}-g1/index.json');chosen={}
        for row in sorted(generation['records'],key=lambda r:digest(['c14-clean-reference-selection',r['id']])):
            chosen.setdefault((row['label'],row['reason'],row['original_actor'],row['horizon']),row)
        for old in chosen.values():
            row={**sources[old['id']],'previous_reference_evidence_id':previous.get(old['id'])}
            fresh=worker((str(out),kind+'-g1',row,data['hash'],kind))
            assert fresh['evidence_id']==old['evidence_id']
            records.append(dict(id=old['id'],kind=kind,evidence_id=old['evidence_id'],
                actual_reported_nodes=fresh['actual_reported_nodes'],raw_sha256=fresh['raw_sha256']))
    write_json(out/'early-reference-replay.json',dict(passed=True,records=records,
        driver_sha256=sha(__file__),source_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        exact_semantic_search_parity=True,
        scope='The same hash-selected actor/horizon/label/cause strata used by the complete clean reproducer. Fresh pinned teacher searches are scheduled early; later verification validates and reuses these immutable records. No model predictions or feature outcomes select analyses.'))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--source',required=True);parser.add_argument('--out',required=True)
    args=parser.parse_args();run(args.source,args.out)
