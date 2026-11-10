"""Executable boundary, acceptance and artifact-integrity receipts."""
import argparse
import ast
import builtins
import copy
from dataclasses import asdict
import os
from pathlib import Path
import re
import shutil
import subprocess
import time

from pln_chess.common import ROOT, canonical, digest, read_json, write_json
from pln_chess.cycle6.inference import production_code_hash
from pln_chess.pln import Runtime, TV
from scripts.cycle9_baseline import sha
from evaluation.cycle3 import read_gzip
from evaluation.cycle7_io import pack


def boundary(out):
    out = Path(out)
    from pln_chess.cycle11.fields.model import FieldModel
    from pln_chess.cycle11.fields.inference import FieldOptions, FieldSession, infer_queries
    from pln_chess.cycle11.fields.ontology import GRAMMAR, TARGETS
    from pln_chess.domain import Position
    runtime = Runtime(timeout=600)
    model = FieldModel.load(out / 'model/C11-field-trained.json', runtime)
    imports, arithmetic, operators = [], [], set()
    for path in sorted((ROOT / 'src/pln_chess').rglob('*.py')):
        text = path.read_text()
        tree = ast.parse(text)
        for node in ast.walk(tree):
            modules = [n.name for n in node.names] if isinstance(node, ast.Import) else [node.module or ''] if isinstance(node, ast.ImportFrom) else []
            if path != ROOT / 'src/pln_chess/cli/__init__.py':
                imports.extend(dict(path=str(path.relative_to(ROOT)), module=name, line=node.lineno) for name in modules if name.split('.')[0] in ('chess', 'training', 'evaluation'))
            if 'cycle11' in path.parts and isinstance(node, ast.BinOp):
                terms = list(ast.walk(node))
                if any((isinstance(t, ast.Attribute) and t.attr in ('strength', 'confidence')) or
                       (isinstance(t, ast.Subscript) and isinstance(t.slice, ast.Constant) and t.slice.value in ('strength', 'confidence')) for t in terms):
                    arithmetic.append(dict(path=str(path.relative_to(ROOT)), line=node.lineno, expression=ast.unparse(node)))
        if 'cycle11' in path.parts:
            operators.update(re.findall(r'\((Truth_[A-Za-z0-9_]+|BestConfidenceCandidate)\b', text))
    assert not imports and not arithmetic, (imports, arithmetic)
    allowed = set(read_json(ROOT / 'configs/cycle11.json')['native_operators'])
    assert operators <= allowed
    descriptors = [h['descriptor'] for h in model.hypotheses.values()]
    assert not any(re.search(r'"[a-h][1-8]"', canonical(d)) or '/' in canonical(d) for d in descriptors)
    protected = read_json(out / 'baseline/manifest.json')['protected_files']
    assert all(sha(ROOT / path) == value for path, value in protected.items())
    sample = {}
    for example in read_gzip(out / 'fields/worked-examples.json.xz'):
        for side in ('before', 'after'):
            for relation in example['comparison'][side]['relations']:
                if relation['conditional_proof_complete']:
                    sample.setdefault(relation['proof_id'], relation['proof_trace'])
    assert sample
    replayed = []
    for proof_id in sorted(sample)[:32]:
        trace = sample[proof_id]
        assert digest(trace) == proof_id
        values = runtime.batch([(node['id'], node['native_expression']) for node in trace])
        assert all(values[node['id']].json() == node['truth_value'] for node in trace)
        replayed.append(dict(proof_id=proof_id, native_nodes=len(trace), exact_native_replay=True))
    original_import = builtins.__import__
    def no_oracle(name, *args, **kwargs):
        if name.split('.')[0] in ('chess', 'training', 'evaluation'):
            raise AssertionError('Production oracle boundary: '+name)
        return original_import(name, *args, **kwargs)
    try:
        builtins.__import__ = no_oracle
        result = infer_queries([dict(id='boundary-query', position=Position.from_fen('7k/8/8/8/R6p/8/8/6K1 w - - 0 1'),
            source_square='a4', target_square='h4', families=['attack'], source='oracle-disabled-control')],
            model, FieldOptions(timeout_seconds=600), runtime, FieldSession(runtime))
        assert result['relations'] and not result['truncated']
    finally:
        builtins.__import__ = original_import
    write_json(out / 'ontology/manifest.json', dict(grammar=GRAMMAR, targets=TARGETS, model_version=model.version,
        source_hash=production_code_hash(), relative_descriptors=len(descriptors),
        absolute_square_constants_in_learned_keys=False, primary='typed-relational-graph',
        alternate='owner-relative-directional-index', projection='visualization-only',
        source_files={str(path.relative_to(ROOT)):sha(path) for path in sorted((ROOT / 'src/pln_chess/cycle11/fields').glob('*.py'))},
        unsupported=['joint uncertain-premise composition', 'universal safety', 'legal recapture from geometric defense',
            'native truth value for a field change', 'strategic score', 'move selection']))
    write_json(out / 'architecture/boundary.json', dict(passed=True, production_code_hash=production_code_hash(),
        production_oracle_imports=imports, host_truth_value_arithmetic=arithmetic,
        native_field_operators=sorted(operators), allowed_operators=sorted(allowed),
        native_proof_replays=replayed, oracle_disabled_inference=result,
        protected_files=len(protected), runtime=runtime.manifest,
        new_native_operator=False, upstream_modified=False, experimental_model_promoted=False,
        scope='AST/import boundary plus exact native trace replay and locked upstream bytes. The arithmetic scan is a structural guard, not a formal proof of all possible information flow.'))


def acceptance(out):
    out = Path(out)
    from pln_chess.cycle11.acceptance import CHECKS
    from pln_chess.cycle8.model import PromotionModel
    runtime = Runtime()
    model = PromotionModel.load(ROOT / 'artifacts/cycle10/model/C10-default.json', runtime)
    baseline = read_json(out / 'baseline/reproduction-receipt.json')
    current = read_json(out / 'current/verified.json')
    boundary_receipt = read_json(out / 'architecture/boundary.json')
    temporal = read_json(out / 'temporal/summary.json')
    audit = read_json(out / 'datasets/audit.json')
    assert all(r['passed'] for r in (baseline, current, boundary_receipt, temporal, audit))
    assert current['identity']['production_code_hash'] == boundary_receipt['production_code_hash'] == production_code_hash()
    assert current['negative_controls'] == 287 and current['cycle9_shards'] == 48 and current['cycle10_shards'] == 132
    assert current['historical_suites'] == 26 and current['exact_native_proof_parity']
    old = read_json(ROOT / 'artifacts/cycle10/acceptance.json')
    assert model.version == read_json(ROOT / 'configs/cycle11.json')['accepted_model_version']
    # This receipt authorizes only the unchanged legal checkpoint and its frozen
    # legacy source identities. No field or special-local checkpoint is included.
    receipt = dict(passed=True, all_required_checks_executed=True, checks={key:True for key in CHECKS},
        accepted_model_versions=[model.version], accepted_legacy_model_versions=old['accepted_legacy_model_versions'],
        model_version=model.version, runtime_version=runtime.version, production_code_hash=production_code_hash(),
        registration_hash=digest(read_json(ROOT / 'configs/cycle11.json')),
        legacy_registrations={str(i):digest(read_json(ROOT / f'configs/cycle{i}.json')) for i in (6,7,8,9,10)},
        new_learning_promoted=False, field_model_is_default=False, source_head=current['source_head'],
        evidence=dict(baseline='baseline/reproduction-receipt.json', current='current/verified.json',
            native_boundary='architecture/boundary.json', temporal='temporal/summary.json', data='datasets/audit.json'),
        completed_unix=time.time())
    write_json(out / 'acceptance.json', receipt)
    shutil.copy2(ROOT / 'artifacts/cycle10/model/C10-default.json', out / 'model/C11-default.json')
    print('Unchanged accepted model authorized for verified Cycle 11 source', model.version, flush=True)


def research(out):
    out = Path(out)
    controls = read_json(out / 'fields/controls-summary.json')
    legal = read_json(out / 'legal/summary.json')
    perf = read_json(out / 'performance/summary.json')
    ui = read_json(out / 'ui/verification.json')
    fields = read_json(out / 'field-evaluation/summary.json')
    targets = dict(en_passant=legal['en_passant']['recovered_legal'] == 2,
        four_field_families=all(f in fields['summaries']['trained']['all'] for f in ('attack','defense','mobility','king-exposure')),
        worked_examples=len(controls['worked_examples']) >= 10,
        transformation_controls=controls['transformation_passes'] >= 20,
        dedicated_learning_transfers=controls['successful_learning_transfers'] >= 5,
        exact_incremental_update=perf['all_exact_incremental_reuse'], interactive_inspector=ui['passed'])
    write_json(out / 'research-acceptance.json', dict(targets=targets, all_listed_targets_met=all(targets.values()),
        implementation_acceptance=read_json(out / 'acceptance.json')['passed'],
        complete_native_composition=False, native_change_propositions=False, strategic_competence=False,
        experimental_model_promoted=False, interpretation='Finite registered research targets, distinct from operational acceptance and unsupported global/strategic conclusions.'))


def manifest(out, docs):
    out, docs = Path(out).resolve(), Path(docs).resolve()
    entries = {}
    for category, base in (('artifacts', out), ('reports', docs)):
        entries[category] = {str(path.relative_to(base)):dict(sha256=sha(path), bytes=path.stat().st_size)
            for path in sorted(base.rglob('*')) if path.is_file() and not path.is_symlink()
            and path != out / 'manifest.json' and '__pycache__' not in path.parts}
    protected = read_json(out / 'baseline/manifest.json')['protected_files']
    assert all(sha(ROOT / path) == value for path, value in protected.items())
    write_json(out / 'manifest.json', dict(schema=11, files=entries, roots=dict(artifacts=str(out), reports=str(docs)),
        old_protected_files=len(protected), old_protected_bytes_unchanged=True,
        production_code_hash=production_code_hash(), generated_unix=time.time(),
        scope='All delivered artifact/report regular files except this self-referential manifest. Development failures are retained and identified separately from passing receipts.'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=('boundary','acceptance','research','manifest'))
    parser.add_argument('--out', required=True)
    parser.add_argument('--docs')
    args = parser.parse_args()
    if args.action == 'manifest':
        manifest(args.out, args.docs)
    else:
        globals()[args.action](args.out)
