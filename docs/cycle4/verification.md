# Cycle 4 delivery verification

The complete clean run used source `373b9da9fc757b93b36aa1a7537a6728b386e218` and passed **194 tests in 121.41 seconds**. A new isolated checkout, initially fresh virtualenv and pinned PeTTa clone were used. After the documented fixes, dependencies were reverified and all final Cycle 4 outputs were generated from an empty directory without `--resume`. The two interrupted attempts and the development failure remain in [clean-attempts.json](../../artifacts/cycle4/clean-attempts.json) and the retained logs. See [clean-build.json](../../artifacts/cycle4/clean-build.json) and [clean-bootstrap.log](../../artifacts/cycle4/clean-bootstrap.log).

After that run, source `47ccd08f4ac916492b842c9b151c617fb832b619` corrected the interpretation of the negative inheritance-to-predicate probe and asserted its empty result. Only the native audit and its explanatory document changed; production code, numerical expressions, training inputs and thresholds did not. The native audit was rerun and every raw output matched the full build, followed by the targeted native test (one passed). This is targeted validation of the final diagnostic correction, not a claim that the entire suite was rerun after it. The [correction receipt](../../artifacts/cycle4/native-audit-correction.json) and [test log](../../artifacts/cycle4/native-audit-correction-tests.txt) record that scope.

All 83 source/configuration/test/lock files in [verification.json](../../artifacts/cycle4/verification.json) match the updated clean checkout. The model and dataset are byte-identical to the independent development run. All 44 executed evaluation reports agree candidate by candidate on classification, raw TV and complete proof digest; timings and resource counters are not expected to be byte-identical. See [reproduction-parity.json](../../artifacts/cycle4/reproduction-parity.json). All 317 protected pre-Cycle-4 files remain unchanged. The final delivery commit adds documentation and evidence without further production changes.

The pinned runtime is Python 3.12.12, SWI-Prolog 10.0.1, PeTTa `ee5cacb6a6ecdd554a1c773aaf47e9a0f8a5af0f`, and PLN `4405956947c4b53c7ff01bd565aa3b114bc970a1`. The PLN library SHA-256 is `cdfb3f18bd7b336440fc7b4409209afddf0e64c41f17dee7eefc8f02718de433`. Runtime files and dependency locks are recorded, and vendored PLN is unchanged.

Three completed ProofShot sessions contain nine screenshots, videos and summaries, covering factored origins, raw C3/C4 comparison, supported-negative evidence, unknown history, downloaded diagnostic JSON, invalid-input clearing and a 390-pixel viewport. No browser-console or server errors were captured. The [UI receipt](../../artifacts/cycle4/ui-verification.json) identifies each session and the web source/model hashes. Later history-scope and benchmark fixes did not change the captured no-history cases or web source; the final clean suite includes the inspector contract.

## Resource scope and retained failures

The comparable fresh-process inference corpus peaks at 217,772 KiB (212.7 MiB) for C4 versus 208,212 KiB (203.3 MiB) for C3. The original 214-candidate cold run takes 2.135 seconds for C4 versus 1.711 seconds for C3: C4 meets the three-second goal but is slower. Reference/cold/warm candidates and full proofs match across all 482 benchmark candidates. Fresh address-space RSS is read from `/proc/self/status` (`VmHWM`); inherited `getrusage` high-water marks are retained separately and excluded from this comparison.

The complete diagnostic research parent peaks at **2,367,052 KiB (2.26 GiB)** while retaining and serializing complete baseline, case and proof ledgers. This exceeds the earlier approximately 660 MiB whole-research-process figure and is a real reporting cost. The inference-only comparison does not erase that cost. Neither measurement is an aggregate peak for the whole native subprocess tree. See [research-process.json](../../artifacts/cycle4/benchmarks/research-process.json).

There is one legal-support coverage regression: `e1g1` in the new independent games becomes unknown because its FEN flag does not establish the required scoped history. The [case receipt](../../artifacts/cycle4/coverage-regressions.json) preserves before/after evidence. Default C4 has no observed false legal, false illegal or incomplete candidate in the reported splits, but legal abstentions remain and count against recall. The older eight-game exact-set result remains zero. The conservative-threshold ablation creates two adversarial and one validation self-check false positives; their full proofs are retained. None of these negative results was removed or used to retune the heldout decision thresholds.

## Reproduction and integrity

From a fresh checkout with the preserved pre-Cycle-4 inputs available:

```bash
TMPDIR=/dev/shm bash scripts/cycle4_reproduce.sh
.venv/bin/python -m pytest -q
.venv/bin/pln-chess cycle4 --action diagnose --split independent-games
.venv/bin/pln-chess analyze-batch --input requests.json --output diagnostics.json
```

The reproduction script already runs the test suite; the second command is an optional standalone test invocation. Batch input is a caller-provided request document, not a bundled fixture. The final [manifest](../../artifacts/cycle4/manifest.json) hashes the delivered source, evidence, documentation and UI artifacts; it excludes itself to avoid a circular hash. Verify it from the repository root:

```bash
.venv/bin/python - <<'PY'
import hashlib, json
from pathlib import Path
manifest = json.loads(Path('artifacts/cycle4/manifest.json').read_text())
for name, expected in manifest['files'].items():
    assert hashlib.sha256(Path(name).read_bytes()).hexdigest() == expected, name
print(f"Verified {len(manifest['files'])} files")
PY
```

The starting HEAD was `38cd26b97c3cf2ffe33eac526006c9820f8c3f82`. The final delivery commit is the local commit containing this manifest and report. Nothing was pushed. Research limits and falsifiable next steps are recorded in [NEXT_CYCLE.md](../../NEXT_CYCLE.md).

The staged whitespace check reports trailing spaces only in preserved raw failure logs and unmodified upstream research snapshots/license text. Those evidence bytes are intentionally retained. Authored source and delivery documents pass the whitespace check.
