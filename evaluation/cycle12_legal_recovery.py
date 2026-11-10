"""Fresh current-source replay of the frozen two recoveries and 76 holdouts."""
import argparse
from pathlib import Path
import shutil
from pln_chess.common import ROOT, read_json, write_json
from pln_chess.cycle6.inference import production_code_hash
from scripts.cycle9_baseline import sha


def run(out):
    out=Path(out);assert read_json(out/'baseline/reproduction-receipt.json')['passed']
    target=out/'legal/recovery'
    for relative,source in [('baseline/reproduction-receipt.json',out/'baseline/reproduction-receipt.json'),
        ('model/C11-special-local.json',ROOT/'artifacts/cycle11/model/C11-special-local.json'),
        ('datasets/legal-curriculum.json',ROOT/'artifacts/cycle11/datasets/legal-curriculum.json'),
        ('legal/en-passant-before.json.xz',ROOT/'artifacts/cycle11/legal/en-passant-before.json.xz')]:
        destination=target/relative;destination.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,destination)
    from evaluation.cycle11_legal import run as evaluate
    evaluate(target)
    summary=read_json(target/'legal/summary.json')
    checks=dict(two_recoveries=summary['en_passant']['recovered_legal']==2,
        full_76_holdouts=summary['independent_holdouts']['cases']==summary['independent_holdouts']['full_position_exact_after']==76,
        no_errors=all(not s['errors'] and s['full_position_false_legal']==s['full_position_false_illegal']==s['full_position_incomplete']==0
            for s in [summary['en_passant'],summary['independent_holdouts'],*summary['historical_interventions'].values()]),
        removal_controls=all(all(status==('supported-legal' if family=='exposure' else 'unknown') for family,status in row.items())
            for row in summary['en_passant_removal_controls'].values()),
        no_new_strict_or_experimental_theorem=summary['strict_en_passant']==summary['experimental_en_passant']==['unknown','unknown'],
        checkpoint_unchanged=sha(target/'model/C11-special-local.json')==sha(ROOT/'artifacts/cycle11/model/C11-special-local.json'))
    write_json(target/'verified.json',dict(passed=all(checks.values()),checks=checks,summary=summary,
        production_code_hash=production_code_hash(),
        exposure_scope='Removing exposure does not retract this operational special-local conclusion. This is a retained inherited limitation, not a complete safety theorem.',
        historical_caveat='The two recovery cases are known development cases; the 76 controlled holdouts and 39 reused historical interventions remain separately labelled.'))
    assert all(checks.values()),checks


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',required=True);run(parser.parse_args().out)
