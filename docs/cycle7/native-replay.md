# Portable native witness replay

The `.metta` files retain the absolute import path used in the recorded run. The portable wrapper reuses their stored bodies with the current checkout's verified pinned library instead. After the main reproduction, run:

```bash
TMPDIR=/dev/shm .venv/bin/python -m scripts.cycle7_witness 75 --transcripts /data/pln-chess-cycle7-output/native/transcripts.json
TMPDIR=/dev/shm .venv/bin/python -m scripts.cycle7_witness 76 --transcripts /data/pln-chess-cycle7-output/native/transcripts.json
```

From the delivered checkout with committed artifacts, the `--transcripts` arguments can be omitted. Both commands were replayed successfully from the corrected fresh checkout; see [the index receipt](../../artifacts/cycle7/native/portable-replay.json) and the [independent-only](../../artifacts/cycle7/logs/native-replay-independent-only.txt) / [supplied-rule](../../artifacts/cycle7/logs/native-replay-supplied-nested.txt) raw outputs.

The independent A/B query returns no `Eligible` conclusion. Adding the supplied nested implication produces an STV with native stamps `learn-A`, `learn-B`, and `supplied-rule`. This verifies the mechanism and its supplied-rule dependency; it does not establish a learned joint rule or a complete positive chess-legality proof. The laboratory also records both premise deletions and the shared-stamp control.
