"""Source-bound legal promotion; experimental fields/concepts cannot be defaults."""
import os
from pathlib import Path
from pln_chess.common import ROOT, read_json, digest
from pln_chess.cycle6.inference import production_code_hash

CHECKS=('baseline','current_native_parity','historical_regression','negative_controls','native_boundary',
    'field_concept_isolation','cache_parity','temporal_robustness','tests','clean_bootstrap','dataset_integrity',
    'api_compatibility','artifact_preservation','complete_legal_review','concept_provenance','temporal_replay',
    'incremental_parity','research_reproduction')


def output_root():return Path(os.environ.get('C12_OUT',ROOT/'artifacts/cycle12'))


def accepted_model(model,legacy=False):
    path=output_root()/'acceptance.json'
    if not path.exists() or getattr(model,'schema',None) not in (6,7,8):return False
    receipt=read_json(path);config=read_json(ROOT/'configs/cycle12.json')
    promoted=receipt.get('legal_candidate_promoted') is True
    allowed=[config['accepted_legal_model_version']]
    if promoted:allowed.append(config['promotion_candidate_version'])
    if legacy:allowed=read_json(ROOT/'artifacts/cycle10/acceptance.json')['accepted_legacy_model_versions']
    field='accepted_legacy_model_versions' if legacy else 'accepted_model_versions'
    expected_default=config['promotion_candidate_version'] if promoted else config['accepted_legal_model_version']
    original=(receipt.get('passed') is True and receipt.get('all_required_checks_executed') is True
        and all(receipt.get('checks',{}).get(key) is True for key in CHECKS)
        and receipt.get('field_model_is_default') is False and receipt.get('concept_model_is_default') is False
        and receipt.get('default_model_version')==expected_default
        and model.version in allowed and model.version in receipt.get(field,[])
        and receipt.get('runtime_version')==model.runtime_version
        and receipt.get('production_code_hash')==production_code_hash()
        and receipt.get('registration_hash')==digest(config)
        and receipt.get('legacy_registrations')=={str(i):digest(read_json(ROOT/f'configs/cycle{i}.json')) for i in (6,7,8,9,10,11)})
    if original:return True
    if 'C12_OUT' in os.environ:return False
    from pln_chess.cycle13.acceptance import accepted_model as current
    return current(model,legacy)


def default_checkpoint(fallback):
    """Use a new default only after its source-bound acceptance is available."""
    if any(key in os.environ for key in ('C6_OUT','C7_OUT','C8_OUT','C9_OUT','C10_OUT','C11_OUT')):return fallback
    path=output_root()/'model/C12-default.json'
    if not path.exists():return fallback
    from pln_chess.learning import Model
    from pln_chess.pln import Runtime
    model=Model.load(path,Runtime())
    if accepted_model(model) and model.version==read_json(output_root()/'acceptance.json')['default_model_version']:return path
    return fallback
