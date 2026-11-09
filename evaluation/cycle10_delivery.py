"""Render the consolidated package from measured, source-bound study artifacts."""
import argparse
import os
from pathlib import Path
from pln_chess.common import ROOT,read_json,write_json
from scripts.cycle9_baseline import sha


def pct(value):return '—' if value is None else f'{100*value:.4f}%'
def num(value):return '—' if value is None else f'{value:.8g}'
def table(headers,rows):
    return '\n'.join(['| '+' | '.join(headers)+' |','|'+'|'.join('---' for _ in headers)+'|',
        *('| '+' | '.join(str(v) for v in row)+' |' for row in rows)])


def artifact_manifest(out,docs):
    out=Path(out).resolve();docs=Path(docs).resolve();manifest={}
    for directory in (out,docs):
        for path in sorted(directory.rglob('*')):
            if path.is_file() and path!=out/'manifest.json':
                manifest[os.path.relpath(path,out)]=dict(sha256=sha(path),bytes=path.stat().st_size)
    write_json(out/'manifest.json',dict(schema=10,base='Directory containing this manifest',files=manifest,
        scope='Artifacts and reports at rendering time; regenerate after browser verification and final report updates. Manifest excludes itself.'))


def run(out,docs):
    out=Path(out).resolve();docs=Path(docs).resolve();docs.mkdir(parents=True,exist_ok=True)
    originals=ROOT/'docs/cycle10'
    if docs!=originals.resolve():
        for name in ('dataset-provenance','study-protocol','strategic-readiness','architecture-decision','reproduction','work-log'):
            content=(originals/(name+'.md')).read_text()
            for directory in ('development','ui-preview'):
                content=content.replace('../../artifacts/cycle10/'+directory+'/',
                    os.path.relpath(ROOT/'artifacts/cycle10'/directory,docs)+'/')
            content=content.replace('../../artifacts/cycle10/',os.path.relpath(out,docs)+'/')
            content=content.replace('../../src/',os.path.relpath(ROOT/'src',docs)+'/')
            content=content.replace('../../configs/',os.path.relpath(ROOT/'configs',docs)+'/')
            content=content.replace('../cycle9/',os.path.relpath(ROOT/'docs/cycle9',docs)+'/')
            (docs/(name+'.md')).write_text(content)
    get=lambda p:read_json(out/p)
    frozen=get('analysis/frozen-summary.json');temporal=get('analysis/temporal-summary.json')
    failures=get('analysis/frozen-failure-index.json');calibration=get('calibration/results.json')
    adaptation=get('adaptation/comparison.json');adapt_regression=get('adaptation/regression-summary.json')
    dependence=get('dependence/summary.json');predictions=get('dependence/predictions.json')
    history=get('temporal/summary.json');performance=get('performance/comparison.json');verification=get('verification.json')
    baseline=get('baseline/cohort-metrics.json');baseline_receipt=get('baseline/reproduction-receipt.json')
    data=get('datasets/dataset.json');secondary=get('analysis/secondary-modes.json');external=frozen['external-test']['complete'];with_history=temporal['external-test']['complete']
    def link(path,label=None):return f'[{label or path}]({os.path.relpath(out/path,docs)})'
    def write(name,lines):
        content='\n\n'.join(lines)+'\n'
        content=content.replace('../../artifacts/cycle10/',os.path.relpath(out,docs)+'/')
        content=content.replace('../../src/',os.path.relpath(ROOT/'src',docs)+'/')
        (docs/(name+'.md')).write_text(content)
    def metric_rows(summary):
        return [[key,pop,m['positions'],m['exact_positions'],pct(m['precision']),pct(m['recall']),pct(m['f1']),
            m['false_positive'],m['false_illegal'],m['self_check_false_legal'],m['unknown'],m['incomplete']]
            for key,value in summary.items() for pop in ('complete','in_board') for m in [value[pop]]]
    metrics_table=table(['Cohort','Population','Positions','Exact','Precision','Recall','F1','False legal','False illegal','Self-check false legal','Unknown','Incomplete'],metric_rows(frozen))
    write('external-generalization',[
        '# Independent external generalization',
        f'The frozen accepted C8 model achieved **{pct(external["recall"])} legal-move recall**, **{pct(external["precision"])} precision**, and **{external["exact_positions"]}/{external["positions"]} exact legal-move sets** on the final external test. It produced {external["false_positive"]} false-legal, {external["false_illegal"]} false-illegal, {external["self_check_false_legal"]} self-check false-legal, and {external["incomplete"]} incomplete classifications. These are new finite-sample measurements. '+link('analysis/frozen-summary.json'),
        'The model checkpoint, native runtime, native formulas and FEN-only inference policy were frozen at the starting commit. All registered operational positions were evaluated before any external adaptation or calibration refit. Secondary strict and experimental evaluations use the registered first ten final-test positions per collection. Their shard receipts retain every candidate, proof and budget outcome. '+link('frozen-complete.json')+'; '+link('evaluation/','evaluation shards')+'.',
        metrics_table,
        'The matched 30-position secondary panel contains '+str(secondary['source_games'])+' source games. Its strict, experimental and operational measurements are separately reported; it is not a second representative source sample. '+link('analysis/secondary-modes.json'),
        'Complete populations include the seeded off-board negative candidates. In-board populations remove that easy negative stratum; exact position sets are evaluated against the same full legal reference set. Unknown candidates are retained in the denominators and are not silently counted as correct negatives. '+link('analysis/frozen-summary.json'),
        'Game-cluster percentile bootstrap intervals are reported separately for every source and split (400 draws). Players, openings and engine opponents can remain correlated across games. Zero-error intervals do not establish universal zero risk. '+link('analysis/frozen-summary.json','metrics and intervals'),
        'Performance is stratified by phase, material count, opening family, tactical density, legal-move count, attacked pieces, multiple attackers and history completeness. These are descriptive associations, not independent causal effects. Per-piece and special-move candidate results are also retained. '+link('analysis/frozen-factors.json')+'; '+link('analysis/frozen-summary.json'),
        f'Supplying actual published game prefixes to the same frozen model yields {pct(with_history["recall"])} recall and {with_history["exact_positions"]}/{with_history["positions"]} exact sets, with {with_history["false_positive"]} false-legal and {with_history["false_illegal"]} false-illegal outcomes. This changes available evidence, not the learned checkpoint or threshold. '+link('analysis/temporal-summary.json'),
        '![External measurements](../../artifacts/cycle10/analysis/figures/external-generalization.png)',
        'The source population, license receipts, sampling restrictions and audits are described in [dataset provenance](dataset-provenance.md). No result establishes correctness outside the measured game, structural and historical distributions.'
    ])
    census=table(['Taxonomy category','Positions','Candidates','Errors','Abstentions','Representative proof indices'],
        [[name,v['positions'],v['candidates'],v['errors'],v['abstentions'],', '.join(map(str,v['representative_proof_indices'])) or 'none observed'] for name,v in failures['categories'].items()])
    write('generalization-failures',[
        '# Complete structural failure census',
        f'Every one of the **{failures["nonexact_positions"]} non-exact frozen positions** is accounted for. The index contains **{failures["unresolved_candidates"]} unresolved or erroneous candidates** across all registered frozen operational cohorts. No final-test position was removed after inference. '+link('analysis/frozen-verification.json')+'; '+link('analysis/frozen-failure-index.json'),
        census,
        'Categories can overlap. Pins, discovered attacks, double check and check-resolution labels describe the position context; membership alone does not establish the cause of the failed candidate. An absent learned local descriptor, unsupported history and an unavailable complete positive native composition are different limitations. Taxonomy assignments are structural triage, with causal claims restricted to the temporal evidence interventions. '+link('analysis/frozen-failure-proofs.json.xz','complete native traces and assessments'),
        'Each indexed proof record includes the original fixture and source game, candidate, native truth values, classification, local conditional values, hypothesis IDs, evidence IDs, dependence groups and the reconstructed native proof graph. The inspector loads records by bounded index and can reopen the candidate. '+link('analysis/frozen-failure-proofs.json.xz'),
        'Candidate-generator omissions are audited before inference against the offline reference library. Budget failures remain separate from missing knowledge and enter the failure census rather than being retried with a different decision criterion. '+link('datasets/manifest.json')+'; '+link('analysis/frozen-failure-index.json'),
        '![Failure categories](../../artifacts/cycle10/analysis/figures/failure-taxonomy.png)',
        'The same complete census is delivered for both experimental adaptations and the actual-history evaluation. '+link('analysis/small-failure-index.json')+'; '+link('analysis/large-failure-index.json')+'; '+link('analysis/temporal-failure-index.json')
    ])
    write('temporal-evidence',[
        '# Historical evidence transport and counterfactuals',
        f'The versioned transport replayed **{history["complete_game_replays"]} complete published game records** and produced **{history["demonstrations"]} inspectable demonstrations**. The native counterfactual error list is `{history["counterfactual_errors"]}`. Historical legality remains explicitly unverified by production replay. '+link('temporal/game-replay.json')+'; '+link('temporal/summary.json'),
        'The `temporal-transport-v10` receipt separates supplied events, trusted imported metadata, inferred structural relationships and unknown history. It records ObservedMove, PreviouslyMoved, LastMoveDoublePawnAdvance, RetainedCastlingRight, HistoricalEvidenceSource and HistoryConfidence as provenance relations. Their transport truth-value field is null: this module introduces neither a host probability formula nor a new native theorem. Existing native temporal inference receives the established history contract. [Implementation](../../src/pln_chess/cycle10/temporal.py).',
        'Event IDs bind source, sequence, predecessor, mover, before/after state and effects. They remain stable across model versions. The enclosing receipt binds model/runtime identity, initial trust and the complete supplied input; appending preserves prefix event IDs and records the parent receipt. A reported-state mismatch is a conflict, not a fabricated transition. Up to 4,096 events are retained; the legacy 512-event window explicitly reports omitted prefixes. '+link('temporal/external-replay-examples.json.xz'),
        'A standard-start PGN import explicitly attests its initial metadata. A partial SetUp game or plain FEN retains unknown prior history. A FEN en-passant flag never becomes an observed double step. Structural replay can represent an illegal proposed sequence and does not certify legal play or repetition termination. The offline PGN preparation command may validate the source with the reference library, within the preparation boundary. [Tests](../../tests/test_cycle10_temporal.py); [offline importer](../../training/cycle10_import.py).',
        'All 16 Cycle 9 adversarial and nine special-move abstentions were reproduced. Each involved castling or en-passant history, with original proof traces retained. Added attestations or reverse-constructed predecessors are labelled controlled interventions; no actual historical record was recovered for those synthetic fixtures. '+link('temporal/historical-abstentions.json.xz'),
        table(['Cohort','Investigated candidates','Resolved under supplied evidence'],[[name,v['cases'],v['resolved']] for name,v in history['by_cohort'].items()]),
        f'Across those interventions, {history["full_position_exact_after_intervention"]} complete position evaluations became exact; removing the temporal evidence channel caused {history["temporal_removal_abstentions"]} abstentions. Removing eligibility left {history["eligibility_removal_supported"]} supported-legal candidates. These are measured controls, not assumptions of success. '+link('temporal/summary.json'),
        'The demonstrations cover both castling sides, moved-and-returned kings and rooks, castling through attack and in check, fresh/stale/conflicting en-passant evidence, en-passant king exposure, and all four straight and capture promotion choices. Paired geometry is identical while evidence or eligibility differs. Each record includes the starting state, supplied events, final state, propositions, expected reference outcome, native result, lineage and relevant removal control. '+link('temporal/counterfactuals.json.xz'),
        'The original FEN-only Cycle 9 measurements remain 112/128 adversarial and 71/80 special exact sets. Conditional interventions do not retrospectively convert those original unknowns into known facts. Independent actual-history evidence is evaluated on all 1,020 final external positions. '+link('baseline/cohort-metrics.json')+'; '+link('analysis/temporal-summary.json'),
        'Replay overhead and fresh-versus-reused native cache proof equality after source, confidence and event changes are measured separately. '+link('performance/temporal.json')
    ])
    calibration_rows=[]
    for key,value in calibration['results'].items():
        for name,m in value['measurements'].items():calibration_rows.append([key,name,m['n'],num(m['brier']),num(m['ece']),num(m['log_loss'])])
    write('calibration-shift',[
        '# Calibration and evidence dependence under shift',
        'The unchanged Cycle 9 empirical map was evaluated on every frozen operational candidate before refitting. The external map then used only 144 positions from 24 calibration games; the 1,020-position final test never chose bins, hypotheses, inference thresholds or a promoted model. Calibration remains diagnostic. '+link('calibration/frozen-evaluation.json')+'; '+link('calibration/results.json'),
        table(['Population / cohort','Diagnostic','Candidates','Brier','ECE','Log loss'],calibration_rows),
        'Strength-bin reliability, confidence-bin legal frequencies, selective risk and coverage curves are included in the JSON. Native confidence is treated as a feature for association and abstention analysis, not automatically as an empirical probability. Overall Brier/coverage/recall uncertainty uses 400 game- or controlled-pair bootstrap draws; bin Wilson intervals are explicitly labelled naive because they ignore dependence. Log loss clips probabilities at 1e-12. '+link('calibration/results.json'),
        '![Calibration shift](../../artifacts/cycle10/analysis/figures/calibration-shift.png)',
        'The same analysis includes freshly reproduced original synthetic, adversarial and special-move cohorts and the external FEN-only history-sensitive candidates. The external mapping is displayed only for its frozen operational model, with a source-bound acceptance receipt and artifact hash; adapted, strict and incomplete outputs do not acquire an unsupported calibration claim. [Diagnostic interface](../../src/pln_chess/cycle10/diagnostics.py).',
        'Dependence experiments preserve native Truth_Revision. A source game contributes at most one observation per hypothesis; the main policy also groups common opening ancestry. Rank-reflected/color-swapped copies retain ancestor groups. Contradictions within a game exclude that group; declared synthetic independent contradictions revise both native channels. '+link('dependence/summary.json'),
        f'Duplicates preserve native values: **{dependence["duplicate_native_values_equal"]}**. Transformed ancestor copies preserve native values: **{dependence["transformed_ancestor_native_values_equal"]}**. Unsafe row counting changes values: **{dependence["unsafe_counting_changes_values"]}**. These are controlled experimental findings. The grouping policy assumes truthful provenance; unrelated game IDs cannot prove statistical independence. '+link('dependence/summary.json'),
        table(['Dependence variant','Observed records','Revised hypotheses','Excluded records','Native revision nodes'],[[name,v['report']['records'],v['report']['revised_hypotheses'],v['report']['excluded_records'],v['report']['native_revision_nodes']] for name,v in dependence['models'].items()]),
        table(['Prediction panel model','Recall','Coverage','False legal','False illegal','Checkpoint bytes'],[[name,pct(v['metrics']['recall']),pct(v['metrics']['coverage']),v['metrics']['false_positive'],v['metrics']['false_illegal'],v['checkpoint_bytes']] for name,v in predictions['models'].items()]),
        'The prediction panel is fixed at twelve held-out games, four per source, and is descriptive. Full final-test evaluation is reserved for the registered frozen/small/large comparison. Complete native values, confidence changes, model sizes, evidence lineage and proof artifacts remain available. '+link('dependence/predictions.json')
    ])
    perfrows=[]
    for record in performance['records']:
        for mode,value in record['modes'].items():
            perfrows.append([record['fixture'],mode,num(value['before']['latency_seconds']['p50']),num(value['after']['latency_seconds']['p50']),num(value['after']['latency_seconds']['p95']),num(value['after']['latency_seconds']['p99']),num(value['median_ratio']),str(value['ratio_interval95'])])
    write('performance',[
        '# Inference performance, memory and proof parity',
        'The original Cycle 9 source and the final Cycle 10 source were each benchmarked serially on six identical workloads, with nine reference/cold/warm repetitions per workload: **324 new comparison samples**. The separate historical baseline replay adds 126 samples. No other study native workers run during timed benchmark arms. '+link('performance/comparison.json')+'; '+link('baseline/performance/C9-reproduced.json'),
        table(['Workload','Mode','C9 p50 s','C10 p50 s','C10 p95 s','C10 p99 s','Median ratio','95% ratio interval'],perfrows),
        'Every reference, cold and warm run preserves the full candidate payload and native proof graph; all warm samples require zero native invocations. Measured timeout and truncation rates, grounded atoms, invocation counts, cache hits, checkpoint loading, checkpoint size, parent RSS and terminated-child RSS are retained per sample. Parent and child high-water marks are separate cumulative quantities, not a simultaneous combined memory peak. '+link('performance/C9-external.json')+'; '+link('performance/C10-current.json'),
        'Nine repetitions support descriptive median comparisons; p95/p99 are observed maxima and cannot establish reliable population tails. Ratio intervals use 2,000 bootstrap resamples within each serial source block. Host drift and block order remain potential confounders. A nonsignificant difference does not prove equal latency. '+link('performance/comparison.json'),
        '![Performance comparison](../../artifacts/cycle10/analysis/figures/performance.png)',
        'Native formulas, candidate grammar, observation construction, proof scheduling and learned model maps remain unchanged for the accepted model. Existing Cycle 9 caching is retained. Profiles investigate candidate generation, observation construction, indexing, proof reconstruction, cache keys and evidence lookup without introducing a speculative optimization. '+link('performance/C9-external-profile.txt')+'; '+link('performance/C10-current-profile.txt'),
        'Temporal receipt construction and verification are timed independently on real full games, empty history and a 520-event structural sequence. Source, confidence and event mutations are checked against fresh native sessions; every candidate and proof must match. '+link('performance/temporal.json')+'; '+link('performance/temporal-cache-proofs.json.xz')
    ])
    packages=[
        ('01','Baseline reproduction','Complete','baseline/reproduction-receipt.json'),
        ('02','External source acquisition','Complete; three collections, two publishers','sources/manifest.json'),
        ('03','Independent corpus and overlap','Complete','datasets/all-symmetry-audit.json'),
        ('04','Frozen external generalization','Complete; measured outcomes reported','analysis/frozen-summary.json'),
        ('05','Structural failure taxonomy','Complete census','analysis/frozen-failure-index.json'),
        ('06','Adversarial abstentions','Complete investigation; unresolved outcomes retained','temporal/historical-abstentions.json.xz'),
        ('07','Special moves','Complete investigation and controls','temporal/counterfactuals.json.xz'),
        ('08','Temporal transport','Implemented and tested','temporal/game-replay.json'),
        ('09','Temporal counterfactuals','Complete','temporal/summary.json'),
        ('10','Calibration shift','Complete; diagnostic only','calibration/results.json'),
        ('11','Evidence dependence','Complete controlled ablations','dependence/predictions.json'),
        ('12','Controlled adaptation','Complete; no promotion','adaptation/comparison.json'),
        ('13','Performance and memory','Complete measurements; tail limits explicit','performance/comparison.json'),
        ('14','Strategic readiness','Design only, as authorized','architecture/strategic-readiness.json'),
        ('15','Native boundary','Existing no-go retained','architecture/decision.json'),
        ('16','API, CLI and inspector','Implemented; desktop/mobile evidence','ui/verification.json'),
        ('17','Acceptance and regression','Mandatory gates passed','verification.json'),
        ('18','Consolidated delivery','Reports, artifacts, local commits','manifest.json')]
    package_table=table(['Package','Work','Status','Evidence'],[[f'C10-{n}',name,status,link(path)] for n,name,status,path in packages])
    write('package-matrix',['# Cycle 10 work-package completion',package_table,
        'Completion denotes delivered engineering and experiments. It does not assert that every research target was achieved. Original FEN-only uncertainty, measured external errors, adaptation regressions and timing uncertainty remain visible. [Engineering report](engineering-report.md).'])
    adaptation_table=table(['Model','Additional observations','Games','Recall','Exact sets','False legal','False illegal'],
        [[name,v['records'],v['games'],pct(v['metrics']['recall']),f"{v['metrics']['exact_positions']}/{v['metrics']['positions']}",v['metrics']['false_positive'],v['metrics']['false_illegal']] for name,v in adaptation['models'].items()])
    write('engineering-report',[
        '# Cycle 10 consolidated engineering report',
        f'Starting commit: `{verification["starting_head"]}`. Verified implementation commit: `{verification["source_head"]}`. Production source hash: `{verification["production_code_hash"]}`. Accepted model remains `{verification["model_version"]}`. All changes and commits are local; this cycle authorizes no push or deployment. '+link('verification.json'),
        package_table,
        'The original 365 tests, 26 established suites, 48 Cycle 9 shards and 287 negative controls were reproduced from unchanged original tracked source with exact native proof parity. The initial runtime symlink was reported as untracked; moving that same pinned link beneath an ignored directory restored a wholly clean checkout before frozen external inference. Original historical artifacts and configuration locks remain byte-identical. Fresh timing is reported as a new host measurement rather than claimed identical wall-clock reproduction. '+link('baseline/reproduction-receipt.json')+'; '+link('baseline/cohort-metrics.json')+'; '+link('baseline/proof-parity.json'),
        f'The independent corpus contains 1,308 external positions from 150 complete published records, with 1,020 final-test positions from 102 games, plus 112 separately labelled synthetic adversarial positions. Frozen final-test recall is {pct(external["recall"])} and exact sets are {external["exact_positions"]}/{external["positions"]}. Source and sampling limitations are explicit. [Provenance](dataset-provenance.md); [external results](external-generalization.md); [failure census](generalization-failures.md).',
        'The temporal mechanism transports supplied history without inventing unavailable predecessors or claiming complete legal-play verification. Its controlled interventions explain historical abstentions, and actual PGN prefixes test independent transfer. [Temporal evidence](temporal-evidence.md).',
        'Controlled adaptation used nested 6-game and 24-game subsets, with 16 unique relative observations per game selected before consulting labels. Learning uses native revision, exact relative descriptors and explicit source/game/opening lineage. Final-test games and opening families remain separate. No adapted model was promoted. '+link('adaptation/summary.json')+'; '+link('adaptation/comparison.json'),
        adaptation_table,
        f'Experimental historical regression comprises {adapt_regression["evaluations"]} evaluations. It records {adapt_regression["false_legal"]} false-legal, {adapt_regression["false_illegal"]} false-illegal and {adapt_regression["self_check_false_positives"]} self-check false-positive outcomes across those repeated suites. Counts include overlapping cohorts and must not be interpreted as independent error events. '+link('adaptation/regression-summary.json'),
        'Any changed final-test prediction occurs outside exact training FENs and source opening families. Local descriptors may recur by design. Paired game bootstrap intervals measure adaptation deltas; unchanged or worse results remain experimental findings. '+link('adaptation/comparison.json'),
        '![Sample efficiency](../../artifacts/cycle10/analysis/figures/sample-efficiency.png)',
        '[Calibration and dependence](calibration-shift.md) distinguish empirical frequencies from raw native truth values. [Performance](performance.md) reports reference/cold/warm parity, RSS and temporal overhead. [Strategic readiness](strategic-readiness.md) is a design proposal; no strategic selector, handcoded evaluation score, native conjunction extension or upstream modification is enabled.',
        f'The implementation passes {verification["test_count"]} automated tests, all 26 established suites, all 48 Cycle 9 comparison shards and 287/287 negative controls in a clean checkout using freshly bootstrapped dependencies. '+link('current/verified.json')+'; '+link('current/logs/tests.txt')+'; '+link(get('current/verified.json')['fresh_dependency_bootstrap_receipt'])+'; '+link('bootstrap/dataset-replay.json'),
        'The interfaces expose provenance, all evaluation arms, calibration shift, failure proofs, event replay, temporal controls, experimental comparisons and performance. The default checkpoint remains accepted C8; experimental checkpoints retain a strict default unless an explicit mode is selected. [CLI/API reproduction](reproduction.md); '+link('ui/verification.json','desktop/mobile checks')+'.',
        'Limitations: three collections from two publishing organizations; restricted archive prefixes; residual opening/player/engine correlation; sparse en-passant and promotion opportunities; externally supplied trust rather than verified original historical legality; partial positive native proofs; finite adaptation budgets; descriptive timing tails. Targets missed under FEN-only evidence are not repaired by relabelling unknown history.',
        'Recommended Cycle 11 priorities: expand licensed sources and rare history-sensitive strata; study evidence coverage for still-unseen relative descriptors; validate transfer and calibration on new locked source windows; investigate dependence beyond game IDs; design small supervised attack/defense-field experiments while retaining the composition no-go until a defensible native probabilistic contract is available.',
        '[Reproduction commands](reproduction.md) and the artifact manifest bind claims to source, input and measured output. Failed command logs and unsuccessful research outcomes remain part of the delivered evidence.'
    ])
    write('executive-summary',[
        '# Cycle 10 executive summary',
        f'The unchanged accepted C8 model was tested on 1,020 held-out positions from 102 published games across three collections. It achieved **{pct(external["recall"])} recall** and **{external["exact_positions"]}/{external["positions"]} exact legal-move sets**, with {external["false_positive"]} false-legal and {external["false_illegal"]} false-illegal classifications. These are finite external measurements. '+link('analysis/frozen-summary.json'),
        f'Supplying actual PGN event prefixes to the same model yielded **{pct(with_history["recall"])} recall** and **{with_history["exact_positions"]}/{with_history["positions"]} exact sets**. The transport preserves source, event identity, dependence, trust and model/runtime lineage. It does not invent history from FEN flags. '+link('analysis/temporal-summary.json'),
        f'All 25 original Cycle 9 adversarial/special abstentions were investigated, with {history["demonstrations"]} temporal and promotion demonstrations. Synthetic predecessor interventions are explicitly conditional evidence; the original FEN-only results remain unchanged. '+link('temporal/summary.json'),
        'The unchanged Cycle 9 calibration map was tested first; external recalibration used a disjoint 24-game validation set. Two nested experimental adaptations used native revision and dependence-aware evidence. Neither was promoted. Duplicate and transformed evidence controls test confidence inflation. '+link('calibration/results.json')+'; '+link('adaptation/comparison.json')+'; '+link('dependence/predictions.json'),
        f'The original baseline reproduced exactly. Final implementation gates include **{verification["test_count"]} tests**, **26 established suites**, **48 Cycle 9 shards**, **287 negative controls**, full native proof/cache parity, clean dependency bootstrap and exact dataset replay. Benchmarks compare six realistic workloads serially and disclose limited tail precision. '+link('verification.json')+'; '+link('performance/comparison.json'),
        'Strategic work remains architectural preparation. The existing native-composition no-go is retained; no chess selector, handcoded score, production oracle or new operator was introduced. Collection coverage, residual dependence, rare special moves and incomplete positive composition remain the main limits. Cycle 11 should prioritize new locked source windows, unresolved relative descriptors, and small evidence-grounded attack/defense experiments. [Full report](engineering-report.md); [18-package matrix](package-matrix.md).'
    ])
    artifact_manifest(out,docs)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--docs',default=str(ROOT/'docs/cycle10'))
    a=p.parse_args();run(a.out,a.docs)
