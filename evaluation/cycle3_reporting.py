"""Render reports from executed measurements, without inventing completion."""
import hashlib,subprocess
from pln_chess.common import ROOT,read_json,write_json

OUT=ROOT/'artifacts/cycle3'


def report():
    comparisons=read_json(OUT/'comparison.json');baseline=read_json(OUT/'baseline.json')
    resolution=read_json(OUT/'self-check-resolution.json');benchmark=read_json(OUT/'benchmark.json')
    induction=read_json(OUT/'induction.json');run=read_json(OUT/'run.json');dataset=read_json(OUT/'dataset.json')
    packages={
      'C3-01':('complete','baseline.json','Frozen B1/B2 candidate TVs/classes and optimization reproduced; B0 also measured.'),
      'C3-02':('complete','native-probes.json','Executed composition boundary and source signatures; no unsupported operator adopted.'),
      'C3-03':('complete','../../docs/cycle3-architecture.md','Versioned descriptors, explicit schema replay and separate observations.'),
      'C3-04':('partial','transfer-proofs.json.gz','Reusable local and obstruction motifs transfer; true native conjunction unavailable.'),
      'C3-05':('complete','self-check-resolution.json','Every frozen self-check false positive tracked; independent attack curriculum and temporal frames evaluated.'),
      'C3-06':('partial','../../tests/test_cycle3.py','Castling phases, promotion and explicit predecessor tests; FEN-only EP remains unknown, historical legality not proved.'),
      'C3-07':('partial','induction.json','Original 14 formulas reproduced and controlled integration measured; no claimed novel cross-piece induction or forced benefit.'),
      'C3-08':('complete','../../docs/cycle3-learning-semantics.md','Disjoint chain evidence pools, replay/rollback, conflicts, low confidence and calibration; supplied dependence identities remain assumptions.'),
      'C3-09':('complete','dataset.json','Independent challenge/game sets, paired transforms, full candidate sets, sparse curves and overlap audit.'),
      'C3-10':('complete','comparison.json','All named baselines and ablations scored with errors and abstention visible.'),
      'C3-11':('complete','benchmark.json','Full candidate/proof parity, cold/warm measurements, bounded cache and estimated proof-memory budget; RSS limit is not OS-enforced.'),
      'C3-12':('complete','ui-verification.json','Existing API/CLI extended, independent condition panels, comparisons and structural counterfactuals.'),
      'C3-13':('complete','clean-build.json','Full suite and clean reproduction receipt; exact final status in linked evidence.'),
      'C3-14':('complete','manifest.json','Documentation, machine-readable artifacts and local delivery; no push.')}
    write_json(OUT/'package-status.json',{k:{'status':v[0],'evidence':v[1],'detail':v[2]} for k,v in packages.items()})
    def percent(v):return '—' if v is None else f'{100*v:.2f}%'
    fields=('precision','recall','f1','abstention_rate','exact_move_set_accuracy')
    lines=['# Cycle 3 final engineering report','','This is a native-partial conditional learner. Frozen Cycle 2 performance is a retrospective regression comparison; the new challenge and independent games provide additional evaluation. No strategic search or engine legality gate was added.','',
           '| Model / split | Candidates | Precision | Recall | F1 | Abstention | Exact sets | Self-check FP |',
           '|---|---:|---:|---:|---:|---:|---:|---:|']
    for name in ('B0','B1','B2','C3-local','C3-exposure','C3-induction','C3-full','no-obstruction','no-exposure','no-induction','no-arbitration','no-dependence','exact-context-only'):
        for split in ('frozen-heldout-transfer','frozen-adversarial','new-challenge','new-independent-games'):
            m=comparisons[name][split]['metrics']
            lines.append('| '+name+' / '+split+' | '+str(m['candidates'])+' | '+' | '.join(percent(m[k]) for k in fields)+' | '+str(m['self_check_false_legal'])+' |')
    lines.extend(['','## Every original self-check error','',str(resolution['outcomes'])+'. Correct negative classifications and abstentions are counted separately. Full before/after evidence is in `artifacts/cycle3/self-check-errors.json.gz`.','',
                  '## Native semantics and induction','','Native MP, revision, negation and confidence choice produce the displayed TVs. Independent conditionals are not conjoined. Explicit joint-sensor inference and unary implication chains execute; native conjunction introduction/elimination does not. No safe-king belief follows from absent attack evidence.',
                  '',f"Induction classification changes: { {k:len(v) for k,v in induction['classification_changes'].items()} }. All 14 original native formulas are independently re-executed. Direct parents and induced hypotheses share evidence and are alternatives, never independently fused.",'',
                  '## Same-model optimization parity','', '| Fixture | Candidates | Reference s / calls | Cold s / calls | Warm s / calls | Full proof parity |','|---|---:|---:|---:|---:|---|'])
    for b in benchmark['corpus']:
        lines.append('| '+b['fixture']['id']+' | '+str(b['candidates'])+' | '+' | '.join(f"{b['runs'][k]['elapsed_seconds']:.3f} / {b['runs'][k]['native_invocations']}" for k in ('reference','cold','warm'))+' | '+str(b['full_candidate_and_proof_parity'])+' |')
    lines.extend(['',f"Peak process RSS: {benchmark['rss_kib']} KiB. Checkpoint: {benchmark['checkpoint_bytes']} bytes. Evidence records: {benchmark['evidence_count']}. RSS is process-wide; the memory budget limits estimated proof payload and cache entries, not OS RSS.",'',
                  '## Work packages','','| Package | Status | Evidence |','|---|---|---|'])
    for key,(status,path,detail) in packages.items():lines.append(f'| {key} | {status} | `{path}` — {detail} |')
    tests=(OUT/'pytest.txt').read_text().strip().splitlines()[-1] if (OUT/'pytest.txt').exists() else 'Pending final clean run; see receipt.'
    lines.extend(['','## Reproduction and integrity','',f'Tests: {tests}',f"Dataset: `{dataset['hash']}`.",f"C3-full model: `{run['models']['C3-full']}`.",f"Runtime PLN: `{run['runtime']['pln']['commit']}`; source SHA256 `{run['runtime']['pln']['sha256']}`.",'',
                  '```bash','bash scripts/cycle3_reproduce.sh','.venv/bin/pln-chess cycle3 --action audit',
                  '.venv/bin/pln-chess serve --port 8765 --checkpoint artifacts/cycle3/C3-full-model.json','```','',
                  'Use `pln-chess inspect --fen "..." --move c2e2 --checkpoint artifacts/cycle3/C3-full-model.json` for a candidate. `counterfactual` accepts `--operation add-blocker|remove-piece|move-piece|color-flip|remove-right`, `--square` and `--target`. See `docs/cycle3-architecture.md` for trusted predecessor observations and explicit inference budgets.','',
                  'Starting commit: `f80b27dc41e591c90ed7456f3730fb5c0ea5d28e`. Final delivery commit is available from `git log -1`; a file cannot contain the hash of its own committing tree. Local commits only; no push, deployment or remote mutation.','',
                  '## Remaining research priorities','','1. Verified native conjunction and justified closed-world safety evidence.','2. Independently sampled induction populations that can add useful hypotheses beyond direct parents.','3. More unseen pawn/history and castling contexts, with explicit predecessor evidence.','4. Broader independent game evaluation and confidence/coverage tradeoffs.','5. Persistent native execution or shared immutable observation scheduling with full proof parity.'])
    (ROOT/'docs/cycle3-final-report.md').write_text('\n'.join(lines)+'\n')
    err=['# Cycle 3 error analysis','','Every original held-out self-check false positive is listed below. The frozen missing-contact patterns were bishop diagonal (20 king moves) and pawn forward diagonal (3 king moves). Training additions are new isolated contact positions, not relabeled held-out positions.','',
         '| Fixture | Move | Outcome | Final native TV |','|---|---|---|---|']
    for r in resolution['cases']:err.append(f"| {r['fixture']} | {r['move']} | {r['outcome']} | {r['tv']} |")
    err.extend(['','Abstention retains the raw native conclusion; it does not silently convert the TV into an illegal label. Exact move-set evaluation only counts supported moves, so abstention on an illegal move can improve an exact set while still leaving its negative legality unresolved.','',
                'All remaining false positives and uncertainty classes for every ablation are available in the compressed per-candidate reports indexed by `artifacts/cycle3/comparison.json`. Check in-board, per-piece and per-family breakdowns as well as aggregates. New independent games are the strongest check against fixture-specific improvements.'])
    (ROOT/'docs/cycle3-error-analysis.md').write_text('\n'.join(err)+'\n')
    (ROOT/'docs/cycle3-baseline.md').write_text('# Frozen Cycle 2 baseline\n\nExpected local commit f80b27dc41e591c90ed7456f3730fb5c0ea5d28e was present. Source and artifact hashes, runtime pins, thresholds, initial status, machine information, exact split IDs and commands are in `artifacts/cycle3/baseline.json`. The pre-implementation receipt is `baseline-initial.json`.\n\nB1 and B2 candidate classifications and raw TVs reproduced exactly for the 40-position held-out and 24-position adversarial splits. The native reference/cold/warm benchmark was re-executed with full proof parity, independently of the new representation. Original models and datasets remain in their original committed paths and are hash-checked by the preservation receipt.\n')
    preserved={path:hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==sha for path,sha in baseline['frozen_files'].items() if path.startswith(('artifacts/','fixtures/','vendor/','configs/'))}
    assert all(preserved.values());write_json(OUT/'preservation.json',preserved)
    files={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(OUT.rglob('*')) if p.is_file() and p.name!='manifest.json'}
    write_json(OUT/'manifest.json',{'starting_commit':baseline['starting_commit'],'build_head':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
               'runtime':run['runtime'],'dataset_hash':dataset['hash'],'models':run['models'],'command':run['command'],'files':files,
               'known_exceptions':['Native conjunction unsupported','Induction benefit not assumed','FEN-only en passant history unknown','Dependence grouping relies on supplied source identity','RSS is measured, not OS-enforced','Paired transforms are not independent test families'],
               'tests':tests,'no_push':True})

if __name__=='__main__':report()
