"""Source-bound authorization of the unchanged operational legal checkpoint."""
import os
from pathlib import Path
from pln_chess.common import ROOT, read_json, digest
from pln_chess.cycle6.inference import production_code_hash

CHECKS=('baseline','current_native_parity','historical_regression','negative_controls','native_boundary',
    'field_isolation','cache_parity','temporal_robustness','tests','clean_bootstrap','dataset_integrity',
    'api_compatibility','artifact_preservation')


def accepted_model(model,legacy=False):
    path=Path(os.environ.get('C11_OUT',ROOT/'artifacts/cycle11'))/'acceptance.json'
    receipt=read_json(path) if path.exists() else {}
    config=read_json(ROOT/'configs/cycle11.json')
    allowed=read_json(ROOT/'artifacts/cycle10/acceptance.json')['accepted_legacy_model_versions'] if legacy else [config['accepted_model_version']]
    field='accepted_legacy_model_versions' if legacy else 'accepted_model_versions'
    original=(receipt.get('passed') is True and receipt.get('all_required_checks_executed') is True
        and all(receipt.get('checks',{}).get(key) is True for key in CHECKS)
        and receipt.get('new_learning_promoted') is False and receipt.get('field_model_is_default') is False
        and model.version in allowed and model.version in receipt.get(field,[])
        and receipt.get('runtime_version')==model.runtime_version
        and receipt.get('production_code_hash')==production_code_hash()
        and receipt.get('registration_hash')==digest(config)
        and receipt.get('legacy_registrations')=={str(i):digest(read_json(ROOT/f'configs/cycle{i}.json')) for i in (6,7,8,9,10)})
    if original:return True
    if 'C11_OUT' in os.environ:return False
    from pln_chess.cycle12.acceptance import accepted_model as current
    return current(model,legacy)
