"""Reports summarize measured artifacts; missing runs are never called passed."""
from pathlib import Path
from pln_chess.common import ROOT,read_json,write_json


def final_report(output=None):
    summary=read_json(ROOT/'artifacts/run-summary.json')
    test_summary=(ROOT/'artifacts/pytest.txt').read_text().strip().splitlines()[-1]
    dataset=read_json(ROOT/'fixtures/dataset.json')
    audit=read_json(ROOT/'artifacts/runtime-audit.json')
    lines=['# Engineering delivery report','',
           'Status: a tested **native-partial** research package. Full compositional chess learning is blocked by the audited runtime’s missing conjunction introduction. This is not a complete chess engine.',
           '',f"Runtime: PLN `{audit['runtime']['pln']['commit']}`, PeTTa `{audit['runtime']['petta']['commit']}`, {audit['runtime']['swipl']}, Python {audit['runtime']['python']}.",
           '',f"Dataset: {len(dataset['positions'])} positions, {len(dataset['examples'])} candidates, seed {dataset['seed']}, chess {dataset['oracle']['version']}, SHA-256 `{dataset['hash']}`.",
           '', '## Measured results','', '| Split | Precision | Recall | F1 | Abstention | Exact move sets |','|---|---:|---:|---:|---:|---:|']
    def fmt(v): return 'n/a' if v is None else f'{v:.4f}'
    for split,data in summary['evaluations'].items():
        m=data['metrics'];lines.append(f"| {split} | {fmt(m['precision'])} | {fmt(m['recall'])} | {fmt(m['f1'])} | {fmt(m['abstention_rate'])} | {fmt(m['exact_move_set_accuracy'])} |")
    lines += ['', 'Abstentions count against recall. Out-of-board candidates are included; each JSON report also gives in-board metrics. Controlled-transfer is a paired demonstration, not independent structural generalization. Strict held-out families and games are disjoint from training.',
              '', '## Actual native traces','', '| Scenario | Strength | Confidence | Display |','|---|---:|---:|---|']
    for item in summary['demonstrations']:
        lines.append(f"| {item['fixture']} | {item['tv']['strength']:.8f} | {item['tv']['confidence']:.8f} | {item['classification']} |")
    lines += ['', 'Every trace is saved under `artifacts/proofs/`, with premise/conclusion TVs, native expressions, rule IDs, evidence lineage, runtime/model versions, budgets, and an evaluation-only oracle comparison.',
              '', '## Boundaries and limitations','',
              '- Native PLN: untouched upstream `|-` rules for modus ponens, negation and revision; native evidence choice. Deduction, inheritance and induction additionally have runnable audit tests.',
              '- Host structural processing: FEN parsing, candidate geometry, raw occupancy categories, structural successor states, typed relational fingerprints, dependency bookkeeping, and native invocation scheduling.',
              '- Oracle: only `training/` and `evaluation/` label and score moves/attacks. Production inference has no chess dependency; tests disable oracle imports at runtime.',
              '- Learned legality is conditional on a joint categorical observation. It is not a proved conjunction of movement, context and safety. The explicit unary attack → exposure → negative-legality chain can add counterevidence; no absence-of-attacks safety theorem is asserted.',
              '- All six piece grammars and structural castling/EP/promotion edits exist. Seen special-move examples have native conditional proofs, but full compositional/history semantics remain blocked. Standard castling boundary conventions appear only in structural state/I/O code.',
              '- Induction executes natively in the audit, but automated chess induction/population marginal estimation is not integrated. Training generalization is explicit host grouping by a finite typed relative schema plus native revision.',
              '- Dependence groups are conservative: only the first observation per hypothesis/group contributes. Correlated conflicts remain in the ledger and are excluded from confidence updates. Positive/negative channels share evidence and are selected, never revised together.',
              '- Sensor TV `(1, 0.99)` is an explicit FEN-reading assumption, not a measured calibration claim. Calibration is post-hoc validation-bin mapping for evaluation, with small-sample limitations.',
              '- Bounded observations intentionally lose information. Unseen relative combinations abstain, and selective accuracy must be read alongside coverage. No claim of chess parity or useful playing strength is made.',
              '- SWI-Prolog 10.0.1 (including Janus/PCRE) is a checked system prerequisite. Bootstrap downloads the exact PeTTa commit and installs pinned Python packages. Missing or mismatched native runtime exits explicitly.',
              '', '## Validation and commands','',
              '```bash','bash scripts/bootstrap.sh','.venv/bin/pytest -q',
              '.venv/bin/pln-chess runtime-audit',
              '.venv/bin/pln-chess inspect --fen "7k/8/8/8/8/8/2R5/2K5 w - - 0 1" --move c2e2',
              '.venv/bin/pln-chess invariance --fixture transfer-source --transform translate',
              '.venv/bin/pln-chess evaluate --split heldout-transfer',
              '.venv/bin/pln-chess benchmark --config configs/benchmark.json',
              '.venv/bin/pln-chess serve --port 8765','```','',
              f"Test suite: **{test_summary}**. Native audit passed: `{audit['passed']}`. Invariance passed: `{summary['invariance']['passed']}`. Test output: `artifacts/pytest.txt`. Timing/peak memory/checkpoint size: `artifacts/benchmark.json`. Calibration: `artifacts/calibration.json`. Ablations: `artifacts/ablations.json`. Evidence replay demonstration: `artifacts/proofs/evidence-revision.json`.",
              '', '## Files and next work','',
              'The exact authored-file inventory is `artifacts/file-manifest.json`. The user-provided plan is preserved. No commits, pushes, or deployment were performed.',
              '', '1. Verify a native conjunction/generalized multi-premise rule in an appropriate upstream runtime before replacing categorical legality with compositional proofs.',
              '2. Add native population-based induction with explicit marginal estimation and stronger dependence semantics.',
              '3. Expand independent structural families and calibration data; quantify and reduce the observed abstention and false-legal rates.',
              '4. Extend full-history and adversarial successor-state modeling; preserve unknown history.',
              '5. Profile and optimize native batching/grounding while preserving proof/evidence identity.']
    target=Path(output or ROOT/'docs/final-report.md');target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text('\n'.join(lines)+'\n');return target


def finish_delivery(runtime=None):
    """Refresh final tables, cross-color proof, and authored-file inventory."""
    import csv
    from pln_chess.pln import Runtime
    from pln_chess.api import compare_transforms,explain_move
    from pln_chess.domain import Position
    from pln_chess.spatial import color_flip
    from pln_chess.learning import Model
    from pln_chess.pln.audit import runtime_audit
    from evaluation.experiments import sample_efficiency
    runtime=runtime or Runtime(); artifacts=ROOT/'artifacts'
    runtime_audit(artifacts/'runtime-audit.json')
    summary=read_json(artifacts/'run-summary.json')
    with (artifacts/'metrics.csv').open('w') as file:
        fields=['precision','recall','f1','abstention_rate','exact_move_set_accuracy','false_legal_rate','incomplete_positions']
        writer=csv.writer(file);writer.writerow(['split']+fields)
        for split,report in summary['evaluations'].items(): writer.writerow([split]+[report['metrics'][k] for k in fields])
    timings=read_json(artifacts/'benchmark.json')
    with (artifacts/'benchmark.csv').open('w') as file:
        writer=csv.DictWriter(file,fieldnames=list(timings['samples'][0]));writer.writeheader();writer.writerows(timings['samples'])
    reports=summary['evaluations']
    write_json(artifacts/'transfer-report.json',{'strict_recall_gap':reports['train']['metrics']['recall']-reports['heldout-transfer']['metrics']['recall'],
               'controlled_recall_gap':reports['train']['metrics']['recall']-reports['controlled-transfer']['metrics']['recall'],
               'invariance':summary['invariance'],'warning':'Strict structural novelty and controlled paired translation are distinct experiments.'})
    model=Model.load(artifacts/'model.json',runtime)
    pawn=Position.from_fen('7k/8/8/8/8/8/2P5/K7 w - - 0 1')
    write_json(artifacts/'proofs/pawn-orientation-transfer.json',{
        'comparison':compare_transforms(pawn,'color-flip',model,'c2c4',runtime),
        'original':explain_move(pawn,'c2c4',model,runtime=runtime),
        'transformed':explain_move(color_flip(pawn),'c7c5',model,runtime=runtime)})
    write_json(artifacts/'sample-efficiency.json',sample_efficiency(read_json(ROOT/'fixtures/dataset.json'),runtime))
    final_report(ROOT/'docs/final-report.md');final_report(artifacts/'final-report.md')
    files=[str(p.relative_to(ROOT)) for parent in ('src','training','evaluation','scripts','tests','docs','configs','vendor') for p in sorted((ROOT/parent).rglob('*')) if p.is_file() and '__pycache__' not in p.parts]
    write_json(artifacts/'file-manifest.json',{'files':files,'root_files':['README.md','pyproject.toml','requirements-dev.lock','.gitignore'],'commits_created':False})
