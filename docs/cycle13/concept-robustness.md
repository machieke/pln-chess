# Independent tactical concept robustness

The external panel contains 96 positions from 96 games and 96 raw structural families, disjoint from preference games and original concept training motifs. Each of eight concept families has eight positive and four negative reference examples. Selection and counterfactual construction are disclosed in the dataset; structural source labels do not prove complete tactical understanding.

| Family | Cases | TP | TN | FP | FN | Abstained |
| --- | --- | --- | --- | --- | --- | --- |
| DiscoveredAttack | 12 | 4 | 1 | 0 | 0 | 7 |
| DiscoveredDefense | 12 | 6 | 0 | 0 | 0 | 6 |
| Fork | 12 | 8 | 0 | 0 | 0 | 4 |
| MultipleAttackers | 12 | 0 | 0 | 0 | 0 | 12 |
| OverloadedDefender | 12 | 0 | 0 | 0 | 0 | 12 |
| Pin | 12 | 8 | 0 | 0 | 0 | 4 |
| ThreatRemoval | 12 | 0 | 0 | 0 | 0 | 12 |
| TrappedPiece | 12 | 1 | 0 | 0 | 0 | 11 |


All 312 dependent transformation and target controls pass. The 48-case generic-fork evaluation tests the new abstraction without the legacy fallback: 20 true positives, 24 true negatives, four abstentions and no incorrect classified answer. That panel includes dependent controls and is not 48 independent games. All 370 legacy native proofs and all previously correct classifications are preserved.

Multiple attackers, overloaded defenders and threat removal remain entirely unanswered on this external panel. Candidate enumeration is bounded and host-side. The system must disclose omitted candidates and unknown relations rather than treat them as negatives. The host assembles a categorical packet from independently inferred field and concept records. Native revision learns three separate conditional channels, and native modus ponens applies those channels to the supplied packet. This is a native conditional derivation, not a native conjunction of uncertain fields, a complete strategic theorem, a proof of legality or an optimal move claim. No scalar strategic utility or automatic move selection is implemented.

Evidence: [concepts/summary.json](../../artifacts/cycle13/concepts/summary.json), [concepts/external.json.xz](../../artifacts/cycle13/concepts/external.json.xz), [concepts/external-controls.json.xz](../../artifacts/cycle13/concepts/external-controls.json.xz), [datasets/external-concepts.json](../../artifacts/cycle13/datasets/external-concepts.json).
