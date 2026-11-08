"""Consolidated reports from completed evidence; no inferred performance claims."""
from pathlib import Path
import argparse
import hashlib
from pln_chess.common import ROOT,read_json,write_json


def pct(v):return 'n/a' if v is None else f'{100*v:.3f}%'
def err(m):return f"{m['false_positive']} / {m['false_illegal']} / {m['self_check_false_legal']}"
def table(headers,rows):return '\n'.join(['| '+' | '.join(headers)+' |','|'+'|'.join('---' for _ in headers)+'|',*['| '+' | '.join(map(str,row))+' |' for row in rows]])


def report(out,docs=None):
    out=Path(out);docs=Path(docs or ROOT/'docs/cycle8');docs.mkdir(parents=True,exist_ok=True)
    a=read_json(out/'acceptance.json');v=read_json(out/'verification.json');all_metrics=read_json(out/'comparison.json')
    selected=a['selected_variant'];transfers=read_json(out/'transfers.json');data=read_json(out/'datasets/dataset.json')
    matrices={};rows=[]
    for split,e in all_metrics['C8-frozen'].items():
        old=e['metrics'];new=all_metrics[selected][split]['metrics'];candidate=all_metrics['C8-promotion-relative'][split]['metrics']
        rows.append([split,pct(old['recall']),pct(new['recall']),pct(candidate['recall']),pct(old['exact_move_set_accuracy']),pct(new['exact_move_set_accuracy']),pct(candidate['exact_move_set_accuracy']),err(new),err(candidate)])
    comparison=table(['Split','C7 recall','Default recall','Promotion candidate recall','C7 exact sets','Default exact sets','Candidate exact sets','Default FL / FI / self-check','Candidate FL / FI / self-check'],rows)
    previous_learned=read_json(out/'baseline/C7-learned-8-locked-summary.json')
    research_rows=[]
    for split in all_metrics['C8-frozen']:
        prior=(all_metrics['C7-learned-8'] if split.startswith('cycle8-') else previous_learned)[split]['metrics']
        candidate=all_metrics['C8-promotion-relative'][split]['metrics']
        research_rows.append([split,pct(prior['recall']),pct(candidate['recall']),pct(prior['exact_move_set_accuracy']),pct(candidate['exact_move_set_accuracy']),err(prior),err(candidate)])
    research_comparison=table(['Split','C7 research recall','C8 candidate recall','C7 research exact sets','C8 candidate exact sets','C7 research FL / FI / self-check','C8 candidate FL / FI / self-check'],research_rows)
    details=[]
    for arm,entries in all_metrics.items():
        for split,e in entries.items():
            m=e['metrics'];details.append([arm,split,pct(m['precision']),pct(m['recall']),pct(m['f1']),pct(m['abstention_rate']),err(m),pct(m['exact_move_set_accuracy']),m['incomplete']])
    evaluation=('# Cycle 8 evaluation and acceptance\n\n'
        f"Selected default: **{selected}**, operational. New learning promoted: **{a['new_learning_promoted']}**. "
        f"The clean study ran {v['evaluations']} registered evaluations after 38 exact C7 baseline replays. "
        'The same seeded candidate grammar, oracle labels and split membership apply within each comparison. All raw reports retain ordered native proofs.\n\n'+comparison+'\n\n'
        'C7 columns are the independently replayed accepted checkpoint. The research candidate and conservative exact-only fallback were registered before any C8 training/evaluation outcomes. Both ran every established and new acceptance suite. A candidate requires zero observed false-legal, false-illegal, self-check and incomplete results; no lost prior supported decisions; no lower recall or exact-set accuracy; and all infrastructure/provenance gates. Destructive ablations are ineligible.\n\n'
        'The [acceptance receipt](../../artifacts/cycle8/acceptance.json) lists every rejection reason and binds the default to model/source/runtime/registration hashes. [Paired changes](../../artifacts/cycle8/paired-summary.json) include 1,000 bootstrap draws, seed 808, clustered by game or constructed source group; color mirrors stay together. Historical standalone fixtures use fixture IDs. Small synthetic samples do not support population-wide guarantees.\n\n'
        'The previous learned research model is also compared directly. Historical columns come from the immutable C7 replay, while C8 partitions run that unchanged checkpoint through the common evaluator.\n\n'+research_comparison+'\n\n'
        'Full metrics below distinguish abstention from incomplete execution. Per-piece, per-family, promotion-specific, in-board-only, empty-terminal exact and proof-coverage results are in [comparison.json](../../artifacts/cycle8/comparison.json). Raw native confidence is not calibrated legality probability.\n\n'+
        table(['Arm','Split','Precision','Recall','F1','Abstention','FL / FI / self-check','Exact sets','Incomplete'],details)+'\n\n'
        'Each incorrect supported decision and each loss of a previously supported decision is retained with its exact evaluation artifact, FEN/move, proof references, evidence IDs and host decision in [all-regressions.json.xz](../../artifacts/cycle8/proofs/all-regressions.json.xz). This includes intended strict-mode abstentions and destructive ablations. Representative successful and unresolved native proofs are in [representative-examples.json.xz](../../artifacts/cycle8/proofs/representative-examples.json.xz).\n\n'
        'Calibration is diagnostic only: empirical strength-decile mappings are fitted on C8 validation and scored on other partitions, separately for all candidates, in-board candidates and promotion candidates. [calibration.json](../../artifacts/cycle8/calibration.json) reports Brier score, log loss, ECE, raw-strength Brier score and native-confidence bins. No mapping affects training, STVs, classification or acceptance. Correlated candidate rows and imbalanced easy negatives limit interpretation.\n')
    (docs/'evaluation.md').write_text(evaluation)
    ablations=[]
    for arm in ('C8-promotion-relative','C8-no-promotion-training','C8-no-destination-context','C8-no-choice-context','C8-no-dependence'):
        for split,e in all_metrics[arm].items():
            if split.startswith('cycle8-') or split=='cycle7-independent-games':
                m=e['metrics'];ablations.append([arm,split,pct(m['recall']),pct(m['exact_move_set_accuracy']),err(m),pct(m['promotion_specific']['recall'])])
    (docs/'ablations.md').write_text('# Ablations and failed experiments\n\n'+
        table(['Arm','Split','Recall','Exact sets','FL / FI / self-check','Promotion recall'],ablations)+'\n\n'
        'Removing destination context pools occupancy and destination piece type. Removing choice context pools promotion choice and resulting identity. Removing dependence handling counts repeated source-group records and disables overlap guards while retaining true evidence IDs. No-promotion-training retains the C7 exact-only learner without C8 transition evidence. Native training ledgers report the actual revised evidence and exclusions. Null outcomes do not establish that a distinction or safeguard is unnecessary outside this corpus.\n\n'
        'Initial development failures are retained under `artifacts/cycle8/development/`: a native negation probe used the wrong symbol casing and returned an unevaluated expression; the corrected signature produced a native STV. A zero-budget test exposed an absent diagnostic `typed_premises` list in C7; initialization fixed the exception without changing completed native derivations. The initial focused run was 26 passed / 1 failed; the corrected focused run passed 28 tests. Full clean-suite results are reported separately. The browser pilot required a persistent ProofShot output config to collect the command timeline; the final verification repeats the flows with that config.\n\n'
        'The first final browser pass passed all functional checks, but the subsequent cleanup check found a detached ProofShot server still running. Its exact verifier source and evidence remain in `development/ui-first-final-pass/`. The corrected verifier records ownership of its server process group, closes that group after recording, and checks that the port has closed. The full browser pass was repeated. Production inference did not change.\n\n'
        'That repetition exposed a browser-tool timing/state issue: a resize command returned success while the measured viewport was still 1280 pixels. The mobile assertion failed, and owned-server cleanup still completed. `development/ui-viewport-retry/` preserves the exact verifier and failed run. The final verifier creates a fresh isolated session, waits for the actual requested viewport, and invalidates stale success receipts before running; the 390-pixel layout requirement remains unchanged.\n\n'
        'No failed experiment was removed to improve an acceptance metric. All candidate-specific release failures, if any, are listed in [acceptance.json](../../artifacts/cycle8/acceptance.json). The isolated composition laboratory did not demonstrate a new native joint introduction rule.\n')
    belief_effects=read_json(out/'ablation-belief-effects.json')
    with (docs/'ablations.md').open('a') as stream:
        stream.write(f"\nRemoving dependence safeguards increased native positive confidence in {belief_effects['confidence_increased_count']}/{belief_effects['matched_hypotheses']} matched learned hypotheses. [ablation-belief-effects.json](../../artifacts/cycle8/ablation-belief-effects.json) retains both native STVs and record/group counts for every key. An unchanged accuracy result would not make repeated ancestry independent evidence. These are diagnostic comparisons of native outputs, not replacement confidence formulas.\n")
    erows=[]
    for arm in ('C8-frozen','C8-promotion-relative','C8-no-promotion-training'):
        r=read_json(out/f'{arm}-original-errors.json');erows.append([arm,r['cases'],r['errors_remaining'],r['correct_supported_decisions'],r['abstentions'],r['incomplete']])
    reps=[]
    for r in transfers['representatives']:
        choice=r['relative_descriptor']['promotion_choice']
        reps.append([r['fixture']['id'],r['fixture']['split'],r['fixture']['focus_move'][:-1]+choice,choice,r['rule_id'],r['raw_truth_value']])
    (docs/'generalization-and-provenance.md').write_text('# Promotion outcomes and causal transfer controls\n\n'+
        table(['Model','Original cases','Errors remaining','Correct supported','Unknown','Incomplete'],erows)+'\n\n'
        'Abstention removes a wrong decision but is not counted as a correct supported resolution. The original eight cases and their first faulty evidence selection are analyzed in [promotion-error-analysis.md](promotion-error-analysis.md). Every replay retains the actual native graph in `proofs/*-original-errors.json.xz`.\n\n'
        f"The transfer study attempted **{transfers['attempts']}** complete focus moves. It found **{transfers['successful_distinct_demonstrations']}** successful case demonstrations from **{transfers['successful_source_groups']}** source groups; **{transfers['strict_holdout_source_groups']}** groups belong to combination/adversarial holdouts. Color mirrors are correlated controls, not additional independent acquisitions.\n\n"+
        'A counted success has the expected supported decision, uses a new promotion hypothesis, differs from every source evidence FEN and complete C4 context, comes from a distinct structural family, and loses the conclusion or raw support after removing that hypothesis. Shared relative local transition categories are intentional. Removal of a whole hypothesis tests that evidence family causally; separate training-replay tests retract source groups. No arbitrary-context or unseen-type safety claim follows.\n\n'+
        table(['Fixture','Split','Tested move','Tested choice','Learned rule','Raw native STV'],reps)+'\n\n'
        'The [representative archive](../../artifacts/cycle8/proofs/representative-transfers.json.xz) includes full training evidence, actual tested move, descriptor, native expressions, raw STV, matched rule, full proof and removal replay. It also retains the original fixture focus when its choice differs from the round-robin tested choice. [All attempts](../../artifacts/cycle8/proofs/transfer-attempts.json.xz) retain unknowns, incorrect decisions and excluded exact-context controls.\n\n'
        'Metamorphic file translations, file reflections, color-relative transformations and all resulting choices are summarized in [transformations.json](../../artifacts/cycle8/transformations.json), with [complete proofs](../../artifacts/cycle8/proofs/transformations.json.xz) retained separately. They share ancestry and do not increase the independent holdout count. Vertical translation across the promotion boundary is not treated as a symmetry.\n\n'
        'Each of C8-frozen, the promotion candidate and the exact-only fallback reexecutes all **287** historical negative/removal pairs and the **36** temporal cases, with four missing-history rejections. Raw archives preserve premise/rule/evidence IDs, groups, runtime/model versions, truth values, derivation order, status and budgets. The verifier reconstructs every evaluation proof digest and requires the frozen native traces to match the original baseline. Temporal replay establishes structural consistency of supplied events, not legal historical play.\n')
    perf=[];shortperf=[]
    for variant in ('C7-frozen','C8-frozen','C8-promotion-relative','C8-no-promotion-training'):
        bench=read_json(out/f'benchmarks/{variant}.json')
        for record in bench['records']:
            shortperf.append([variant,record['fixture']['scope'],*[f"{record['aggregates'][arm]['latency_seconds']['p50']:.3f}" for arm in ('reference','cold','warm')]])
            for arm,r in record['aggregates'].items():
                perf.append([variant,record['fixture']['scope'],arm,*[f"{r['latency_seconds'][p]:.3f}" for p in ('p50','p95','p99')],r['native_invocations'][0],r['grounded_atoms'][0],r['cache_hits'][0],r['cache_misses'][0],r['peak_rss_kib'],bench['checkpoint_bytes'],r['truncation_rate'],r['timeout_rate']])
    perf_table=table(['Checkpoint','Fixture','Reference p50 s','Cold p50 s','Warm p50 s'],shortperf)
    (docs/'performance.md').write_text('# Latency, native work and cache equivalence\n\n'+perf_table+'\n\n'+
        table(['Checkpoint','Fixture','Arm','p50 s','p95 s','p99 s','Native calls','Grounded atoms','Cache hits','Misses','Peak KiB','Checkpoint bytes','Truncation','Timeout'],perf)+'\n\n'
        'Each fixture has five serial reference/cold/warm triplets. Cold uses a fresh session; warm reuses only that triplet\'s cold session. Every triplet requires identical whole-candidate exports, including native STVs, evidence IDs and proofs, and zero warm native invocations. Different models have different semantics; cross-model timing differences are not described as cache-equivalent optimizations.\n\n'
        'Reported quantiles use nearest rank. With five observations p95 and p99 equal the sample maximum; they do not estimate population tails reliably. Timings are measured after concurrent study workers end on this shared host. Peak RSS is the Python process\'s cumulative high-water mark, not per-call allocation; native interpreter child RSS is not included. Native/proof counts shown in the table are from the first repetition; every sample, serialized proof size, model size and proof digest is retained in [benchmarks/](../../artifacts/cycle8/benchmarks).\n')
    ui=read_json(out/'ui-verification.json') if (out/'ui-verification.json').exists() else {'passed':False}
    ui_link=(f"[Browser video, screenshots and logs](../../artifacts/cycle8/{ui['session_dir']}/SUMMARY.md). " if ui.get('session_dir') else '')
    package_docs=['evaluation.md','promotion-error-analysis.md','ontology-and-curriculum.md','ontology-and-curriculum.md','ablations.md','generalization-and-provenance.md','native-composition-proposal.md','mathematical-validation.md','native-composition-proposal.md','generalization-and-provenance.md','performance.md','architecture-and-api.md','evaluation.md','final-report.md']
    packages={f'C8-{i:02}':{'status':'complete' if i!=12 or ui['passed'] else 'browser verification pending','evidence':'docs/cycle8/'+name} for i,name in enumerate(package_docs,1)}
    packages['C8-05']['outcome']=selected;packages['C8-09']['outcome']='Research specification/laboratory complete; no native operator enabled'
    write_json(out/'package-status.json',packages)
    matrix=table(['Package','Status','Evidence'],[[k,r['status'],f"[{Path(r['evidence']).name}]({Path(r['evidence']).name})"] for k,r in packages.items()])
    candidate_errors=read_json(out/'C8-promotion-relative-original-errors.json')
    runtime=v['runtime']
    bootstrap=read_json(out/'bootstrap-context.json');transition=bootstrap.get('source_transition_before_C8_execution')
    lineage=(f"The clean checkout bootstrapped at `{transition['from']}` and advanced while the isolated original-C7 workers ran to `{transition['to']}` before any C8 execution. This committed change fixes explicit benchmark-mode routing and adds reports; dependency/native pins are unchanged. Every C8 test, training, inference, benchmark and acceptance subprocess executes the latter clean source. Both revisions and the clean transition are retained in `bootstrap-context.json`.\n\n" if transition else '')
    (docs/'reproduction.md').write_text('# Clean reproduction and evidence manifest\n\n'
        f"Verified native study source: `{v['source_head']}`. Starting baseline: `{data.get('starting_head','c6ee658352395abe6e276cafdf1ddf59830a17a0')}`. "
        f"Python {runtime['python']}; {runtime['swipl']}; PLN `{runtime['pln']['commit']}`; PeTTa `{runtime['petta']['commit']}`. "
        f"PLN SHA-256 `{runtime['pln']['sha256']}`.\n\n"
        '```bash\ngit clone /path/to/pln-chess /data/pln-chess-cycle8-reproduction\ncd /data/pln-chess-cycle8-reproduction\n'
        f"git checkout --detach {v['source_head']}\n"
        'C8_OUT=/data/pln-chess-cycle8-output bash scripts/cycle8_reproduce.sh\n```\n\n'
        'The host must supply uv and audited SWI-Prolog 10.0.1 with Janus/PCRE. Bootstrap creates a fresh Python environment and pinned PeTTa checkout. The driver creates a separate original-C7 checkout and runs baseline imports from it; changed C8 code never silently regenerates the historical baseline. It then generates/trains deterministic C8 data/models, runs the entire test suite, laboratory, forensics, evaluation arms, controls, serial benchmarks, analysis, acceptance and actual application smoke checks. Independent subprocesses are bounded to three. No Python inference fallback exists.\n\n'
        +lineage+'The original pre-edit baseline and development failures remain separately under `development/`. The clean baseline reruns all 38 evaluations using the freshly bootstrapped runtime. `configs/cycle8-replay.json` records pre-study dataset/model sentinels; verification requires exact replay. Commands, logs, bootstrap context, full tests and source hashes are recorded under `commands/`, `logs/`, `bootstrap-context.json`, `pytest.txt` and `verification.json`.\n\n'
        'After the clean study completes, return to the delivery checkout (which contains the final reporting and browser helpers) and use the same newly reproduced output:\n\n'
        '```bash\n.venv/bin/python -m scripts.cycle8_supplement --out /data/pln-chess-cycle8-output\n'
        'TMPDIR=/dev/shm .venv/bin/python -m scripts.cycle8_ui_verify --out /data/pln-chess-cycle8-output --work /data/pln-chess-cycle8-ui-replay\n'
        'cp /data/pln-chess-cycle8-ui-replay/owned-server.{py,json} /data/pln-chess-cycle8-output/ui/\n'
        '# Refresh the repository delivery bundle while retaining its development evidence.\n'
        'cp -a /data/pln-chess-cycle8-output/. artifacts/cycle8/\n'
        '.venv/bin/python -m evaluation.cycle8_reporting --out artifacts/cycle8\n```\n\n'
        'The browser step requires ProofShot, agent-browser and Chromium. Its real form interactions, export Blob hash, video and screenshots are retained. The standalone native `.metta` witnesses contain the original library path; when moving them, replace only that import path with the pinned local `vendor/pln/lib_pln.metta`.\n\n'
        '`manifest.json` hashes the delivered artifacts and reports; it excludes itself to avoid a circular hash. Lossless `.json.xz` reports use ordered proof references into interned native DAGs. Virtual environments, native caches, temporary query files and clean checkouts are generated but not committed. All Cycle 8 commits are local; this brief prohibits a push.\n')
    (docs/'decision-memo.md').write_text('# Cycle 8 architectural decision memo\n\n'
        f"**1. Promotion errors:** The promotion candidate leaves {candidate_errors['errors_remaining']}/8 original errors, with {candidate_errors['correct_supported_decisions']}/8 correct supported decisions and {candidate_errors['abstentions']} abstentions. These outcomes are distinct from broad acceptance.\n\n"
        f"**2. Accepted learner:** The registered selection chose **{selected}**. New learning promoted: **{a['new_learning_promoted']}**. The same zero-error/no-loss gates apply to the promotion candidate and preregistered exact-only fallback. Full reasons are in the acceptance receipt; a research improvement cannot override a failed gate.\n\n"
        f"**3. Generalization:** {transfers['successful_source_groups']} source groups produced causal supported transfers, including {transfers['strict_holdout_source_groups']} combination/adversarial groups. Their full contexts differ from training; local transition categories deliberately recur. This is evidence of limited relational transfer, not arbitrary-context legality.\n\n"
        '**4. Missing PLN capability:** Native introduction of a joint proposition with explicit dependence semantics, plus independently justified conditional knowledge connecting that joint event to the target. Existing modus ponens can use a supplied nested rule; it does not learn the missing relation from marginal premises.\n\n'
        '**5. Extension justification:** A bounded research implementation of richer probability constraints is technically justified for upstream review. Production activation is not justified by this cycle, and no native operator is added. Continued exact/conditional operational learning remains independently useful.\n\n'
        '**6. Mathematical risks:** Unidentified joint dependence; confusing event independence with sampling independence; duplicate ancestry; incompatible scopes; converting native STV confidence into coverage; losing dependence through interval compression; missing complement conditionals; and treating inconsistent constraints as ordinary uncertainty.\n\n'
        '**7. Authorized future work would entail:** A separately approved truth type and exact small-universe solver, native introduction/projection operators, feasibility and bound certificates, type/scope validation, evidence retraction, resource limits, duplicate/conflict attacks, oracle-independent differential/property tests, upstream review and a versioned API. A statistical calibration front end and conditional-learning contract remain separate proof obligations. No implicit STV adapter is approved.\n\n'
        '**8. Cycle 9 priority:** Preserve the accepted operational model; investigate every remaining promotion/exposure abstention or failed candidate case with independent evidence; strengthen causal family splits and external-game evaluation; then, only with authorization, implement the isolated native credal prototype. Keep operational acceptance independent of that research.\n')
    (docs/'final-report.md').write_text('# Cycle 8 consolidated engineering delivery\n\n'
        f"Starting commit: `c6ee658352395abe6e276cafdf1ddf59830a17a0`. Verified implementation: `{v['source_head']}`. The ending delivery commit is the commit containing this report; `git log c6ee658..HEAD` lists local cycle commits. No push was performed.\n\n"
        f"Default: **{selected}, operational**. Tests: **{v['test_count']} passed**. The clean study reproduced 38 baseline evaluations and ran {v['evaluations']} C8 matrix evaluations. "
        f"All {v['protected_files']} protected historical files remain byte-identical; {v['reconstructed_row_proofs']} native row proofs were reconstructed and checked. "
        'New native positive composition remains **not demonstrated**. Its formal design and mathematical reference laboratory are separate from production.\n\n'+matrix+'\n\n'+comparison+'\n\n'
        f"The promotion candidate correctly supports {candidate_errors['correct_supported_decisions']}/8 original error cases. Generalization controls establish {transfers['successful_source_groups']} successful source groups, including {transfers['strict_holdout_source_groups']} strict held-out groups; mirrors are not independent samples. Each registered default candidate preserved all 287 negative/removal controls. See [generalization and provenance](generalization-and-provenance.md).\n\n"+
        perf_table+'\n\n'
        'Performance tables show empirical p50 seconds. [Performance](performance.md) includes p95/p99, calls, grounding, memory, model/proof sizes and full cache parity. Five samples make tail estimates exploratory. [Evaluation](evaluation.md) includes precision, recall, F1, abstention, exact sets, promotion/per-piece metrics, paired intervals and validation-only calibration. [Ablations](ablations.md) retains failed and null experiments.\n\n'
        'The [composition proposal](native-composition-proposal.md) separates conjunction, dependence, implication, aggregation and confidence. Exact finite checks and analytic arguments establish bounds conditional on supplied constraints; they do not establish STV calibration or a chess legality theorem. Existing-native, proposed-reference and unsupported results have distinct statuses.\n\n'
        f"Browser verification passed: **{ui['passed']}**; [receipt](../../artifacts/cycle8/ui-verification.json). "
        +ui_link+
        '[Reproduction](reproduction.md) documents the clean commands, lineage and evidence manifest. The [decision memo](decision-memo.md) answers all eight architectural questions.\n\n'
        'Known limits: all new games are synthetic; constructed family separation uses complete configurations while atomic motifs recur; some extra pieces are remote; candidate grammar is an inductive bias; native positives remain partial learned conditionals; temporal replay is structural; confidence is uncalibrated; and small-sample performance/accuracy findings do not establish universal safety. The accepted default and research candidate remain separate whenever gates differ.\n')
    files={}
    for path in sorted(out.rglob('*')):
        if path.is_file() and path!=out/'manifest.json':files['artifacts/cycle8/'+str(path.relative_to(out))]={'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bytes':path.stat().st_size}
    for path in sorted(docs.glob('*.md')):files['docs/cycle8/'+path.name]={'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bytes':path.stat().st_size}
    write_json(out/'manifest.json',{'source_head':v['source_head'],'files':files,'self_hash_exclusion':'manifest.json','generated_not_committed':['.venv/','.runtime/','clean study checkouts','temporary native queries']})
    return packages


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',required=True);parser.add_argument('--docs');args=parser.parse_args();report(args.out,args.docs)
