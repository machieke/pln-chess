"""Measured delivery report and checksummed evidence index."""
import hashlib,platform,subprocess
from pathlib import Path
from pln_chess.common import ROOT,read_json,write_json

PACKAGE_ROWS=[
 ('C2-01','complete','Frozen baseline and fresh reproduction','baseline/manifest.json; baseline/tests.txt'),
 ('C2-02','partial','Executable native probes; conjunction unavailable; two alternate layouts not integrated','native-probes.json; upstream-audit.json'),
 ('C2-03','complete','Schema-2 tiers and versioned loading','../../tests/test_cycle2.py; B1-model.json'),
 ('C2-04','complete','Local-key independence in focused perturbation and transforms','demonstrations.json'),
 ('C2-05','complete','Distance-agnostic occupancy and destination conditionals','demonstrations.json; dataset.json'),
 ('C2-06','complete','Specificity, native choice and conflict abstention','B2-model.json; ../../tests/test_cycle2.py'),
 ('C2-07','partial','Integrated opt-in induction; curriculum marginal assumptions remain experimental','B2-model.json; native-probes.json'),
 ('C2-08','complete','Idempotency, dependence, replay, rollback and integrity','pytest.txt; evidence.jsonl'),
 ('C2-09','complete','Disjoint context families/games, paired splits separate','dataset.json'),
 ('C2-10','partial','Separate learned attacks and exposure bridges; full temporal composition unsupported','demonstrations.json; B4-adversarial.json'),
 ('C2-11','complete','Exact native calculation reuse with full proof parity','benchmark.json'),
 ('C2-12','complete','API schema dispatch, CLI selectors, inspector comparison','ui-verification.json; pytest.txt'),
 ('C2-13','complete','Identical-split B0–B7, calibration and uncertainty','run-summary.json; calibration.json; B6-baselines.json'),
 ('C2-14','partial','Local reproduction verified; clean copy status below','clean-build.json; pytest.txt')]

def report():
    out=ROOT/'artifacts/cycle2';summary=read_json(out/'run-summary.json');bench=read_json(out/'benchmark.json');demos=read_json(out/'demonstrations.json')
    clean=read_json(out/'clean-build.json') if (out/'clean-build.json').exists() else {'status':'not yet executed'}
    ui=read_json(out/'ui-verification.json') if (out/'ui-verification.json').exists() else {'status':'not yet executed'}
    rows=[]
    for code,status,description,evidence in PACKAGE_ROWS:
        if code=='C2-14' and clean['status']=='passed':status='complete'
        if code=='C2-12' and ui['status']!='passed':status='partial'
        rows.append({'package':code,'status':status,'delivery':description,'evidence':evidence})
    write_json(out/'package-status.json',rows)
    fmt=lambda x:'n/a' if x is None else f'{x:.4f}'
    lines=['# Cycle 2 engineering delivery','',
           'Status: **native-partial**, with hierarchical relational transfer. No claim of complete compositional chess legality.',
           '',f"Baseline HEAD: `{summary['baseline_head']}`. The final delivery commit is available through `git log -1`; this report is generated before that commit. No Cycle 2 push or deployment is performed.",
           '',f"Dataset SHA-256: `{summary['dataset_hash']}`; seed {summary['seed']}. B2 model: `{summary['models']['B2']}`.",
           '', '## Package status','', '| Package | Status | Evidence / scope |','|---|---|---|']
    lines += [f"| {r['package']} | {r['status']} | {r['delivery']}. `artifacts/cycle2/{r['evidence']}` |" for r in rows]
    lines += ['', '## Identical independent held-out comparison','',
              '| Variant | Precision | Recall | F1 | Abstention | Exact sets | False legal |','|---|---:|---:|---:|---:|---:|---:|']
    for name,reports in summary['metrics'].items():
        m=reports['heldout-transfer'];lines.append('| '+name+' | '+' | '.join(fmt(m[k]) for k in ('precision','recall','f1','abstention_rate','exact_move_set_accuracy','false_legal_rate'))+' |')
    lines += ['', 'B0 is the frozen Cycle 1 checkpoint scored on this same new dataset. B6 evaluation-only geometry/absolute baselines are in `artifacts/cycle2/B6-baselines.json`. Full reports contain in-board/per-piece metrics, uncertainty, self-check errors and proof-tier coverage. The 40 held-out positions comprise 36 long-ray/clutter cases and four independent source games; these results do not establish all-chess competence.',
              '', '### Split detail and regressions','', '| Variant | Split | Precision | Recall | Abstention | Self-check false legal |','|---|---|---:|---:|---:|---:|']
    for name in ('B0','B1','B2'):
        for split,m in summary['metrics'][name].items():lines.append(f"| {name} | {split} | {fmt(m['precision'])} | {fmt(m['recall'])} | {fmt(m['abstention_rate'])} | {m['self_check_false_legal']} |")
    lines += ['', 'Induction alternatives are retained with their native premises and population counts, even when direct revised evidence wins native confidence choice. Equal B1/B2 metrics are a null result for induction selection, not evidence of improvement from induction. Calibration is fit on validation only; confidence is not a calibrated outcome probability.',
              '', '## New reusable motifs','']
    for example in demos['generalization_examples']:
        fixture=example['test_fixture'];h=example['hypothesis']
        lines += [f"- **{example['piece']} / {example['classification']}**: unseen `{fixture['fen']}`, move `{fixture['focus_move']}`. Rule `{h['id']}` (tier {h['tier']}), native TV `{example['truth_value']}`. Local descriptor `{h['descriptor']}`. Training evidence: `{example['training_examples'][0]}`. {example['novelty']}"]
    lines += ['',f"Irrelevant-context movement ID/TV checks: `{demos['locality_invariance']}`. Complete proofs and training references: `artifacts/cycle2/demonstrations.json`.",
              '', '## Native execution and performance','',
              'Production uses untouched upstream `Truth_Revision`, `Truth_ModusPonens`, `Truth_Negation` and `BestConfidenceCandidate`. Opt-in induction additionally uses `Truth_w2c` and `Truth_Induction`. Exact source lines, expressions and outputs: `artifacts/cycle2/native-probes.json`. The inheritance wrapper marginal-order issue and conjunction boundary are documented in `docs/cycle2/native-pln-feasibility.md`.',
              '', '| Schedule | Native calls | Logical nodes | Seconds |','|---|---:|---:|---:|']
    for r in bench['runs']:lines.append(f"| {r['mode']} | {r['native_invocations']} | {r['scheduled_invocations']} | {r['elapsed_seconds']:.4f} |")
    lines += ['',f"On {bench['candidates']} candidates: cold speedup {bench['cold_speedup']:.2f}×; call reduction {bench['call_reduction']:.2f}×. Exact proof/TV/rule/lineage parity: **{bench['parity']}**. Warm results reuse raw native computations; no persistent PeTTa process. This scheduler comparison uses the same Cycle 2 model on both sides. The reproduced Cycle 1 timings are separately archived in `artifacts/cycle2/baseline/benchmark.json`.",
              '', '## Verification and reproduction','', f"Tests: **{summary['tests']}**. Clean-copy status: **{clean['status']}**. Browser verification: **{ui['status']}**.",
              '', '```bash','bash scripts/cycle2_reproduce.sh',
              '.venv/bin/pln-chess cycle2 --action audit',
              '.venv/bin/pln-chess inspect --checkpoint artifacts/cycle2/B1-model.json --fen "8/6k1/8/8/8/2R5/2K5/8 w - - 0 1" --move c3f3',
              '.venv/bin/pln-chess serve --port 8765 --checkpoint artifacts/cycle2/B1-model.json','```',
              '', 'Prerequisites remain SWI-Prolog 10.0.1 with Janus/PCRE and uv. Bootstrap verifies native hashes and installs pinned Python 3.12.12 dependencies. The reproduction archive restores the frozen baseline if outputs are absent; it never regenerates over Cycle 1 originals. `--resume` reuses compatible evaluation outputs, while the default regenerates all Cycle 2 experiments.',
              '', '## Remaining work','',
              'Native conjunction remains unsupported. Priorities are a maintained multi-premise rule with dependence semantics, statistically justified induction populations, broader independent games/special moves and perturbations, stronger temporal constraints, and bounded cache retention. See `limitations.md` for every host-derived/non-compositional step and measurement limitation.']
    (ROOT/'docs/cycle2/final-report.md').write_text('\n'.join(lines)+'\n')
    write_json(out/'environment.json',{'python':platform.python_version(),'platform':platform.platform(),'machine':platform.machine(),'cpu':platform.processor(),
                                      'swipl':subprocess.check_output(['swipl','--version'],text=True).strip(),'runtime_lock':'configs/runtime-lock.json'})
    inventory={}
    for parent in (ROOT/'src',ROOT/'training',ROOT/'evaluation',ROOT/'scripts',ROOT/'tests',ROOT/'docs/cycle2',out):
        for p in sorted(parent.rglob('*')):
            if p.is_file() and '__pycache__' not in p.parts and p.name not in ('file-manifest.json','reproduction.log','clean-bootstrap.log') and '.egg-info' not in str(p):inventory[str(p.relative_to(ROOT))]=hashlib.sha256(p.read_bytes()).hexdigest()
    write_json(out/'file-manifest.json',{'files':inventory,'baseline_head':summary['baseline_head'],'generated_before_delivery_commit':True})
    return ROOT/'docs/cycle2/final-report.md'
