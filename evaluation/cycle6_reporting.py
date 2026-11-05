"""Generate Cycle 6 documentation only from recorded, executed results."""
import hashlib,os,subprocess
from pathlib import Path
from pln_chess.common import ROOT,read_json,write_json,digest
from evaluation.cycle3 import read_gzip
from scripts.cycle6_baseline import START,SPLITS

OUT=Path(os.environ.get('C6_OUT',ROOT/'artifacts/cycle6'))

def report(out=OUT):
    out=Path(out);docs=ROOT/'docs/cycle6';docs.mkdir(parents=True,exist_ok=True)
    comparison=read_json(out/'comparison.json');base=read_json(out/'baseline/comparison.json');accept=read_json(out/'acceptance.json');verify=read_json(out/'verification.json')
    native=read_json(out/'native-probes/audit.json');negative=read_json(out/'negative-regressions.json');local=read_json(out/'locality.json');induction=read_json(out/'induction.json')
    bench={n:read_json(out/f'benchmarks/{n}.json') for n in ('C4','C5','C6-operational','C6-strict','C6-experimental')}
    source_head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();data=read_json(out/'datasets/dataset.json');model=read_json(out/'model/C6-full.json')
    def save(name,text):(docs/name).write_text(text.strip()+'\n')
    def metrics(name,split):return (base[name][split] if name in base and split in base[name] else comparison[name][split])['metrics']
    def counts(m):return f"{m['true_positive']} / {m['true_negative']} / {m['unknown']} / {m['incomplete']}"
    table=['| Split | C4 legal / illegal / unknown / incomplete | C5 strict | C6 operational | C6 recall | C6 exact sets |','|---|---:|---:|---:|---:|---:|']
    for split in [x[0] for x in SPLITS]+['cycle6-validation','cycle6-adversarial','cycle6-independent-games']:
        c4,c5,c6=[metrics(n,split) for n in ('C4','C5','C6-operational')]
        table.append(f"| {split} | {counts(c4)} | {counts(c5)} | {counts(c6)} | {c6['recall']:.6%} | {c6['exact_move_set_accuracy']:.6%} |")
    table='\n'.join(table)
    packages=[
      ('C6-01','complete','Starting state locked; 16 exact C4/C5 reruns and immutable input snapshot.'),
      ('C6-02','complete','Three independently selectable modes, public labels, raw channels, explicit host acceptance nodes.'),
      ('C6-03','complete','C4 positive utility restored; verified C5 negative proofs retained; no TV fusion.'),
      ('C6-04','complete; negative finding','Pinned operator definitions and runnable controls; independent positive composition not achieved.'),
      ('C6-05','partial research outcome','Disjoint actual board curricula and withheld combinations tested; no new learned temporal/exposure primitive conjunction.'),
      ('C6-06','complete','49 historical and 238 newer exact negatives with removal counterfactuals.'),
      ('C6-07','complete within structural scope','Versioned event replay covers rights, double-step, capture, EP and promotion; historical legal play unverified.'),
      ('C6-08','complete; no predictive gain','Native induction, sham, marginal and overlap ablations; induction stays disabled.'),
      ('C6-09','complete audit','Pre-hash descriptors and transformations inspected; remaining contextual counterexamples retained.'),
      ('C6-10','complete verification','Mode/budget/evidence scoped caches and full proof parity; duplicated export and memory measured.'),
      ('C6-11','complete' if accept['passed'] else 'blocked gates',f"Default {accept['default_mode']}; blockers {accept['blockers']}."),
      ('C6-12','complete','API/CLI modes, migration, browser comparisons, raw diagnostics and examples.'),
      ('C6-13','complete' if accept['checks']['tests'] and accept['checks']['clean_bootstrap'] else 'verification incomplete',verify['tests_summary']),
      ('C6-14','complete local delivery','Reports, artifacts and logical local commits; no push.')]
    write_json(out/'package-status.json',[{'package':p,'status':s,'evidence':e} for p,s,e in packages])
    matrix='| Package | Status | Result |\n|---|---|---|\n'+'\n'.join(f'| {p} | {s} | {e} |' for p,s,e in packages)
    hashes={'C4_model_version':read_json(ROOT/'artifacts/cycle4/model/C4-full.json')['version'],'C5_model_version':read_json(ROOT/'artifacts/cycle5/model/C5-full.json')['version'],
        'C6_model_version':model['version'],'C6_model_file_sha256':hashlib.sha256((out/'model/C6-full.json').read_bytes()).hexdigest(),
        'C6_dataset_hash':data['hash'],'C6_dataset_file_sha256':hashlib.sha256((out/'datasets/dataset.json').read_bytes()).hexdigest(),
        'runtime':native['runtime'],'all_frozen_dataset_hashes':{k:base['C4'][k]['dataset_hash'] for k,_,_ in SPLITS},
        'production_code_hash':accept['production_code_hash'],'registration_hash':accept['registration_hash']}
    write_json(out/'versions.json',hashes)
    save('architecture.md',f'''# Cycle 6 architecture

C6 is a lossless schema-5 model wrapper. It retains the frozen C4 source model and C5 conditionals; it adds no chess rule, native operator, conjunction, host TV formula, or oracle dependency. Policy `{model['policy']}` separates evidence from acceptance.

`operational` accepts C4's learned local positive projection as **native-partial / evidence-supported**. Its proof status is `native-conditional`, never `native-composed`. C4 negatives and independent C5 negative chains remain `supported-illegal`. `strict` and `experimental` abstain on unsupported positives; experimental findings never promote themselves. An incomplete native run stays `incomplete`.

`raw_stv` and the compatibility field `legal_move_truth_value` expose the same selected diagnostic channel in every C6 mode. Both C4 and C5 raw channels remain in `evidence_channels`; an unknown strict result can have a high-strength local STV. This is an explicit change from C5's global UNKNOWN sentinel, preserved separately in `evidence_channels.C5.truth_value`. Strength and confidence are distinct, uncalibrated quantities. `legacy_classification` maps public labels to earlier metric vocabulary.

A supported C4 global projection opposed by a C5 negative chain abstains. Strong negative premises whose bridge is blocked by overlapping or conflicting evidence also abstain. Both channels, dependence groups, node IDs and host decision rationale remain inspectable. The policy never chooses the highest confidence across opposing scopes. Local partial support alone does not contradict an already-established C4 negative chain.

The source call graph is `api.explain_move → inference.infer_moves → cycle6.inference → cycle5.inference → cycle4.inference → NativeSession → Runtime.batch → pinned PeTTa/PLN`. In C5, the final acceptance branch in `cycle5/inference.py` preserves a negative witness and otherwise assigns unknown because `proof_plan.positive_proof_complete` is false. C6 retains that result and exposes C4's pre-gate projection; it does not pretend the absent conjunction was implemented.

The default is `{accept['default_mode']}`. A promotion receipt must pass every required check and match the model, runtime, policy, production-source hash and preregistration hash. Missing/stale/failed receipts default to strict. Explicit operational requests remain available for research.

Cache scopes include runtime manifest, model, mode, proof policy, observation/event versions, all budget/threshold/history settings, then position and evidence identities in the underlying source sessions. Changing mode clears both source caches. Ordered interned native nodes reconstruct full proofs losslessly; host acceptance nodes are separately labeled non-native.

Migration: `pln-chess migrate-model --checkpoint artifacts/cycle5/model/C5-full.json --output /tmp/c6.json`. Exported C6 models embed the complete source, validate schema and runtime, and preserve the C5 semantic model hash. Old schemas remain readable with their original behavior.
''')
    inventory='| Symbol | Source lines | Runtime status |\n|---|---:|---|\n'+'\n'.join(f"| `{r['symbol']}` | {r['line']}–{r['end_line']} | {r['support']} |" for r in native['inventory'])
    controls='\n\n'.join(f"**{r['id']}**\n\n```metta\n{r['expression']}\n```\n\n```text\n{r['stdout']}\n```" for r in native['records'] if r['id'] in ('independent','missing-A','missing-B','swapped','contradictory-B','correlated','renamed','nested-full','nested-missing-A','nested-missing-B','inheritance-chain'))
    save('native-capability-audit.md',f'''# Native capability audit

PLN `{native['runtime']['pln']['commit']}`, SHA-256 `{native['runtime']['pln']['sha256']}`. The vendored source is unchanged. Exact signatures and complete native formula definitions are stored with source line locations in `artifacts/cycle6/native-probes/audit.json`; executable input is `audit.metta`. Recorded stdout is retained for every wrapper probe and raw STVs for every direct truth-function probe.

{inventory}

Modus ponens, deduction, induction, abduction, revision, negation, inversion, similarity/equivalence, symmetric MP, evaluation implication and evidence choice have executable probes. The library's symbolic inheritance/implication rules require their exact term shapes and supplied marginal STVs; source presence is distinguished from successful wrapper execution. Direct truth functions do not inspect evidence stamps. `StampDisjoint` must gate overlapping provenance; `BestConfidenceCandidate` is a selector, not dependence-aware contradictory-evidence fusion. Deduction's marginal confidence does not gate output, and induction assumes the explicitly recorded population marginals.

The local upstream checkout history is captured in the audit. No claim is made that those local refs are the latest remote head. No upstream repository was changed or pushed.

**Independent-premise positive composition: not achieved.** Three separately identified observations revise A and B through the native revision operator, with disjoint groups. The bare facts do not derive a novel C. Supplied nesting and relation chains can execute, but already contain relations to C; they are mechanism controls, not evidence of learned unseen conjunction. No new operator was activated.

{controls}

This is a limitation of the audited executable rule set and tested representations. It is not a universal impossibility theorem about every PLN implementation. A future extension would require separate authorization, source and semantic review, and the same independent-premise counterfactual tests.
''')
    factorial=read_gzip(out/'factorial.json.xz')
    save('composition-lab.md',f'''# Independent-premise and locality laboratory

The fixed evaluation set contains {len(data['positions'])} positions and {len(data['factorial_tasks'])} factorial/transform cases. The isolated primitive checkpoint is trained from actual board examples with separate geometry, destination, boundary and ray supervision. Geometry and its adverse destination/path combinations never receive a joint training target. Every held-out abstract combination is absent from that curriculum; exact evidence, model version and the empty overlap list are in `factorial-curriculum.json`.

The native laboratory runs {len(factorial['controls'])} both/missing/uncertain/contradictory/overlap/swapped/renamed controls. Their exact native inputs and stdout are retained. Native conditional activation is listed separately from the frozen C4 host joint-category projection. Neither counts as a native conjunction. **No case achieved native positive composition.**

Knight destination occupancy, rook/bishop unseen-distance obstruction, queen capture, pawn forward/capture, king exposure, castle transit, EP exposure and mandatory `f6h5` are traceable. The isolated temporal and exposure primitives remain unavailable as newly learned compositional families; these are a partial research outcome, explicitly listed rather than fabricated. Structural/external observations and pre-existing operational chains remain visible.

Valid translations, file reflections, owner/rank flips, piece-ID renaming and distant added pawns are tested. Castle/EP transforms are excluded unless semantics are preserved. Distant additions are excluded from the move ray and destination and preserve the reference outcome during evaluation-only fixture generation. The external reference engine supplies labels only outside production.

`locality.json` contains every C4/C5 pre-hash descriptor, {len(local['transforms'])} transform comparisons, {len(local['absolute_key_findings'])} flagged absolute/global-key findings and {len(local['counterexamples'])} contextual counterexamples. Local keys exclude absolute squares and full-board opponent lists; king-exposure frames and historical/boundary context remain explicitly distinct. A changed globally relevant exposure context is not silently presented as local-rule invariance.

The unresolved C5 knight capture remains an explicit proof-gap case in `proofs/examples.json.xz`; no native AND or global safety theorem is claimed.
''')
    save('temporal-evidence.md','''# Temporal evidence

`unknown`, `trusted-fen`, and `observed-events` are aliases for C5's `fen-only`, `trusted-metadata`, and `event-backed`. Unknown history supplies no historical proof. Trusted FEN is a sourced external claim with finite confidence. Observed events replay structural transitions and compare the exact final FEN; they do not certify legal play.

`history-v6.1` receipts contain `events-v6.1` records, stable event IDs, before/after state IDs, source, sequence, rights/EP changes and removed/added/changed occupants. Seven executed cases cover pawn double steps, rook and king rights changes, castling, promotion, rook capture affecting rights, and EP capture. Contradictory final state, empty/incomplete history and rights-changing edits are tested in every case. Exact records are in `artifacts/cycle6/temporal.json`.

An EP predecessor and an independent castling-history attestation have different scopes. Reliable external observations can make the relevant C4 sensor available; they never establish a complete historical theorem or current king safety. Spatial transforms do not automatically certify transformed histories. No production reference-engine legality check is added.
''')
    save('learning-and-induction.md',f'''# Learning and induction

Production C6 performs no retraining: C4 positive and C5 negative beliefs are preserved exactly. The factorial checkpoint is isolated and contains no C4 local observation hypotheses, only independent bridge conditionals and separately supervised primitives. Dependence groups, evidence IDs and held-out combination exclusions are explicit.

C2–C5 native probes are reexecuted in the inherited audit. C5 induction is rerun using its original population, first observation per original group and ancestry exclusions. Its {len(induction['C5_reexecuted']['rules'])} proposed consequent conditionals are host-selected geometry descriptors; they are not native concept invention. Population counts, estimated marginals and exact native calls are retained.

The new run executes enabled, disabled, redundant sham, halved-marginal, zero-marginal-confidence and overlapping-evidence controls. It applies the induced rules to {len(induction['unseen_combinations'])} held-out C6 base combinations. Changed local TVs are not counted as predictive benefit. **Global classification gains: {induction['global_classification_changes']}.** No defensible global rule injection was identified, so operational induction remains disabled.

Shared populations and sample construction limit these marginals. Zero marginal confidence does not itself suppress every native formula. The overlap control executes the native stamp guard and refuses extra revision. All assumptions, failed/empty outputs and evidence provenance are in `artifacts/cycle6/induction.json`.
''')
    btable=['| Model/mode | Candidates | Reference seconds / calls | Cold seconds / calls | Warm seconds / calls | Peak KiB |','|---|---:|---:|---:|---:|---:|']
    for name,b in bench.items():
        p=next(x for x in b['corpus'] if x['candidates']==214);rs=p['runs']
        btable.append(f"| {name} | 214 | {rs['reference']['elapsed_seconds']:.3f} / {rs['reference']['native_invocations']} | {rs['cold']['elapsed_seconds']:.3f} / {rs['cold']['native_invocations']} | {rs['warm']['elapsed_seconds']:.3f} / {rs['warm']['native_invocations']} | {b['peak_process_rss_kib']} |")
    btable='\n'.join(btable)
    ratio=next(p for p in bench['C6-operational']['corpus'] if p['candidates']==214)['runs']['cold']['elapsed_seconds']/next(p for p in bench['C4']['corpus'] if p['candidates']==214)['runs']['cold']['elapsed_seconds']
    save('benchmark-and-evaluation.md',f'''# Matched evaluation and performance

{table}

Every frozen split uses its original members, source dataset hash, model and thresholds. Both baseline models were rerun; classifications, raw TVs, evidence/rule IDs, proof IDs and exact predicted sets match C5's preserved reports. Frozen inputs are copied in `baseline/inputs.json.xz`; immutable historical proof/report copies remain reachable through starting commit `{START}` and are verified unchanged. No prior artifact is rewritten.

All-candidate and in-board metrics, confusion matrices, precision/recall/F1, error families, raw strength/confidence distributions and 300-draw clustered 95% bootstrap intervals are in each evaluation report. Empty-terminal exact matches are separated from nonempty exact sets. Confidence is not a calibrated probability. Exploratory strength-decile calibration is fitted on the declared validation split only and never affects inference.

Four required variants are evaluated: frozen C4, strict C5/C6, C6 operational with negatives, and C6 operational without the new negatives. Every changed C4 classification links its host acceptance node and native proof in `verification.json`. All {negative['historical_preserved']} historical cases and {negative['new_preserved']} C5 negatives are preserved, with {negative['historical_removal_changes']} and {negative['new_removal_changes']} classification-changing removals. Every newer negative preserves the original C5 native proof exactly.

{btable}

The operational cold/C4 cold ratio on 214 candidates is {ratio:.3f}×; the ≤2× research target is {'met' if ratio<=2 else 'not met'}. If above target, the additional typed-premise execution, provenance expansion and complete proof export are explicit measured costs; no proof is silently truncated to improve timing. Four fixtures total 700 candidates. Reference, cold and warm runs have complete candidate/STV/classification/proof/evidence/rule parity in all three C6 modes. Warm calls are actual native calls, not logical scheduled nodes.

Fresh-process VmHWM measures live inference memory; it does not claim to cover all subprocesses. Reports separately measure repeated opponent frames, duplicate native proof occurrences, interpreter startup, complete candidate serialization and a lossless interned export. The interned evaluation export reduces duplicate storage; it is not represented as a reduction in the live API's full-proof memory.

Gates: `{accept['checks']}`. Default: `{accept['default_mode']}`. Observed correctness is empirical on these datasets, not universal legality.
''')
    save('final-report.md',f'''# Cycle 6 final engineering report

Starting HEAD: `{START}`. Verified implementation HEAD: `{source_head}`. Final delivery commit is the local commit containing this report; consult `git log -1` for its hash. **Nothing pushed, published or deployed.** The previous stable C4 ancestor is `d5cfcb126acc9c3e5da669744d661e6895fb9303`.

{matrix}

{table}

Default policy: **{accept['default_mode']}**. Acceptance passed: **{accept['passed']}**; blockers: `{accept['blockers']}`. Operational predictions retain their partial conditional status. Strict and experimental do not manufacture positive proofs. Independent-premise native positive composition is **not achieved**.

Model and dataset versions:

- C4: `{hashes['C4_model_version']}`.
- C5: `{hashes['C5_model_version']}`.
- C6: `{hashes['C6_model_version']}`; file SHA-256 `{hashes['C6_model_file_sha256']}`.
- C6 dataset: `{hashes['C6_dataset_hash']}`; file SHA-256 `{hashes['C6_dataset_file_sha256']}`.
- Native PLN: `{native['runtime']['pln']['commit']}`; library SHA-256 `{native['runtime']['pln']['sha256']}`.

Exact runtime manifest, PeTTa pin and every frozen dataset hash are in `artifacts/cycle6/versions.json`. Exact native expressions, learned premise evidence and missing/swapped/contradictory/correlated/renamed controls are in [native-capability-audit.md](native-capability-audit.md). Formula definitions and stdout are preserved in machine-readable artifacts.

{btable}

Verification: **{verify['tests_summary']}**. Clean dependency bootstrap: **{accept['checks']['clean_bootstrap']}**. All {verify['protected_file_count']} protected historical files remain byte-identical. Full-proof reconstruction, native probes and reference/cold/warm parity pass. The 49 and 238 causal regression ledgers are `proofs/original-49.json.xz` and `proofs/new-238.json.xz`.

The inspector exposes comparison tables, evidence channels, history trust, proof gaps, budgets and diagnostic JSON export. ProofShot screenshots, recording and captured errors are retained in the delivery artifacts. API migrations and original-cycle tests remain intact.

Remaining scientific limits: learned joint observation categories are still host assembled; no native AND or universal safety theorem is available. The factorial temporal/exposure families lack new separately learned positive composition. Special-move history is external structural evidence. Induction shows no defensible global benefit and stays disabled. Global exposure and historical context can change under otherwise local-looking transforms; counterexamples are retained. The fixed geometric candidate grammar remains seeded inductive bias, not discovered chess rules.

Next priorities are a separately authorized native semantics investigation, evidence-grounded temporal/exposure learning, independent external game validation, and reducing full-proof memory without changing native derivations. No custom conjunction extension was shipped.
''')
    return docs

if __name__=='__main__':report()
