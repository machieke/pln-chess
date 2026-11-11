"""Source-bound recognition of the unchanged legal model, without preferences."""
import hashlib
import os
from pathlib import Path
from pln_chess.common import ROOT,read_json,digest
from pln_chess.cycle6.inference import production_code_hash

CHECKS=('baseline','current_native_parity','negative_controls','tests','clean_bootstrap','native_boundary',
    'preference_isolation','cache_parity','concept_preservation','dataset_integrity','artifact_preservation',
    'api_compatibility','temporal_robustness','research_reproduction')


def output_root():
    return Path(os.environ.get('C13_OUT',ROOT/'artifacts/cycle13'))


def accepted_model(model,legacy=False):
    if getattr(model,'schema',None) not in (6,7,8):
        return False
    path=output_root()/'acceptance.json'
    if not path.exists():
        return False
    receipt=read_json(path);config=read_json(ROOT/'configs/cycle13.json')
    allowed=read_json(ROOT/'artifacts/cycle12/acceptance.json')['accepted_legacy_model_versions'] if legacy else [config['accepted_legal_model_version']]
    field='accepted_legacy_model_versions' if legacy else 'accepted_model_versions'
    original=(receipt.get('passed') is True and receipt.get('all_required_checks_executed') is True
        and all(receipt.get('checks',{}).get(name) is True for name in CHECKS)
        and receipt.get('preference_model_is_default') is False and receipt.get('new_legal_learning_promoted') is False
        and receipt.get('default_model_version')==config['accepted_legal_model_version']
        and model.version in allowed and model.version in receipt.get(field,[])
        and receipt.get('runtime_version')==model.runtime_version
        and receipt.get('production_code_hash')==production_code_hash()
        and receipt.get('registration_hash')==digest(config)
        and receipt.get('legacy_registrations')=={str(i):digest(read_json(ROOT/f'configs/cycle{i}.json')) for i in range(6,13)})
    if not original:
        return False
    gates=receipt.get('gate_receipts',{})
    if set(gates)!=set(CHECKS):
        return False
    for gate in gates.values():
        relative=Path(gate.get('path',''))
        if relative.is_absolute() or '..' in relative.parts or not relative.parts:
            return False
        target=output_root()/relative
        if not target.is_file() or hashlib.sha256(target.read_bytes()).hexdigest()!=gate.get('sha256'):
            return False
    return True


def default_checkpoint(fallback):
    from pln_chess.cycle12.acceptance import default_checkpoint as previous
    if any(f'C{i}_OUT' in os.environ for i in range(6,13)):
        return previous(fallback)
    path=output_root()/'model/C13-default.json'
    if path.exists():
        from pln_chess.learning import Model
        from pln_chess.pln import Runtime
        if accepted_model(Model.load(path,Runtime())):
            return path
    return previous(fallback)
