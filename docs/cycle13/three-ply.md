# 3-ply supplied relational consequences

The API accepts explicit supplied branches, with at most two branches per candidate and a maximum depth of three. This study uses one offline reference PV per candidate on 60 registered games. The first ten registered test plans produce the ten 3-ply demonstrations below, without selecting them by PLN or reference outcome.

Each transition retains an independent legality belief; each endpoint retains attack, defense, ordinary mobility, king-exposure and concept observations with native proofs. Host differences describe creation/removal and concept persistence/disappearance. The original actor remains fixed across the sequence. History transport records that continuations are hypothetical and unverified; unexamined responses remain unknown.

| Plan | A branch | B branch | Immediate | Continued | Endpoint label |
| --- | --- | --- | --- | --- | --- |
| c13-puzzle-09PBd | d3e2 f1e2 h6e3 | e8c8 b6c8 h6e3 | indeterminate | indeterminate | unknown |
| c13-puzzle-05CIO | e7f8 g8f8 d8e6 | e7f7 f8f7 a1d1 | indeterminate | indeterminate | unknown |
| c13-puzzle-05KTd | d5d2 c3a4 d2c2 | d1h1 c3a4 h1b1 | indeterminate | indeterminate | A |
| c13-puzzle-055TQ | c6c7 b6b1 c7d8 | c6b6 d3c3 b6a5 | indeterminate | indeterminate | B |
| c13-puzzle-097H4 | b2b3 d4c3 a1b1 | d3h7 g8h7 d1d4 | indeterminate | indeterminate | B |
| c13-puzzle-03tiQ | d4d5 f5h6 g3g2 | g3g6 g8h8 h6g5 | B-preferred | B-preferred | B |
| c13-puzzle-03LTp | a7a6 b6a6 d7c6 | a7a4 c6d7 a4a8 | A-preferred | indeterminate | A |
| c13-c10-game-09348683fd05e83c7c8dc30f | f5g4 b4c5 e5e4 | c5b4 a3b4 c6b4 | A-preferred | A-preferred | unknown |
| c13-puzzle-01mWH | e5d5 b2b3 d5e5 | a5a4 g5g4 c5c4 | indeterminate | indeterminate | unknown |
| c13-c10-game-00765e6604066a35d47959c9 | c7e7 c1e1 e8c8 | g6f5 g4f5 c5d3 | indeterminate | indeterminate | unknown |


| Panel | Pairs | Resolved A/B | Answered A/B | Correct | Answered accuracy | Coverage | Abstention-inclusive accuracy |
| --- | --- | --- | --- | --- | --- | --- | --- |
| train | 36 | 20 | 18 | 18 | 1.000 | 0.900 | 0.900 |
| calibration | 12 | 8 | 4 | 1 | 0.250 | 0.500 | 0.125 |
| test | 12 | 5 | 1 | 1 | 1.000 | 0.200 | 0.200 |


No minimax, alpha-beta, tactical search, exhaustive response coverage or scalar rollout evaluation occurs in production. Captured tracked movers and omitted domain members are disclosed; their removed queries are not false relations. Missing required endpoints or exhausted native work produce incomplete results.

The host assembles a categorical packet from independently inferred field and concept records. Native revision learns three separate conditional channels, and native modus ponens applies those channels to the supplied packet. This is a native conditional derivation, not a native conjunction of uncertain fields, a complete strategic theorem, a proof of legality or an optimal move claim. No scalar strategic utility or automatic move selection is implemented.

Evidence: [temporal/demonstrations.json.xz](../../artifacts/cycle13/temporal/demonstrations.json.xz), [temporal/features/index.json](../../artifacts/cycle13/temporal/features/index.json), [datasets/temporal-plans.json](../../artifacts/cycle13/datasets/temporal-plans.json). Each demonstration links its complete endpoint artifact.
