# Final packaged application verification

This session starts the repository CLI without checkpoint or mode overrides, using the accepted packaged C7 default. The real form submit/fetch/render path was exercised for default, comparison, strict, experimental, negative, unknown and incomplete results. The actual export button generated the comparison Blob stored as `../../proofs/browser-export.json`; its browser SHA-256 matches the saved bytes. CLI stdout limits required extracting the unchanged Blob string in chunks.

Use `mobile-top-390-verified.png` and `mobile-result-390-verified.png` for the actual 390 x 844 mobile checks. Earlier files with mobile names captured 1280 x 900 while the browser wrapper was ignoring its implicit-session viewport command. An explicit session viewport command resolved this. All attempts are retained. DOM measurements confirm document width 375 at viewport width 390. The desktop comparison is `c6-c7-comparison.png`.

The generated ProofShot summary reports wall duration 314 seconds and a stale default viewport. ffprobe verifies the trimmed recording duration as 155.9 seconds, size 1,339,302 bytes. Desktop captures are 1280 x 900; final mobile captures are 390 x 844. Console errors: zero; server errors: zero. The owned application server was explicitly stopped after ProofShot completed. No remote upload or PR was performed.
