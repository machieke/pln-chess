# Native PLN feasibility

Production stays pinned to PLN `4405956947c4b53c7ff01bd565aa3b114bc970a1` and PeTTa `ee5cacb6a6ecdd554a1c773aaf47e9a0f8a5af0f`; dependency verification uses the existing source hashes and exact SWI version. No custom native connective was added.

Run `.venv/bin/pln-chess cycle2 --action audit`. The executable corpus and actual outputs are in `artifacts/cycle2/native-probes.json` and `.metta`. Each formula entry records its upstream source line. The original `|-` regression corpus continues to execute as well.

| Capability | Use and boundary |
|---|---|
| `Truth_Revision` | Production finite-evidence belief updates; confidence-one revision yields no result |
| `Truth_ModusPonens` | Production conditional grounding and learned attack/exposure chaining |
| `Truth_Negation` | Production negative-channel conversion, retaining native confidence |
| `BestConfidenceCandidate` | Native alternative selection, not conjunction or evidence fusion; zero-confidence-only input has no result |
| `Truth_w2c` | Experimental induction confidence from measured representative count |
| `Truth_Induction` | Integrated opt-in B2 learner with recorded marginals and inference premises |
| `|-` inheritance induction | Executable but unsafe to assume standard parameter roles; see below |
| Deduction, inversion, abduction, equivalence, similarity | Formula probes execute, experimental only; domains/marginals matter |
| Stamp disjointness | Executable overlap/disjoint probes; production uses stricter per-hypothesis group bookkeeping |
| Unary conditional chaining | Executable; cannot prove an AND of independently evidenced observations |
| Conjunction introduction/elimination, conditionalization | Candidate rule-layer probes return no derivation in this core |

The source's `Truth_Induction` parameters are target A, common class B, outcome C. The `|-` inheritance wrapper for C→A and C→B passes `(STV A), (STV B), (STV C)` in that order; non-symmetric marginals expose the mismatch between wrapper naming and formula roles. Cycle 2 therefore invokes the verified truth function directly with explicit semantic roles. This is not a fabricated formula or silent use of the mismatched wrapper.

Source inspection plus isolated executable probes cover pinned main and `pln0.9` (`faa3f39697480c2eab6ced183792f8e74a20da31`); their core files are byte-identical and return no conjunction. `PLN_v0.6` and `Modularity` were inspected at recorded SHAs but have different module layouts, so no drop-in compatibility is claimed. See `artifacts/cycle2/upstream-audit.json`. This bounded investigation does not establish absence from every upstream repository. No alternate runtime is enabled.

The minimal missing upstream capability is a maintained, tested multi-premise rule with explicit dependence and joint-distribution assumptions. Chaining unary implications, grouping sensor fields, or interpreting confidence choice as logical AND does not supply it. Until then, local conditionals plus separate exposure evidence provide native-partial generalization.

Primary sources: [pinned native core](https://github.com/trueagi-io/PLN/blob/4405956947c4b53c7ff01bd565aa3b114bc970a1/lib_pln.metta), [maintained upstream repository](https://github.com/trueagi-io/PLN). All scientific conclusions above are backed by the locally executed probes, rather than inferred from repository descriptions.
