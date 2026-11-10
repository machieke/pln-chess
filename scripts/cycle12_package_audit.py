"""Read-only final integrity check of the consolidated Cycle 12 package."""
import argparse
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

from pln_chess.common import ROOT, read_json
from pln_chess.cycle6.inference import production_code_hash
from scripts.cycle9_baseline import sha
from scripts.cycle12_reports import REQUIRED_REPORTS


def run(out, docs, require_visual_review=False):
    out, docs = Path(out).resolve(), Path(docs).resolve()
    manifest = read_json(out/'manifest.json')
    delivery = read_json(out/'delivery.json')
    code_hash = production_code_hash()
    assert manifest['production_code_hash'] == delivery['production_code_hash'] == code_hash
    assert delivery['passed'] and delivery['complete_delivery'] and delivery['engineering_packages'] == 20
    assert not any(delivery[k] for k in ('pushed', 'deployed', 'upstream_modified', 'new_native_operators'))
    checked = 0
    for category, base in (('artifacts', out), ('reports', docs)):
        actual = {str(p.relative_to(base)) for p in base.rglob('*')
                  if p.is_file() and not p.is_symlink() and p != out/'manifest.json'
                  and '__pycache__' not in p.parts and not p.name.endswith('.lock')}
        entries = manifest['entries'][category]
        assert actual == set(entries), (category, actual ^ set(entries))
        for name, identity in entries.items():
            path = base/name
            assert path.stat().st_size == identity['bytes'] and sha(path) == identity['sha256'], name
            checked += 1
    protected = read_json(out/'baseline/manifest.json')['protected_files']
    assert len(protected) == manifest['protected_prior_files'] == 7959
    assert all(sha(ROOT/name) == expected for name, expected in protected.items())
    for name, expected in delivery['evidence'].items():
        assert sha(out/name) == expected, name
    for name in ('acceptance.json', 'baseline/reproduction-receipt.json', 'current/verified.json',
                 'clean-research/verified.json', 'final-tests/verified.json', 'architecture/boundary.json',
                 'cli-smoke/verified.json', 'performance/summary.json', 'ui/verification.json'):
        assert read_json(out/name)['passed'], name
    legal = read_json(out/'legal/promotion-decision.json')
    default = read_json(out/'model/C12-default.json')
    assert default['version'] == legal['default_version'] == delivery['default_model_version']
    selected = ROOT/('artifacts/cycle11/model/C11-special-local.json' if legal['promoted']
                     else 'artifacts/cycle10/model/C10-default.json')
    assert sha(out/'model/C12-default.json') == sha(selected)
    reviews = list((out/'legal/evaluation').glob('*.receipt.json'))
    assert len(reviews) == 206
    if legal['promoted']:
        assert all(read_json(p)['passed'] for p in reviews)
    performance = read_json(out/'performance/summary.json')
    workers = list((out/'performance/workers').glob('*.json'))
    assert len(workers) == 42 and performance['repetitions'] == 7
    assert all(read_json(p)['exact_proof_evidence_graph_parity'] for p in workers)
    ui = read_json(out/'ui/verification.json')
    assert not ui['development_only'] and ui['source_hash'] == code_hash
    assert all(n == 0 for n in ui['errors'].values())
    assert ui['actual_export']['matchesServerResult']
    assert ui['server_cleanup']['port_closed'] and not ui['server_cleanup']['remaining_owned_browser_pids']
    if require_visual_review:
        assert read_json(out/'ui/visual-review.json')['passed']
    links = 0
    for name in REQUIRED_REPORTS:
        path = docs/(name+'.md')
        assert path.is_file(), path
        for target in re.findall(r'\]\(([^)]+)\)', path.read_text()):
            target = target.strip('<>')
            parts = urlsplit(target)
            if parts.scheme or not parts.path:
                continue
            linked = path.parent/unquote(parts.path)
            assert linked.exists(), (path, target)
            links += 1
    print(f'Cycle 12 package integrity passed: {checked} hashed files, {len(protected)} protected prior files, '
          f'{len(REQUIRED_REPORTS)} required reports, {links} local links, 206 legal reviews, 42 benchmark workers.', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True)
    parser.add_argument('--docs', default='docs/cycle12')
    parser.add_argument('--require-visual-review', action='store_true')
    args = parser.parse_args()
    run(args.out, args.docs, args.require_visual_review)
