# Native consequence results

Each of 1,256 episode and model pairs received two separate native queries over the same facts and rules. The 2,512 queries comprise 1,792 natural queries, 648 occupancy or withholding queries and 72 representation queries. The answer and contrary channels retain their native strength, confidence and stamps.

A training arm fits clearance first and terminal influence second. D-AB uses group A for clearance and B for influence. D-BA reverses the assignment. S-AA and S-BB reuse the same group for both. H uses the frozen Cycle 17 S-AA generation. F uses supplied parameters. P starts both learned rules at their prior.

| Population | Split | Arm | Target | Games | Queries | Ref + / − / unresolved | Support + / − / unknown | Conflict / incomplete | FP / explicit FN | Precision | Recall | Coverage |
|---|---|---|---|---:|---:|---|---|---|---|---:|---:|---:|
| natural-development | development | D-AB | Attack | 24 | 24 | 7 / 17 / 0 | 7 / 17 / 0 | 0 / 0 | 0 / 0 | 100.0% | 100.0% | 100.0% |
| natural-development | development | D-AB | Clear | 24 | 24 | 7 / 17 / 0 | 7 / 0 / 17 | 0 / 0 | 0 / 0 | 100.0% | 100.0% | 29.2% |
| natural-development | development | D-BA | Attack | 24 | 24 | 7 / 17 / 0 | 7 / 17 / 0 | 0 / 0 | 0 / 0 | 100.0% | 100.0% | 100.0% |
| natural-development | development | D-BA | Clear | 24 | 24 | 7 / 17 / 0 | 7 / 0 / 17 | 0 / 0 | 0 / 0 | 100.0% | 100.0% | 29.2% |
| natural-development | development | F | Attack | 24 | 24 | 7 / 17 / 0 | 7 / 17 / 0 | 0 / 0 | 0 / 0 | 100.0% | 100.0% | 100.0% |
| natural-development | development | F | Clear | 24 | 24 | 7 / 17 / 0 | 7 / 0 / 17 | 0 / 0 | 0 / 0 | 100.0% | 100.0% | 29.2% |
| natural-development | development | H | Attack | 24 | 24 | 7 / 17 / 0 | 0 / 17 / 7 | 0 / 0 | 0 / 0 | undefined | 0.0% | 70.8% |
| natural-development | development | H | Clear | 24 | 24 | 7 / 17 / 0 | 7 / 0 / 17 | 0 / 0 | 0 / 0 | 100.0% | 100.0% | 29.2% |
| natural-development | development | P | Attack | 24 | 24 | 7 / 17 / 0 | 0 / 17 / 7 | 0 / 0 | 0 / 0 | undefined | 0.0% | 70.8% |
| natural-development | development | P | Clear | 24 | 24 | 7 / 17 / 0 | 0 / 0 / 24 | 0 / 0 | 0 / 0 | undefined | 0.0% | 0.0% |
| natural-development | development | S-AA | Attack | 24 | 24 | 7 / 17 / 0 | 0 / 17 / 7 | 0 / 0 | 0 / 0 | undefined | 0.0% | 70.8% |
| natural-development | development | S-AA | Clear | 24 | 24 | 7 / 17 / 0 | 7 / 0 / 17 | 0 / 0 | 0 / 0 | 100.0% | 100.0% | 29.2% |
| natural-development | development | S-BB | Attack | 24 | 24 | 7 / 17 / 0 | 0 / 17 / 7 | 0 / 0 | 0 / 0 | undefined | 0.0% | 70.8% |
| natural-development | development | S-BB | Clear | 24 | 24 | 7 / 17 / 0 | 7 / 0 / 17 | 0 / 0 | 0 / 0 | 100.0% | 100.0% | 29.2% |
| natural-test | test | D-AB | Attack | 56 | 56 | 30 / 26 / 0 | 30 / 26 / 0 | 0 / 0 | 0 / 0 | 100.0% | 100.0% | 100.0% |
| natural-test | test | D-AB | Clear | 56 | 56 | 30 / 26 / 0 | 30 / 0 / 26 | 0 / 0 | 0 / 0 | 100.0% | 100.0% | 53.6% |
| natural-test | test | D-BA | Attack | 56 | 56 | 30 / 26 / 0 | 30 / 26 / 0 | 0 / 0 | 0 / 0 | 100.0% | 100.0% | 100.0% |
| natural-test | test | D-BA | Clear | 56 | 56 | 30 / 26 / 0 | 30 / 0 / 26 | 0 / 0 | 0 / 0 | 100.0% | 100.0% | 53.6% |
| natural-test | test | F | Attack | 56 | 56 | 30 / 26 / 0 | 30 / 26 / 0 | 0 / 0 | 0 / 0 | 100.0% | 100.0% | 100.0% |
| natural-test | test | F | Clear | 56 | 56 | 30 / 26 / 0 | 30 / 0 / 26 | 0 / 0 | 0 / 0 | 100.0% | 100.0% | 53.6% |
| natural-test | test | H | Attack | 56 | 56 | 30 / 26 / 0 | 0 / 26 / 30 | 0 / 0 | 0 / 0 | undefined | 0.0% | 46.4% |
| natural-test | test | H | Clear | 56 | 56 | 30 / 26 / 0 | 30 / 0 / 26 | 0 / 0 | 0 / 0 | 100.0% | 100.0% | 53.6% |
| natural-test | test | P | Attack | 56 | 56 | 30 / 26 / 0 | 0 / 26 / 30 | 0 / 0 | 0 / 0 | undefined | 0.0% | 46.4% |
| natural-test | test | P | Clear | 56 | 56 | 30 / 26 / 0 | 0 / 0 / 56 | 0 / 0 | 0 / 0 | undefined | 0.0% | 0.0% |
| natural-test | test | S-AA | Attack | 56 | 56 | 30 / 26 / 0 | 0 / 26 / 30 | 0 / 0 | 0 / 0 | undefined | 0.0% | 46.4% |
| natural-test | test | S-AA | Clear | 56 | 56 | 30 / 26 / 0 | 30 / 0 / 26 | 0 / 0 | 0 / 0 | 100.0% | 100.0% | 53.6% |
| natural-test | test | S-BB | Attack | 56 | 56 | 30 / 26 / 0 | 0 / 26 / 30 | 0 / 0 | 0 / 0 | undefined | 0.0% | 46.4% |
| natural-test | test | S-BB | Clear | 56 | 56 | 30 / 26 / 0 | 30 / 0 / 26 | 0 / 0 | 0 / 0 | 100.0% | 100.0% | 53.6% |
| natural-training | A | D-AB | Attack | 24 | 24 | 24 / 0 / 0 | 24 / 0 / 0 | 0 / 0 | 0 / 0 | 100.0% | 100.0% | 100.0% |
| natural-training | A | D-AB | Clear | 24 | 24 | 24 / 0 / 0 | 24 / 0 / 0 | 0 / 0 | 0 / 0 | 100.0% | 100.0% | 100.0% |
| natural-training | A | D-BA | Attack | 24 | 24 | 24 / 0 / 0 | 24 / 0 / 0 | 0 / 0 | 0 / 0 | 100.0% | 100.0% | 100.0% |
| natural-training | A | D-BA | Clear | 24 | 24 | 24 / 0 / 0 | 24 / 0 / 0 | 0 / 0 | 0 / 0 | 100.0% | 100.0% | 100.0% |
| natural-training | A | F | Attack | 24 | 24 | 24 / 0 / 0 | 24 / 0 / 0 | 0 / 0 | 0 / 0 | 100.0% | 100.0% | 100.0% |
| natural-training | A | F | Clear | 24 | 24 | 24 / 0 / 0 | 24 / 0 / 0 | 0 / 0 | 0 / 0 | 100.0% | 100.0% | 100.0% |
| natural-training | A | H | Attack | 24 | 24 | 24 / 0 / 0 | 0 / 0 / 24 | 0 / 0 | 0 / 0 | undefined | 0.0% | 0.0% |
| natural-training | A | H | Clear | 24 | 24 | 24 / 0 / 0 | 24 / 0 / 0 | 0 / 0 | 0 / 0 | 100.0% | 100.0% | 100.0% |
| natural-training | A | P | Attack | 24 | 24 | 24 / 0 / 0 | 0 / 0 / 24 | 0 / 0 | 0 / 0 | undefined | 0.0% | 0.0% |
| natural-training | A | P | Clear | 24 | 24 | 24 / 0 / 0 | 0 / 0 / 24 | 0 / 0 | 0 / 0 | undefined | 0.0% | 0.0% |
| natural-training | A | S-AA | Attack | 24 | 24 | 24 / 0 / 0 | 0 / 0 / 24 | 0 / 0 | 0 / 0 | undefined | 0.0% | 0.0% |
| natural-training | A | S-AA | Clear | 24 | 24 | 24 / 0 / 0 | 24 / 0 / 0 | 0 / 0 | 0 / 0 | 100.0% | 100.0% | 100.0% |
| natural-training | A | S-BB | Attack | 24 | 24 | 24 / 0 / 0 | 0 / 0 / 24 | 0 / 0 | 0 / 0 | undefined | 0.0% | 0.0% |
| natural-training | A | S-BB | Clear | 24 | 24 | 24 / 0 / 0 | 24 / 0 / 0 | 0 / 0 | 0 / 0 | 100.0% | 100.0% | 100.0% |
| natural-training | B | D-AB | Attack | 24 | 24 | 24 / 0 / 0 | 24 / 0 / 0 | 0 / 0 | 0 / 0 | 100.0% | 100.0% | 100.0% |
| natural-training | B | D-AB | Clear | 24 | 24 | 24 / 0 / 0 | 24 / 0 / 0 | 0 / 0 | 0 / 0 | 100.0% | 100.0% | 100.0% |
| natural-training | B | D-BA | Attack | 24 | 24 | 24 / 0 / 0 | 24 / 0 / 0 | 0 / 0 | 0 / 0 | 100.0% | 100.0% | 100.0% |
| natural-training | B | D-BA | Clear | 24 | 24 | 24 / 0 / 0 | 24 / 0 / 0 | 0 / 0 | 0 / 0 | 100.0% | 100.0% | 100.0% |
| natural-training | B | F | Attack | 24 | 24 | 24 / 0 / 0 | 24 / 0 / 0 | 0 / 0 | 0 / 0 | 100.0% | 100.0% | 100.0% |
| natural-training | B | F | Clear | 24 | 24 | 24 / 0 / 0 | 24 / 0 / 0 | 0 / 0 | 0 / 0 | 100.0% | 100.0% | 100.0% |
| natural-training | B | H | Attack | 24 | 24 | 24 / 0 / 0 | 0 / 0 / 24 | 0 / 0 | 0 / 0 | undefined | 0.0% | 0.0% |
| natural-training | B | H | Clear | 24 | 24 | 24 / 0 / 0 | 24 / 0 / 0 | 0 / 0 | 0 / 0 | 100.0% | 100.0% | 100.0% |
| natural-training | B | P | Attack | 24 | 24 | 24 / 0 / 0 | 0 / 0 / 24 | 0 / 0 | 0 / 0 | undefined | 0.0% | 0.0% |
| natural-training | B | P | Clear | 24 | 24 | 24 / 0 / 0 | 0 / 0 / 24 | 0 / 0 | 0 / 0 | undefined | 0.0% | 0.0% |
| natural-training | B | S-AA | Attack | 24 | 24 | 24 / 0 / 0 | 0 / 0 / 24 | 0 / 0 | 0 / 0 | undefined | 0.0% | 0.0% |
| natural-training | B | S-AA | Clear | 24 | 24 | 24 / 0 / 0 | 24 / 0 / 0 | 0 / 0 | 0 / 0 | 100.0% | 100.0% | 100.0% |
| natural-training | B | S-BB | Attack | 24 | 24 | 24 / 0 / 0 | 0 / 0 / 24 | 0 / 0 | 0 / 0 | undefined | 0.0% | 0.0% |
| natural-training | B | S-BB | Clear | 24 | 24 | 24 / 0 / 0 | 24 / 0 / 0 | 0 / 0 | 0 / 0 | 100.0% | 100.0% | 100.0% |
| occupancy-intervention | diagnostic | D-AB | Attack | 12 | 48 | 12 / 36 / 0 | 12 / 36 / 0 | 0 / 0 | 0 / 0 | 100.0% | 100.0% | 100.0% |
| occupancy-intervention | diagnostic | D-AB | Clear | 12 | 48 | 12 / 36 / 0 | 12 / 0 / 36 | 0 / 0 | 0 / 0 | 100.0% | 100.0% | 25.0% |
| occupancy-intervention | diagnostic | F | Attack | 12 | 48 | 12 / 36 / 0 | 12 / 36 / 0 | 0 / 0 | 0 / 0 | 100.0% | 100.0% | 100.0% |
| occupancy-intervention | diagnostic | F | Clear | 12 | 48 | 12 / 36 / 0 | 12 / 0 / 36 | 0 / 0 | 0 / 0 | 100.0% | 100.0% | 25.0% |
| occupancy-intervention | diagnostic | S-AA | Attack | 12 | 48 | 12 / 36 / 0 | 0 / 36 / 12 | 0 / 0 | 0 / 0 | undefined | 0.0% | 75.0% |
| occupancy-intervention | diagnostic | S-AA | Clear | 12 | 48 | 12 / 36 / 0 | 12 / 0 / 36 | 0 / 0 | 0 / 0 | 100.0% | 100.0% | 25.0% |
| representation-transform | diagnostic | D-AB | Attack | 12 | 36 | 21 / 15 / 0 | 21 / 15 / 0 | 0 / 0 | 0 / 0 | 100.0% | 100.0% | 100.0% |
| representation-transform | diagnostic | D-AB | Clear | 12 | 36 | 21 / 15 / 0 | 21 / 0 / 15 | 0 / 0 | 0 / 0 | 100.0% | 100.0% | 58.3% |
| withheld-observations | diagnostic | D-AB | Attack | 12 | 60 | 26 / 34 / 0 | 0 / 24 / 36 | 0 / 0 | 0 / 0 | undefined | 0.0% | 40.0% |
| withheld-observations | diagnostic | D-AB | Clear | 12 | 60 | 26 / 34 / 0 | 0 / 0 / 60 | 0 / 0 | 0 / 0 | undefined | 0.0% | 0.0% |
| withheld-observations | diagnostic | F | Attack | 12 | 60 | 26 / 34 / 0 | 0 / 24 / 36 | 0 / 0 | 0 / 0 | undefined | 0.0% | 40.0% |
| withheld-observations | diagnostic | F | Clear | 12 | 60 | 26 / 34 / 0 | 0 / 0 / 60 | 0 / 0 | 0 / 0 | undefined | 0.0% | 0.0% |
| withheld-observations | diagnostic | S-AA | Attack | 12 | 60 | 26 / 34 / 0 | 0 / 24 / 36 | 0 / 0 | 0 / 0 | undefined | 0.0% | 40.0% |
| withheld-observations | diagnostic | S-AA | Clear | 12 | 60 | 26 / 34 / 0 | 0 / 0 / 60 | 0 / 0 | 0 / 0 | undefined | 0.0% | 0.0% |

All four new arms fitted each conditional from 24 qualified observations. Both conditionals reached strength 1 and confidence 0.960 through native revision. The prior retained strength 0.5 and confidence 0. Each training group contained only antecedent-qualified positives. Each arm included 48 target-specific annotations. Disjoint arms retained 48 game identities across the two conditionals, and shared arms retained 24. The four primary native fits used 192 revisions across 96 distinct measured annotations.

The denominator for precision is supported positive predictions with resolved reference truth. Recall uses all reference positives. An unknown outcome on a reference positive reduces recall. An explicit false negative requires supported NoAttack on a reference-positive case. Coverage uses all queries in the registered population. Each row retains conflict, unresolved, incomplete, and disagreement counts.

Machine-readable rows include the reference and scoring denominators, native TV observations, Wilson intervals for natural game-level proportions, and deterministic root-cluster bootstrap intervals for dependent-variant coverage. Wilson intervals assume exchangeability. Shared engines and openings constrain extrapolation, and the 12 diagnostic roots limit the bootstrap. [Metrics and proof references](../../artifacts/cycle19/native-results.json)

The first natural positive uses two separately measured conditionals. The supplied or disjoint chain supports both stages. Shared training ancestry permits clearance support but blocks positive terminal composition. On blocked rays, the supplied obstruction rule can derive the explicit contrary even under the prior. The encoding provides no negative Clear channel. Withheld evidence can leave an answer unknown even when the hidden reference occupancy is resolved.

A complete bounded search can still return unknown. The native program exposes selected and retained statements. The evidence journal separately records input dependencies. Each compact demonstration links both stage proofs and their original facts, complete templates, answers, contrary channels and execution receipts. [Demonstrations](../../artifacts/cycle19/demonstrations/index.json)
