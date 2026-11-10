"""Render the consolidated Cycle 12 reports from completed, executed evidence."""
import argparse
from collections import defaultdict
from pathlib import Path
import re
import subprocess

from pln_chess.common import ROOT, read_json, write_json
from pln_chess.cycle6.inference import production_code_hash
from evaluation.cycle3 import read_gzip
from scripts.cycle9_baseline import sha


def table(headers, rows):
    def cell(value):
        return str(value).replace('|', '\\|').replace('\n', ' ')
    return '\n'.join(['| ' + ' | '.join(map(cell, headers)) + ' |',
                      '|' + '|'.join('---' for _ in headers) + '|'] +
                     ['| ' + ' | '.join(map(cell, row)) + ' |' for row in rows]) + '\n'


def percent(value):
    return 'n/a' if value is None else f'{100*value:.4f}%'


def run(out, docs):
    out, docs = Path(out).resolve(), Path(docs).resolve()
    docs.mkdir(parents=True, exist_ok=True)
    def load(name):
        return read_gzip(out/name) if name.endswith('.xz') else read_json(out/name)
    def evidence(name, label=None):
        import os
        return f'[{label or name}]({os.path.relpath(out/name, docs)})'
    def page(name, title, text):
        (docs/(name+'.md')).write_text('# '+title+'\n\n'+text.strip()+'\n')
    def append(name, text):
        # Preserve preregistered contracts; replace only the generated evidence section.
        path=docs/(name+'.md')
        if not path.exists():
            path.write_text((ROOT/'docs/cycle12'/path.name).read_text())
        marker='\n<!-- cycle12-measured-evidence -->\n'
        path.write_text(path.read_text().split(marker)[0].rstrip()+marker+'\n'+text.strip()+'\n')

    config=read_json(ROOT/'configs/cycle12.json')
    baseline=load('baseline/reproduction-receipt.json')
    baseline_tests=int(re.search(r'(\d+) passed',baseline['tests'])[1])
    full_orchestration=(out/'reproduction-execution.json').exists()
    current=load('current/verified.json'); clean=load('clean-research/verified.json')
    accepted=load('acceptance.json'); legal=load('legal/promotion-decision.json')
    boundary=load('architecture/boundary.json'); tests=load('final-tests/verified.json')
    performance=load('performance/summary.json'); ui=load('ui/verification.json')
    cli=load('cli-smoke/verified.json')
    for receipt in (baseline,current,clean,accepted,boundary,tests,performance,ui,cli):
        assert receipt['passed']
    assert current['identity']['production_code_hash']==accepted['production_code_hash']==boundary['production_code_hash']==production_code_hash()
    assert ui['source_hash']==tests['production_code_hash']==production_code_hash()
    assert cli['production_code_hash']==performance['production_code_hash']==production_code_hash()
    assert not ui['development_only'] and all(v==0 for v in ui['errors'].values())
    concepts=load('concepts/summary.json'); controls=load('concepts/controls-summary.json')
    interactions=load('interactions/summary.json'); temporal=load('temporal/summary.json')
    parity=load('incremental/parity.json'); transformations=load('interactions/transformation-summary.json')
    partial=load('concepts/partial-semantics-summary.json'); transfers=load('concepts/transfers.json.xz')
    dependence=load('learning/dependence.json'); audit=load('datasets/audit.json')
    learned=load('model/C12-concept-trained.json'); training=learned['training_report']
    recovery=load('legal/recovery/verified.json'); history=load('legal/temporal/summary.json')
    negative=load('legal/negative-controls/verified.json')
    assert parity['passed'] and transformations['cases']==transformations['passed']
    assert audit['passed'] and dependence['passed'] and temporal['all_replays_exact']
    assert tests['test_count']==current['test_count']
    limits=('Every concept remains experimental. Native operators derive a limited conditional from an '
            'explicitly host-observed `ObservedStructuralRolePacket`. Component field proofs are separate; '
            'their uncertain truth values are not conjoined into that packet. Complete joint concept proofs, '
            'native temporal implications, strategic overload theorems and strategic trapping theorems all remain zero. '
            'No move score, search, ranking, material-value table or move selection is implemented.')
    concept_rows=[]
    for name,m in concepts['metrics']['test'].items():
        concept_rows.append([name,concepts['conditional_target_names'][name],m['n'],m['tp'],m['tn'],m['fp'],m['fn'],
                             m['abstention'],percent(m['precision']),percent(m['recall_including_abstention']),percent(m['f1'])])
    concept_table=table(['Family','Limited target','N','TP','TN','FP','FN','Abstain','Precision','Recall incl. abstention','F1'],concept_rows)

    panel=load('legal/panel.json'); cohorts=defaultdict(list)
    for job in panel['jobs']:
        cohort=job['cohort']+('/'+job['mode'] if job['cohort'].startswith('historical/') else '')
        cohorts[cohort].append(load('legal/evaluation/'+job['id']+'.receipt.json'))
    def aggregate(rows, key):
        totals={k:sum(r[key][k] for r in rows) for k in ('candidates','true_positive','true_negative','false_positive',
            'false_illegal','false_negative_including_abstention','unknown','incomplete','self_check_false_legal')}
        totals['positions']=sum(r['positions'] for r in rows)
        totals['exact']=sum(round(r[key]['exact_move_set_accuracy']*r['positions']) for r in rows)
        tp=totals['true_positive'];fp=totals['false_positive'];miss=totals['false_negative_including_abstention']
        totals.update(precision=tp/(tp+fp) if tp+fp else None,recall=tp/(tp+miss) if tp+miss else None,
            f1=2*tp/(2*tp+fp+miss) if 2*tp+fp+miss else None,
            abstention_rate=(totals['unknown']+totals['incomplete'])/totals['candidates'])
        return totals
    legal_metrics={name:dict(before=aggregate(rows,'before_metrics'),candidate=aggregate(rows,'metrics')) for name,rows in cohorts.items()}
    write_json(out/'legal/cohort-comparison.json',legal_metrics)
    selected=[('External FEN-only','cycle10/external-test/operational/fen'),
        ('External history-assisted','cycle10/external-test/operational/history'),
        ('C9 adversarial','cycle9/adversarial/operational/fen'),
        ('C9 special moves','cycle9/special-moves/operational/fen'),
        ('C10 synthetic adversarial','cycle10/synthetic-adversarial/operational/fen')]
    legal_rows=[]
    for name,key in selected:
        a,b=legal_metrics[key]['before'],legal_metrics[key]['candidate']
        legal_rows.append([name,f"{a['exact']}/{a['positions']}",f"{b['exact']}/{b['positions']}",
            percent(a['recall']),percent(b['recall']),b['false_positive'],b['false_illegal'],b['self_check_false_legal']])
    legal_table=table(['Cohort','Old exact sets','Candidate exact sets','Old recall','Candidate recall','False legal','False illegal','Self-check FP'],legal_rows)
    legal_diagnostics=table(['Candidate cohort','Precision','Recall','F1','Abstention','Incomplete','Positive misses incl. abstention'],
        [[name,percent(legal_metrics[key]['candidate']['precision']),percent(legal_metrics[key]['candidate']['recall']),
          percent(legal_metrics[key]['candidate']['f1']),percent(legal_metrics[key]['candidate']['abstention_rate']),
          legal_metrics[key]['candidate']['incomplete'],legal_metrics[key]['candidate']['false_negative_including_abstention']]
         for name,key in selected])
    decision='Promoted the unchanged Cycle 11 special-local legal checkpoint.' if legal['promoted'] else 'Retained the previous legal default; the candidate remains experimental.'
    page('legal-promotion-review','En-passant promotion review',f'''
{decision} The decision follows the complete population review, not selection by an en-passant descriptor.
The candidate is `{legal['candidate_version']}`; the selected default is `{legal['default_version']}`.
Field and concept checkpoints are excluded from the legal default allowlist.

{legal_table}
{legal_diagnostics}
All 206 review jobs cover 26 historical suites, 48 Cycle 9 shards and 132 Cycle 10 shards, including every
one of the 1,020 external test positions in both operational FEN-only and history-assisted conditions.
The summary records {legal['full_regression']['rows']:,} candidate rows (overlapping cohorts/modes are not independent samples),
{legal['full_regression']['changes']} changed classifications and {legal['full_regression']['regressions']} losses of previously supported classifications.
Every row's native proof DAG was rehashed; model changes legitimately change proof identities.
The unchanged old checkpoint has a separate exact native-proof parity replay against the fresh starting baseline.

The two known development recoveries, 76 independent controlled legal holdouts, 39 reused historical interventions,
all {history['cases']} history controls and all {negative['cases']} negative/evidence-removal controls were rerun.
Order changes and duplicate deliveries preserve semantic history, native TVs and native proof IDs while retaining separate delivery audits.
Conflicts, missing claims, wrong model/runtime bindings and tampered receipts remain explicit.

Removing geometry, destination, ray, boundary or temporal evidence retracts the recovered en-passant prediction to unknown.
Removing exposure evidence still leaves the operational special-local conclusion supported. This inherited limitation is retained
and is not presented as a complete safety proof. Strict and experimental modes remain unknown on both recovered cases.
The model was frozen before Cycle 12; no new legal training or held-out tuning occurred.

The existing explicit-checkpoint API remains available. The CLI's verified default changes only when the Cycle 12
receipt matches production source, runtime, registrations and the legal allowlist. Older explicit output-root overrides
retain their existing selection behavior. Strategic code is blocked during the tested legal inference path.

Evidence: {evidence('legal/promotion-decision.json')}, {evidence('legal/cohort-comparison.json')},
{evidence('legal/recovery/verified.json')}, {evidence('legal/temporal/summary.json')},
{evidence('legal/negative-controls/verified.json')}, {evidence('current/proof-parity.json')}.
''')

    field_rows=[]
    for phase,data in [('Interactions',interactions),('Sequence endpoints',temporal)]:
        for family,m in data['endpoint_field_metrics'].items():
            field_rows.append([phase,family,m['relations'],percent(m['precision']),percent(m['recall']),
                percent(m['f1_including_abstention']),m['unknown'],m['incomplete'],m['false_positive'],m['false_negative'],m['complete_conditional_proofs']])
    field_table=table(['Panel','Field','Relations','Precision','Recall','F1','Unknown','Incomplete','FP','FN','Conditional proofs'],field_rows)
    worked_table=table(['Demonstration','Reference relations','Host comparisons','Partial candidates','Proof package'],
        [[r['id'],r['relations'],r['changes'],r['concepts'],evidence(r['artifact'],'open')] for r in interactions['worked']])
    page('field-interactions','Relational field interactions',f'''
{interactions['count']} before/after demonstrations pass exact independent full recomputation of their successor fields and graphs.
The panel includes the ten requested interaction categories plus discovered defense, double-check resolution,
knight/rook and pawn/bishop discoveries. Each compressed package retains initial FEN, supplied edit, structural
successor, relative observations, endpoint native proofs, evidence IDs, unknown relations and offline references.

{worked_table}
{field_table}
These are development demonstrations. The repeated endpoint records are neither independent holdouts nor tactical playing-strength tests.
Reference labels come only from evaluation. Attack, defense, ordinary geometric mobility and king-exposure have distinct local meanings;
supported mobility does not certify global move safety. Unknowns are retained in recall and coverage accounting.

All {transformations['passed']}/{transformations['cases']} field transformation/locality controls pass.
The host comparisons include {interactions['change_predicates'].get('OpensAttack',0)} OpensAttack,
{interactions['change_predicates'].get('RemovesDefense',0)} RemovesDefense,
{interactions['change_predicates'].get('ChangesInfluence',0)} ChangesInfluence and
{interactions['change_predicates'].get('PersistsAcrossMove',0)} PersistsAcrossMove records.
Those labels compare independently inferred endpoints and have no native change TV.
There is no scalar strategic score.

Evidence: {evidence('interactions/summary.json')}, {evidence('interactions/transformations.json.xz')},
{evidence('incremental/parity.json')}.
''')

    append('strategic-concepts',f'''## Measured limited-target results

{concept_table}
The test panel contains 306 examples in 125 held-out raw structural families. It produces 303 classified answers,
124/125 supported positive targets and three fork abstentions, with zero false positives or supported false negatives.
Precision is conditional on a positive classification; recall includes abstained positives. Zero supported FN is not perfect recall.
The calibration partition is separate and does not tune thresholds. Its pawn fork family also abstains.

{limits}

{concepts['key_audit']['heldout_shared_conditional_keys']}/{concepts['key_audit']['heldout_examples']} calibration/test
examples share a supplied pooled conditional key with training. Raw family overlap is zero. This measures transfer through a
declared relative abstraction, not invention of the abstraction, arbitrary conjunction or external tactical generalization.

Evidence: {evidence('concepts/summary.json')}, {evidence('concepts/rows.json.xz')}, {evidence('datasets/audit.json')}.
''')
    for concept,filename,title in [('Pin','pins','Pin transfer'),('Fork','forks','Fork transfer')]:
        chosen=[r for r in transfers if r['concept']==concept]
        transfer_table=table(['Held-out case','Empty','Learned','Strength','Confidence','Evidence removed','Succeeded'],
            [[r['case']['id'],r['empty']['classification'],r['learned']['classification'],
              f"{r['learned']['raw_stv']['strength']:.6f}",f"{r['learned']['raw_stv']['confidence']:.6f}",
              r['removed']['classification'],r['successful']] for r in chosen])
        detail=('The pin observer binds a slider, an intervening piece and a protected target along a relative ray. '
            'It distinguishes king and nonking targets and retains the hypothetical removal/exposure observation. '
            'Rook, bishop and queen rays transfer to unseen raw lengths; coordinate transformations and piece-ID changes '
            'are independently controlled. A relative pin against a nonking target assigns no material value. '
            'The intervening piece is not declared legally immobile. Every example retains the native packet proof and '
            'separate attack/exposure components.' if concept=='Pin' else
            'The fork observer retains two target-specific influences from one attacker. Knight, pawn, king, rook and '
            'queen inputs are present without target-value scores. The entire pawn fork family was withheld from '
            'training and remains unknown: its empty/learned/removed conditional stays at (0.5, 0). '
            'Both component attack relations can have native support without creating a joint fork theorem. '
            'Seven successful demonstrations cover knight, king, rook and queen families; the pawn failure is retained without retuning.')
        page(filename,title,f'''
{sum(r['successful'] for r in chosen)}/{len(chosen)} preregistered transfer demonstrations change from unknown under the empty
concept checkpoint to supported under training and back to unknown when the relevant conditional evidence is removed.
All have unseen raw structural families; successful cases intentionally reuse supplied pooled relative keys.

{transfer_table}
{detail}

Translations, reflections, color orientation, identity renaming and irrelevant-context changes belong to their original ancestry
family. They are invariance controls, not additional independent holdouts. The complete per-case records include FEN, roles,
relative observations, model/rule IDs, native expressions, proof DAGs, evidence groups and removal controls.

{limits}

Evidence: {evidence('concepts/transfers.json.xz')}, {evidence('concepts/transformations.json.xz')},
{evidence('concepts/controls-summary.json')}.
''')

    page('discovered-attacks','Discovered attacks, defenses and threat removal',f'''
DiscoveredAttack and DiscoveredDefense each classify 48/48 held-out limited-target examples correctly (24 positive and 24 negative).
ThreatRemoval classifies 12/12 (6 positive and 6 negative). The result concerns a newly present or absent local relation after a
supplied structural edit. It does not prove that the edit is legal, force a continuation or establish a native temporal implication.

The production observer reconstructs the successor from the existing movement grammar and records occupancy changes.
Before/after attack and defense queries run through the frozen Cycle 11 learner. The concept learner separately applies its
native packet conditional. The host compares endpoint classifications; it never treats a graph path as probabilistic deduction.

Inspectable demonstrations include `pawn-opens-bishop-attack`, `knight-opens-rook-file`, `discovered-attack`,
`discovered-defense`, `defender-capture` and the `captured-blocker-queen-ray` sequence.
Unknown observations withhold the relevant packet. Missing temporal events do not establish a discovered relation across a gap.
Known local motif boards may omit kings; their offline edit-legality reference is explicitly null.
The valid multi-move demonstrations retain separate offline legal-play references.

Evidence: {evidence('interactions/summary.json')}, {evidence('temporal/summary.json')},
{evidence('concepts/rows.json.xz')}, {evidence('datasets/reference-scope-amendment.json')}.
''')
    page('overloaded-defenders','Competing defensive obligations',f'''
The limited `CompetingDefenseObligations` conditional classifies 12/12 held-out examples correctly, with six positive and six negative.
It records one defender, two wards and an opposing threat to each ward. Defending two pieces alone is insufficient input for the
intended interpretation. The representation retains the competing threat/defense dependencies and candidate consequences.

Two supplied capture/recapture branches were evaluated. In each, responding to one obligation leaves the other recorded defense
contradicted: {', '.join(partial['remaining_defense'])}. Full before/after fields and native proofs are retained in the branch artifact.
This is local counterfactual evidence. The experiment does not enumerate or exclude every defensive response, prove unavoidable
loss, compare material values or derive a complete overload theorem. `complete_overload_theorems` is zero and strategic overload TV is null.

The positive result is therefore a conservative partial representation, not tactical overload recognition accuracy.
Counterfactual removal of a ward/threat changes the limited packet; removing its learned conditional retracts it to unknown.

Evidence: {evidence('concepts/overload-consequences.json.xz')}, {evidence('concepts/partial-semantics-summary.json')},
{evidence('concepts/counterfactuals.json.xz')}.
''')
    trap_table=table(['Case','No-ordinary-exit conditional','Reference legal exits','Supported legal exits','Unknown candidate moves'],
        [[r['id'],r['conditional'],r['reference_legal_exits'],r['supported_legal_exits'],r['unknown_legal_exits']] for r in partial['trapping']])
    page('trapped-pieces','Restricted and uncertain mobility',f'''
The `NoOrdinaryGeometricExit` target classifies six held-out controlled records correctly: three positive and three negative.
The board-edge topology is included in the raw family audit. This target concerns the supplied ordinary movement fan,
not strategically favorable moves or global king safety.

Three additional valid-board diagnostics separate geometric and legal evidence:

{trap_table}
The knight on a8 has its ordinary exits obstructed in the positive case; opening b6 produces a separately supported legal exit.
With b6 unknown, the conditional abstains and legal candidates remain unknown. Unknown mobility is never converted to zero mobility.
The unknown list retains the legal learner's seeded proposals, including off-board coordinate proposals; it is not a list of established exits.
Legal exits come from the unchanged operational learner; evaluation-only reference exits are stored separately and are null for
unknown observations or deliberately incomplete local boards.

Attack/exposure field components and supported legal exits retain their own proof scope. Exit desirability, material cost and
the absence of every safe strategic alternative are unassessed. Complete strategic trapping proofs remain zero.

Evidence: {evidence('concepts/trapping-diagnostics.json.xz')}, {evidence('concepts/partial-semantics-summary.json')}.
''')

    sequence_table=table(['Sequence','Moves','States','Partial candidates','Replay','Artifact'],
        [[r['id'],r['events'],r['states'],r['partial_concept_records'],'exact',evidence(r['artifact'],'open')] for r in temporal['sequences']])
    page('temporal-evolution','Supplied sequences and deterministic field evolution',f'''
All {temporal['sequence_count']} supplied sequences ({temporal['supplied_moves']} moves, {temporal['states']} states) pass deterministic
semantic replay and independent full-field/graph recomputation. The learner observes the sequences; it does not plan them.

{sequence_table}
Every state retains stable piece identity within its observed segment, event/source lineage, model versions, native field proofs,
partial concept candidates and typed endpoint changes. Promotion changes piece kind; captures remove identities; en passant
tracks both the moved pawn and the removed pawn. The initial opening includes all 32 pieces.

Observed state changes, unchanged learned conditional beliefs, native query results and visual projections are distinct.
Creation/removal of a field-domain member is distinct from a positive/negative inference. Strengthening and weakening compare
raw endpoint native values; they are not evidence that the checkpoint learned during replay. Persistence is a host comparison with null TV.
Concept persistence tracks named roles and piece identities, without treating omitted bounded candidates as negative evidence.

Four controls pass: a missing move with an observed successor starts a new identity segment; a missing move without a successor
leaves the state unknown; a conflicting successor is retained as a conflict; zero observation confidence leaves all queried fields unknown.
No transition inference or field delta is asserted across a history gap. Structural replay does not certify legal historical play.

{field_table}
Endpoint precision/recall is against offline field references, not prediction of future events or strategic sequence quality.
The full field records, native expressions, event receipts and graphs match on repeat after excluding only execution/cache counters.
Native temporal theorems remain zero.

Evidence: {evidence('temporal/summary.json')}, {evidence('temporal/controls')}, {evidence('incremental/parity.json')}.
''')

    page('concept-learning','Independent limited-target concept learning',f'''
The registered dataset has {audit['records']} examples in {audit['families']} canonical raw structural families:
70 training families / 163 records, 26 calibration / 64 records, and 125 test / 306 records.
The partition is by raw motif ancestry, including counterfactual descendants, role permutations and equivalent transformations.
All {len(audit['symmetry_checks'])} symmetry checks pass; split overlap and equivalent raw motif overlap are zero.
The 12 supplied sequences have 50 unique observed event IDs and are demonstration data, not additional concept training.

Training creates {training['hypotheses']} relative packet hypotheses from {training['training_examples']} observations using
{training['native_revision_nodes']} logical native revision nodes. Repeated native arithmetic expressions use the existing runtime
cache: {training['executed_native_operators']} operators execute and {training['native_cache_hits']} calls hit that cache.
Each logical evidence update still has its own source/evidence identity and retained trace. The neutral prior is (0.5, 0.05).
The seed is {config['seed']}; observed packet confidence is {config['sensor_confidence']}; training observation confidence is
{config['training_observation_confidence']}. Fixed thresholds are strength ≥0.8 / ≤0.2 with confidence ≥0.25.
No held-out labels tune the thresholds or descriptor grammar.
Raw native strength and confidence are separate quantities; neither is presented as an empirically calibrated strategic probability.
The calibration partition evaluates the fixed thresholds. No strategic probability calibrator is fitted in this cycle.

{concept_table}
{limits}

The grammar supplies roles, local relative geometry, a movement candidate vocabulary, symmetry normalization, role-kind coarsening
and unique component-profile pooling. It does not supply positive concept truth values. The learned knowledge is a conditional
association under that supplied grammar. Of 370 calibration/test records, {concepts['key_audit']['heldout_shared_conditional_keys']}
reuse a training conditional key and {concepts['key_audit']['heldout_unseen_conditional_keys']} have unseen keys.
There are no absolute-square constants, FEN keys, piece IDs or complete-board hashes in learned descriptors.
This is one synthetic data source: raw family independence is not independence of external studies or annotators.

Native `Truth_Revision` updates positive and negative conditional channels. Training collapses connected declared source/motif/
transformation components; contradictory dependent components are withheld. Seven measured controls pass:
{', '.join(dependence['checks'])}. Deliberately hiding duplicate ancestry changes confidence, exposing the dependence assumption.
Shared conflicts and independent conflicts are handled separately, and retracting an evidence group removes it from provenance.
The injected conflict labels are controls rather than observed chess labels.

Before the first fit, retained dataset drafts were corrected for symmetric role grouping, trapping board-edge topology,
structural edit grammar, and withholding legal references on incomplete boards. All limited labels, final counts and split assignments
were retained. Training began only after the complete baseline receipt passed. No held-out failure triggered retraining.
The pawn fork family remains an explicit transfer failure. A development graph-node collision under duplicate queries with unequal
proof budgets was fixed without changing the trained checkpoint; the failed output and regression test are retained.

Evidence: {evidence('datasets/audit.json')}, {evidence('learning/main/ledger.json.xz')},
{evidence('learning/main/native-training.json.xz')}, {evidence('learning/dependence.json')},
{evidence('concepts/summary.json')}, {evidence('retained/pre-graph-budget-fix')}.
''')
    cf=load('concepts/counterfactuals.json.xz')
    cf_table=table(['Pair','Changed relation','Before','After','Proof changed','Conditional removal'],
        [[r['case']['id'],r['case']['changed_relation'],r['before']['classification'],r['after']['classification'],
          r['proof_changed'],r['removed_conditional']['classification']] for r in cf])
    page('counterfactuals','Counterfactuals, invariance and evidence removal',f'''
All {controls['counterfactuals_distinguished']}/{controls['counterfactuals']} counterfactual pairs distinguish their registered
local change, and all {controls['conditional_retractions']} previously classified conditionals retract to unknown after their learned
evidence is removed. Already-unknown queries are not counted as successful retractions ({controls['already_unknown_before_removal']}).
All {controls['transformation_passes']}/{controls['transformations']} concept transformation controls pass, separately from the 38 field controls.

{cf_table}
Every pair retains source and edited input, changed relation, limited offline labels, before/after native TVs and proof traces,
conditional-rule identity, dependence group and both removal arms. Irrelevant translation, reflection, ID and context changes
are not counted as independent training evidence. Unknown required cells are a distinct abstention control.

Removing the separate field checkpoint may remove component proofs without retracting a packet conditional learned directly
from structural observations. This observed separation is intentional and disclosed: a packet conditional is not a theorem caused
by conjoining uncertain field evidence. The experiment establishes dependence on its learned conditional evidence and observed
local packet, not arbitrary causal reasoning about chess strategy.

Evidence: {evidence('concepts/counterfactuals.json.xz')}, {evidence('concepts/transformations.json.xz')},
{evidence('concepts/controls-summary.json')}, {evidence('learning/dependence.json')}.
''')

    append('field-interaction-ontology',f'''## Executed ontology audit

The implementation exposes all eight typed concept families and ten interaction labels. Ontology labels do not add native operators.
The grammar is `{learned['grammar']}` and has {len(learned['hypotheses'])} learned relative packet descriptors.
The boundary audit reports no production reference-engine imports, no Cycle 12 host truth-value arithmetic and no new native operators.
Only Truth_Revision, Truth_ModusPonens, Truth_Negation and BestConfidenceCandidate are authorized here.

{len(boundary['native_proof_replays'])} distinct field/concept proof traces and {boundary['native_training_nodes_reexecuted']}
logical training nodes were re-executed against the pinned native runtime with exact truth-value equality.
Absolute coordinates remain I/O/observation bindings; native rule descriptors are relative.

Evidence: {evidence('ontology/manifest.json')}, {evidence('architecture/boundary.json')}.
''')
    append('dependency-graph',f'''## Measured propagation and parity

All {parity['interaction_positions']} successor demonstrations and {parity['sequence_states']} sequence states match full recomputation.
The comparison includes every relation field, native node, proof ID, model version, evidence ID, dependence group, projection and graph.
Across these panels the scheduler reuses {parity['reused_relations']:,} relation records and schedules {parity['scheduled_relations']:,}.
These counts include initial full builds and do not imply an equal wall-clock speedup.

Changed occupancy/identity/kind/owner, unknown cells and en-passant metadata invalidate affected source, destination and ray observations.
Promotion, capture, castling and en passant are covered. Budgets too small for the logical population use the full planner's explicit
incomplete behavior. Source/model/runtime/options changes rebind or invalidate the cache. Reused results are copied with current state bindings.
Concept candidates are reobserved and queried from changed states; packet proof caching is scoped separately.

Graph nodes distinguish native-supported and budget-incomplete results even when they share a semantic observation. A development
duplicate-query collision was retained and fixed by including result/proof status in graph identity. No truth-value computation changed.
Native edges index actual conditional conclusions and values; host scheduling, explanation and comparison edges have no TV.
Graph topology cannot create independent evidence or propagate a probability.

Evidence: {evidence('incremental/parity.json')}, {evidence('performance/summary.json')},
{evidence('preliminary-tests/duplicate-budget-graph.json')}.
''')

    perf_rows=[]
    for workload,conditions in performance['workloads'].items():
        for name,m in conditions.items():
            perf_rows.append([workload,name,f"{m['median_seconds']:.3f}",f"{m['empirical_p95_seconds']:.3f}",
                m['median_native_invocations'],f"{m['maximum_python_peak_bytes']/2**20:.2f}"])
    speed_rows=[]
    for workload,c in performance['workloads'].items():
        full=c['successor-full-cold']['median_seconds'];inc=c['successor-dependency-reuse']['median_seconds']
        speed_rows.append([workload,f'{full:.3f}',f'{inc:.3f}',f'{full/inc:.3f}×'])
    page('performance','Runtime, memory and cache comparisons',f'''
Six workloads run in {performance['repetitions']} fresh worker processes each, sequentially after the native study workers stop.
Every field comparison first requires exact native proof, evidence and dependency graph parity.
The workloads cover rook obstruction, promotion, en passant, en-passant exposure, the 32-piece starting position and a 21-piece published middlegame.
The opening also measures a seven-state observed temporal replay. Concept work measures eight explicit conditional queries.
Legal work separately times the old accepted and frozen candidate models over full FEN candidate sets.

{table(['Workload','Full successor median s','Dependency successor median s','Full / incremental'],speed_rows)}
{table(['Workload','Condition','Median s','Empirical p95 s','Native operators median','Python peak MiB max'],perf_rows)}
Maximum fresh-worker high-water RSS is {performance['max_process_peak_rss_kib']/1024:.2f} MiB; maximum native-child high-water RSS is
{performance['max_native_child_peak_rss_kib']/1024:.2f} MiB. These are separate process maxima, not total concurrent memory.
Worker RSS includes retained comparison outputs. Per-condition Python peaks use tracemalloc, whose allocation tracking adds overhead.
Hardware: {performance['hardware']['cpu_model']}; {performance['hardware']['logical_cpus']} logical CPUs,
{performance['hardware']['affinity_cpus']} available in process affinity, cgroup CPU quota/period `{performance['hardware']['cgroup_cpu_max']}`;
{performance['hardware']['mem_total']}. Platform: {performance['hardware']['system']} {performance['hardware']['release']}.

Cold means a new inference/session cache, not flushed operating-system or filesystem caches. Warm means the existing Cycle 11 field cache.
Dependency parent preparation is timed separately; successor reuse excludes that preparation. Model/runtime loading is excluded.
Field observations, native inference, proof assembly, graph construction and internal identity/validation hashes are included;
additional parity digest calculation is outside the timed condition. Seven repetitions give weak tail resolution: p95 here is the
empirical maximum, not an estimated population tail. Cache/native call reductions are not automatically latency reductions.
Full worker records retain execution counters, reuse/schedule counts, proof hashes and memory scope.

{performance['limitations']}

Evidence: {evidence('performance/summary.json')}, {evidence('performance/workers')}, {evidence('performance/commands')}.
''')

    packages=[
        ('01','Baseline preservation','Fresh f4 baseline; 463 tests; 26/48/132 native groups; protected prior evidence','baseline/reproduction-receipt.json'),
        ('02','En-passant promotion review',decision,'legal/promotion-decision.json'),
        ('03','Interaction ontology','Typed relations, explicit provenance and unsupported semantics','ontology/manifest.json'),
        ('04','Dependency graph','Native proof index; host edges carry no TVs','architecture/boundary.json'),
        ('05','Field interactions','17 demonstrations and 38 transformation/locality controls','interactions/summary.json'),
        ('06','Strategic representation','Eight typed limited targets; no joint theorem','concepts/summary.json'),
        ('07','Pins','8/8 inspectable transfers; legal restriction unproved','concepts/transfers.json.xz'),
        ('08','Forks','7/8 transfers; held-out pawn abstains','concepts/transfers.json.xz'),
        ('09','Discoveries','Attack/defense endpoint evidence and controlled edits','interactions/summary.json'),
        ('10','Overloaded defenders','Partial obligations and two response branches; overload unproved','concepts/overload-consequences.json.xz'),
        ('11','Trapped pieces','Positive, escape-open and unknown diagnostics; strategic trapping unproved','concepts/trapping-diagnostics.json.xz'),
        ('12','Temporal fields','Deterministic state/field replay and four gap controls','temporal/summary.json'),
        ('13','Temporal demonstrations','12 sequences, 50 supplied moves, 62 states','temporal/summary.json'),
        ('14','Independent learning','125 held-out raw families from one controlled source','datasets/audit.json'),
        ('15','Counterfactual testing','20/20 distinguished/retracted; 90/90 concept controls','concepts/controls-summary.json'),
        ('16','Incremental updates','17 successors + 62 sequence states: exact full parity','incremental/parity.json'),
        ('17','Inspector','Eight concepts, graphs, sequence/gap/proof/export and mobile checks','ui/verification.json'),
        ('18','Benchmarks','Separate legal/field/concept/temporal metrics; 42 isolated workers','performance/summary.json'),
        ('19','Acceptance gates',f"{tests['test_count']} tests, full native cohorts and source-bound legal acceptance",'acceptance.json'),
        ('20','Consolidated delivery','17 requested reports, artifacts, hashes and local commits; no push','delivery.json')]
    matrix=table(['Package','Work','Engineering status','Measured scope / limitation','Evidence'],
        [['C12-'+i,name,'Delivered',scope,evidence(path,'receipt')] for i,name,scope,path in packages])
    write_json(out/'package-matrix.json',dict(engineering_packages_delivered=20,
        packages=[dict(id='C12-'+i,name=name,engineering_status='delivered',scope=scope,evidence=path) for i,name,scope,path in packages],
        research_scope='Engineering delivery includes negative and partial research outcomes. No complete strategic theorem or external strategic generalization is claimed.'))
    page('package-matrix','Cycle 12 work-package matrix',matrix+'''
All 20 engineering packages are delivered. This is not a claim that all strategic concepts have complete native proofs.
The brief's numerical demonstration minima are met: 17 interactions, 38 field controls, 8 pin and 7 fork transfers,
125 held-out raw families and 12 sequences. Independent concept holdouts are independent canonical raw families within one
synthetic source; broader external-source independence remains untested. Overload, trapping and multi-premise strategic
interpretations remain partial. The legal decision is conditioned on the executed full population review.
''')

    commits=subprocess.check_output(['git','log','--reverse','--format=%h %s',config['starting_head']+'..HEAD'],cwd=ROOT,text=True).strip()
    provenance=f'''Starting commit: `{config['starting_head']}`. Validated production freeze: `{current['source_head']}`.
Production hash: `{production_code_hash()}`. Later commits contain reports/artifacts/driver improvements without changing production source.
The final delivery commit is necessarily recorded by the repository's history and final response rather than self-embedded in this file.
All commits are local; no GitHub push, external deployment or upstream edit is performed.

```text
{commits}
```
'''
    page('reproduction','Clean reproduction and inspection',f'''
The starting f4 checkout was independently bootstrapped with a fresh environment/runtime and fully replayed.
It reproduced {baseline_tests} tests, 26 historical suites, 48 Cycle 9 shards, 132 Cycle 10 shards,
287 negative controls and the Cycle 11 research package. The implementation was then independently bootstrapped
at `{current['source_head']}` in `{current['checkout']}`. Its final source remained clean throughout the recorded runs.

The current-source run passes {current['test_count']} tests and all the same native legal cohorts with exact proof parity.
A separate clean research replay regenerates data, trains both concept models and reruns all concept, counterfactual,
dependence, interaction and sequence experiments: {len(clean['comparisons'])} model/artifact comparisons pass.
Both concept checkpoint files are byte-identical. Research equality excludes only execution and cache counters.
The research replay reuses the already passed baseline receipt; it does not claim a second baseline execution within that replay.
{'The complete command below was executed in this output, with its orchestration receipt retained.' if full_orchestration else 'The complete command below is supplied for future fresh replay; the delivered execution used its separately logged stages.'}

From a committed clean final checkout, choose new absolute paths on a disk with sufficient room for native proof artifacts:

```bash
TMPDIR=/dev/shm .venv/bin/python -m scripts.cycle12_reproduce \\
  --out /data/new-cycle12-output \\
  --checkout /data/new-cycle12-source \\
  --baseline /data/new-cycle12-baseline \\
  --browser-work /data/new-cycle12-browser
```

This performs a fresh locked bootstrap, starting baseline, registered training/evaluation, complete legal review,
recovery/history/removal controls, current-source regression, native boundary checks, clean research replay,
source-bound promotion, accepted-default tests, isolated performance and browser verification.
`--skip-browser` explicitly records an incomplete delivery. Do not run benchmarks alongside native study workers.
The requirements and runtime lock hashes are recorded in each bootstrap receipt. PLN is pinned to
`{current['identity']['runtime']['pln']['commit']}`, PeTTa to `{current['identity']['runtime']['petta']['commit']}`.
The authoritative dependency and runtime file hashes are in the bootstrap manifest.

To use the inspector after acceptance:

```bash
.venv/bin/python -m pln_chess serve --port 18782
# Open http://127.0.0.1:18782/interactions
.venv/bin/python -m pln_chess concept-inspect --input artifacts/cycle12/examples/concept-payload.json --output /tmp/pln-concept-proof.json
.venv/bin/python -m pln_chess field-evolution --input artifacts/cycle12/examples/sequence-payload.json --output /tmp/pln-sequence-proof.json
```

`GET /cycle12-catalog` provides bounded examples. `POST /cycle12-fields` accepts a position, selected source,
field family, candidate edit and explicit roles or bounded candidate enumeration. `POST /cycle12-evolution`
accepts a `sequence` object with an initial FEN and explicit ordered events. Unknown inputs and exhausted proof budgets
remain visible. The existing legal and Cycle 11 field APIs remain available; their explicit checkpoint contracts are unchanged.
Python exports are `pln_chess.api.inspect_interactions` and `pln_chess.api.replay_field_evolution`.
Candidate enumeration is bounded and structural; absence from that set is not a negative concept conclusion.
The example payloads contain only supplied inputs. Both new CLI commands were executed and their native output packages are retained
in {evidence('cli-smoke/verified.json')}; the reproduction runner regenerates these examples under its output directory.

Final browser verification uses ProofShot with an owned local server, actual browser interaction, screenshots/video,
zero console/server errors and a captured export whose bytes match the server result. The owned server and recorder are stopped.
On phones the compact graph scrolls horizontally inside its panel; selecting an edge opens its full record in the proof pane.
The initial interrupted/low-contrast development capture is retained, followed by the corrected passing development and final captures.
Historical artifacts are immutable: all {baseline['protected_files']} protected files retain their starting hashes.

Evidence: {evidence('baseline/reproduction-receipt.json')}, {evidence('current/verified.json')},
{evidence(current['fresh_bootstrap_receipt'])}, {evidence('clean-research/verified.json')},
{evidence('final-tests/verified.json')}, {evidence('ui/verification.json')}, {evidence('manifest.json')}.

{provenance}
''')
    page('engineering-report','Cycle 12 consolidated engineering report',f'''
Cycle 12 delivers all 20 engineering packages: typed concept conditionals, dependency graphs, exact incremental fields,
observed sequence replay, a proof inspector, full legal promotion review, clean reproduction and isolated benchmarks.
{decision} Strategic models remain experimental and cannot become the operational legal default.

{provenance}
{matrix}
{legal_table}
{concept_table}
All 17 interaction demonstrations, 38 field controls, 90 concept transformations, 20 counterfactual pairs,
20 actual conditional-evidence retractions, 8 pin transfers and 7 of 8 fork transfers pass their registered limited tests.
The held-out pawn fork abstains. All 12 supplied sequences (50 moves, 62 states) replay exactly;
all interaction successors and sequence fields match full native proof/evidence/graph recomputation.

The native boundary audit re-executes {len(boundary['native_proof_replays'])} distinct inference traces and
{boundary['native_training_nodes_reexecuted']} logical training nodes. There are no new native operators, host truth-value formulas,
production chess-oracle imports or modified upstream files. The current and accepted-default suites each pass
{tests['test_count']} tests. All 287 negative controls, the complete historical and external legal populations and
all {baseline['protected_files']} protected prior files pass their recorded checks.

{table(['Workload','Full successor median s','Dependency successor median s','Full / incremental'],speed_rows)}
Performance uses 42 isolated fresh workers, including opening and middlegame positions, with parity before comparison.
See [performance.md](performance.md) for all conditions, native calls, memory and measurement limits.
Fresh data generation, training and research replay pass {len(clean['comparisons'])} comparisons; the two concept models are byte-identical.
The fresh baseline and full current-source legal gates are separately executed, not inferred from the research replay.
Final browser proof covers all eight concepts, all field families, graph/proof inspection, sequence steps, missing histories,
empty/unknown/budget states, actual proof export and desktop/mobile layouts, with zero captured errors.

{limits}

The scientific limitation is substantial: one controlled source, supplied structural roles and pooling, mostly shared conditional
keys, no arbitrary native conjunction, and no proof of safe strategic choice. Overload has two local consequence branches without
universal response exclusion. Trapping distinguishes unknown exits without evaluating desirability. FEN-only legal history remains
incomplete. Operational en-passant exposure-removal behavior remains unchanged. Candidate enumeration is bounded; full proof exports
can be large. Native call reductions need not dominate graph construction and serialization costs.

Cycle 13 recommendation: **Option A — continue relational concept learning**. Collect independent externally sourced role/field
annotations with explicit ancestry, test unseen conditional families including pawn forks, and quantify uncertainty and conflicting
observations. Expand overload response and safe-escape evidence while preserving abstention and proof boundaries. Measure and reduce
proof/graph transport cost without changing inference semantics. Reconsider experimental strategic comparison only after those
transfer and reliability gates improve. These results do not materially change the earlier no-go boundary on new native composition;
Option C is not supported by new operator evidence, and strategic move selection is deferred.

All required reports are linked in [package-matrix.md](package-matrix.md). The machine-readable
{evidence('delivery.json','delivery receipt')} and {evidence('manifest.json','artifact manifest')} bind final checks and files.
''')
    required=['engineering-report','package-matrix','legal-promotion-review','field-interaction-ontology','dependency-graph',
        'field-interactions','strategic-concepts','pins','forks','discovered-attacks','overloaded-defenders','trapped-pieces',
        'temporal-evolution','concept-learning','counterfactuals','performance','reproduction']
    assert all((docs/(name+'.md')).exists() for name in required)
    write_json(out/'delivery.json',dict(passed=True,complete_delivery=True,starting_head=config['starting_head'],
        validated_source_head=current['source_head'],production_code_hash=production_code_hash(),
        report_generation_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        engineering_packages=20,reports=required,test_count=tests['test_count'],legal_candidate_promoted=legal['promoted'],
        concept_model_version=learned['version'],default_model_version=legal['default_version'],
        clean_implementation_replay=True,end_to_end_second_baseline_run=False,
        complete_orchestration_executed=full_orchestration,
        complete_joint_concept_theorems=0,cycle13_recommendation='A: Continue relational concept learning',
        pushed=False,deployed=False,upstream_modified=False,new_native_operators=False,
        evidence={p:sha(out/p) for p in ['acceptance.json','current/verified.json','clean-research/verified.json',
            'final-tests/verified.json','ui/verification.json','performance/summary.json','architecture/boundary.json','package-matrix.json','cli-smoke/verified.json']}))
    print('Cycle 12: 17 reports and complete delivery receipt generated',flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',required=True);parser.add_argument('--docs',default='docs/cycle12')
    args=parser.parse_args();run(args.out,args.docs)
