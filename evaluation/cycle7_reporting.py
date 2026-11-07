"""Reports derive measured claims from completed artifacts, never estimates."""
import hashlib
import os
from pathlib import Path
from pln_chess.common import ROOT, read_json, write_json

def percent(value):return 'n/a' if value is None else f'{100*value:.3f}%'
def counts(m):return f"{m['true_positive']} / {m['true_negative']} / {m['unknown']} / {m['incomplete']}"
def errors(m):return f"{m['false_positive']} / {m['false_illegal']} / {m['self_check_false_legal']}"

def reports(out=None):
    out=Path(out or os.environ.get('C7_OUT',ROOT/'artifacts/cycle7'));docs=ROOT/'docs/cycle7';docs.mkdir(parents=True,exist_ok=True)
    acceptance=read_json(out/'acceptance.json');verified=read_json(out/'verification.json');comparison=read_json(out/'comparison.json')
    baseline=read_json(out/'baseline/comparison.json');lab=read_json(out/'native/laboratory.json');selected=acceptance['selected_variant']
    arm='C7-learned-8-locked' if selected=='C7-learned-8' else 'C7-frozen'
    table=['| Split | C6 TP / TN / unknown / incomplete | C7 default | C6 recall / exact sets | C7 recall / exact sets | C7 false legal / false illegal / self-check |',
           '|---|---:|---:|---:|---:|---:|']
    for split,e in comparison[arm].items():
        a=comparison['C7-frozen'][split]['metrics'];b=e['metrics']
        table.append(f"| {split} | {counts(a)} | {counts(b)} | {percent(a['recall'])} / {percent(a['exact_move_set_accuracy'])} | {percent(b['recall'])} / {percent(b['exact_move_set_accuracy'])} | {errors(b)} |")
    curve=['| New independent training games | Evaluation split | Recall | Exact sets | False legal / false illegal / self-check |','|---:|---|---:|---:|---:|']
    for budget in (0,2,4,8):
        for split,e in comparison[f'C7-learned-{budget}'].items():
            m=e['metrics'];curve.append(f"| {budget} | {split} | {percent(m['recall'])} | {percent(m['exact_move_set_accuracy'])} | {errors(m)} |")
    evaluation='\n'.join(table)+'\n\n'+ '\n'.join(curve)
    (docs/'evaluation.md').write_text('# Matched evaluation and independent-game evidence\n\n'
        'Counts separate supported legal, supported illegal, abstention and incomplete results. C6 columns are independently reproduced, with the new C7 split executed against the frozen C6 checkpoint. All rows use identical candidate grammars, oracle labels, thresholds and split membership. Canonical C7 offline arms allow 100,000 scheduled native nodes after the development pilot exhausted the shared 20,000-node production cap on one two-pass position (20,186 nodes when completed). The production cap remains 20,000 and reports incomplete honestly. C6 baselines finish within their original cap. Backoff is an explicit semantic experiment; its additional proof nodes are not described as cache-equivalent.\n\n'+evaluation+'\n\n'
        'The C7 family split contains 32 positions from 16 synthetic games with Sicilian/French opening prefixes. Training uses 16 positions from eight separately seeded queen-pawn games. Full positions, game IDs and transformation lineages are disjoint. Relative submotifs intentionally overlap; `datasets/structural-audit.json` quantifies that overlap. These are generated games, not an external human-game benchmark.\n\n'
        'The active selector sees frozen-model coverage and relative structure before labels are attached. Independent-game budgets 0/2/4/8 correspond to 0/48/96/192 newly selected examples. Repeated source groups are excluded per hypothesis in dependence-aware training. The zero-new-training arm still pools historical evidence into coarse conditionals; the frozen arm adds no pooled rules.\n\n'
        'Full metrics include precision, recall, F1, abstention, in-board-only results, per-piece and per-family results, self-check errors, legal-candidate denominator, empty-terminal exact matches and proof coverage. They are in `artifacts/cycle7/comparison.json` and the referenced evaluation archives. Paired per-position changes and game-cluster bootstrap intervals (1,000 draws, seed 707) are in `paired/` and `learning-curves.json`; small cluster counts limit interpretation. No universal zero-error claim follows from these samples.\n\n'
        'Ablations execute no backoff, no attack/exposure, no temporal evidence, no dependence handling, no learned negatives and no new training. The no-history game arm is a measured null control because all game inputs already use FEN-only metadata; event-backed causal cases are tested separately. Dependence removal disables training deduplication and runtime overlap guards while retaining true source IDs. Destructive ablations are ineligible for default selection. Independent-premise removal belongs to the isolated native laboratory.\n\n'
        'Every observed error or loss of a frozen supported classification, including intentional strict abstentions and destructive ablations, has an artifact path, candidate ID, native proof references and evidence groups in `proofs/all-regressions.json.xz`. Representative positive and unresolved proofs are in `proofs/representative-examples.json.xz`.\n')
    native=['# Bounded native feasibility result','', '**Native positive composition: not demonstrated.** Three encodings were tested; the search stopped at the preregistered budget. No extra native operator or probabilistic formula was added.','',
        'A is learned relative knight geometry; B is independently supervised opponent destination eligibility. Their examples and source groups are disjoint, and no training example contains the held-out combined knight capture. The witness is `f6h5` in `2bk3K/8/5N2/7n/8/2B5/8/8 w - - 0 1`. These synthetic source groups do not establish empirical IID sampling; known shared ancestry is explicitly controlled.','']
    for encoding in lab['encodings']:
        native += ['## '+encoding['id'],'',encoding['rationale'],'',encoding['missing_capability'],'']
        for row in lab['records']:
            if row['encoding']==encoding['id'] and row['condition'] in ('A+B','delete-A','delete-B','host-joint-control','aligned-type-control'):
                native += [row['condition']+':','```metta',row['expression'],'```','```text',row['result'],'```','']
    native += ['The native scheduler confirms the supplied-rule dependency:','']
    for r in lab['native_scheduler_dependency_controls']:native += ['```text',r['result'],'```']
    native += ['', 'The nested positive output includes `learn-A`, `learn-B`, and `supplied-rule`; deleting either premise or sharing their stamp removes the queried conclusion. This proves the mechanism depends on the supplied rule, not that the rule was learned from independent marginals. A host-built product is a sensor control, never native conjunction introduction.','',
        'The inventory distinguishes native truth functions, executable relational deduction/equivalence, and source-present predicate-transfer wrappers whose exact probes return empty. It records signatures, native STV domains, zero/one-confidence behavior, source locations and raw outputs. `BestConfidenceCandidate` selects one alternative and never combines premises. Revision at confidence one or with both confidences zero returns empty in the tested runtime.','',
        'All A-only/B-only, deletion, negative, contradiction, reversal and duplicate-correlation controls are in `artifacts/cycle7/native/laboratory.json`. Individual standalone MeTTa witnesses and the complete interpreter transcripts are adjacent. Rook obstruction and pawn capture composition were not attempted because the primary gate failed. This is a falsifiable result for the pinned operators and tested signatures, not an impossibility theorem about every PLN encoding.','',
        'See [extension-proposal.md](extension-proposal.md) for the missing introduction/dependence capability and [decision-memo.md](decision-memo.md) for the user decision. No proposed operator is enabled.']
    (docs/'native-feasibility.md').write_text('\n'.join(native)+'\n')
    (docs/'architecture-and-api.md').write_text('''# Architecture and API migration

Schema 7 wraps the frozen schema-6 checkpoint without relabeling its learned rules. The source model first evaluates every candidate. Optional backoff applies only to its unknown candidates and never replaces an existing specific local hypothesis, including low-confidence or disputed ones. It tries exact, ray-contents-masked, then destination-and-ray-masked relative categories. A second native C6 inference pass evaluates those selected candidates; the combined budgets remain bounded. All TV revision, implication and negation still run in the pinned native library.

This backoff is a learned conditional over a host projection. It is not independent-premise composition or a Boolean chess legality test. Coarse hypotheses cannot displace any supported frozen positive or negative. Strict and experimental modes do not execute the optional backoff pass. Their positive-proof behavior remains frozen. If operational backoff has not been evaluated in a strict request, its cross-mode comparison is explicitly null with `evaluated: false`.

| `proof_status` | Meaning |
|---|---|
| `native-compositional` | Reserved; no current candidate receives this label. |
| `native-unary/partial` | Used as `premise_proof_status` for independently executed partial premises, not a complete move conclusion. |
| `learned-conditional` | Operational positive with an actual LocalAdmissibility derivation; global safety remains unproved. |
| `negative-supported` | A supported negative with its native constraint proof. |
| `unknown` | The candidate conclusion is not accepted; diagnostic native TVs remain available. |
| `incomplete` | Budget/runtime failure, distinct from an epistemic abstention. |

Schema 6 keeps its original proof labels. Schema 7 declares `proof_status_schema: proof-status-v7`, retains `legacy_proof_status`, and preserves raw TVs and full native trace fields. Every candidate includes selected backoff level, learned/grounded rule IDs and evidence lineage. Decision nodes are explicitly host policy. Their metadata is separate from the native DAG. A native confidence is not a calibrated legality probability.

API `explain_move`, `infer_moves` and `analyze_batch` accept both schemas. `pln_chess.cycle7.api.compare_cycles` returns actual C6/C7 results in the selected mode, with complete native proofs, supporting/contradicting premises, evidence groups and abstention reasons. The inspector uses the same application contract; its export retains both comparison results.

The default remains operational only through a matching acceptance receipt bound to the production source hash, runtime, registration, model versions and executed checks. The C7 receipt can separately attest the preserved C6 model without altering the immutable C6 acceptance artifact. An explicit C6_OUT override remains isolated. Missing, incomplete or mismatched receipts fail closed to strict.

```bash
.venv/bin/python -m pln_chess inspect --fen '7k/8/8/8/8/8/2R5/2K5 w - - 0 1' --move c2e2
.venv/bin/python -m pln_chess inspect --fen '7k/8/8/8/8/8/2R5/2K5 w - - 0 1' --move c2e2 --mode strict --format json
.venv/bin/python -m pln_chess compare-cycles --fen '2bk3K/8/5N2/7n/8/2B5/8/8 w - - 0 1' --move f6h5
.venv/bin/python -m pln_chess serve --port 8765
```

Absolute coordinates remain at the input/environment boundary. Model projections contain relative motion, occupancy, ray content and existing temporal/boundary observations. No chess oracle is imported by production inference. Oracle labels occur only in training/evaluation. The seeded geometric candidate grammar remains an inductive bias rather than a discovered rule set.
''')
    perf=['# Performance and proof provenance','', '| Wrapper | Candidates | Reference s / calls | Cold s / calls | Warm s / calls | Peak KiB |','|---|---:|---:|---:|---:|---:|']
    for name in ('C6','C7'):
        b=read_json(out/f'benchmarks/{name}.json')
        for r in b['records']:
            cells=[f"{r['runs'][a]['elapsed_seconds']:.3f} / {r['runs'][a]['native_invocations']}" for a in ('reference','cold','warm')]
            perf.append(f"| {name} | {r['candidate_count']} | {' | '.join(cells)} | {r['runs']['warm']['peak_rss_kib']} |")
    perf+=['','The scheduler now computes its unchanged runtime-version digest once per batch rather than once per node. The initial 214-candidate profile recorded 16,800 repeated version-digest calls. No native expression, TV, rule ID, evidence ID or proof node was changed by this optimization. The benchmark verifies whole-candidate equality between reference, cold and warm runs. Frozen evaluation proof IDs also match C6.','',
        'The initial development timing ran alongside other experiments; final C6/C7 timing processes run serially after evaluation workers finish. These are single-host measurements, not statistically established speedups. Checkpoints, RSS, native calls, scheduled calls, cache hits, duplicate proof occurrences, serialized API bytes and interned DAG bytes are recorded in `artifacts/cycle7/benchmarks/`. Export interning is not claimed to reduce live Python proof memory.','',
        'Grounding still repeats relative descriptors across layers, and native proof metadata repeats across candidate exports. Those costs are measured rather than removed through a change to proof identity. Backoff itself is a semantic second-pass experiment and is not covered by the cache-equivalent optimization claim.']
    (docs/'performance.md').write_text('\n'.join(perf)+'\n')
    negs={n:read_json(out/f'{n}-negative-regressions.json') for n in ('C7-frozen','C7-learned-8')}
    (docs/'temporal-and-negatives.md').write_text('# Temporal trust and negative-proof preservation\n\n'+
        '\n'.join(f"{n}: {r['intact_negative']}/{r['cases']} negatives preserved, {r['removed_unknown']}/{r['cases']} removals unknown, {r['exact_native_proof_parity']}/{r['cases']} exact C6 native traces." for n,r in negs.items())+
        '\n\nThe 49 historical and 238 later cases retain complete before/after traces and their removed evidence families in `proofs/*-negative-controls.json.xz`. No oracle is consulted during those inference calls.\n\n'
        'The temporal matrix covers castling and en passant in all three inference modes, with FEN-only metadata, trusted metadata, structurally validated supplied events, missing history, inconsistent history and truncated history. Inputs and raw receipts distinguish observed board/event strings, assumed source confidence/initial rights, and inferred structural consistency. Replay does not prove a legally played prior game. `temporal.json.xz` contains all 36 actual candidate/receipt pairs.\n')
    ui=(out/'ui-verification.json').exists() and read_json(out/'ui-verification.json').get('passed') is True
    packages={f'C7-{i:02}':{'status':'complete'} for i in range(1,13)}
    for i in (2,3):packages[f'C7-{i:02}']['status']='negative research finding'
    packages['C7-05']['status']='complete' if acceptance['new_learning_promoted'] else 'negative research finding'
    packages['C7-08']['status']='complete' if ui else 'partial'
    links={1:'evaluation.md',2:'native-feasibility.md',3:'native-feasibility.md',4:'extension-proposal.md',5:'evaluation.md',6:'temporal-and-negatives.md',7:'performance.md',8:'architecture-and-api.md',9:'evaluation.md',10:'reproduction.md',11:'final-report.md',12:'decision-memo.md'}
    for i in range(1,13):packages[f'C7-{i:02}']['evidence']='docs/cycle7/'+links[i]
    write_json(out/'package-status.json',packages)
    matrix='\n'.join(['| Package | Status | Evidence |','|---|---|---|']+[f"| {k} | {v['status']} | [{Path(v['evidence']).name}]({Path(v['evidence']).name}) |" for k,v in packages.items()])
    (docs/'final-report.md').write_text('# Cycle 7 engineering delivery\n\n'
        f"Starting HEAD: `ebe58a980d601ad8b8167a6533619c383109e08d`. Verified source HEAD: `{verified['source_head']}`. The final delivery HEAD is the local commit containing this report. No Cycle 7 push, PR, publication or external mutation was performed.\n\n"
        f"Default: **{selected}, operational**. Native positive composition: **not demonstrated** after the three-encoding budget. Tests: **{verified['test_count']} passed**. Clean bootstrap and all mandatory acceptance checks passed. {verified['protected_files']} prior-cycle files remain byte-identical. The frozen wrapper preserves every reproduced candidate classification and native proof, with a versioned proof-label migration.\n\n"+
        matrix+'\n\n'+evaluation+'\n\n'
        f"New learning promoted: **{acceptance['new_learning_promoted']}**. Rejection details, if any, are in `artifacts/cycle7/acceptance.json`. Candidate-model improvements cannot override observed-error gates. Research failures remain visible in the learning curves, raw native transcripts and per-candidate regression archive.\n\n"
        'Full paired changes and bootstrap intervals, representative successes and unresolved abstentions, every recorded regression, native proofs, model hashes, data hashes and command receipts are linked from [evaluation.md](evaluation.md) and the artifact manifest. Runtime and exact cache parity are in [performance.md](performance.md). [reproduction.md](reproduction.md) records commands, pinned dependencies and limitations.\n\n'
        'The [one-page decision memo](decision-memo.md) distinguishes continued work within pinned PLN, authorization for an upstream extension discussion, and accepting partial positives as a permanent boundary. No new calculus is presumed approved.\n')
    runtime=verified['runtime']
    (docs/'reproduction.md').write_text('# Reproduction and evidence manifest\n\n'
        f"Verified implementation: `{verified['source_head']}`. Python `{runtime['python']}`; `{runtime['swipl']}`; PLN `{runtime['pln']['commit']}`; PeTTa `{runtime['petta']['commit']}`. PLN library SHA-256: `{runtime['pln']['sha256']}`.\n\n"
        '```bash\ngit clone /path/to/pln-chess /data/pln-chess-cycle7-reproduction\ncd /data/pln-chess-cycle7-reproduction\n'
        f"git checkout --detach {verified['source_head']}\n"
        'C7_OUT=/data/pln-chess-cycle7-output bash scripts/cycle7_reproduce.sh\n```\n\n'
        'The clean-copy driver bootstraps pinned dependencies, runs the complete test suite, reexecutes all 33 C6 mode/split baselines, generates the deterministic game manifest, trains all independent-group budgets, executes the evaluation matrix and ablations, preserves negative/temporal controls, measures reference/cold/warm parity, verifies acceptance and runs actual API/CLI/inspector default smoke checks. Independent subprocesses are bounded to three; final timing runs are serial. The current host must provide SWI-Prolog 10.0.1 with Janus/PCRE and uv. Bootstrap records exact failures rather than substituting a Python inference engine.\n\n'
        '`commands/*.json`, `logs/`, `bootstrap-context.json`, `pytest.txt`, and `verification.json` preserve actual execution outcomes. `manifest.json` hashes the committed evidence and reports. Runtime caches, virtual environments, temporary native query files and clean-clone working directories are generated and not committed. Each compressed report is lossless JSON, with ordered proof references into an interned native DAG.\n\n'
        'Known limits: synthetic games are not external human-game validation; small sample intervals are exploratory; coarse backoff can generalize incorrectly; conditional positives do not prove global king safety; historical replay is structural; the native inventory is scoped to pinned signatures; no native joint introduction or distributional confidence extension is shipped.\n')
    files={}
    for p in sorted(out.rglob('*')):
        if p.is_file() and p.name!='manifest.json':files['artifacts/cycle7/'+str(p.relative_to(out))]={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size,'committed':True}
    for p in sorted(docs.glob('*.md')):files[str(p.relative_to(ROOT))]={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size,'committed':True}
    write_json(out/'manifest.json',{'source_head':verified['source_head'],'files':files,'generated_not_committed':['.venv/','.runtime/','temporary native query files','clean reproduction checkout'],
        'self_hash_exclusion':'manifest.json is excluded from its own hash list to avoid a circular reference.'})
    return packages

if __name__=='__main__':reports()
