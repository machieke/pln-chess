"""Source-bound implementation acceptance, with no promotion of new learning."""
import os
from pathlib import Path
from pln_chess.common import ROOT,read_json,digest
from pln_chess.cycle6.inference import production_code_hash

CHECKS=('baseline','historical_regression','negative_controls','native_boundary','proof_provenance',
        'cache_parity','tests','clean_bootstrap','dataset_integrity','evidence_replay','temporal_controls')


def accepted_model(model,legacy=False):
    path=Path(os.environ.get('C9_OUT',ROOT/'artifacts/cycle9'))/'acceptance.json'
    r=read_json(path) if path.exists() else {};field='accepted_legacy_model_versions' if legacy else 'accepted_model_versions'
    original=(r.get('passed') is True and r.get('all_required_checks_executed') is True
        and all(r.get('checks',{}).get(k) is True for k in CHECKS)
        and r.get('new_learning_promoted') is False and model.version in r.get(field,[])
        and r.get('runtime_version')==model.runtime_version and r.get('production_code_hash')==production_code_hash()
        and r.get('registration_hash')==digest(read_json(ROOT/'configs/cycle9.json'))
        and r.get('legacy_registrations')=={str(i):digest(read_json(ROOT/f'configs/cycle{i}.json')) for i in (6,7,8)})
    if original:return True
    if 'C9_OUT' in os.environ:return False
    from pln_chess.cycle10.acceptance import accepted_model as current
    return current(model,legacy)
