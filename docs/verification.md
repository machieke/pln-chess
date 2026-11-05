# Delivery verification

The complete `bash scripts/bootstrap.sh` command exited successfully in a clean temporary copy with no `.venv`, `.runtime`, or `artifacts` directory at startup. It installed the pinned Python packages, cloned and checked out the exact PeTTa commit, audited native operators, regenerated data, trained the model, generated proofs, evaluated complete candidate sets, ran six ablations and benchmarks, and passed **61 tests**. The checked native system prerequisite was SWI-Prolog 10.0.1 with Janus and PCRE.

The delivered production, training, evaluation, script, test, config and vendored source files were compared byte-for-byte against that clean copy. Generated outputs were copied back into the working checkout. The installed CLI was then exercised against the rebuilt model.

Evidence:

- [Clean bootstrap log](../artifacts/clean-bootstrap.log)
- [Clean-build verification manifest](../artifacts/clean-build-verification.json)
- [Test output](../artifacts/pytest.txt)
- [Installed CLI proof](../artifacts/installed-cli-smoke.json)
- [Browser verification and recording](ui-verification.md)
- [Measured model results and limitations](final-report.md)

All synthetic starting positions pass reference validity checks. Dedicated tests verify the dataset content hash and the actual double-check, mate and stalemate properties. Production inference remains independent of the reference oracle.

The software delivery passes its engineering checks; the model remains native-partial. Strict held-out recall is 0%, so training demonstrations and controlled translation results do not establish general chess competence. Missing native conjunction and incomplete automatic induction/history modeling remain explicitly documented.
