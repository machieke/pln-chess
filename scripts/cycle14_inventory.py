"""Final local package audit and noncircular content inventory."""
import argparse
from pathlib import Path
import re
import subprocess

from pln_chess.common import ROOT, read_json, write_json
from pln_chess.cycle6.inference import production_code_hash
from scripts.cycle9_baseline import sha


DOCUMENTS=('engineering-report','package-matrix','research-registration','reference-label-audit','dataset-provenance',
    'relative-representation','preference-learning','evidence-dependence','temporal-study','preference-reversals',
    'response-coverage','concept-generalization','evaluation-calibration','ablations','proof-storage','performance',
    'reproduction','readiness-decision')


def run(out):
    out=Path(out).resolve();code=production_code_hash()
    accepted=read_json(out/'acceptance.json');post=read_json(out/'post-acceptance/verified.json')
    assert accepted['passed'] and post['passed'] and accepted['production_code_hash']==code==post['production_code_hash']
    matrix=read_json(out/'delivery/package-matrix.json')['packages']
    assert [r['id'] for r in matrix]==[f'C14-{i:02}' for i in range(1,21)]
    assert all(r['engineering_delivery_status'] and r['research_outcome'] for r in matrix)
    documents=[ROOT/'docs/cycle14'/(name+'.md') for name in DOCUMENTS]
    assert all(p.is_file() and len(p.read_text())>200 for p in documents)
    broken=[];link_targets=[]
    generated={out/'delivery/artifact-inventory.json',out/'delivery/final-audit.json',out/'delivery/local-history.json'}
    all_documents=sorted(set(documents)|set((ROOT/'docs/cycle14').glob('*.md')))
    for path in all_documents:
        for target in re.findall(r'\]\(([^)]+)\)',path.read_text()):
            if target.startswith(('http:','https:','#')):continue
            local=target.split('#',1)[0]
            if local:
                resolved=(path.parent/local).resolve();link_targets.append(resolved)
                if not resolved.exists() and resolved not in generated:
                    broken.append(dict(document=str(path.relative_to(ROOT)),target=target))
    assert not broken,broken
    protected=read_json(out/'baseline/manifest.json')['protected_files']
    changes=[name for name,expected in protected.items() if not (ROOT/name).is_file() or sha(ROOT/name)!=expected]
    assert not changes
    assert sha(out/'model/C14-default.json')==sha(ROOT/'artifacts/cycle12/model/C12-default.json')
    assert sha(ROOT/'artifacts/cycle13/model/C13-default.json')==sha(out/'model/C14-default.json')
    partials=list(out.rglob('*.partial'));assert not partials,partials
    start=read_json(ROOT/'configs/cycle14.json')['starting_head']
    parent=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    commits=subprocess.check_output(['git','rev-list','--reverse',start+'..'+parent],cwd=ROOT,text=True).splitlines()
    write_json(out/'delivery/local-history.json',dict(starting_head=start,inventory_parent_head=parent,
        commits=[dict(commit=commit,subject=subprocess.check_output(['git','show','-s','--format=%s',commit],cwd=ROOT,text=True).strip()) for commit in commits],
        no_remote_write_performed=True,
        scope='Local history through the parent of the final inventory/evidence commit. The final commit cannot contain its own hash; the ending hash and clean worktree are reported after commit.'))
    excluded={out/'delivery/artifact-inventory.json',out/'delivery/final-audit.json'}
    artifacts={str(path.relative_to(out)):dict(bytes=path.stat().st_size,sha256=sha(path))
        for path in sorted(out.rglob('*')) if path.is_file() and path not in excluded}
    source_paths=set(all_documents)|{ROOT/'README.md',ROOT/'configs/cycle14.json',ROOT/'PLN_Chess_Cycle_14_Codex_Brief.md',ROOT/'proofshot.config.json'}
    source_paths.update(ROOT/name for name in read_json(out/'source-freeze.json')['production_sources'])
    for pattern in ('src/pln_chess/cycle14/*.py','src/pln_chess/cli/*14.py','training/cycle14*.py',
            'evaluation/cycle14*.py','scripts/cycle14*','tests/test_cycle14*.py'):
        source_paths.update(p for p in ROOT.glob(pattern) if p.is_file())
    write_json(out/'delivery/artifact-inventory.json',dict(schema='c14-local-delivery-inventory-v1',
        artifacts=artifacts,source_and_docs={str(p.relative_to(ROOT)):sha(p) for p in sorted(source_paths)},
        excluded_self_receipts=[str(p.relative_to(out)) for p in sorted(excluded)],
        scope='All retained Cycle 14 evidence, including failed/interrupted attempts; passing gates are identified separately by acceptance. Excludes these two mutually referring inventory/audit files to avoid circular hashes.'))
    write_json(out/'delivery/final-audit.json',dict(passed=True,production_code_hash=code,packages=20,
        required_documents=len(documents),all_documents=len(all_documents),document_links_checked=True,broken_links=broken,
        unchanged_historical_files=len(protected),historical_changes=changes,
        legal_checkpoint_byte_identical=True,artifact_files=len(artifacts),artifact_bytes=sum(v['bytes'] for v in artifacts.values()),
        inventory_sha256=sha(out/'delivery/artifact-inventory.json'),acceptance_sha256=sha(out/'acceptance.json'),
        post_acceptance_probe_sha256=sha(out/'post-acceptance/verified.json'),
        report_generation_parent_head=parent,
        no_push_or_deployment_performed=True,preferences_promoted=False,automatic_selection=False,
        scope='Local complete package audit before its evidence/documentation commit; the final commit hash and clean worktree are reported after commit.'))
    # These three targets are created by this invocation, including links to
    # the inventory itself. Validate their existence after writing them.
    assert all(path.exists() for path in link_targets)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',default='artifacts/cycle14');run(parser.parse_args().out)
