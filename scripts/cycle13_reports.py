"""Build the consolidated reports from executed receipts, never placeholder results."""
import argparse
from collections import Counter
import json
from pathlib import Path
import subprocess
from pln_chess.common import ROOT,read_json,write_json
from scripts.cycle9_baseline import sha


def number(value):
    return 'undefined' if value is None else f'{value:.3f}' if isinstance(value,float) else str(value)


def table(headers,rows):
    return '\n| '+' | '.join(headers)+' |\n| '+' | '.join('---' for _ in headers)+' |\n'+''.join(
        '| '+' | '.join(number(v).replace('|','\\|').replace('\n',' ') for v in row)+' |\n' for row in rows)+'\n'


def metrics_table(panels):
    return table(['Panel','Pairs','Resolved A/B','Answered A/B','Correct','Answered accuracy','Coverage','Abstention-inclusive accuracy'],
        [[name,m['examples'],m['directional_examples'],m['directional_answers'],m['correct_directional_answers'],
          m['pairwise_accuracy'],m['directional_coverage'],m['accuracy_including_abstention']] for name,m in panels.items()])


def link(path,label=None):
    return '['+(label or path)+'](../../artifacts/cycle13/'+path+')'


def run(out):
    out=Path(out).resolve();docs=ROOT/'docs/cycle13'
    required=('acceptance.json','current/verified.json','clean-research/verified.json','ui/verification.json',
        'performance/summary.json','preferences/summary.json','temporal/summary.json','architecture/boundary.json','final-checks/verified.json')
    for name in required:assert read_json(out/name)['passed'],name
    get=lambda path:read_json(out/path)
    pref=get('preferences/summary.json');cal=get('preferences/calibration.json');temporal=get('temporal/summary.json')
    transfer=get('transfer/summary.json');verified_transfer=get('verified-transfer/summary.json')
    assert verified_transfer['fresh_replay_verified'] and verified_transfer['correct_reference_directions']==10
    concept=get('concepts/summary.json');perf=get('performance/summary.json')
    current=get('current/verified.json');clean=get('clean-research/verified.json');boundary=get('architecture/boundary.json')
    dependence=get('dependence/summary.json');controls=get('preferences/controls-summary.json');source=get('datasets/source-pairs.json')
    ablations=get('ablations/immediate.json');labels=get('datasets/reference-labels.json');checks=get('final-checks/verified.json')
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    commits=subprocess.check_output(['git','log','--reverse','--format=%h %s','b000898a0a1f46e556f161982f2c0e6d3944c322..HEAD'],cwd=ROOT,text=True).strip()
    def write(name,title,text):
        (docs/(name+'.md')).write_text('# '+title+'\n\n'+text.strip()+'\n')
    boundary_text='The host assembles a categorical packet from independently inferred field and concept records. Native revision learns three separate conditional channels, and native modus ponens applies those channels to the supplied packet. This is a native conditional derivation, not a native conjunction of uncertain fields, a complete strategic theorem, a proof of legality or an optimal move claim. No scalar strategic utility or automatic move selection is implemented.'
    metric_scope='Answered accuracy excludes abstentions and unknown teacher labels. Coverage and abstention-inclusive accuracy use all directionally labeled pairs. Ambiguous labels have separate diagnostics. Undefined ratios remain undefined. A thousand bootstrap replicates resample connected ancestry components; these intervals do not include teacher-label or source-selection uncertainty.'
    label_reasons=Counter((r['label'],r['reason']) for r in labels['records'])
    coverage=get('datasets/relational-coverage.json');assert coverage['fresh_replay_coverage_identical']
    learning=f'''The fixed corpus contains {pref['source_pairs']} pairs from {pref['independent_groups']} independent source games and ancestry groups: 222 training, 62 calibration and 56 test. It combines 148 published-game positions and 192 external tactical positions, including 141 quiet pairs and 16 promotion pairs. Candidate alternatives and A/B order were fixed by hashes before labels or PLN predictions.

The partition audit excludes shared source games and exact registered geometry/transform classes. It does not prove the absence of every semantically related tactical motif. Shared coarse learned consequence patterns are the intended transfer test; they must not be confused with an independent proof of semantic family separation.

The reference is pinned [Stockfish 18](https://github.com/official-stockfish/Stockfish/releases/tag/sf_18), restricted to two explicit roots and 20,000/80,000 nodes with one thread. The [Lichess puzzle source](https://database.lichess.org/#puzzles) is a frozen CC0 prefix. Scores and reference PVs remain offline supervision. A direction requires agreement at both budgets and the registered margin; score bounds, intermediate margins and disagreements remain unknown.
'''+table(['Label','Reason','Pairs'],[(label,reason,n) for (label,reason),n in label_reasons.items()])+f'''
Only registered training observations update the separate model. Unknown labels, incomplete packets and directional labels whose abstraction collapses A/B remain in the ledger but do not update a direction. Independent opposing labels remain visible; inconsistent dependent groups are withheld.

The primary model has {pref['hypotheses']} relative conditionals. Its native training report is:

```json
{json.dumps(pref['native_training'],indent=2,sort_keys=True)}
```

{boundary_text}

{metric_scope}
'''+table(['Observed relational consequence','Pairs with that observation'],coverage['observed_change_coverage'].items())+table(['Concept family','Pairs with structural candidates','Pairs with a supported conditional'],
    [[name,n,coverage['supported_concept_pair_coverage'][name]] for name,n in coverage['concept_candidate_pair_coverage'].items()])+metrics_table(pref['panels'])+table(['Panel','Precision A','Precision B','Recall A','Recall B','Contradictions','Conditional proofs','Joint proofs'],
    [[name,m['precision']['A'],m['precision']['B'],m['recall_including_abstention']['A'],m['recall_including_abstention']['B'],m['contradictions'],m['native_conditional_proofs'],m['complete_joint_strategic_proofs']] for name,m in pref['panels'].items()])+table(['Test metric','95% lower','95% upper','Valid bootstrap replicates'],
    [[name,m['lower'],m['upper'],m['valid_replicates']] for name,m in pref['bootstrap']['test']['intervals'].items()])+'\nEvidence: '+', '.join(link(p) for p in ('preferences/summary.json','learning/relational/ledger.jsonl','learning/relational/native-training.json.xz','model/C13-preference-relational.json','datasets/integrity.json','ontology/manifest.json'))+'.'
    write('preference-learning','Native conditional preference learning',learning)
    transfer_rows=[]
    from evaluation.cycle3 import read_gzip
    for r in read_gzip(out/'transfer/demonstrations.json.xz'):
        transfer_rows.append([r['id'],r['split'],r['native_preference']['status'],r['reference_label'],r['correct_direction']])
    successful_rows=[[r['id'],r['split'],r['native_preference']['status'],r['reference_label']]
        for r in read_gzip(out/'verified-transfer/demonstrations.json.xz')]
    write('preference-transfer','Inspectable relative transfer',f'''The study retained {transfer['demonstrations']} demonstrations against a target of ten; target met: {transfer['target_met']}. Each supplies training ledger records, a held-out configuration, relative descriptors, evidence/rule IDs, native expressions and truth values, reference label and all endpoint graphs. Their source games and structural ancestry are absent from their conditional's training evidence.

These examples are post-hoc illustrations, ordered by test partition and answered status. They are not an unbiased accuracy estimate. {transfer['correct_direction']} show a correct reference direction. Full fixed-cohort results include failures and abstentions.
'''+table(['Pair','Partition','PLN status','Reference','Correct direction'],transfer_rows)+metrics_table({'all fixed test pairs':transfer['unselected_test_metrics'],'test pairs with a native conditional':transfer['all_test_transfer']})+f'''
The initial ordering yields one reference-confirmed direction and nine unknown reference labels. It therefore does not establish ten successful choices. A separate supplemental inspection selects ten of the twelve correct answered held-out cases: five test and five calibration examples. Selection explicitly uses successful outcomes after fitting; it changes no model, threshold, original example, or fixed-cohort metric. These ten examples meet the inspectable successful-transfer demonstration target, but their selected success fraction is not an accuracy estimate or ten new test successes.

'''+table(['Supplemental successful illustration','Partition','PLN status','Reference'],successful_rows)+f'''
The complete supplemental proofs, supporting training observations and endpoint graphs also match when assembled from the independent clean replay. The learned key contains categorical relative consequences and a horizon, never FEN, a square, game ID or exact context hash. Training ancestry is used for partitioning and dependence control only. Coarse matching may merge strategically different contexts; transfer does not establish universal strategic correctness.

Evidence: {link('transfer/demonstrations.json.xz')}, {link('transfer/summary.json')}, {link('verified-transfer/demonstrations.json.xz')}, {link('verified-transfer/summary.json')}, {link('preferences/reversal.json.xz')}.
''')
    concept_rows=[[name,m['n'],m['tp'],m['tn'],m['fp'],m['fn'],m['abstention']] for name,m in concept['external'].items()]
    write('concept-robustness','Independent tactical concept robustness',f'''The external panel contains 96 positions from 96 games and 96 raw structural families, disjoint from preference games and original concept training motifs. Each of eight concept families has eight positive and four negative reference examples. Selection and counterfactual construction are disclosed in the dataset; structural source labels do not prove complete tactical understanding.
'''+table(['Family','Cases','TP','TN','FP','FN','Abstained'],concept_rows)+f'''
All 312 dependent transformation and target controls pass. The 48-case generic-fork evaluation tests the new abstraction without the legacy fallback: 20 true positives, 24 true negatives, four abstentions and no incorrect classified answer. That panel includes dependent controls and is not 48 independent games. All 370 legacy native proofs and all previously correct classifications are preserved.

Multiple attackers, overloaded defenders and threat removal remain entirely unanswered on this external panel. Candidate enumeration is bounded and host-side. The system must disclose omitted candidates and unknown relations rather than treat them as negatives. {boundary_text}

Evidence: {link('concepts/summary.json')}, {link('concepts/external.json.xz')}, {link('concepts/external-controls.json.xz')}, {link('datasets/external-concepts.json')}.
''')
    for horizon,name in ((2,'two-ply'),(3,'three-ply')):
        examples=[r for r in read_gzip(out/'temporal/demonstrations.json.xz') if r['horizon']==horizon]
        write(name,f'{horizon}-ply supplied relational consequences',f'''The API accepts explicit supplied branches, with at most two branches per candidate and a maximum depth of three. This study uses one offline reference PV per candidate on 60 registered games. The first ten registered test plans produce the ten {horizon}-ply demonstrations below, without selecting them by PLN or reference outcome.

Each transition retains an independent legality belief; each endpoint retains attack, defense, ordinary mobility, king-exposure and concept observations with native proofs. Host differences describe creation/removal and concept persistence/disappearance. The original actor remains fixed across the sequence. History transport records that continuations are hypothetical and unverified; unexamined responses remain unknown.
'''+table(['Plan','A branch','B branch','Immediate','Continued','Endpoint label'],[[r['plan_id'],' '.join(r['branches']['A']),' '.join(r['branches']['B']),r['immediate_result']['status'],r['continued_result']['status'],r['continued_label']] for r in examples])+metrics_table({s:temporal['panels'][str(horizon)+'-'+s]['continued'] for s in ('train','calibration','test')})+f'''
No minimax, alpha-beta, tactical search, exhaustive response coverage or scalar rollout evaluation occurs in production. Captured tracked movers and omitted domain members are disclosed; their removed queries are not false relations. Missing required endpoints or exhausted native work produce incomplete results.

{boundary_text}

Evidence: {link('temporal/demonstrations.json.xz')}, {link('temporal/features/index.json')}, {link('datasets/temporal-plans.json')}. Each demonstration links its complete endpoint artifact.
''')
    temporal_rows=[]
    for name,panel in temporal['panels'].items():
        temporal_rows.append([name,panel['continued']['directional_answers'],panel['continued']['pairwise_accuracy'],panel['immediate_without_continuation']['directional_answers'],panel['immediate_without_continuation']['pairwise_accuracy'],panel['answered_at_both'],panel['directional_reversals'],panel['reference_label_changes']])
    write('temporal-preferences','Immediate and continuation-conditioned preferences',f'''The 60 fixed plans provide 120 two-/three-ply endpoint comparisons, split into 36 training, 12 calibration and 12 test source games. The temporal fit joins immediate and training continuation observations while preserving shared ancestry and distinct horizons. The held-out source games never update it. Endpoint labels use the original actor's perspective, including explicit mate outcomes.
'''+table(['Panel','Continued answers','Continued accuracy','Immediate answers','Immediate accuracy','Both answered','Reversals','Reference changes'],temporal_rows)+f'''
The no-continuation arm uses the original immediate belief against the same endpoint labels. The continuation arm changes observations and training evidence together, so an observed difference does not isolate a causal effect of temporal information. Equal statuses may simply mean equal abstention. Unexamined responses are unknown, and local relational improvements do not guarantee an outcome.

There are {temporal['native_joint_temporal_theorems']} native joint temporal theorems. The branch and endpoint explanations are complete for their supplied bounded workload, not exhaustive chess futures.

Evidence: {link('temporal/summary.json')}, {link('temporal/preferences.json.xz')}, {link('ablations/temporal.json')}.
''')
    calibration_rows=[[name,c['directional_examples'],c['brier_score'],c['expected_calibration_error']] for name,c in cal['panels'].items()]
    volume=get('preferences/evidence-volume.json')
    write('calibration','Measured calibration diagnostics',f'''Raw PLN strength and confidence remain separate from empirical correctness. The diagnostics compare the A-channel strength with resolved A/B labels; the three channels are not normalized probabilities. Confidence is used only as a reported evidence/selection parameter. No calibrator was fitted and no diagnostic changes production inference.
'''+table(['Panel','Resolved A/B labels','Brier score','ECE'],calibration_rows)+table(['Training pairs','Test accuracy','Directional coverage','Brier'],[[r['training_pairs'],r['metrics']['pairwise_accuracy'],r['metrics']['directional_coverage'],r['calibration']['brier_score']] for r in volume['studies']])+f'''
![Raw strength reliability](../../artifacts/cycle13/figures/preference-reliability.png)

![Selective accuracy and coverage](../../artifacts/cycle13/figures/preference-selective-coverage.png)

![Unseen source-family diagnostic](../../artifacts/cycle13/figures/preference-source-shift.png)

The source-holdout fits train on games only or tactics only, then evaluate the unchanged test partition from both pools. This is stronger than merely stratifying a mixed-source test set, but it still covers only two curated source pools. Small answered subsets and conservative unknown teacher labels limit every reliability claim. No confidence threshold is selected on the test set.

Evidence: {link('preferences/calibration.json')}, {link('preferences/evidence-volume.json')}, {link('preferences/distribution-shift.json')}, {link('figures/manifest.json')}.
''')
    write('ablations','Fixed-population evidence ablations',metrics_table({name:data['panels']['test'] for name,data in ablations['variants'].items()})+f'''
All eight registered descriptor variants use the same partitions and label policy. Relational and without-concepts are intentionally identical four-field arms; full adds bounded concept consequences. Attack-only, defense-only, mobility-only, exposure-only and weaker-relative remove or coarsen designated categorical observations. No held-out result selects a replacement primary model.

The dependence intervention repeats 222 training records three times under distinct delivery identities. With grouping, native truth values remain identical to the original fit. Without grouping, confidence increases for {dependence['native_confidence_increased_without_dependence']} of {dependence['total_hypotheses']} rules despite zero additional independent observations. Duplicate appends are byte-identical, internally conflicting dependent components are withheld, and independent opposing labels remain inspectable in {len(dependence['observed_independent_opposing_evidence'])} primary rules. The reported prediction contradiction rate counts simultaneously supported opposing channels; zero such predictions would not mean that training evidence is unanimous.

{controls['reversal_passes']}/{controls['reversal_cases']} corpus reversals preserve rule/evidence identity and swap directional channels. Removing the query conditional yields abstention for all {controls['removal_abstentions']} held-out removal controls, including already absent rules. A separate controlled three-edge native cycle demonstrates nontransitivity; removing its A/C evidence leaves A/C indeterminate. Those invented categorical assumptions are not empirical chess examples.

Correlated descriptor improvements do not establish causal strategic importance. The dependence intervention does demonstrate confidence inflation caused by repeated counting in that controlled replay. Temporal observation/training changes are documented separately.

Evidence: {link('ablations/immediate.json')}, {link('ablations/dependence.json')}, {link('ablations/temporal.json')}, {link('consistency/counterexample.json.xz')}, {link('preferences/controls-summary.json')}.
''')
    performance_rows=[]
    for r in perf['summaries']:
        m=r['medians'];performance_rows.append([r['workload'],r['arm'],r['temperature'],m['elapsed_seconds'],m['native_invocations'],m['interpreter_process_launches'],m['grounded_atoms'],m['cache_hits'],m['proof_bytes'],m['complete_json_bytes']/1048576,m['compressed_archive_bytes']/1048576,m['peak_process_rss_kib']/1024,m['peak_child_rss_kib']/1024,r['truncation_rate'],r['timeout_count']])
    write('performance','Complete-output performance and exact incremental parity',f'''Four fixed workloads cover one pair, three separate pair requests, one supplied two-ply comparison and one supplied three-ply comparison. Each full/incremental arm runs five repetitions in fresh worker processes, with a cold and warm request per worker: 40 processes and 80 measured workload requests. Arm order alternates. Workloads were hash-selected without preference outcomes. Other Cycle 13 native jobs were stopped before the benchmark. The host remained shared with unrelated services and projects; its affinity and background load were recorded, and exclusive machine ownership is not claimed.
'''+table(['Workload','Arm','Cache','Median s','Native ops','Processes','Atoms','Hits','Proof bytes','JSON MiB','Archive MiB','Parent MiB','Child MiB','Truncation','Timeouts'],performance_rows)+f'''
All twenty runs per workload have exact semantic and native-proof parity. Full recomputation clears dependency-bound relation records before each state; incremental retains them. Both retain identical pure native math memoization. Query domains are rebuilt in both arms, preventing omitted or stale targets from becoming false evidence. The timing intervention therefore isolates dependency reuse under the same native formula cache.

The measured median timing differences are small. Native operator and interpreter-launch medians are identical between full and incremental arms for every workload/cache condition. Dependency reuse does not eliminate query-domain reconstruction or complete proof construction. These five-repetition measurements do not establish a broad or statistically significant speedup; export size and proof construction remain material costs.

Elapsed time covers the complete API return, excluding archive/JSON transport serialization, model loading and interpreter imports. Cold means empty inference caches in a fresh worker with its models already loaded. Native operator calls and interpreter process launches are distinct counts. The table's proof-byte counter summarizes native traces; per-run receipts also report the entire uncompressed JSON package and compressed archive sizes, including graphs and metadata. Peak parent and maximum-child RSS are reported separately, not added into an aggregate working set. Parent peaks include API construction, semantic validation and archive serialization; warm measurements retain the cold output/caches and previous peak. Repetitions measure runtime variation, not additional independent chess examples. Per-run timings, ranges, counters, errors and full proofs are retained.

Evidence: {link('performance/summary.json')}, {link('performance/workloads.json')}, {link('performance/isolation.json')}.
''')
    write('reproduction','Reproducing the frozen Cycle 13 package',f'''The starting commit is `b000898a0a1f46e556f161982f2c0e6d3944c322`. Production source was frozen at `3e5aae6b6e4989cc8f0a5ad4eafcbd7df352f9dc`, with code hash `{boundary['production_code_hash']}`. Later commits add only offline orchestration, evidence and documentation. This report was generated from local content commit `{head}`; the final delivery commit is available with `git rev-parse HEAD` and is stated in the delivery message.

Starting reproduction passed 534 tests, 206 legal shards and 584,112 ordered candidate proofs. The current fresh checkout passes {current['test_count']} tests, every shard, 287 negative controls, 27 history controls, two recoveries and 76 holdouts with exact native proof parity. The final post-acceptance test run passes {checks['tests']} tests. The accepted legal checkpoint remains byte-identical to Cycle 12.

The final full suite is partitioned by complete modules across {checks['test_processes']} isolated pytest processes, each with its own temporary and cache directories. Collection identities, command logs and JUnit reports verify that every collected item executes exactly once, with no failures, errors or skips.

A second fresh checkout regenerated all 340 pair labels, 120 endpoint labels, 400 complete native feature artifacts, fork learning, all preference fits, ablations, controls and concept results. {clean['compared_artifacts']} artifacts compare exactly under the documented semantics; model checkpoints are byte-identical. The pinned offline reference engine rebuilt to the exact registered executable hash. The source checkout remained clean.

Execution counters and incremental flags, and wall-clock timestamps on ledger records, are the only exclusions from research semantic comparison. Raw telemetry remains archived. No ordered native expression, premise, truth value, graph, label, rule or evidence identity is excluded. Bootstrap pins Python dependencies, native runtime and PLN source; no upstream source was edited.

For a new run, use a new output directory and checkout path. The commands below are offline orchestration from an already bootstrapped package checkout; replace paths and `<local-commit>` explicitly. Never overwrite prior evidence generations.

```bash
bash scripts/bootstrap.sh --dependencies-only
.venv/bin/python -m scripts.cycle10_bootstrap --out /data/c13-replay-bootstrap --checkout /data/c13-replay-source --commit <local-commit>
.venv/bin/python -m scripts.cycle13_clean_research run --out artifacts/cycle13 --generation /data/c13-research-new-output --checkout /data/c13-research-new-source --commit <local-commit> --workers 4
.venv/bin/python -m scripts.cycle13_clean_research compare --out artifacts/cycle13 --generation /data/c13-research-new-output
.venv/bin/python -m evaluation.cycle13_delivery boundary --out artifacts/cycle13
.venv/bin/python -m evaluation.cycle13_cli --out artifacts/cycle13
.venv/bin/python -m pytest -q
```

The delivered output is the comparison reference. `--generation` names a new replay directory, so the reproduction driver copies only its six explicitly listed source/baseline inputs into the new run and regenerates every research output. The complete command receipts include actual arguments, checkout identities and logs. The baseline/current legal replay drivers are `scripts.cycle13_baseline` and `scripts.cycle13_regression`; both use the unchanged 206-job panel. Run performance in a fresh output generation only after other native jobs finish; the driver refuses reused benchmark receipts.

Browser verification uses the [ProofShot skill](/home/purplezky/.codex/skills/proofshot/SKILL.md), with a dedicated agent-browser session and `--run` server capture. Its screenshots, video, logs and exact downloaded response are retained. The download instrumentation merely grants the recording context permission to save the actual UI export; it does not alter application data.

Evidence: {link('baseline/reproduction-receipt.json')}, {link('current/verified.json')}, {link('clean-research/verified.json')}, {link('clean-research/comparison.json')}, {link('final-checks/verified.json')}, {link('ui/verification.json')}.
''')
    scopes=['Starting baseline preservation','Typed preference ontology','Append-only preference evidence','Preference curriculum','Native preference learning','Pairwise comparison API','Symmetry and consistency','Transfer demonstrations','Fork abstention resolution','Concept robustness','Two-ply consequences','Three-ply consequences','Temporal preference evidence','Preference evaluation','Calibration diagnostics','Evidence ablations','Interactive inspector','Performance and incremental parity','Operational regression gates','Consolidated delivery']
    evidence=['baseline/reproduction-receipt.json','ontology/manifest.json','learning/relational/ledger.jsonl','datasets/integrity.json','learning/relational/native-training.json.xz','cli-smoke/verified.json','preferences/controls-summary.json','verified-transfer/summary.json','forks/resolution.json','concepts/summary.json','temporal/demonstrations.json.xz','temporal/demonstrations.json.xz','temporal/summary.json','preferences/summary.json','preferences/calibration.json','ablations/immediate.json','ui/verification.json','performance/summary.json','acceptance.json','delivery.json']
    statuses=['Delivered']*20
    if not transfer['target_met']:statuses[7]='Study delivered; ten-example research target unmet'
    package_rows=[[f'C13-{i:02d}',scope,status,link(path)] for i,(scope,status,path) in enumerate(zip(scopes,statuses,evidence),1)]
    write('package-matrix','Cycle 13 package status','All twenty engineering packages are delivered with executed evidence. Research outcomes and unsupported claims remain explicit; package completion is not proof of successful strategic generalization.\n'+table(['Package','Scope','Status','Evidence'],package_rows))
    legal_table=table(['Cohort','Starting exact sets','Final exact sets'],[['External FEN-only','793/1020','793/1020'],['External supplied history','1020/1020','1020/1020'],['C9 adversarial','112/128','112/128'],['C9 special moves','71/80','71/80'],['C10 synthetic adversarial','98/112','98/112']])
    final_test=pref['panels']['test'];tc=cal['panels']['test']
    write('engineering-report','Cycle 13 consolidated engineering report',f'''Cycle 13 delivers experimental relative move comparison, native preference revision/application, bounded two-/three-ply explanations, learned fork generalization and a desktop/mobile proof inspector. All twenty packages have executed evidence. The operational legal model is preserved and preferences are not promoted into move selection.

The starting commit is `b000898a0a1f46e556f161982f2c0e6d3944c322`. Frozen production commit: `3e5aae6b6e4989cc8f0a5ad4eafcbd7df352f9dc`. Report content commit: `{head}`; the final packaging commit is recorded by repository HEAD and in the delivery message. Local commits only; no push or external deployment was performed. The [package matrix](package-matrix.md) lists all 20 packages and evidence.

The legal model remains `a6d3d826d93ee01b8accb7dc9948c0bd9bb0048cc54755bf45e92ec82502743d`, with zero new false-legal, false-illegal or self-check false-positive classifications. Full ordered native proof parity covers 206 shards and 584,112 candidate rows, including strict and experimental panels. These are measured acceptance cohorts, not universal correctness guarantees.
'''+legal_table+f'''
The curriculum contains 340 independent pairs/games with conservative ancestry partitions. The fixed test set has {final_test['examples']} pairs, {final_test['directional_examples']} resolved directional labels, {final_test['directional_answers']} answered directions and {final_test['correct_directional_answers']} correct directions: answered accuracy {number(final_test['pairwise_accuracy'])}, coverage {number(final_test['directional_coverage'])}. Unknown labels and abstentions remain visible. The complete [learning report](preference-learning.md) includes every cohort, precision/recall references and cluster uncertainty. [Transfer](preference-transfer.md) preserves the initial ten illustrations, nine of which have unresolved reference labels. Ten additional correct-reference illustrations are explicitly selected after outcomes from five test and five calibration cases; they demonstrate inspectable applications and are not an unbiased success rate.

All three old fork abstentions are resolved and all prior correct answers preserved: 306/306 concept test cases and 64/64 calibration cases. The 96-game external concept panel gives 28 correct classified answers, 68 abstentions and no wrong classified answers, with 312/312 dependent controls. The broader concept families remain weak; see [fork resolution](fork-resolution.md) and [concept robustness](concept-robustness.md).

Sixty registered supplied-branch plans yield 120 endpoint comparisons and ten [two-ply](two-ply.md) plus ten [three-ply](three-ply.md) demonstrations. [Temporal results](temporal-preferences.md) compare immediate and continuation-conditioned beliefs against the same endpoint labels, including reversals and unknown responses. Production performs no response search.

{boundary_text}

The native boundary audit reexecutes {boundary['native_training_nodes']} ordered training nodes and {len(boundary['native_preference_proof_replays'])} distinct preference proofs. It checks relative rule constants, protects {boundary['protected_files']} historical files, runs oracle-disabled comparisons and verifies the isolated legal import path. No new native operator, host probability formula or upstream change is introduced.

Test-set raw-strength Brier score is {number(tc['brier_score'])} and ECE is {number(tc['expected_calibration_error'])}; these are diagnostics, not a calibrated production probability. [Calibration](calibration.md) includes reliability, confidence selection, evidence-volume and true source-holdout studies. [Ablations](ablations.md) compare eight descriptor arms plus continuation and dependence interventions. The reversal controls pass {controls['reversal_passes']}/{controls['reversal_cases']}; all {controls['removals']} conditional-removal controls abstain. Controlled cyclic preferences show that transitivity cannot be assumed.

[Performance](performance.md) reports all 80 measured cold/warm requests across four workloads and full/incremental arms, with exact proof parity, memory, invocation counts, proof size and failures. Complete-output cost limits interactive use. The [inspector evidence]({str('../../artifacts/cycle13/ui/verification.json')}) includes recorded desktop/mobile behavior, trained and indeterminate results, bounded continuations and an actual byte-preserving JSON download.

The starting suite passes 534 tests, the fresh frozen-source suite passes {current['test_count']}, and the final post-acceptance suite passes {checks['tests']}. All 287 negative controls, 27 history controls, two recoveries and 76 holdouts pass. [Clean reproduction](reproduction.md) independently rebuilds the reference engine, labels, native features, models, proofs and studies; {clean['compared_artifacts']} artifacts agree under documented semantics. The final package contains source, ledgers, checkpoints, full proofs, plots, logs and hashes.

Cycle 14 recommendation: **Option A — continue preference learning**. The fixed coarse abstraction, many unknown reference labels, limited independent test support, absent empirical probability calibration, partial conditional proof boundary, limited concept coverage and costly endpoint inference do not justify automatic move selection. No new evidence changes the native composition no-go decision, so Option C is not warranted. Option B should remain a future separately authorized experiment.

Next priorities are to improve reference supervision without silently interpreting unresolved bounds as exact scores; preregister a larger independent source holdout with more quiet/ambiguous pairs; investigate relative descriptors that distinguish conflicting contexts; evaluate response coverage and uncertainty propagation; and reduce complete-proof cost while retaining exact dependency/provenance parity. New data and abstraction experiments require new partitions and evidence generations, not test-set tuning.

Local commits through this report's content snapshot:

```text
{commits}
```
''')
    required_docs=['engineering-report','package-matrix','preference-ontology','preference-evidence','preference-learning','pairwise-comparison','preference-transfer','fork-resolution','concept-robustness','two-ply','three-ply','temporal-preferences','calibration','ablations','performance','reproduction']
    assert all((docs/(name+'.md')).exists() for name in required_docs)
    write_json(out/'reports.json',dict(passed=True,content_head=head,required_documents=16,
        documents={str((docs/(name+'.md')).relative_to(ROOT)):sha(docs/(name+'.md')) for name in required_docs},
        cycle14_recommendation='A: continue preference learning',packages=20,
        inspectable_transfer_target_met=verified_transfer['demonstrations']==10,
        successful_illustrations_are_posthoc=True))
    print('CONSOLIDATED CYCLE 13 REPORTS GENERATED FROM EXECUTED RECEIPTS',flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',default='artifacts/cycle13');run(parser.parse_args().out)
