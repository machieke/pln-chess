"""Render the consolidated delivery from measured artifacts, never placeholders."""
import argparse
from collections import Counter
from pathlib import Path
import statistics
import chess
from pln_chess.common import ROOT,read_json,write_json
from scripts.cycle9_baseline import sha,START


def pct(x):return '—' if x is None else f'{100*x:.3f}%'
def table(headers,rows):return '\n'.join(['| '+' | '.join(headers)+' |','|'+'|'.join(['---']*len(headers))+'|',*['| '+' | '.join(map(str,row))+' |' for row in rows]])
def link(name):return f'../../artifacts/cycle9/{name}'


def run(out):
    out=Path(out).resolve();docs=ROOT/'docs/cycle9';docs.mkdir(exist_ok=True)
    v=read_json(out/'verification.json');assert v['passed']
    study_head=v.get('native_study_source_head',v['source_head'])
    receipt=read_json(out/'acceptance.json');summary=read_json(out/'analysis/evaluation-summary.json')
    cal=read_json(out/'calibration/results.json');dataset=read_json(out/'datasets/manifest.json')
    before=read_json(out/'performance/C8-original.json');after=read_json(out/'performance/C9-optimized.json')
    controls=read_json(out/'C8-promotion-relative-negative-regressions.json');abstention=read_json(out/'abstention/summary.json')
    ui=read_json(out/'ui-verification.json');assert ui['passed']
    smoke=read_json(out/'smoke/verified.json');assert smoke['passed']
    assert read_json(out/'fresh-source-bootstrap/verified.json')['passed']
    presentation_note=''
    if v.get('presentation_only_change'):
        assert read_json(out/'presentation/verified.json')['passed']
        presentation_note=f"The final mobile check exposed overflow from the 64-character report hash. Source `{v['source_head']}` adds one CSS wrapping attribute. Every other production byte, including native inference, acceptance and JavaScript, is identical to the executed native study. The original verifier rechecked every native gate; all {v['test_count']} tests and actual API/CLI smoke were rerun on the corrected source before browser verification. Native evaluations and timings were reused only after that exact one-attribute equivalence check. [Source equivalence]({link('presentation/source-equivalence.json')}), [qualification]({link('presentation/verified.json')}), [original receipts]({link('presentation/native-study/')}), [current test log]({link('presentation/pytest.txt')})."
    def write(name,text):(docs/name).write_text(text.strip()+'\n')
    cohort_rows=[]
    for split in ('development','calibration','independent-games','adversarial','special-moves'):
        entry=summary['operational/'+split];m=entry['complete'];inside=entry['in_board']
        cohort_rows.append([split,m['positions'],m['candidates'],inside['candidates'],pct(m['recall']),f"{m['exact_positions']}/{m['positions']}",m['false_positive'],m['false_illegal'],m['self_check_false_legal'],m['unknown']])
    cohorts=table(['Cohort','Positions','All candidates','In-board','Recall','Exact sets','False legal','False illegal','Self-check FP','Unknown'],cohort_rows)
    population_rows=[]
    interval_rows=[]
    for split in ('independent-games','adversarial','special-moves'):
        entry=summary['operational/'+split]
        for population in ('complete','in_board'):
            m=entry[population]
            population_rows.append([split,population,m['candidates'],pct(m['precision']),pct(m['recall']),pct(m['coverage']),pct(m['selective_accuracy'])])
        u=entry['uncertainty'];intervals=u['interval95']
        interval_rows.append([split,u['clusters'],' – '.join(map(pct,intervals['recall'])),' – '.join(map(pct,intervals['exact_move_set_accuracy']))])
    populations=table(['Held-out cohort','Population','Candidates','Precision','Recall','Coverage','Selective accuracy'],population_rows)
    intervals_table=table(['Held-out cohort','Source clusters','Recall 95% interval','Exact-set 95% interval'],interval_rows)
    raw_data=read_json(out/'datasets/dataset.json');coverage={}
    for split in raw_data['counts']:
        fixtures=[p for p in raw_data['positions'] if p['split']==split]
        counts={k:Counter() for k in ('phase','piece_count','pawn_count','castling_rights','en_passant_square','checkers','opening_or_structural_family')}
        pawn_patterns=set()
        for p in fixtures:
            b=chess.Board(p['fen'])
            for k,value in [('phase',p.get('phase','controlled-position')),('piece_count',len(b.piece_map())),
                ('pawn_count',len(b.pieces(chess.PAWN,chess.WHITE))+len(b.pieces(chess.PAWN,chess.BLACK))),
                ('castling_rights',b.castling_xfen()),('en_passant_square',chess.square_name(b.ep_square) if b.ep_square is not None else 'none'),
                ('checkers',len(b.checkers())),('opening_or_structural_family',p['family'])]:counts[k][str(value)]+=1
            pawn_patterns.add((int(b.pieces(chess.PAWN,chess.WHITE)),int(b.pieces(chess.PAWN,chess.BLACK))))
        coverage[split]=dict(positions=len(fixtures),distinct_absolute_pawn_patterns=len(pawn_patterns),
            **{k:dict(sorted(v.items())) for k,v in counts.items()})
    write_json(out/'analysis/dataset-coverage.json',dict(cohorts=coverage,
        scope='Offline descriptive distribution counts, not independence or robustness guarantees. Pawn patterns use absolute board locations only for dataset auditing.'))
    history=[]
    for name in ('frozen-heldout-transfer','cycle7-independent-games','cycle8-independent-games','cycle8-adversarial'):
        old=read_json(out/'baseline/C8-promotion-relative-summary.json')[name]
        new=read_json(out/f'regression/C8-promotion-relative-{name}.receipt.json')
        history.append([name,pct(old['metrics']['recall']),pct(new['metrics']['recall']),pct(old['metrics']['exact_move_set_accuracy']),pct(new['metrics']['exact_move_set_accuracy']),'Exact'])
    historical=table(['Historical cohort','C8 recall','C9 replay recall','C8 exact sets','C9 exact sets','Native proof parity'],history)
    comparison_rows=[]
    for mode in ('operational','strict','experimental'):
        for split in ('independent-games','special-moves'):
            m=(read_json(out/'evaluation/operational-independent-games-0000.receipt.json')['metrics']
               if mode=='operational' and split=='independent-games' else summary[mode+'/'+split]['complete'])
            comparison_rows.append([mode,split,25 if split=='independent-games' else 80,pct(m['recall']),pct(m['exact_move_set_accuracy']),m['false_positive'],m['false_illegal'],m['unknown']])
    comparisons=table(['Mode','Matched cohort','Positions','Recall','Exact sets','False legal','False illegal','Unknown'],comparison_rows)
    perf_rows=[];full=None
    for a,b in zip(before['records'],after['records']):
        if a['fixture']['id']=='full-214':full=(a,b)
        for mode in ('reference','cold','warm'):
            x=a['aggregates'][mode]['latency_seconds'];y=b['aggregates'][mode]['latency_seconds']
            perf_rows.append([a['fixture']['id'],mode,f"{x['p50']:.3f}",f"{y['p50']:.3f}",f"{y['p95']:.3f}",f"{y['p99']:.3f}",f"{100*(x['p50']-y['p50'])/x['p50']:.1f}%"])
    performances=table(['Workload','Native cache mode','C8 p50 s','C9 p50 s','C9 p95 s','C9 p99 s','p50 reduction'],perf_rows)
    independent=summary['operational/independent-games'];adversarial=summary['operational/adversarial']
    c7=next(r for r in read_json(ROOT/'artifacts/cycle8/benchmarks/C7-frozen.json')['records'] if r['fixture']['scope']=='full-214')
    targets=[]
    for split,target in (('independent-games',.85),('adversarial',.95)):
        m=summary['operational/'+split]['complete']
        targets.append(dict(metric=split+' exact sets',target=target,measured=m['exact_move_set_accuracy'],met=m['exact_move_set_accuracy']>=target))
    targets.append(dict(metric='independent-game recall',target=.98,measured=independent['complete']['recall'],met=independent['complete']['recall']>=.98))
    for metric in ('false_positive','false_illegal','self_check_false_legal'):
        total=sum(e['complete'][metric] for key,e in summary.items() if key.startswith('operational/'))
        targets.append(dict(metric=metric,target=0,measured=total,met=total==0))
    for mode in ('cold','warm'):
        target=c7['aggregates'][mode]['latency_seconds']['p50'];actual=full[1]['aggregates'][mode]['latency_seconds']['p50']
        targets.append(dict(metric='full-214 '+mode+' p50 seconds',target=target,measured=actual,met=actual<=target))
    write_json(out/'analysis/research-targets.json',dict(targets=targets,scope='Aspirational research outcomes, separate from mandatory historical correctness gates.'))
    target_table=table(['Research target','Threshold','Measured','Met'],[[r['metric'],f"{r['target']:.6g}",f"{r['measured']:.6g}",'Yes' if r['met'] else 'No'] for r in targets])
    measured=f"{v['test_count']} tests passed; {v['baseline_evaluations']} original baseline and {v['regression_evaluations']} optimized historical evaluations passed; {controls['cases']}/287 negative controls preserved; {v['new_proof_records']:,} new and {v['historical_proof_records']:,} historical row proofs reconstructed; {v['benchmark_samples']} serial benchmark samples passed full candidate/proof identity checks."
    write('executive-summary.md',f'''# Cycle 9 executive summary

The accepted **C8-promotion-relative checkpoint is retained**. Cycle 9 adds immutable-state/serialization optimizations, a larger independent evaluation, offline calibration, typed temporal provenance, and inspector/CLI exports. No new operational model, threshold, native operator or production oracle was introduced. Isolated dependence ablations retain their experimental checkpoints separately.

The final game test comprises **100 complete synthetic games and 500 sampled nonterminal positions**, separate from 20 development and 20 calibration games. Independent-game recall is **{pct(independent['complete']['recall'])}**, with **{independent['complete']['exact_positions']}/500 exact legal sets**. The 128-position adversarial cohort has **{adversarial['complete']['exact_positions']}/128 exact sets**. Error and in-board counts are in the [engineering report](engineering-report.md); these finite synthetic cohorts do not establish universal correctness.

The historical 214-candidate workload changed from **{full[0]['aggregates']['cold']['latency_seconds']['p50']:.3f} → {full[1]['aggregates']['cold']['latency_seconds']['p50']:.3f} seconds cold** and **{full[0]['aggregates']['warm']['latency_seconds']['p50']:.3f} → {full[1]['aggregates']['warm']['latency_seconds']['p50']:.3f} seconds warm**. Proof payloads match exactly. Timing tails remain weak estimates from seven repetitions per arm. [Measured benchmark evidence]({link('performance/C9-optimized.json')}).

{abstention['resolved']} of {abstention['cases']} developmental castling abstentions resolve when supplied full game events are reused; missing events, removed rights and temporal-channel removal remove support. Raw native TVs and thresholds stay unchanged. Positive support remains partial conditional evidence. [Experiment]({link('abstention/summary.json')}).

Calibration is fit only on separate games and is displayed as an empirical diagnostic. Native confidence is not a probability of correctness. [Calibration findings](calibration-report.md).

**Architecture recommendation:** retain existing operators in production. A separately authorized, bounded credal prototype is justified as research; production activation is **no-go** until statistical, conditional-learning, solver and provenance obligations are met. [Decision](architecture-decision.md).

{measured} Fresh bootstrap and desktop/mobile browser verification passed. The delivery contains local commits only; no push or external deployment is authorized by this brief. [Verification]({link('verification.json')}), [browser evidence]({link('ui-verification.json')}).
''')
    packages=[
        ('01','Baseline lock','26 exact original evaluations; 1,941 historical files protected','baseline/verified.json'),
        ('02','Independent expansion','140 complete games / 700 samples; 128 adversarial; 80 special-move positions','datasets/manifest.json'),
        ('03','Structural generalization','Per-piece and relational strata; classified failure families and native traces','analysis/evaluation-summary.json'),
        ('04','Adversarial robustness','64 controlled pairs plus dedicated special moves and transformations','analysis/adversarial-pairs.json.xz'),
        ('05','Abstention resolution',f"{abstention['resolved']}/{abstention['cases']} development cases resolve through supplied events; removal controls retained",'abstention/development-experiment.json.xz'),
        ('06','Calibration','Independent calibration fit; reliability, proper scores, selective curves, uncertainty','calibration/results.json'),
        ('07','Dependence and revision','Idempotence, correlated ancestry, conflict, replay and removal ablations','dependence/summary.json'),
        ('08','Temporal evidence','Versioned observed/metadata/inferred categories plus historical controls','temporal/summary.json'),
        ('09','Performance','Six workloads; 252 before/after samples; exact proof parity','performance/C9-optimized.json'),
        ('10','Composition review','Complete specification review and three exact counterexamples; no new operator','composition/review.json'),
        ('11','Architectural decision','A operational; B conditional research only; production B no-go','composition/review.json'),
        ('12','API / CLI / inspector','Reports, per-piece metrics, calibration export, failure/provenance navigation; desktop/mobile','ui-verification.json'),
        ('13','Verification',f"{v['test_count']} tests, all historical suites, 287 controls, clean bootstrap and native boundary",'verification.json'),
        ('14','Consolidated delivery','Reports, proofs, models, commands, hashes and local commits','manifest.json')]
    write('package-matrix.md','# Cycle 9 work-package completion\n\n'+table(['WP','Package','Status','Evidence / outcome'],[
        ['C9-'+n,title,'Complete',f'[{detail}]({link(path)})'] for n,title,detail,path in packages])+'''

Completion records executed engineering and research work. Aspirational accuracy/latency targets are evaluated separately; a measured shortfall is not relabeled as a passed research target. No experimental model is promoted.
''')
    write('engineering-report.md',f'''# Cycle 9 engineering report

The delivery retains the accepted C8 checkpoint and optimizes host state/serialization work while preserving native proof semantics. Starting commit: `{START}`. Verified native-study source: `{study_head}`. Qualified application source: `{v['source_head']}`. Current production source hash: `{v['production_code_hash']}`. Model version: `{v['model_version']}`. Local commit history and final working-tree status are reported with the delivery; these source commits are distinct from the final evidence/report commit.

The implementation memoizes identities, FEN and square lookup on immutable state objects; detaches mutable constructor sequences; hashes model dataclasses without a redundant deep copy; and exports native TVs directly as fresh dictionaries. Model hashes are deliberately not memoized, so changing evidence still changes model identity. Native arithmetic, native source pins, learned descriptors, inference thresholds and operational/strict/experimental policies are unchanged.

{presentation_note}

## Historical acceptance comparison

{historical}

All 16 historical operational suites and all 10 established strict/experimental comparisons replay exactly. [Original summaries]({link('baseline/C8-promotion-relative-summary.json')}), [optimized regression receipt]({link('regression/verified.json')}).

## New cohorts

{cohorts}

{populations}

{intervals_table}

These cohorts have no historical C8 measurement on the same complete test population; the table is a new study of the unchanged model under the optimized implementation. Complete and in-board metrics, source-game/pair bootstrap intervals, per-piece scores and all structural strata are retained in the [evaluation summary]({link('analysis/evaluation-summary.json')}). No final held-out outcome was used to alter learning or thresholds. [Protocol](study-protocol.md).

Intervals use 500 deterministic source-cluster bootstrap draws. Related opening families can remain correlated; finite zero-error results do not bound population risk to zero. [Dataset coverage]({link('analysis/dataset-coverage.json')}) separately records phase, material, pawn structures, opening/structural families, check multiplicity, castling rights and en-passant metadata. These are descriptive counts, not additional independent samples.

## Mode comparisons and research targets

{comparisons}

The independent-game comparison above uses the same first 25 registered positions in every mode; it does not compare 500 operational positions with 25 strict positions. All modes score the same 80 special-move positions. Strict positive abstention reflects the missing native joint theorem, even when local evidence is strong. [Shard receipts and native proofs]({link('evaluation/')}).

{target_table}

Proportions in the target table are fractions, not percentages. Error totals cover all 908 new operational positions. Historical zero-error gates passed separately. [Target assessment]({link('analysis/research-targets.json')}).

## Verification and interfaces

{measured} The fresh runtime and dependency lock are recorded in the [bootstrap receipt]({link('bootstrap-context.json')}). Native-source hashes and all protected historical files remain unchanged. Actual CLI export and accepted API behavior passed [application smoke checks]({link('smoke/verified.json')}); the browser verified diagnostics, calibration export, failure proof navigation, temporal categories, strict/incomplete modes, invalid-input clearing and 390-pixel mobile layout with zero captured console/server errors. [UI receipt]({link('ui-verification.json')}), [recording and screenshots]({link(ui['session_dir']+'/SUMMARY.md')}).

The API adds `research_report` and `inspect_temporal_v9`. CLI commands add `research-report`, `calibration-export` and `temporal-inspect-v9`. Existing public inference paths remain available. Empirical mapping lookup occurs only in diagnostic presentation, after native inference, and carries `native: false` and `changes_classification: false`.

## Research findings and limits

Supplied events resolve {abstention['resolved']} developmental castling abstentions without changing native TVs; the full graph, rule IDs, evidence, source game and counterfactual controls are retained. [Abstention study]({link('abstention/development-experiment.json.xz')}). Dependence policies remain unchanged after duplicate, correlation, conflict and retraction controls. [Evidence audit]({link('dependence/summary.json')}). The [composition decision](architecture-decision.md) recommends existing operators operationally and no production extension.

Games are synthetic; opening and adversarial family dependence remains; special-move history is often incomplete; empirical calibration may shift across cohorts; native confidence is not calibrated correctness probability; positive legality remains partial; p95/p99 timing estimates are sample maxima. [Calibration](calibration-report.md), [performance](performance-report.md), [generalization](generalization-analysis.md).

Recommended Cycle 10 priorities: evaluate diverse human/engine game provenance under frozen splits; study temporal evidence transport and long histories; target remaining structural failure families through independently acquired relational evidence; improve calibration under shift with family-level uncertainty; and, only after explicit authorization, specify a bounded isolated credal prototype with proof certificates and a statistical front end. No new operator or universal-correctness claim follows from this delivery.
''')
    calrows=[];diagnostic_rows=[];calibration_intervals=[]
    for name,entry in cal['evaluations'].items():
        e=entry['in-board'];raw=e['raw-strength'];mapped=e['empirical-calibrated']
        calrows.append([name,raw['n'],f"{raw['brier']:.6f}",f"{mapped['brier']:.6f}",f"{raw['ece']:.6f}",f"{mapped['ece']:.6f}",f"{raw['log_loss']:.6f}",f"{mapped['log_loss']:.6f}"])
        for score in ('raw-strength','raw-confidence-as-diagnostic-score','strength-confidence-diagnostic','empirical-calibrated'):
            m=e[score];diagnostic_rows.append([name,score,m['n'],f"{m['brier']:.6f}",f"{m['ece']:.6f}",f"{m['log_loss']:.6f}"])
        u=e['cluster_uncertainty'];calibration_intervals.append([name,u['clusters'],' – '.join(f'{v:.6f}' for v in u['interval95']['calibrated_brier'])])
    write('calibration-report.md',f'''# Strength, confidence and empirical calibration

Native STV strength and confidence remain unchanged. The empirical mapping is fit on {cal['fit_games']} calibration games, {cal['fit_positions']} positions and {cal['fit_rows']:,} complete candidates from separate opening families. Ten strength bins use Laplace smoothing; empty bins retain zero observations and a one-half estimate. It is a diagnostic frequency estimate, never an inference gate. [Mapping and results]({link('calibration/results.json')}).

{table(['Held-out cohort (in-board)','Candidates','Raw Brier','Mapped Brier','Raw ECE','Mapped ECE','Raw log loss','Mapped log loss'],calrows)}

The raw-score columns assess numeric diagnostic behavior, not a claim that native STVs have probability semantics. The separate four-score comparison is:

{table(['Held-out cohort (in-board)','Diagnostic score','Candidates','Brier','ECE','Clipped log loss'],diagnostic_rows)}

Confidence-stratified precision/recall and selective risk/coverage retain the original supported classifications; they do not turn unknowns into decisions. Per-piece, special-move and evidence-volume strata report their own sample counts in the linked artifact.

{table(['Held-out cohort (in-board)','Source clusters','Calibrated Brier 95% interval'],calibration_intervals)}

![Reliability plots]({link('calibration/reliability.png')})

![Selective diagnostic curves]({link('calibration/selective-risk.png')})

Overall Brier and accuracy uncertainty resamples source games or controlled pairs (500 deterministic bootstrap draws), conditional on the fitted mapping; it does not include refitting uncertainty from the 20 calibration games. Bin-level Wilson intervals are explicitly naive to within-game dependence. Zero observed error produces a degenerate bootstrap risk interval and does not establish zero population risk. The full intervals and sample sizes are in the JSON; [per-candidate export]({link('calibration/predictions.csv')}) links every score to its native proof hash. SVG/PDF figures accompany the PNGs.

No mapping was fit to final held-out, adversarial or special-move labels. Performance across these cohorts is evidence about distribution shift, not grounds to retune the mapping on the final test. Independent games are synthetic and related opening families can remain correlated. Calibration does not supply the premise-validity certificates required by the composition proposal.
''')
    pieces=independent['per_piece'];families=independent['failure_families'];index=read_json(out/'analysis/failure-index.json')
    write('generalization-analysis.md',f'''# Structural generalization and abstention

The frozen checkpoint is evaluated on 100 held-out complete games, 500 nonterminal positions, 128 controlled adversarial positions and 80 special-move positions. Complete candidate sets and in-board sets are reported separately. Registered operational training examples are empty; isolated dependence ablations retrain controls only. The dataset generator and replay tests verify that every reference legal move occurs in the bounded candidate grammar. [Dataset and leakage manifest]({link('datasets/manifest.json')}).

{table(['Piece (held-out games)','Candidates','Recall','False legal','False illegal','Unknown'],[[p,m['candidates'],pct(m['recall']),m['false_positive'],m['false_illegal'],m['unknown']] for p,m in pieces.items()])}

{table(['Held-out unknown family','Candidates'],sorted(families.items(),key=lambda x:(-x[1],x[0])))}

The [full structural metrics]({link('analysis/evaluation-summary.json')}) group movement geometry, ray length, intermediate/destination occupancy, capture type, king exposure, pins, double checks, check resolution, promotion choice, castling, en passant, missing history and unknown sensory observations. These are offline evaluation labels; no oracle is introduced into production inference. Empty/unobserved strata are not evidence of robustness.

Primary-cause screening distinguishes missing hypotheses, supporting observations, dependence conflicts, thresholds, missing history and native-composition/specific-abstraction limits. Some categories remain ambiguous without a controlled intervention and are named accordingly; the taxonomy is not presented as a proven causal diagnosis. All major observed failure categories have representative native traces in the [proof archive]({link('analysis/failure-proofs.json.xz')}) and [navigable index]({link('analysis/failure-index.json')}). Each record retains rule IDs, evidence, native TVs, row proof hashes and its original evaluation shard.

{table(['Representative index','Mode','Failure family','Fixture / move','Classification'],[[r['index'],r['mode'],r['family'],r['fixture']+' / '+r['move'],r['classification']] for r in index[:12]])}

The adversarial study evaluates 64 counterfactual pairs with shared provenance: relevant occupancy/attack edits test sensitivity; irrelevant blocker edits test invariance. Outcomes, including unsupported members and any errors, remain explicit in [paired results]({link('analysis/adversarial-pairs.json.xz')}) and the [pair summary]({link('analysis/verification.json')}). All 287 historical native negative/removal controls remain valid; promotion transformations are retained separately.

The development-only history experiment resolves {abstention['resolved']}/{abstention['cases']} castling abstentions at unchanged raw TVs and thresholds. Missing events, suppressed temporal evidence and removed rights remove positive support. The native graph still does not prove universal king safety or historical legal play. No final held-out labels informed this intervention. [Full experiment]({link('abstention/development-experiment.json.xz')}).

Dependence ablations show stable native beliefs under duplicates and explicitly shared ancestry, deterministic replay, stable checkpoint reconstruction, and removal of the selected learned hypothesis after retracting every source group. The conflict intervention deliberately flips an observation label, first assigning a separate source group and then the original group; it tests revision policy and is not an independently acquired chess counterexample. The ancestry intervention copies an observation and annotates its shared lineage; actual spatial transformations are exercised by the separate 32 historical promotion controls. An ambiguous same-group observation is excluded conservatively. Raw duplicate rows can change the audit ledger/model identity while leaving beliefs equal. Unannotated correlated sources remain a provenance risk. [Ablation values, exclusions and native revision expressions]({link('dependence/summary.json')}).
''')
    write('performance-report.md',f'''# Inference performance

The initial profile identified repeated immutable-state identities/FENs, square scans, dataclass copying and native-TV export. Cycle 9 removes that redundant host work. It changes no native formula, rule ordering, proof field or learned descriptor. [Pre-edit profile]({link('performance/baseline-warm.txt')}), [optimized profile]({link('performance/C9-optimized-profile.txt')}).

{performances}

Seven repetitions per arm and six workloads produce 252 samples. Reference means native-operator caching disabled; cold means a new native session; warm reuses that session. Immutable input objects and loaded checkpoints are prepared before inference timing, matching the original benchmark convention. Exact complete candidate payload digests match reference/cold/warm and the original/optimized implementations. Every warm sample has zero native invocations and every sample is untruncated. [Original samples]({link('performance/C8-original.json')}), [optimized samples]({link('performance/C9-optimized.json')}).

The original and optimized arms ran serially at different times on the same shared host, after other study workers stopped. They are matched fixtures, not a randomized alternating timing trial; unrelated host activity may contribute to timing differences. Cold refers to native-session caching, not a new operating-system process or an unloaded checkpoint.

Historical Cycle 7 full-position p50 targets are {c7['aggregates']['cold']['latency_seconds']['p50']:.3f} seconds cold and {c7['aggregates']['warm']['latency_seconds']['p50']:.3f} seconds warm; their provenance was verified through the protected Cycle 8 manifest. They are historical host-specific measurements, not same-session C7 samples. The matched C8/C9 table supplies the current direct comparison. Research-target flags use point estimates; no statistical test establishes superiority over historical C7 timing.

Checkpoint size is {after['checkpoint_bytes']:,} bytes. The single checkpoint-load observations were {before['checkpoint_load_seconds']:.3f} seconds before and {after['checkpoint_load_seconds']:.3f} seconds after; they are not repeated timing estimates. Native calls, grounded atoms, hit rates and parent/child RSS are retained for every workload. Memory figures are separate cumulative high-water marks; they are not simultaneous total process-tree memory. p95/p99 are sample maxima and cannot establish reliable tail latency.

Inspector diagnostic decoration took a median {1000*statistics.median(s['decorate_seconds'] for s in smoke['presentation_samples']):.3f} ms, with JSON serialization taking {1000*statistics.median(s['json_serialization_seconds'] for s in smoke['presentation_samples']):.3f} ms in the single-candidate smoke workload. This adds zero native calls and preserves the input native result. Calibration is read and integrity-checked once per inspector response. [Presentation measurements]({link('smoke/verified.json')}).
''')
    write('reproduction.md',f'''# Reproducing Cycle 9

Verified native-study source: `{study_head}`. Qualified application source: `{v['source_head']}`. Starting baseline: `{START}`. Runtime: Python 3.12.12, SWI-Prolog 10.0.1, PLN `{v['runtime']['pln']['commit']}`, PeTTa `{v['runtime']['petta']['commit']}`. Dependencies and native file hashes are pinned and verified. The host must supply uv and the audited SWI-Prolog build; no Python inference fallback exists.

```bash
git clone /path/to/pln-chess /data/pln-chess-cycle9-replay
cd /data/pln-chess-cycle9-replay
git checkout --detach {study_head}
C9_OUT=/data/pln-chess-cycle9-replay-output bash scripts/cycle9_reproduce.sh
```

Use a fresh checkout without `.venv` or `.runtime` and a fresh output directory outside the checkout. From scratch, the driver executes the original C8 snapshot, regenerates data exactly, runs all tests/controls, historical regressions, new evaluation shards, serial paired benchmarks, analysis, source-bound acceptance and actual API/CLI smoke checks. Command receipts and logs retain source identities, parameters, exit status and duration. Interrupted shards resume only with matching production/driver/data/model identities and artifact hashes.

The delivered run bootstrapped at `682237b5a0aacf8495eb56fd1393150f05e0d3d4`, then advanced cleanly to `{study_head}` before any new native study execution. The exact dataset-replay gate exposed a checkout-name-dependent path filter; its correction changed only the offline generator and its test. The production hash did not change. The failed dataset and logs are preserved under `development/clean-path-audit-failure`. [Bootstrap transition]({link('bootstrap-context.json')}).

A second fresh checkout at the exact corrected study commit independently passed dependency bootstrap, identical runtime/production hashes, and exact registered dataset replay. Both its initial and final working trees were clean. This closes the bootstrap-source distinction without pretending the first failed invocation succeeded. [Fresh corrected-source receipt]({link('fresh-source-bootstrap/verified.json')}), [commands]({link('fresh-source-bootstrap/commands.json')}). The full native study is the main recorded run; this supplemental check does not claim a second execution of all native evaluations.

For this delivery, the original baseline replay and original serial benchmark were completed before source edits in an isolated original checkout, then copied into the fresh study output with their original source/command receipts. The optimized regressions, new cohorts, controls and tests ran against the fresh pinned runtime. Its complete runtime manifest matches the pre-edit runtime. The from-scratch command above reruns both sides when no preexisting receipts are supplied.

{presentation_note}

After the study, use the delivery checkout (with its dependencies installed using `bash scripts/bootstrap.sh --dependencies-only` if necessary), the reproduced output, and an environment with matplotlib 3.7.5 for figures. The supplemental bootstrap uses another fresh checkout. The presentation qualification rejects any production change beyond the exact CSS attribute and reruns the full tests before restoring the source-bound operational default:

```bash
.venv/bin/python -m scripts.cycle9_bootstrap_check --source "$PWD" --checkout /data/pln-chess-cycle9-bootstrap-replay --out /data/pln-chess-cycle9-replay-output
.venv/bin/python -m scripts.cycle9_presentation --out /data/pln-chess-cycle9-replay-output --study-checkout /data/pln-chess-cycle9-replay
python3 evaluation/cycle9_plots.py --out /data/pln-chess-cycle9-replay-output
C9_OUT=/data/pln-chess-cycle9-replay-output TMPDIR=/dev/shm .venv/bin/python -m scripts.cycle9_ui_verify --out /data/pln-chess-cycle9-replay-output --work /data/pln-chess-cycle9-browser
cp -a /data/pln-chess-cycle9-replay-output/. artifacts/cycle9/
.venv/bin/python -m evaluation.cycle9_reporting --out artifacts/cycle9
```

Browser verification requires ProofShot, agent-browser and Chromium. It records real requests, screenshots, video, actual JSON export hashes and owned-server cleanup; it publishes nothing. The report renderer hashes artifacts and documents, excluding the manifest itself. Wall times, timestamps and videos are naturally run-specific; dataset/model identities and semantic proof equality are the deterministic reproduction gates.
''')
    write_json(out/'package-status.json',dict(all_14_packages_complete=True,packages=[dict(id='C9-'+n,name=title,status='complete',evidence=path) for n,title,detail,path in packages],
        source_head=v['source_head'],native_study_source_head=study_head,new_learning_promoted=False,new_native_operator=False,pushed=False))
    files=[p for p in out.rglob('*') if p.is_file() and p!=out/'manifest.json']+list(docs.glob('*.md'))
    manifest={str(p.relative_to(ROOT)):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(files)}
    assert not [p for p,v in manifest.items() if v['bytes']>=100*1024*1024], 'Split oversized artifact before delivery'
    write_json(out/'manifest.json',dict(schema=9,source_head=v['source_head'],files=manifest,total_bytes=sum(v['bytes'] for v in manifest.values()),
        scope='Delivered Cycle 9 artifact and document hashes; manifest excludes itself. Source commits and production hash bind implementation.'))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);run(p.parse_args().out)
