"""Source-bound implementation acceptance; experimental learning is never default."""
import os
from pathlib import Path
from pln_chess.common import ROOT,read_json,digest
from pln_chess.cycle6.inference import production_code_hash

CHECKS=('baseline','historical_regression','cycle9_comparison','negative_controls','native_boundary',
        'proof_provenance','cache_parity','tests','clean_bootstrap','dataset_integrity',
        'frozen_external','temporal_transport','temporal_controls','calibration_shift','adaptation_reporting')


def accepted_model(model,legacy=False):
    path=Path(os.environ.get('C10_OUT',ROOT/'artifacts/cycle10'))/'acceptance.json'
    receipt=read_json(path) if path.exists() else {};field='accepted_legacy_model_versions' if legacy else 'accepted_model_versions'
    original=(receipt.get('passed') is True and receipt.get('all_required_checks_executed') is True
        and all(receipt.get('checks',{}).get(k) is True for k in CHECKS)
        and receipt.get('new_learning_promoted') is False and model.version in receipt.get(field,[])
        and receipt.get('runtime_version')==model.runtime_version
        and receipt.get('production_code_hash')==production_code_hash()
        and receipt.get('registration_hash')==digest(read_json(ROOT/'configs/cycle10.json'))
        and receipt.get('legacy_registrations')=={str(i):digest(read_json(ROOT/f'configs/cycle{i}.json')) for i in (6,7,8,9)})
    if original:return True
    if 'C10_OUT' in os.environ:return False
    from pln_chess.cycle11.acceptance import accepted_model as current
    return current(model,legacy)
