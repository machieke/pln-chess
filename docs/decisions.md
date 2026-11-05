# Engineering decisions

1. Use the maintained TrueAGI MeTTa PLN core, unmodified and pinned, with the already installed compatible SWI-Prolog/PeTTa runtime. The old C++/URE stack is superseded; experimental formula investigations do not provide a verified replacement for missing operators.
2. Keep the audited PLN core vendored with its MIT license. Fetch PeTTa by commit at bootstrap and verify hashes of its Prolog sources and runner on every new bridge. Refuse a runtime version mismatch instead of silently changing semantics.
3. Respect the missing conjunction gate. Ship native categorical conditional inference, independent learned attack frames, and a unary exposure counterevidence chain. Do not relabel a fold of MP, Boolean path test, or host probability multiplication as native conjunction.
4. Retain every bounded candidate, including illegal occupancy, absent rights and board-boundary proposals. Host successor editing is structural and never an acceptance gate. A null out-of-board successor is recorded as structural absence.
5. Preserve raw occupancy sequences rather than adding a hand-calibrated RayClear compound sensor. A joint category is an explicit representation limitation, not a claim of decomposed logical inference.
6. Use separate positive/negative conditional channels and native confidence choice. The channels are correlated, so revising them together would double count evidence. Choice also integrates native exposure counterevidence without a hard king-safety veto.
7. Use conservative first-contribution-per-group revision. It is reproducible and prevents confidence inflation, but does not exploit later correlated conflicts. The ablation quantifies what happens when this policy is disabled.
8. Keep strict structural-family/game held-out tests separate from controlled translations. A translated training motif is a valid invariance test, but not independent structural generalization.
9. Implement a standard-library loopback web inspector in addition to the CLI. It only renders real API outputs; no remote service, account, deployment, or UI chess engine is involved.
10. Provide a reproducible checkout workflow rather than claim a standalone wheel bundles native interpreters. The package can be installed editable; resources are resolved from this checkout or `PLN_CHESS_ROOT`. Bootstrap explicitly checks the exact native system prerequisite.
11. Do not perform commits or push. The original plan remains untouched. Generated evidence/checkpoints/reports make all local changes reviewable.
