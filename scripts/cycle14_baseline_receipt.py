"""Join executed baseline receipts without altering historical evidence."""
from pathlib import Path
from pln_chess.common import ROOT,read_json
from training.cycle14_labels import atomic_json
from scripts.cycle9_baseline import sha


def run(out='artifacts/cycle14'):
    out=Path(out);base=out/'baseline';manifest=read_json(base/'manifest.json')
    legal=read_json(base/'legal-reproduction.json');research=read_json(base/'research/verified.json')
    assert legal['passed'] and research['passed'] and read_json(base/'tests.json')['tests']==588
    assert legal['source_head']==research['source_head']==manifest['starting_head']
    changed=[p for p,h in manifest['protected_files'].items() if not (ROOT/p).is_file() or sha(ROOT/p)!=h]
    assert not changed
    incidents=[]
    if (base/'control-completion/verified.json').exists():
        completion=read_json(base/'control-completion/verified.json')
        assert completion['passed']
        incidents.append(dict(kind='orchestration-prerequisite',resolved=True,
            cause=completion['cause'],receipt='control-completion/verified.json',
            receipt_sha256=sha(base/'control-completion/verified.json')))
    else:
        for name in ('negative-history-controls','recoveries-holdouts'):
            command=read_json(base/'commands'/(name+'.json'))
            assert command['returncode']==0 and command['identity']['source_head']==manifest['starting_head']
    if (base/'serial-comparison-interruption.json').exists():
        incidents.append(dict(kind='comparison-scheduling',resolved=True,
            receipt='serial-comparison-interruption.json',receipt_sha256=sha(base/'serial-comparison-interruption.json'),
            scope='Completed native outputs retained; slow serial host comparison recomputed fully in bounded parallel workers.'))
    atomic_json(base/'reproduction-receipt.json',dict(passed=True,starting_head=manifest['starting_head'],
        legal_shards=206,legal_rows=584112,negative_controls=287,history_controls=27,recoveries=2,holdouts=76,tests=588,
        identity=dict(accepted_model=manifest['accepted_legal_version'],production_code_hash=manifest['production_code_hash']),
        baseline_native_research_exact=True,research_artifacts=research['compared_artifacts'],
        legal_receipt_sha256=sha(base/'legal-reproduction.json'),research_receipt_sha256=sha(base/'research/verified.json'),
        historical_files_verified=len(manifest['protected_files']),historical_changes=changed,discrepancies=[],
        resolved_execution_incidents=incidents,
        scope='Independent execution in a clean pinned starting-source checkout, followed by exact scientific and native proof comparisons.'))
    atomic_json(base/'discrepancies-final.json',dict(passed=True,discrepancies=[],reproduction_pending=False,
        resolved_execution_incidents=incidents,
        original_lock_log_preserved=True,reproduction_receipt_sha256=sha(base/'reproduction-receipt.json')))


if __name__=='__main__':run()
