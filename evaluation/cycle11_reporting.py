"""Generate Cycle 11 reports from executed receipts, never projected results."""
import argparse
import json
import os
from pathlib import Path
import subprocess

from pln_chess.common import ROOT, read_json, write_json
from evaluation.cycle3 import read_gzip


def pct(value):
    return '—' if value is None else f'{100*value:.3f}%'


def run(out, docs):
    out, docs = Path(out).resolve(), Path(docs).resolve()
    docs.mkdir(parents=True, exist_ok=True)
    baseline = read_json(out / 'baseline/reproduction-receipt.json')
    current = read_json(out / 'current/verified.json')
    acceptance = read_json(out / 'acceptance.json')
    legal = read_json(out / 'legal/summary.json')
    regression = read_json(out / 'legal/regression/summary.json')
    temporal = read_json(out / 'temporal/summary.json')
    fields = read_json(out / 'field-evaluation/summary.json')
    calibration = read_json(out / 'field-evaluation/calibration.json')
    controls = read_json(out / 'fields/controls-summary.json')
    learning = read_json(out / 'field-learning/summary.json')
    dependence = read_json(out / 'field-learning/dependence.json')
    performance = read_json(out / 'performance/summary.json')
    ui = read_json(out / 'ui/verification.json')
    research = read_json(out / 'research-acceptance.json')
    audit = read_json(out / 'datasets/audit.json')
    unresolved = read_json(out / 'legal/unresolved-baseline-summary.json')
    sharing = read_json(out / 'field-learning/relative-sharing-summary.json')
    failure_audit = read_json(out / 'field-evaluation/post-freeze-false-negatives.json')
    proof_examples = read_json(out / 'fields/worked-proof-index.json')['examples']
    ep = read_gzip(out / 'legal/en-passant-after.json.xz')
    assert all(r['passed'] for r in (baseline, current, acceptance, temporal, dependence, performance, ui, audit))
    link = lambda path: os.path.relpath(out / path, docs)
    artifact = lambda path, label=None: f'[{label or path}]({link(path)})'
    def write(name, text):
        (docs / name).write_text(text.strip()+'\n')
    def field_table(population='all'):
        lines = ['| Field | Relations | Precision | Recall | Abstention | False support / contradiction | Native conditional proofs |',
                 '|---|---:|---:|---:|---:|---:|---:|']
        for family in ('attack', 'defense', 'mobility', 'king-exposure'):
            metric = fields['summaries']['trained'][population][family]['metrics']
            lines.append(f"| {family} | {metric['relations']} | {pct(metric['precision'])} | {pct(metric['recall'])} | {pct(metric['abstention_rate'])} | {metric['false_positive']} / {metric['false_negative']} | {metric['complete_conditional_proofs']} |")
        return '\n'.join(lines)

    package_specs = [
        ('01', 'Baseline preservation', 'Verified', 'baseline/reproduction-receipt.json'),
        ('02', 'En-passant completion', f"Experimental: {legal['en_passant']['recovered_legal']}/2 recovered", 'legal/en-passant-after.json.xz'),
        ('03', 'Adversarial legality completion', 'Inventory and isolated intervention measured; residual abstentions retained', 'legal/regression/summary.json'),
        ('04', 'Historical robustness', f"Verified on {temporal['cases']} registered cases", 'temporal/summary.json'),
        ('05', 'Potential-field ontology', 'Implemented typed relative conditional representation', 'ontology/manifest.json'),
        ('06', 'Attack potential', 'Implemented; conditional influence, not legal capture', 'field-evaluation/summary.json'),
        ('07', 'Defense potential', 'Implemented; geometric protection, legal recapture remains partial', 'field-evaluation/summary.json'),
        ('08', 'Mobility potential', 'Implemented ordinary occupancy mobility; special/legal mobility separate', 'field-evaluation/summary.json'),
        ('09', 'King-exposure potential', 'Implemented per-source influence; universal safety unsupported', 'field-evaluation/summary.json'),
        ('10', 'Spatial transfer', f"{controls['transformation_passes']}/{controls['transformations']} registered controls", 'fields/transformations.json.xz'),
        ('11', 'Successor fields', f"{len(controls['worked_examples'])} structural before/after examples", 'fields/worked-examples.json.xz'),
        ('12', 'Field differences', 'Typed host diagnostics; native change propositions unsupported', 'fields/worked-examples.json.xz'),
        ('13', 'Worked examples', f"{len(controls['worked_examples'])} complete recorded examples", 'fields/controls-summary.json'),
        ('14', 'Field learning', f"Native revision; {controls['successful_learning_transfers']}/{controls['transfer_attempts']} dedicated transfers", 'field-learning/summary.json'),
        ('15', 'Field evaluation', 'Separate relation labels, calibration and group uncertainty', 'field-evaluation/summary.json'),
        ('16', 'Interactive inspector', 'Verified desktop/mobile browser workflow', 'ui/verification.json'),
        ('17', 'Incremental performance', 'Exact native proof parity and isolated timings', 'performance/summary.json'),
        ('18', 'Operational gates', 'Verified unchanged accepted model', 'current/verified.json'),
        ('19', 'Research acceptance', f"{sum(research['targets'].values())}/{len(research['targets'])} targets met; original FEN adversarial improvement unmet", 'research-acceptance.json'),
        ('20', 'Consolidated delivery', 'Local source, artifacts and reports; no push', 'delivery.json'),
    ]
    matrix = '| Package | Scope | Evidence-backed status | Receipt |\n|---|---|---|---|\n'+'\n'.join(
        f'| C11-{number} | {name} | {status} | {artifact(path, "evidence")} |' for number, name, status, path in package_specs)
    write('package-matrix.md', '# Cycle 11 work-package matrix\n\n'+matrix+'\n\n“Implemented” identifies delivered engineering. It does not assert complete native composition, universal correctness, legal recapture, or strategic competence. Experimental failure counts and unsupported conclusions remain in the linked reports.')

    ep_table = '| Fixture / candidate | Before | After | Native local TV after | Without history |\n|---|---|---|---|---|\n'+'\n'.join(
        f"| {r['fixture']['id']} / {r['move']} | {r['before']['candidate']['classification']} | {r['after']['candidate']['classification']} | `{r['after']['candidate']['local_admissibility_truth_value']}` | {r['without_history']['candidate']['classification']} |" for r in ep)
    reg_table = '| Experimental cohort | Positions | Exact sets | Recall | False legal / illegal | Incomplete |\n|---|---:|---:|---:|---:|---:|\n'+'\n'.join(
        f"| {name} | {m['positions']} | {m['exact_positions']} | {pct(m['recall'])} | {m['false_positive']} / {m['false_illegal']} | {m['incomplete']} |" for name, m in regression['cohorts'].items())
    write('legal-completion.md', f'''# Legal completion and limitations

The accepted C8 checkpoint remains unchanged. Its full native proof parity is verified before and after Cycle 11 source changes. The experimental local revision recovered {legal['en_passant']['recovered_legal']} of the two known en-passant abstentions.

{ep_table}

Both original cases already had native temporal eligibility `(1, 0.99)`. In `c10-position-00861`, the inherited positive observation had confidence zero, leaving the local conditional at its neutral prior. `c10-position-01151` lacked the signed local en-passant conditional. Complete published games, prefixes, predecessor evidence and old proof graphs are retained in {artifact('legal/en-passant-before.json.xz')}. The old heuristic history taxonomy is not used as the causal diagnosis.

The isolated checkpoint revises exact existing local keys with 96 new controlled training observations in six layout groups, preserving color-transform ancestry. It uses native revision, the original thresholds and the frozen native source. Its 76 independent holdouts include EP king-exposure and promotion controls. Castling pseudo-legality in the offline reference includes attack-path conditions; this can create disagreement under a local descriptor that omits those conditions. Such observations are retained and dependence conflicts are disclosed, rather than relabeled to force success. {artifact('legal/training.json.xz', 'Training evidence and revisions')}; {artifact('legal/independent-holdouts.json.xz', 'holdout proofs')}.

The unresolved inventory contains {unresolved['cases']:,} unknown/incomplete candidate rows, including negative as well as positive reference labels, and {unresolved['native_nodes']:,} native proof nodes. It covers all registered C9 adversarial/special, C10 synthetic and C10 external FEN/history populations. {artifact('legal/unresolved-baseline.json.xz')}.

{reg_table}

The experimental external panel contains {regression['selected_external_positions']}/{regression['external_population']} positions, selected before training by potential exact-key applicability. Every candidate in each selected position is reevaluated, both FEN-only and with its actual published prefix. This is not a fresh full-external evaluation of the experimental checkpoint. The unchanged accepted model receives the complete external regression. {artifact('datasets/legal-regression-panel.json', 'Panel definition')}.

Synthetic predecessor/rights interventions for old adversarial fixtures remain labeled interventions, not reconstructed original histories. Geometry, destination, ray, boundary, exposure and temporal removals preserve the before/after proofs for both EP cases. Strict and experimental legality modes retain their positive-composition restrictions. Removing new learning or historical evidence is recorded separately. {artifact('legal/summary.json', 'All intervention outcomes')}; {artifact('legal/historical-interventions.json.xz')}.

The experimental checkpoint recovers {legal['independent_holdouts']['recovered_legal']} previously unknown legal candidates across the 76 holdouts, with {legal['independent_holdouts']['full_position_exact_after']}/76 exact complete legal-move sets and {legal['independent_holdouts']['full_position_false_legal']} false-legal / {legal['independent_holdouts']['full_position_false_illegal']} false-illegal classifications. These independent controlled holdouts differ from the two known published development failures. Removing temporal evidence leaves {legal['temporal_removal_supported']} supported special candidates across holdouts and historical interventions.

For both published EP cases, removing geometry, destination, ray, boundary or temporal premises yields unknown. Removing exposure still leaves operational support; strict and experimental modes remain unknown even with the full evidence. This reflects the inherited operational projection and its missing complete positive-composition theorem, not a native proof of universal safety.

No experimental checkpoint is promoted. Remaining abstentions and errors are research outcomes. These finite panels cannot establish universal legal accuracy or a complete native positive safety proof.
''')

    write('temporal-robustness.md', f'''# Robust historical evidence

All {temporal['cases']} registered claim controls passed their transport expectations: {temporal['native_available']} allowed the conservative legacy bridge and {temporal['withheld']} withheld it. {artifact('temporal/summary.json')}; {artifact('temporal/controls.json.xz', 'full claims, receipts and native consequences')}.

The new v11 contract separates delivered claims from canonical event order. Exact duplicates do not add revision weight; reversed/shuffled delivery and duplicate controls preserve the same semantic replay, legacy evidence and native proof. Full delivery receipts differ because their audit histories differ. Consistent corroborating sources remain distinct provenance claims without a numerical confidence bonus.

Missing sequence numbers, truncated expected event counts, contradictory moves, state claims, imported metadata and reused publisher identifiers produce explicit gaps/conflicts. A later contradictory claim retains every earlier claim and the parent receipt identity. Inferred or unknown history is not promoted to directly observed history. Partial PGN history may establish an observed immediate predecessor while leaving earlier castling history unknown.

Native bridging selects the lowest explicitly supplied finite confidence. This is a conservative input-trust policy, not probability fusion or a replacement PLN formula. No chess oracle validates historical play. Structural consistency, supplied metadata trust, native eligibility and historical legality are separate statements.

Tamper tests reject recomputed receipt hashes with false semantic contents and wrong model/runtime bindings. Existing v10 APIs remain supported. New callers can use the v11 claim contract through the public API; a v11 conflict supplies FEN-only native options and keeps the complete conflict receipt visible. {artifact('temporal/summary.json', 'Integrity and native-parity checks')}.
''')

    semantics = {
        'attack': ('Attack potential', 'Geometric influence under observed occupancy. Friendly occupied endpoints and pinned attackers are included. It does not imply a legal capture.', 'Rook obstruction, bishop opening, discovered attack and knight relocation'),
        'defense': ('Defense potential', 'Geometric protection of an observed friendly occupied target. Recapture legality, pin constraints and global king safety remain separate.', 'Defended pawns/minor pieces, rook batteries, pinned defenders, multiple defenders and discovered defense'),
        'mobility': ('Mobility potential', 'Ordinary occupancy-constrained movement. Pawn end-rank queries use a queen-promotion witness in offline labels; castle and en-passant eligibility are outside this relation domain.', 'Blocker removal, knight relocation and promotion to a new piece kind'),
        'king-exposure': ('King-exposure potential', 'Individual opposing-source influence toward an observed king. A contradicted relation does not prove absence of all attacks or universal safety.', 'Opened king rays, pinned blockers, multiple simultaneous attackers and en-passant exposure'),
    }
    for family, (title, meaning, examples) in semantics.items():
        m = fields['summaries']['trained']['all'][family]['metrics']
        external = fields['summaries']['trained']['external-game-panel'][family]['metrics']
        empty = fields['summaries']['empty']['all'][family]['metrics']
        uncertainty = fields['summaries']['trained']['all'][family]['uncertainty']
        cal = calibration['families'][family]
        domain_note = (f"The post-freeze audit identifies {failure_audit['castling_alias_count']} king-to-rook castling aliases among the {failure_audit['count']} primary false-negative rows. The offline reference accepts those aliases, while the ordinary-mobility adapter excluded only two-cell king castling moves. This is a label-domain mismatch. All original labels, errors and denominators remain in the primary results; no model, threshold or test selection was changed. {artifact('field-evaluation/post-freeze-false-negatives.json')}" if family=='mobility' else
            'The published-game subpanel contains only one positive king-exposure relation. Its perfect positive recall therefore provides very little independent evidence of generalization.' if family=='king-exposure' else '')
        sample=next(e for e in proof_examples if e['family']==family and e['after'] and e['after']['proof_trace'])
        relation=sample['after']
        trace_table='| Native operator | Returned truth value |\n|---|---|\n'+'\n'.join(
            f"| `{node['operator']}` | `{node['truth_value']}` |" for node in relation['proof_trace'])
        write(family+'-field.md', f'''# {title}

{meaning}

On the registered mixed test panel, precision is {pct(m['precision'])}, recall {pct(m['recall'])}, and abstention {pct(m['abstention_rate'])}, across {m['relations']:,} relations. False supported positives: {m['false_positive']}; false supported contradictions: {m['false_negative']}. Native conditional proofs: {m['complete_conditional_proofs']:,}; global composition proofs: {m['global_composition_proofs']}. {artifact('field-evaluation/summary.json')}.

On the published-game subpanel alone, precision is {pct(external['precision'])}, recall {pct(external['recall'])}, and abstention {pct(external['abstention_rate'])}. The empty checkpoint abstains on {pct(empty['abstention_rate'])} of the full panel. These are relation labels, not legal-move or strategic-success labels.

{domain_note}

The source/target context is observed by the host. A relative learned conditional is revised through native `Truth_Revision`, then applied through native modus ponens, negation and evidence selection. Every supported result retains native expressions, returned truth values, rule IDs, evidence IDs, dependence groups and model/runtime identities. The observation is one supplied local-context premise; the graph does not claim a native conjunction proof over independently uncertain subpremises.

For the `{sample['example']}` demonstration, the hypothetical after-state relation `{relation['source_square']} → {relation['target_square']}` is `{relation['classification']}` under rule `{relation['rule_id']}`. Its complete trace identity is `{relation['proof_id']}`. The first two nodes apply the positive and negative learned channels; negation reverses the negative conclusion, and evidence selection returns the chosen native result.

{trace_table}

The exact expressions, premise values, source observation and evidence IDs are retained in {artifact('fields/worked-proof-index.json', 'the proof index')}. This example is selected for review and adds no statistical evidence.

Worked coverage includes: {examples}. Before/after values and native proofs are retained even when the proposed candidate is unknown or contradicted by the accepted legality learner. {artifact('fields/worked-examples.json.xz')}.

Group-bootstrap 95% intervals: `{json.dumps(uncertainty['percentile_95'], sort_keys=True)}`. Only two controlled test generator groups limit uncertainty resolution; source games can share further dependencies. Raw-strength Brier diagnostic: {cal['raw_all']['brier']:.6f}; calibration-only fitted diagnostic on test: {cal['mapped_all']['brier']:.6f}. Raw PLN confidence is not an empirical probability. Neither calibration nor visualization changes the native result. {artifact('field-evaluation/calibration.json')}.

Missing required occupancy or an unlearned conditional remains unknown; execution limits remain incomplete. Shape/occupancy pooling and symmetry are supplied ontology assumptions. Accurate conditional influence cannot establish strategic competence.
''')

    example_table = '| Worked example | Candidate status | Before / after relations | Changed relations |\n|---|---|---:|---:|\n'+'\n'.join(
        f"| {r['id']} | {r['candidate_classification']} | {r['before_relations']} / {r['after_relations']} | {r['differences']} |" for r in controls['worked_examples'])
    write('field-differences.md', f'''# Candidate fields and typed differences

{len(controls['worked_examples'])} worked examples preserve full initial/successor environments, selected candidate status, relative observations, field records, native proofs and offline reference checks. {artifact('fields/worked-examples.json.xz')}.

The compact {artifact('fields/worked-proof-index.json', 'proof review index')} selects one declared relation per worked example for inspection, retaining both complete native traces and environment bindings. Its post-evaluation selection is for review only, not an accuracy estimate or model-selection step.

{example_table}

The structural successor applies movement, destination capture, promotion, castling rook relocation and off-destination en-passant removal without deciding legality. Candidate legality comes from the separate accepted C8 learner. A hypothetical successor is not an observed state or verified legal continuation.

The comparison is a typed collection. Each changed relation retains its before/after truth values, conditional rule IDs, evidence IDs, dependency footprints and proof identities. Missing relations are not zero-valued negative beliefs. Unknown-to-supported transitions remain distinguishable from contradicted-to-supported transitions. Opened/obstructed rays are structural observations.

All change propositions are labeled `host-diagnostic` and carry `change_truth_value: null`. Native proofs establish the separately scoped before/after conditionals, not a native probabilistic theorem for their difference. No strengths are added or multiplied, and no aggregate strategic score or move ranking is produced.

The inspector exposes piece/family/candidate selection, before/after board projections, relative relation rows, proof inspection and export. The board is a display coordinate system only. {artifact('ui/verification.json', 'Desktop/mobile browser evidence')}.
''')

    lr = learning['training_report']
    write('field-learning.md', f'''# Native field learning and transfer

The main learner used {lr['training_queries']:,} registered training queries to produce {lr['hypotheses']:,} relative conditionals. It scheduled {lr['native_revision_nodes']:,} native revision nodes and executed {lr['executed_native_operators']:,} after pure native-expression reuse. No calibration or test label entered revision. {artifact('field-learning/summary.json')}; {artifact('field-learning/main/native-training.json.xz', 'complete revision traces and exclusions')}.

The neutral prior is `(0.5, 0.05)` and training sensor confidence is 0.5. Positive and negative observations revise separate channels through the pinned native implementation. The ontology supplies typed fields, shape categories, pawn orientation, relevant boundary features and distance/occupancy pooling. It does not seed positive influence labels. The learned evidence determines conditional strengths and confidences.

Train/calibration/test source groups and whole-position symmetries are disjoint. The external panel deliberately reuses Cycle 10's published source-game partitions; it is not newly acquired independent evidence. {artifact('datasets/audit.json')}; {artifact('datasets/ATTRIBUTION.txt', 'source attribution')}.

Sliding training distances are 1, 2 and 4. All eight dedicated transfer queries have raw relative displacements and whole positions absent from training. {controls['successful_learning_transfers']}/{controls['transfer_attempts']} satisfy the registered empty-model → learned support → selected-hypothesis removal pattern. Shared pooled local categories are explicitly disclosed; this is transfer under a supplied representation, not autonomous discovery of a distance abstraction. {artifact('fields/learning-transfers.json.xz')}.

The post-freeze sharing audit records {sharing['training_observed_keys']:,} observed pooled keys, {sharing['training_raw_relative_contexts']:,} distinct raw relative contexts and {sharing['training_conflicting_pooled_keys']} pooled keys containing conflicting training labels. For test attack relations, {sharing['counts']['test/attack']['pooled_key_observed_in_training']:,}/{sharing['counts']['test/attack']['relations']:,} share a supplied pooled category with training; {sharing['counts']['test/attack']['raw_relative_context_observed_in_training']:,} share the more detailed raw displacement/typed-ray context. Exact-key reuse and unseen-distance transfer must not be conflated. Every dedicated transfer's matched training displacements and evidence are retained. {artifact('field-learning/relative-sharing-summary.json')}; {artifact('field-learning/relative-sharing.json.xz')}.

At most one representative per connected dependence/ancestry component revises each conditional. Contradictory dependent components are withheld with all records retained; independently declared contradictions revise the native channels. Duplicate and color-transform ancestry controls preserve belief values, while deliberately unannotated duplicate evidence and injected contradictions test the boundary. These are declared controls, not claims of newly acquired contradictory games. {artifact('field-learning/dependence.json')}.

Checkpoint `{learning['model_version']}` remains experimental and independent of legal classification. Empty checkpoints and selected-hypothesis removal prevent the observer from supplying learned influence conclusions by itself.
''')

    write('field-evaluation.md', f'''# Relational field evaluation

The evaluator joins offline reference labels only after production inference returns. Geometry, attack, defense, ordinary mobility and per-source king exposure have distinct labels and domains. Full native proof graphs and their hashes accompany each shard. No legal-move accuracy is substituted for field accuracy.

{field_table()}

Published-game subpanel:

{field_table('external-game-panel')}

{controls['transformation_passes']}/{controls['transformations']} registered transformation/counterfactual controls passed. Failures, if any: `{controls['transformation_failures']}`. Controls cover translation, valid reflection, color-relative orientation, piece-ID renaming, irrelevant distant edits, inserted blockers and unknown ray cells. They test sensitivity as well as invariance. {artifact('fields/transformations.json.xz')}.

Calibration uses only the separate calibration partition to fit ten-bin Laplace diagnostic mappings. Raw and mapped Brier/log-loss/ECE, reliability bins and covered-only scores are retained. Thresholds and native classifications remain unchanged. Confidence is not plotted as a probability. {artifact('field-evaluation/calibration.json')}.

The frozen primary mobility results include {failure_audit['count']} false negatives, of which {failure_audit['castling_alias_count']} are reference king-to-rook castling aliases missed by the label adapter's two-cell castle exclusion. The post-freeze audit documents this domain mismatch without changing original labels, denominators, models or thresholds. A future independently registered ordinary-mobility panel should exclude every castling encoding before sampling. {artifact('field-evaluation/post-freeze-false-negatives.json')}. The external king-exposure subpanel has only one positive, so its positive recall is particularly weak evidence.

The panel is a deliberately structured mixture, not a representative sample of chess positions. Some controlled contexts are invalid as complete game states; their local relation labels remain defined, and reference-valid-only metrics are reported separately. Group bootstrap resamples connected source/generator/declared-ancestry components, including shared openings, not individual related queries. Two controlled holdout generator groups provide weak interval resolution. Native conditional coverage and unsupported global composition are reported separately. {artifact('field-evaluation/summary.json')}.
''')

    perf_rows = []
    for name, values in performance['workloads'].items():
        cold, warm, full, incremental = (values[k] for k in ('full-cold', 'full-warm', 'successor-full-cold', 'successor-incremental'))
        perf_rows.append(f"| {name} | {cold['median_seconds']:.4f} | {warm['median_seconds']:.4f} | {full['median_seconds']:.4f} | {incremental['median_seconds']:.4f} | {incremental['median_relation_cache_hits']} / {incremental['median_relation_cache_invalidations']} |")
    write('performance.md', f'''# Field performance and exact reuse

Each workload ran in a fresh worker for {performance['repetitions']} repetitions, after other native study workers finished. Full and incremental outputs have identical relation values and native proof IDs. Pure native-expression caching and exact local-relation reuse are separately counted. {artifact('performance/summary.json')}.

Cold means a fresh field/native-expression session; operating-system file caches are not flushed. Warm means an identical request using the same field session. Neither label includes interpreter or model-loading startup.

| Workload | Cold field median s | Warm median s | Full successor median s | Incremental median s | Reused / invalidated relations |
|---|---:|---:|---:|---:|---:|
{chr(10).join(perf_rows)}

The cache binds model identity, runtime manifest, inference options, observation source and complete relevant dependencies. Long rays include every participating cell; there is no fixed neighborhood radius. Source motion, promotion, target identity, capture, off-destination EP removal, unknown-cell edits and castling rook motion invalidate affected relations. An unrelated distant edit may preserve a local proof while the enclosing state certificate changes.

The current implementation recomputes observation fingerprints for the requested relations and returns complete proof records even on a warm request. Reuse saves native calculation and proof construction; it does not eliminate observation scanning, copying or serialization. Speedup is therefore measured separately from cache-hit counts and is not guaranteed for every workload.

The raw measurements include single-candidate full/incremental updates, three successive alternatives sharing a parent cache, native operator counts, grounded atoms, proof bytes, hits/invalidations and Python allocation peaks. Maximum fresh-worker RSS: {performance['max_process_peak_rss_kib']:,} KiB. Maximum child-process high-water RSS: {performance['max_native_child_peak_rss_kib']:,} KiB. These are not summed concurrent memory. {artifact('performance/measurements.json.xz')}.

Model/runtime initialization, the structural successor edit and separate candidate legality inference are excluded from per-condition field timing. Observation, grounding, native execution, proof assembly and proof-size accounting are included. The multiple-candidate conditions measure field construction for three structural alternatives; they do not time move search or selection. `tracemalloc` adds overhead. Nine repetitions give weak p95 resolution; minima/maxima and all individual samples are retained. Cache reuse is an exact engineering optimization, not a probabilistic inference or strategic search result.
''')

    write('strategic-roadmap.md', '''# Strategic architecture roadmap

Cycle 11 supplies an experimental descriptive layer: typed relative influence beliefs, structural hypothetical successors, native conditional proofs and provenance-preserving comparisons. It supplies no strategic move selector or optimality claim.

```mermaid
flowchart TD
  O[Observed environment and history] --> R[Relative local propositions]
  R --> L[Accepted legal-move beliefs]
  R --> F[Experimental influence conditionals]
  L --> S[Candidate structural successor]
  F --> S
  S --> D[Before and after relations]
  D --> H[Typed diagnostic changes]
  H -. future research .-> C[Probabilistic consequences and planning]
```

Verified native revision, unary conditional modus ponens, negation and evidence selection support the existing layer. Existing negative exposure chains support specific candidate illegality evidence. They do not establish a joint probabilistic model of interacting fields, universal safety, a native change proposition, or long-horizon utility.

| Future requirement | Present support | Research needed |
|---|---|---|
| Learned strategic concepts | Typed local relations and evidence ledger | Define and independently label consequences such as recoverable material, coordination and durable threats; avoid handcoded weighted sums |
| Field interactions | Separate relations and dependence metadata | Semantics for shared-cause evidence and uncertain-premise composition; independent native audit and explicit authorization before new operators |
| Field propagation | Exact dependency graph and structural edits | Valid causal transitions and temporal decay/update semantics; no informal diffusion of strengths |
| Temporal planning | Supplied-event replay and hypothetical successors | Branch-specific provenance, observation/action distinctions, delayed consequences and uncertainty-preserving search |
| Move comparison | Candidate legality and typed changes | Learn preference/utility targets separately; retain incomparable or unknown outcomes |
| Experience-based learning | Native revision and ancestry-aware ingestion | Prospective data acquisition, policy-induced selection bias and clean held-out strategic outcomes |
| Long-term memory | Immutable evidence/model/receipt identities | Retrieval by relative structure, contradiction/retraction, distribution shifts and bounded memory |
| Native composition | Audited conditional and negative chains | Joint premise semantics, proof certificates and calibration before any positive-composition extension |

Cycle 12 should first test independently acquired relation panels, broaden observed occupancy/temporal coverage, and investigate residual local abstentions without weakening gates. It should then define small, falsifiable consequence targets with prospective splits. A composition proposal must explain dependencies and native semantics before implementation. Strategic strength needs separate outcome-based evaluation; attack-map accuracy cannot establish it.
''')

    fresh_research_note = (f"The new research stages also executed independently in the fresh checkout: data regeneration, native field/legal learning, held-out field evaluation, all transformations/transfers/examples and temporal controls. Model bytes, datasets, every frozen field metric/proof row and worked native relations matched exactly. {artifact('clean-research/verified.json')}. This reuses the already executed unchanged-source baseline by its receipt; it is not a second full end-to-end baseline run." if (out/'clean-research/verified.json').exists() else '')
    write('reproduction.md', f'''# Cycle 11 reproduction

Starting source: `{baseline['starting_head']}`. The original accepted checkpoint, runtime locks, datasets and historical artifacts remain byte-identical. The unchanged-source baseline executes the original 399 tests, 287 negative controls, 26 historical suites, 48 Cycle 9 shards and 132 frozen/history Cycle 10 shards. {artifact('baseline/reproduction-receipt.json')}.

The current implementation was bootstrapped into `{current['checkout']}` with fresh dependencies and the pinned native runtime. It passed {current['test_count']} tests and the same complete native acceptance replay; every candidate's proof, value, rule/evidence lineage and predicted set matches the original. {artifact('current/verified.json')}; {artifact('current/proof-parity.json')}.

{fresh_research_note}

To inspect a field with the delivered checkpoint:

```bash
.venv/bin/python -m pln_chess field-inspect \\
  --fen '7k/8/8/8/R2N3p/8/8/6K1 w - - 0 1' \\
  --piece a4 --family attack --move d4f5 --output /tmp/field-comparison.json
.venv/bin/python -m pln_chess history-claims --input supplied-claims.json --output /tmp/history-receipt.json
.venv/bin/python -m pln_chess serve --port 8765
```

The local browser route is `http://127.0.0.1:8765/fields`; the existing legal inspector remains at `/`. Public Python callers use `pln_chess.api.inspect_fields` and `replay_history_claims`. A candidate comparison returns separate legal status, before/after relations and diagnostic differences. The field checkpoint remains experimental even when the separate candidate is supported legal.

The staged reproduction entry point is `scripts/cycle11_reproduce.py`. Use a new output, checkout, baseline-snapshot and browser-work directory. The driver preserves command logs, return codes and source identities; it reuses the exact bundled licensed source bytes rather than reacquiring games. Timings and capture metadata may differ. Dataset/model/native proof identities are the reproducible scientific objects.

```bash
.venv/bin/python -m scripts.cycle11_reproduce \\
  --out /data/pln-chess-cycle11-replay-output \\
  --checkout /data/pln-chess-cycle11-replay-checkout \\
  --baseline /data/pln-chess-cycle11-replay-baseline \\
  --browser-work /data/pln-chess-cycle11-replay-browser
```

The required system tools are the pinned SWI-Prolog runtime prerequisites, Python/bootstrap dependencies, `zstd` for bundled PGN data, and ProofShot/browser tooling for the UI phase. Plotting uses the explicitly selected plotting interpreter. No GitHub push, external deployment, new operator or upstream modification is part of reproduction.

Executed stage receipts, their source hashes and any retained failed development attempts are distinguished in {artifact('delivery.json', 'delivery status')}. A supplied driver is not by itself evidence of a second complete end-to-end run. The delivery receipt states exactly which clean-checkout stages actually executed.
''')

    commits = subprocess.check_output(['git', 'log', '--format=%h %s', baseline['starting_head']+'..HEAD'], cwd=ROOT, text=True).strip()
    write('engineering-report.md', f'''# Cycle 11 engineering report

The accepted legal learner is preserved, and the experimental field subsystem learns and explains four distinct relative relation families. Native conditional proofs are retained; before/after change propositions remain explicitly host diagnostics. Experimental models remain unpromoted. No push or deployment is included.

Starting commit: `{baseline['starting_head']}`. Accepted checkpoint: `{learning.get('accepted_model_version', '1217e17552ff611bebf0efc650245b05fb71c93a8175b579b025d6273d5d781d')}`. Current source identity and final local Git state are recorded in {artifact('delivery.json')}. [Work-package matrix](package-matrix.md).

The full accepted native replay preserves 793/1,020 exact external FEN-only sets and 1,018/1,020 history-assisted sets, with no new false-legal, false-illegal or self-check false-positive classification. The independently named local experiment recovers {legal['en_passant']['recovered_legal']}/2 known EP abstentions; its separate adversarial/holdout/external-applicability outcomes and limits are in [legal completion](legal-completion.md).

{field_table()}

The study records {len(controls['worked_examples'])} before/after demonstrations, {controls['transformation_passes']}/{controls['transformations']} transformation controls and {controls['successful_learning_transfers']}/{controls['transfer_attempts']} dedicated unseen-configuration transfers. All {temporal['cases']} robust-history controls pass their registered expectations. [Learning](field-learning.md), [evaluation](field-evaluation.md), [temporal evidence](temporal-robustness.md), [typed differences](field-differences.md).

The proposed research target of improving original FEN-only adversarial exact-set accuracy was not met. Those three cohorts remain at 112/128, 71/80 and 98/112 exact sets. Supplied-history interventions and controlled holdouts improve separately. Implementation acceptance and completion of the engineering package do not imply every research target succeeded. {artifact('research-acceptance.json')}.

Mandatory implementation checks include {current['test_count']} tests, all 287 negative controls, 26 historical suites, 180 full native comparison shards, fresh dependency bootstrap, no production oracle/new operator, exact proof/cache parity and browser verification. Exact incremental reuse is measured in [performance](performance.md). The inspector exposes separate strength/confidence, unknown/incomplete states and inspectable native proofs on desktop and mobile.

The system learns local conditional influence under supplied geometry and occupancy abstractions. It does not learn the abstraction grammar itself, infer legal recapture from defense alone, prove universal safety from absent attacks, derive a native probabilistic field-change theorem, or choose an optimal move. Group dependence, controlled invalid whole-board contexts, limited calibration populations and finite no-error tests constrain generalization. [Ontology](potential-field-ontology.md), [strategic roadmap](strategic-roadmap.md), [reproduction](reproduction.md).

Local commits at report generation (the final documentation/manifest commit follows and is listed in the delivery receipt):

```text
{commits}
```
''')
    write_json(out / 'report-index.json', dict(files=sorted(p.name for p in docs.glob('*.md')),
        model_version=fields['model_version'], accepted_model_changed=False,
        package_status=[dict(package='C11-'+n, name=name, status=status, evidence=path) for n,name,status,path in package_specs]))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True)
    parser.add_argument('--docs', required=True)
    args = parser.parse_args()
    run(args.out, args.docs)
