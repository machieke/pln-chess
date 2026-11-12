"""Render delivery tables from closed, source-bound Cycle 14 receipts."""
import argparse
from pathlib import Path
import statistics

from pln_chess.common import ROOT, read_json, write_json
from evaluation.cycle3 import read_gzip


def pct(value):
    return 'undefined' if value is None else f'{100*value:.1f}%'


def table(headers, rows):
    def line(row):
        return '| ' + ' | '.join(str(x).replace('|', '\\|').replace('\n', ' ') for x in row) + ' |'
    return '\n'.join([line(headers), line(['---']*len(headers)), *map(line, rows)])


def measurement(row):
    c=row['counts']
    return [c[k] for k in ('N_all','N_directional','N_answered','N_correct','N_wrong')]+[
        pct(c['answered_accuracy']),pct(c['directional_coverage']),c['N_reference_unknown']]


def interval(row, name):
    values=row['intervals']['estimates'][name]
    return f"{pct(values['low'])}–{pct(values['high'])} ({values['defined_replicates']}/1000 defined replicates)"


def run(out):
    out=Path(out).resolve()
    def get(name):return read_json(out/name)
    gates={name:get(name) for name in ('acceptance.json','current/verified.json','baseline/reproduction-receipt.json',
        'clean-research/verified.json','clean-research/proof-replay/verified.json','interfaces/verified.json',
        'ui/verified.json','datasets/integrity.json','performance/summary.json','responses/summary.json',
        'reversals/summary.json','dependence/summary.json','architecture/boundary.json')}
    assert all(x['passed'] for x in gates.values())
    acceptance=gates['acceptance.json'];current=gates['current/verified.json'];clean=gates['clean-research/verified.json']
    proof=gates['clean-research/proof-replay/verified.json'];perf=gates['performance/summary.json']
    response=gates['responses/summary.json'];reversal=gates['reversals/summary.json'];dependence=gates['dependence/summary.json']
    registry=get('model/registry.json');evaluation=get('evaluation/summary.json')['models'];selection=get('development/selection.json')
    ablations=get('ablations/summary.json');primary=registry['primary_immediate'];temporal=registry['primary_temporal']
    def cohort(model,split='test',horizon=1):
        return next(r for r in evaluation[model]['cohorts'] if r['split']==split and r['horizon']==horizon)
    immediate=cohort(primary);two=cohort(temporal,horizon=2);three=cohort(temporal,horizon=3)
    source=cohort('source-family-heldout','source-holdout')
    resources=get('resources.json')
    headings=['Panel','All','Directional references','Answered','Correct','Wrong','Answered accuracy','Directional coverage','Unknown reference']
    primary_table=table(headings,[[name,*measurement(row)] for name,row in (
        ('Immediate / new final test',immediate),('Two supplied plies / same 50 roots',two),
        ('Three supplied plies / same 50 roots',three),('TCEC / TCEC-excluded preference fit',source))])
    uncertainty_table=table(['Panel','Independent groups','Answered accuracy 95% interval','Directional coverage 95% interval'],
        [[label,row['intervals']['groups'],interval(row,'answered_accuracy'),interval(row,'directional_coverage')]
         for label,row in (('Immediate',immediate),('Two supplied plies',two),
                           ('Three supplied plies',three),('TCEC family holdout',source))])
    model_rows=[]
    for name,entry in registry['models'].items():
        report=read_json((ROOT if entry.get('historical') else out)/entry['path']).get('training_report',{})
        model_rows.append([name,entry['training_cases'],report.get('hypotheses','see checkpoint'),
            entry['abstraction'],entry['concepts'],entry['dependence'],entry['version']])
    docs=ROOT/'docs/cycle14';docs.mkdir(parents=True,exist_ok=True)
    def write(name,text):
        (docs/name).write_text(text.strip()+'\n')

    # Keep the methodological specification, then replace only the generated
    # result section so rerendering cannot duplicate or alter the protocol.
    calibration_path=docs/'evaluation-calibration.md'
    calibration_spec=calibration_path.read_text().split('\n## Registered final results\n',1)[0]
    score_rows=[];reliability_rows=[];risk_rows=[]
    def number(value):return 'undefined' if value is None else f'{value:.6f}'
    for label,row in (('Immediate final test',immediate),('Two supplied plies',two),
                      ('Three supplied plies',three),('TCEC family holdout',source)):
        diagnostic=row['calibration']
        for arm,score in diagnostic['scores'].items():
            intervals=diagnostic['clustered_95_intervals'][arm]
            bounds=lambda metric: number(intervals[metric]['low'])+'–'+number(intervals[metric]['high'])
            score_rows.append([label,arm,score['N'],number(score['brier']),bounds('brier'),
                number(score['log_loss']),bounds('log_loss')])
        for bin_ in diagnostic['reliability']:
            reliability_rows.append([label,bin_['arm'],bin_['bin'],bin_['N'],
                number(bin_['mean_probability']),number(bin_['observed_A_fraction'])])
        for risk in diagnostic['selective_risk']:
            risk_rows.append([label,risk['diagnostic_certainty_threshold'],risk['N'],
                risk['N_wrong'],pct(risk['risk']),pct(risk['coverage'])])
    write('evaluation-calibration.md',calibration_spec+'\n\n## Registered final results\n\n'+
        'These scores use the frozen mappings and resolved directional references only. Lower Brier score and log loss indicate better diagnostic fit to that event; they do not establish useful move selection. Intervals resample source groups. Empty reliability bins and undefined selective risks remain visible.\n\n'+
        table(['Panel','Diagnostic arm','Resolved N','Brier','Brier 95% interval','Log loss','Log-loss 95% interval'],score_rows)+
        '\n\nReliability bin numbers 0–4 correspond to [0,.2), [.2,.4), [.4,.6), [.6,.8), and [.8,1]. These are evaluation-bin populations, separate from the calibration fitting populations retained in each frozen mapping.\n\n'+
        table(['Panel','Arm','Bin','N','Mean diagnostic probability','Observed A fraction'],reliability_rows)+
        '\n\nSelective-risk thresholds below are fixed diagnostics on native directional answers. No threshold was selected from final outcomes and native classifications remain unchanged.\n\n'+
        table(['Panel','Diagnostic certainty threshold','Selected N','Wrong','Risk','Resolved-direction coverage'],risk_rows))

    write('preference-learning.md',f'''# Native preference learning

Development selected **{registry['selected_descriptor']}**, using correct-answer yield, answered accuracy and then the registered simpler descriptor as tie breakers. The selected immediate model is `{primary}` and the continuation model is `{temporal}`. Selection used 80 development roots; the [selection receipt](../../artifacts/cycle14/development/selection.json) states that final predictions were not observed. Thresholds, checkpoint hashes and calibration mappings were then bound in the [evaluation freeze](../../artifacts/cycle14/evaluation-freeze.json).

{primary_table}

The immediate answered-accuracy 95% source-group bootstrap interval is {interval(immediate,'answered_accuracy')}; directional coverage is {interval(immediate,'directional_coverage')}. The source-held-out accuracy interval is {interval(source,'answered_accuracy')}. Undefined or very sparse answered denominators do not establish reliable preference quality.

{uncertainty_table}

{table(['Model','Training observations','Hypotheses','Abstraction','Concepts','Dependence handled','Version'],model_rows)}

All fitted models remain experimental. Native `Truth_Revision` updates three independent channels from registered, generation-bound evidence. Native `Truth_ModusPonens` applies a learned conditional to an explicitly supplied observation packet. Host code supplies bounded descriptors, ancestry grouping and observation trust; it does not calculate substitute truth-value formulas. A, B and nondirectional channels are not a normalized distribution. Unknown labels are excluded from directional updates. Incomplete observations and indistinguishable directional packets are explicitly excluded, with counts in each [learning receipt](../../artifacts/cycle14/learning/).

Frozen C13, old-label historical, revised-label historical, expanded-corpus, refined-descriptor, concept, source-family and temporal arms remain separate checkpoint identities. The matched studies distinguish their effects. New data and repeated old observations are separate arms; unsafe counting is never a default. The dedicated source-family preference fit excludes all TCEC preference-training records. It retains the common development-selected descriptor and frozen upstream field/concept checkpoints; this is not an end-to-end claim of no prior exposure to that family.

The accepted legal checkpoint remains `{current['model_version']}`. No experimental preference checkpoint becomes a legal default, strategic utility or automatic selector. Every answer is a native conditional on host-assembled relative evidence; complete joint strategic proofs remain unavailable.
''')

    effect_rows=[]
    for row in ablations['effects']:
        delta=row['effect']['right_minus_left'];ci=row['effect']['clustered_95_intervals']['correct_answer_yield']
        effect_rows.append([row['factor'],row['split'],row['horizon'],
            f"{row['left_counts']['N_correct']}/{row['left_counts']['N_answered']}",
            f"{row['right_counts']['N_correct']}/{row['right_counts']['N_answered']}",
            pct(delta['directional_coverage']),pct(delta['correct_answer_yield']),f"{pct(ci['low'])}–{pct(ci['high'])}"])
    temporal_rows=[]
    for panel in ablations['temporal']:
        for contrast in panel['paired']:
            effect=contrast['effect'];ci=effect['clustered_95_intervals']['correct_answer_yield']
            temporal_rows.append([panel['split'],panel['horizon'],contrast['factor'],
                pct(effect['right_minus_left']['directional_coverage']),pct(effect['right_minus_left']['correct_answer_yield']),
                f"{pct(ci['low'])}–{pct(ci['high'])}"])
    majority_rows=[[row['split'],row['majority_class'],*measurement(row)]
        for row in ablations['evaluation_only_majority']]
    write('ablations.md',f'''# Matched ablations

Each contrast below uses the same evaluation rows, references and ancestry groups. Differences are right arm minus left arm. Percentage differences are percentage points. `correct/answered` displays directional answers only; unknown references remain outside agreement scoring. The [full receipt](../../artifacts/cycle14/ablations/summary.json) binds both checkpoint names, all denominators and 1,000 paired source-group bootstrap replicates.

{table(['Factor','Split','Horizon','Left correct/answered','Right correct/answered','Coverage difference','Correct-yield difference','Yield 95% interval'],effect_rows)}

Temporal contrasts hold the endpoint reference target fixed even when the input contains only root observations. Immediate, continued and explicitly omitted input are evaluated under the same checkpoints where stated. Horizon-specific keys may cause an immediate-only model to abstain on unseen horizon keys; this is a representation limitation, not an empirical gain in reasoning.

{table(['Split','Horizon','Matched temporal contrast','Coverage difference','Correct-yield difference','Yield 95% interval'],temporal_rows)}

The training-only majority baseline is evaluation code and never enters production inference. Its class is chosen from training labels only; it answers every resolved test direction and retains unknown references outside agreement scoring.

{table(['Split','Training majority',*headings[1:]],majority_rows)}

Repeated reference analyses and continuations preserve channel truth values with dependence handling; the unsafe control inflates confidence in {len(dependence['unsafe_inflated_rules'])} rules. The [dependence report](evidence-dependence.md) distinguishes identical native beliefs from different delivery provenance. Concept additions, descriptor refinements and omission training are not assumed beneficial because they were implemented. These finite controlled comparisons do not establish strategic playing strength or isolate every interaction among supervision, abstraction and source distribution.
''')

    write('response-coverage.md',f'''# Bounded response coverage

The registered response panel contains **{response['branch_comparisons']} conditional comparisons in {response['independent_groups']} root groups**, with at most three supplied branches per candidate. Its labels comprise 106 directional, four nondirectional and 70 unknown observations. Twenty primary references are reused and 160 additional reference analyses are retained. The branch crossproducts are dependent, not 180 independent positions.

{table(headings,[['Supplied branch crossproducts',*measurement({'counts':response['counts']})]])}

There are {response['opposed_supported_panels']} panels with opposing supported branch-conditioned directions, {response['incomplete_endpoint_comparisons']} incomplete endpoint comparisons, {response['unknown_legality_branch_occurrences']} branch occurrences with unknown legality and {response['supported_illegal_branch_occurrences']} with supported illegality. Offline enumeration records {response['known_unexamined_replies']} unexamined legal replies across the candidate roots. No exhaustive coverage or global robust preference is asserted. [Every result and archive](../../artifacts/cycle14/responses/) retains branch indices, ancestry, selection provenance and coverage.

Selection retains the registered teacher-assisted PV and adds up to two deterministic hash-sampled legal replies and actor continuations. It does not use PLN success. Teacher, sampled and controlled diagnostic branches are explicitly identified; a published game continuation is not inferred from a teacher PV. Supplied lines are hypothetical conditional evidence, never an optimal-response search.

The king-exposing candidate remains a diagnostic branch with separate legality status. Missing two/three-ply endpoints remain incomplete. A fourth response branch is rejected. A controlled native test produces opposing A/B answers on two supplied branches and verifies that both survive archive reconstruction while global preference and automatic selection remain absent. [Native branch test](../../tests/test_cycle14_branches.py) and [test receipt](../../artifacts/cycle14/branch-semantics-unit.txt) are disclosed unit evidence, not independent strategic successes.

Identical final board layouts reached through different supplied histories have distinct request identities. The inspector exposes branch coverage and before/after conditional outputs; no average, product or minimum of branch strengths is labeled a native robust conclusion.

The first dense archive attempt exceeded the interactive serialization limit and is retained. Offline export, import and full comparison use a separately registered ten-million object-occurrence limit; {response['panels_exceeding_interactive_archive_budget']} panels exceed the default interactive limit of two million. The default interface still rejects those full exports explicitly. See [the storage policy](proof-storage.md); summaries and paginated graphs remain available, and no scientific predictions or cohort membership changed.
''')

    timings=[];audits=[]
    for summary in perf['summaries']:
        metrics=summary['metrics']
        timings.append([summary['workload'],summary['arm'],summary['temperature'],
            f"{metrics['interactive_total_seconds']['median']:.6f}",
            f"{metrics['inference_seconds']['median']:.6f}",
            int(metrics['canonical_interactive_bytes']['median']),int(metrics['compressed_audit_bytes']['median']),
            int(metrics['process_peak_rss_kib']['median']),metrics['interpreter_process_launches']['median']])
        retrieval=metrics['graph_page_retrieval_seconds']['median']
        audits.append([summary['workload'],summary['arm'],summary['temperature'],
            int(metrics['canonical_full_bytes']['median']),
            f"{metrics['full_audit_validation_and_compression_seconds']['median']:.6f}",
            'not applicable' if retrieval is None else f'{retrieval:.6f}',
            f"{metrics['interactive_total_seconds']['p95']:.6f}",
            f"{metrics['interactive_total_seconds']['sample_p99']:.6f}",
            int(metrics['largest_child_peak_rss_kib']['median'])])
    loading=[]
    for workload in sorted({r['workload'] for r in perf['rows']}):
        for arm in ('legacy','compact'):
            rows=[r for r in perf['rows'] if r['workload']==workload and r['arm']==arm and r['temperature']=='cold']
            loading.append([workload,arm,len(rows),f"{statistics.median(r['runtime_load_seconds'] for r in rows):.6f}",
                f"{statistics.median(r['model_load_seconds'] for r in rows):.6f}"])
    ratios=[]
    for row in perf['comparisons']:
        r=row['paired_speed_ratio'];ratios.append([row['workload'],row['temperature'],f"{r['median']:.2f}×",
            f"{r['median_bootstrap_95'][0]:.2f}–{r['median_bootstrap_95'][1]:.2f}×",pct(row['paired_payload_reduction']['median'])])
    write('performance.md',f'''# Matched performance measurements

Four frozen workloads compare legacy full responses and compact summaries with the same C13 checkpoints, native evidence and inputs. Each arm has **{perf['repetitions']} repetitions**, in fresh processes, with cold and warm requests. All {len(perf['rows'])} measured request groups have exact native/evidence parity. Workloads cover one quiet pair, three mixed pairs including promotion/tactical cases, two supplied plies and three supplied plies. Alternating arm order reduces ordering bias.

{table(['Workload','Arm','Temperature','Median interactive seconds','Median inference seconds','Interactive bytes','Compressed audit bytes','Parent peak KiB','Interpreter launches'],timings)}

{table(['Workload','Temperature','Median paired legacy/compact latency','95% median-ratio interval','Interactive payload reduction'],ratios)}

Complete-audit costs and interactive tail samples are separate measurements. The benchmark requests 64 proof objects per page. All time columns below are seconds; audit, retrieval, byte and RSS values are medians over twenty runs.

{table(['Workload','Arm','Temperature','Reconstructed full bytes','Audit validation + compression seconds','Graph page seconds','Interactive p95 seconds','Interactive sample p99 seconds','Largest child peak KiB'],audits)}

{table(['Workload','Arm','Fresh processes','Median runtime load seconds','Median model load seconds'],loading)}

Interactive latency includes inference and canonical serialization. Model/runtime loading is measured separately and excluded symmetrically. Compact warm requests reuse a durable request bound to source, state, history, models, runtime, branches and options. This avoids repeated work; it is not a native interpreter speedup. Cold construction, complete archive validation/compression and graph-page retrieval have separate distributions in the [benchmark receipt](../../artifacts/cycle14/performance/summary.json). Returning less data is an interface improvement, not proof that complete-audit execution became equally fast.

Parent peak RSS is measured in a fresh process per workload/arm/repetition and includes audit validation/export. Warm RSS retains the prior cold peak and caches. Child maximum RSS is reported separately and never added to parent lifetime maxima as a fictitious simultaneous working set. Twenty-observation p99 is a sample statistic, not a service guarantee. Median uncertainty uses 1,000 bootstrap samples.

The [pre-optimization profile](../../artifacts/cycle14/profile-before/profile.json) and storage profiles are instrumented diagnostics under concurrent work. Their cumulative times overlap and cannot supply headline speed ratios. The isolated benchmark rejects concurrent owned study/native workers; unrelated host load remains uncontrolled and is disclosed. No browser transfer/rendering latency guarantee is inferred from functional screenshots.

Per-request data-access records distinguish persistent learned checkpoint hypotheses, host relation/cache entries, grounded proposition occurrences, derived proof nodes, stored proof objects and invalidations. Persistent native-resident atoms are zero. A reused summary retains its original proof census while recording zero newly materialized grounding. The host Merkle index is not a persistent native reasoning graph.
''')

    legal_table=table(['Accepted legal cohort','Exact legal sets'],[
        ['External FEN-only','793/1,020'],['External supplied history','1,020/1,020'],
        ['C9 adversarial','112/128'],['C9 special moves','71/80'],['C10 synthetic adversarial','98/112']])
    reversal_table=table(['Panel','Horizon','All','Structural criterion','Both references resolved','Reference flips','Model flips','Successful controlled outcome'],[
        [r['arm'],r['horizon'],r['N'],r['structural_criteria_met'],r['N_resolved_both'],r['reference_reversals'],r['model_reversals'],r['successes']]
        for r in reversal['panels']])
    reversal_path=docs/'preference-reversals.md'
    reversal_spec=reversal_path.read_text().split('\n## Registered final outcomes\n',1)[0]
    cases=read_gzip(out/'reversals/panel.json.xz')
    case_rows=[[r['id'],r['arm'],r['horizon'],r['initial_label']+' → '+r['endpoint_label'],
        r['before']['status']+' → '+r['after']['status'],r['successful_registered_outcome'],
        ', '.join(r['failed_reasons']) or 'none'] for r in cases]
    write('preference-reversals.md',reversal_spec+'\n\n## Registered final outcomes\n\n'+
        reversal_table+'\n\nEvery registered opportunity and persistence control appears below at both horizons. Three plies remains primary. The two horizons reuse the same twenty independent roots. Failure reasons are diagnostic criteria, not independent observations.\n\n'+
        table(['Root','Registered arm','Horizon','Reference before → after','Native before → after','Successful outcome','Failed conditions'],case_rows))
    primary_counts=immediate['counts']
    target=primary_counts['N_answered']>=50 and (primary_counts['answered_accuracy'] or 0)>=.8 and (primary_counts['directional_coverage'] or 0)>=.5
    findings=[
        ('01','Baseline lock and reproduction','Delivered and independently reproduced','588 baseline tests; 527 research artifacts; 206 legal shards with exact native proof parity.'),
        ('02','Registered study and evaluation contract','Delivered and frozen','940 roots, fixed partitions, three descriptor candidates and frozen final-evaluation barrier.'),
        ('03','Reference adapter audit','Delivered and tested','Synthetic stale-bound defect reproduced; zero stale-bound pairs observed in 41 empirical reruns.'),
        ('04','Reference uncertainty','Delivered and evaluated','28/41 former immediate unknowns directional; 34/50 former temporal unknowns directional, one nondirectional.'),
        ('05','Independent corpus','Delivered; coverage limitation recorded','600 new roots, 200 final-test groups, 145 directional test references; zero new promotion roots.'),
        ('06','Relative representation','Delivered and evaluated',f"Selected {registry['selected_descriptor']}; seven locality controls pass; abstraction adequacy is judged by final transfer."),
        ('07','Native preference learning','Delivered and evaluated',f"Immediate {primary_counts['N_correct']}/{primary_counts['N_answered']} answered correctly; {pct(primary_counts['directional_coverage'])} directional coverage; quality target {'met on the registered count criterion' if target else 'not demonstrated'}."),
        ('08','Dependence and label revision','Delivered and replayed',f"Handled repeats preserve native TVs; unsafe repetition inflates {len(dependence['unsafe_inflated_rules'])} rules; byte replay and rollback pass."),
        ('09','Controlled temporal study','Delivered and evaluated',f"Two-ply {two['counts']['N_correct']}/{two['counts']['N_answered']}; three-ply {three['counts']['N_correct']}/{three['counts']['N_answered']}; matched target contrasts retained."),
        ('10','Reversal and persistence','Delivered with all outcomes',f"Primary-horizon successful outcomes: {sum(r['successes'] for r in reversal['panels'] if r['horizon']==3)}/20 across opportunities and controls; see separate arms."),
        ('11','Response coverage','Delivered and tested',f"180 dependent comparisons / ten roots; {response['opposed_supported_panels']} opposed supported panels; no global robust preference."),
        ('12','Concept generalization','Delivered and evaluated','21 correct / 80 new groups, 59 abstentions, zero wrong supported; 258/258 controls; prior concepts preserved.'),
        ('13','Evaluation and calibration','Delivered and frozen','Explicit denominators, source-clustered intervals, separate diagnostic calibration; no native-channel renormalization.'),
        ('14','Factorial ablations','Delivered and evaluated','Matched supervision, representation, evidence, concept, dependence and temporal contrasts; negative and undefined estimates retained.'),
        ('15','Compact proof representation','Delivered and fully replayed',f"{proof['archives']} full archive reconstructions and complete native trace coverage; all 109 earlier-generation features match."),
        ('16','Caching and performance','Delivered and benchmarked','Twenty repetitions per arm/workload; exact evidence parity; measured summary gains distinguished from complete-audit cost.'),
        ('17','API, CLI and inspector','Delivered with documented interface limits','Actual CLI restarts, durable graph/archive retrieval, desktop/mobile and byte-exact browser reconstruction. Direct /compact-preferences entry is required; dense bulk archives can exceed the interactive export budget.'),
        ('18','Preservation and isolation','Delivered; mandatory gates passed',f"{current['test_count']} tests, 584,112 legal rows, 287 negative and 27 history controls, two recoveries/76 holdouts; 16,596 old files unchanged."),
        ('19','Clean reproduction and resources','Delivered with resource-accounting shortfalls','Fresh pinned environment; all native feature proofs replayed, selected observations/references rerun, all model/ledger/study outputs compared. Complete global CPU/process/transient-byte totals remain unavailable; six baseline terminal analyses omitted node counters.'),
        ('20','Delivery and readiness','Delivered locally','Continue preference research; no move selection, new operator, legal promotion, push or deployment.')]
    write_json(out/'delivery/package-matrix.json',dict(schema='c14-delivery-matrix-v1',packages=[dict(id='C14-'+number,
        title=title,engineering_delivery_status=engineering,research_outcome=research) for number,title,engineering,research in findings],
        production_code_hash=acceptance['production_code_hash'],recommendation='Continue preference research',remote_writes=False))
    write('package-matrix.md','# Twenty-package delivery matrix\n\nEngineering completion and research outcomes are separate. A passing execution receipt does not establish the tested hypothesis.\n\n'+
        table(['Package','Scope','Engineering delivery status','Research outcome'],[['C14-'+n,t,e,r] for n,t,e,r in findings])+
        '\n\n[Machine matrix](../../artifacts/cycle14/delivery/package-matrix.json) · [Engineering evidence](engineering-report.md) · [Readiness decision](readiness-decision.md)')

    write('engineering-report.md',f'''# Cycle 14 engineering report

Cycle 14 delivers the registered preference-research and compact-proof package locally. Engineering gates passed; preference conclusions remain conditional and experimental. The [twenty-package matrix](package-matrix.md) records delivery separately from research success. The recommendation is **continue preference research**. No push, deployment, autonomous selection, new native operator or legal checkpoint change occurred.

The starting commit is `54353579e7921f9b47f43bbde1aa61cb887bc6e4`. Frozen production hash is `{acceptance['production_code_hash']}`. The clean research source is `{clean['source_head']}` and current legal/test source is `{current['source_head']}`. Later evidence/documentation commits do not alter the frozen production code. [Source freeze](../../artifacts/cycle14/source-freeze.json) and [acceptance](../../artifacts/cycle14/acceptance.json) bind the runtime, source and unchanged legal model.

## New preference measurements

{primary_table}

Immediate 95% source-clustered intervals: answered accuracy {interval(immediate,'answered_accuracy')}; directional coverage {interval(immediate,'directional_coverage')}. Source-held-out answered accuracy: {interval(source,'answered_accuracy')}. The immediate numerical quality target is {'met on the registered answer-count criterion' if target else 'not demonstrated'}. Sparse answered samples, abstention and reference resolution remain separate limitations. [Learning and model inventory](preference-learning.md), [calibration](evaluation-calibration.md), and [matched ablations](ablations.md) retain every arm and uncertainty estimate.

The corpus has 940 registered independent root groups, 600 new, partitioned into 422 training, 80 development, 60 calibration, 200 final test, 60 source holdout, 62 historical calibration and 56 historical test diagnostics. The final test has 145 directional references, three nondirectional and 52 unknown. The four collection strata share some publishers; zero new promotion roots is a recorded coverage gap. [Provenance and ancestry](dataset-provenance.md) states the overlap checks and their limits.

The revised supervision resolves 28/41 historical immediate unknowns to directions, leaving 13; among 50 historical temporal unknowns, 34 become directional, one nondirectional and 15 remain unknown. Remaining immediate causes are seven budget disagreements, three overlapping bounds, two insufficient margins and one mate-order ambiguity; remaining temporal causes are six disagreements, six overlapping bounds and three insufficient margins. The synthetic stale-bound parser defect was not observed in the 41 empirical reruns. [Complete label audit](reference-label-audit.md) distinguishes methodological revisions from proven corrections.

## Temporal transfer and controls

Two and three plies share the same 50 independent final roots. The [temporal study](temporal-study.md) compares fixed checkpoints and observation contexts against matched endpoint targets; teacher-supplied continuations are not optimal play.

{reversal_table}

All opportunities, persistence controls, unsuccessful patterns and removal fits are retained in [the reversal report](preference-reversals.md). The [response study](response-coverage.md) has 180 crossproducts from only ten independent roots and retains known unexamined replies, unknown legality and incomplete endpoints. Native outputs remain separate by branch; no global robust preference is manufactured.

Frozen concept models answer 21/80 new independent cases correctly and abstain on 59, with zero wrong supported classifications and 258/258 dependent controls passing. Positive recall including abstention is 20/48. Current-source replay preserves all 466 historical native concept outputs, including 306/306 prior test results and the external 28 correct/68 unknown result. [Concept transfer](concept-generalization.md) discloses the missing-conditional census and limited structural targets.

Handled repeated evidence preserves native TVs; unsafe counting inflates {len(dependence['unsafe_inflated_rules'])} rules. Checkpoint/ledger replay, supersession and rollback are byte-identical where inputs are identical. Calibration is host diagnostic scoring on resolved references and never changes native TVs or decisions.

## Preservation, proof integrity and reproduction

The starting environment independently regenerated 527 research artifacts, 340 immediate labels, 120 temporal labels and 400 native feature artifacts, with byte-identical checkpoints and native proof parity. Its 588 tests passed. The frozen verification checkout passes **{current['test_count']} tests**, all 206 legal shards / 584,112 candidate rows, 287 negative controls, 27 history controls, two recoveries and 76 holdouts. There are zero changed classifications and exact native proof parity; 16,596 historical files remain unchanged.

{legal_table}

The accepted checkpoint remains `{current['model_version']}`, byte-identical to Cycle 12. The architecture gate executes oracle-disabled production imports and native training/final-inference replay; it is a concrete audit, not a formal proof of every possible flow.

All **{proof['archives']}** selected compact archives reconstruct exactly and cover every archived native node with an ordered replayed trace. Selected fresh observation construction complements complete proof replay. All 109 completed pre-optimization features preserve exact observations and canonical evidence. Actual CLI restarts and browser upload/download reconstruction verify durable audit access. [Proof storage](proof-storage.md), [performance distributions](performance.md), and [reproduction scope](reproduction.md) distinguish host storage, cached computation, native inference, and audit cost.

The inspector is available directly at `/compact-preferences`; the legacy homepage does not render its intended navigation link. This entry-navigation limitation remains explicit in [browser evidence](../../artifacts/cycle14/ui/final-trained/navigation-note.json) and the package matrix. The functional inspector checks do not claim that the homepage link passed.

Dense response roots can also exceed the default interactive full-archive serialization budget. The offline response study uses the explicit ten-million occurrence policy, retaining the failed default-budget run and validating exact reconstruction without changing scientific predictions. A separate dense archive regression passes in the fresh research checkout, supplementing the full frozen-source test suite. [The storage contract](proof-storage.md) states both limits.

Clean reproduction compares {clean['compared_artifacts']} research artifacts with byte-identical models and ledgers. The full reference generation is an explicit immutable input; selected raw reference searches are repeated independently. It does not claim every new engine search or observation construction was rerun. Complete recorded native proofs are replayed.

[Resource accounting](../../artifacts/cycle14/resources.json) records {resources['reference_reported_nodes']['total']:,} available reported reference nodes, {resources['measured_cpu_hours_lower_bound']:.2f} measured CPU hours as a lower bound, and {resources['retained_artifact_bytes']/(1024**3):.2f} GiB of retained artifacts at its snapshot. Six baseline terminal analyses lack node counters, and early CPU, interpreter-launch and transient-byte accounting is incomplete. Available node counts and retained storage satisfy their recorded ceilings; complete global compute/launch/node compliance is unverified. The original missing-prerequisite baseline control failure remains retained beside its successful fresh recovery; it caused no scientific baseline discrepancy.

Remaining limits include coarse/fine descriptor tradeoffs, sparse source-held-out directions, short teacher PVs, no new promotion roots, unresolved references, uncertain correlated premises, high concept abstention, non-exhaustive branches and absent native joint strategic composition. Preference agreement alone establishes no playing strength. [Readiness](readiness-decision.md) states the next research decision.
''')
    print('C14 EVIDENCE TABLES AND PACKAGE MATRIX RENDERED',flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',default='artifacts/cycle14')
    run(parser.parse_args().out)
