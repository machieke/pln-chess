!(import! &self "/data/pln-chess-cycle6-delivery/vendor/pln/lib_pln.metta")

!(println! (C7PROBE mp (Truth_ModusPonens (stv 0.9 0.8) (stv 0.95 0.8))))

!(println! (C7PROBE deduction (Truth_Deduction (stv 0.2 0.8) (stv 0.4 0.8) (stv 0.5 0.8) (stv 0.9 0.8) (stv 0.8 0.8))))

!(println! (C7PROBE induction (Truth_Induction (stv 0.2 0.8) (stv 0.1 0.8) (stv 0.5 0.8) (stv 1.0 0.8) (stv 0.8 0.8))))

!(println! (C7PROBE abduction (Truth_Abduction (stv 0.2 0.8) (stv 0.4 0.8) (stv 0.3 0.8) (stv 0.8 0.8) (stv 0.7 0.8))))

!(println! (C7PROBE revision (Truth_Revision (stv 1.0 0.8) (stv 0.0 0.8))))

!(println! (C7PROBE negation (Truth_Negation (stv 0.9 0.8))))

!(println! (C7PROBE inversion (Truth_inversion (stv 0.4 0.8) (stv 0.9 0.8))))

!(println! (C7PROBE equivalence (Truth_equivalenceToImplication (stv 0.2 0.8) (stv 0.4 0.8) (stv 0.5 0.8))))

!(println! (C7PROBE similarity (Truth_transitiveSimilarity (stv 0.4 0.8) (stv 0.4 0.8) (stv 0.4 0.8) (stv 0.7 0.8) (stv 0.7 0.8))))

!(println! (C7PROBE evaluation (Truth_evaluationImplication (stv 0.4 0.8) (stv 0.2 0.8) (stv 0.5 0.8) (stv 0.9 0.8) (stv 0.8 0.8))))

!(println! (C7PROBE symmetric-mp (Truth_SymmetricModusPonens (stv 0.9 0.8) (stv 0.95 0.8))))

!(println! (C7PROBE choice (let ($tv $e) (BestConfidenceCandidate (((stv 0.9 0.7) (sourceA)) ((stv 0.1 0.8) (sourceB)))) $tv)))
(= (STV A) (stv 0.4 0.8))
(= (STV B) (stv 0.4 0.8))
(= (STV C) (stv 0.4 0.8))
!(println! (C7PROBE inheritance-deduction (collapse (|- ((Inheritance A B) (stv 0.9 0.8)) ((Inheritance B C) (stv 0.8 0.8))))))
(= (STV A) (stv 0.4 0.8))
(= (STV B) (stv 0.4 0.8))
(= (STV C) (stv 0.4 0.8))
!(println! (C7PROBE inheritance-predicate (collapse (|- ((Evaluation (Predicate Eligible) (List (Concept B))) (stv 0.9 0.8)) ((Inheritance (Concept A) (Concept B)) (stv 0.95 0.8))))))
(= (STV A) (stv 0.4 0.8))
(= (STV B) (stv 0.4 0.8))
(= (STV C) (stv 0.4 0.8))
!(println! (C7PROBE equivalence-wrapper (collapse (|- ((Equivalence A B) (stv 0.5 0.8))))))
(= (STV A) (stv 0.4 0.8))
(= (STV B) (stv 0.4 0.8))
(= (STV C) (stv 0.4 0.8))
!(println! (C7PROBE unary-chain (collapse (let ($p $tv) (|- (A (stv 0.9 0.8)) ((Implication A B) (stv 0.95 0.8))) (|- ($p $tv) ((Implication B C) (stv 0.95 0.8)))))))
(= (STV A) (stv 0.4 0.8))
(= (STV B) (stv 0.4 0.8))
(= (STV C) (stv 0.4 0.8))
!(println! (C7PROBE negative-wrapper (collapse (|- ((Not A) (stv 0.9 0.8))))))
(= (STV A) (stv 0.4 0.8))
(= (STV B) (stv 0.4 0.8))
(= (STV C) (stv 0.4 0.8))
!(println! (C7PROBE revision-zero (collapse (Truth_Revision (stv 0.5 0.0) (stv 0.5 0.0)))))
(= (STV A) (stv 0.4 0.8))
(= (STV B) (stv 0.4 0.8))
(= (STV C) (stv 0.4 0.8))
!(println! (C7PROBE revision-one (collapse (Truth_Revision (stv 1.0 1.0) (stv 1.0 0.5)))))
(= (STV A) (stv 0.4 0.8))
(= (STV B) (stv 0.4 0.8))
(= (STV C) (stv 0.4 0.8))
!(println! (C7PROBE mp-zero (Truth_ModusPonens (stv 1.0 0.0) (stv 1.0 1.0))))
(= (STV A) (stv 0.4 0.8))
(= (STV B) (stv 0.4 0.8))
(= (STV C) (stv 0.4 0.8))
!(println! (C7PROBE mp-one (Truth_ModusPonens (stv 1.0 1.0) (stv 1.0 1.0))))
(= (STV A) (stv 0.4 0.8))
(= (STV B) (stv 0.4 0.8))
(= (STV C) (stv 0.4 0.8))
!(println! (C7PROBE choice-zero (BestConfidenceCandidate (((stv 1.0 0.0) (a)) ((stv 0.0 0.0) (b))))))
(= (STV A) (stv 0.4 0.8))
(= (STV B) (stv 0.4 0.8))
(= (STV C) (stv 0.4 0.8))
!(println! (C7PROBE choice-tie (BestConfidenceCandidate (((stv 0.9 0.8) (a)) ((stv 0.1 0.8) (b))))))
(= (STV A) (stv 0.4 0.8))
(= (STV B) (stv 0.4 0.8))
(= (STV C) (stv 0.4 0.8))
!(println! (C7PROBE symmetric-domain-counterexample (Truth_SymmetricModusPonens (stv 0.0 0.8) (stv 1.0 0.8))))
(= (STV A) (stv 0.4 0.8))
(= (STV B) (stv 0.4 0.8))
(= (STV C) (stv 0.4 0.8))
!(println! (C7PROBE stamp-shared (StampDisjoint (a shared) (b shared))))
(= (STV A) (stv 0.4 0.8))
(= (STV B) (stv 0.4 0.8))
(= (STV C) (stv 0.4 0.8))
!(println! (C7PROBE stamp-independent (StampDisjoint (a) (b))))
!(let* (($learn (Truth_Revision (stv 0.5 0.05) (stv 1.0 0.5)))) (progn (println! (RESULT learn $learn))))
!(let* (($learn (Truth_Revision (stv 0.9750000000000001 0.5128205128205129) (stv 1.0 0.5)))) (progn (println! (RESULT learn $learn))))
!(let* (($learn (Truth_Revision (stv 0.9871794871794872 0.6724137931034483) (stv 1.0 0.5)))) (progn (println! (RESULT learn $learn))))
!(let* (($learn (Truth_Revision (stv 0.9913793103448276 0.7532467532467534) (stv 1.0 0.5)))) (progn (println! (RESULT learn $learn))))
!(let* (($learn (Truth_Revision (stv 0.5 0.05) (stv 1.0 0.5)))) (progn (println! (RESULT learn $learn))))
!(let* (($learn (Truth_Revision (stv 0.9750000000000001 0.5128205128205129) (stv 1.0 0.5)))) (progn (println! (RESULT learn $learn))))
!(let* (($learn (Truth_Revision (stv 0.9871794871794872 0.6724137931034483) (stv 1.0 0.5)))) (progn (println! (RESULT learn $learn))))
!(let* (($learn (Truth_Revision (stv 0.9913793103448276 0.7532467532467534) (stv 1.0 0.5)))) (progn (println! (RESULT learn $learn))))

!(println! (C7PROBE nested-implication-A-only (collapse (let ($p $tv) (|- (A (stv 0.9935064935064936 0.8020833333333335)) ((Implication A (Implication B Eligible)) (stv 0.95 0.8))) (|- (B (stv 0.5 0.0)) ($p $tv))))))

!(println! (C7PROBE nested-implication-B-only (collapse (let ($p $tv) (|- (A (stv 0.5 0.0)) ((Implication A (Implication B Eligible)) (stv 0.95 0.8))) (|- (B (stv 0.9935064935064936 0.8020833333333335)) ($p $tv))))))

!(println! (C7PROBE nested-implication-A+B (collapse (let ($p $tv) (|- (A (stv 0.9935064935064936 0.8020833333333335)) ((Implication A (Implication B Eligible)) (stv 0.95 0.8))) (|- (B (stv 0.9935064935064936 0.8020833333333335)) ($p $tv))))))

!(println! (C7PROBE nested-implication-negative-B (collapse (let ($p $tv) (|- (A (stv 0.9935064935064936 0.8020833333333335)) ((Implication A (Implication B Eligible)) (stv 0.95 0.8))) (|- (B (stv 0.0 0.8)) ($p $tv))))))

!(println! (C7PROBE nested-implication-delete-A (collapse (let ($p $tv) (|- (A (stv 0.5 0.0)) ((Implication A (Implication B Eligible)) (stv 0.95 0.8))) (|- (B (stv 0.9935064935064936 0.8020833333333335)) ($p $tv))))))

!(println! (C7PROBE nested-implication-delete-B (collapse (let ($p $tv) (|- (A (stv 0.9935064935064936 0.8020833333333335)) ((Implication A (Implication B Eligible)) (stv 0.95 0.8))) (|- (B (stv 0.5 0.0)) ($p $tv))))))

!(println! (C7PROBE nested-implication-reverse (collapse (let ($p $tv) (|- (A (stv 0.9935064935064936 0.8020833333333335)) ((Implication A (Implication B Eligible)) (stv 0.95 0.8))) (|- (B (stv 0.9935064935064936 0.8020833333333335)) ($p $tv))))))

!(println! (C7PROBE nested-implication-contradict-B (collapse (let ($p $tv) (|- (A (stv 0.9935064935064936 0.8020833333333335)) ((Implication A (Implication B Eligible)) (stv 0.95 0.8))) (|- (B (stv 0.5 0.8)) ($p $tv))))))

!(println! (C7PROBE nested-implication-no-supplied-conditional (collapse (|- (A (stv 0.9935064935064936 0.8020833333333335)) (B (stv 0.9935064935064936 0.8020833333333335))))))

!(println! (C7PROBE nested-implication-premise-reversal (collapse (let ($p $tv) (|- (B (stv 0.9935064935064936 0.8020833333333335)) ((Implication A (Implication B Eligible)) (stv 0.95 0.8))) (|- (A (stv 0.9935064935064936 0.8020833333333335)) ($p $tv))))))

!(println! (C7PROBE nested-implication-correlated-duplicate (collapse (if (StampDisjoint (A shared) (B shared)) (collapse (let ($p $tv) (|- (A (stv 0.9935064935064936 0.8020833333333335)) ((Implication A (Implication B Eligible)) (stv 0.95 0.8))) (|- (B (stv 0.9935064935064936 0.8020833333333335)) ($p $tv)))) (empty)))))

!(println! (C7PROBE nested-implication-duplicate-revision-unguarded (Truth_Revision (stv 0.9935064935064936 0.8020833333333335) (stv 0.9935064935064936 0.8020833333333335))))

!(println! (C7PROBE nested-implication-duplicate-revision-guarded (collapse (if (StampDisjoint (A) (A)) (Truth_Revision (stv 0.9935064935064936 0.8020833333333335) (stv 0.9935064935064936 0.8020833333333335)) (empty)))))

!(println! (C7PROBE product-antecedent-A-only (collapse (let ($p $tv) (|- (A (stv 0.9935064935064936 0.8020833333333335)) (B (stv 0.5 0.0))) (|- ($p $tv) ((Implication (Product A B) Eligible) (stv 0.95 0.8)))))))

!(println! (C7PROBE product-antecedent-B-only (collapse (let ($p $tv) (|- (A (stv 0.5 0.0)) (B (stv 0.9935064935064936 0.8020833333333335))) (|- ($p $tv) ((Implication (Product A B) Eligible) (stv 0.95 0.8)))))))

!(println! (C7PROBE product-antecedent-A+B (collapse (let ($p $tv) (|- (A (stv 0.9935064935064936 0.8020833333333335)) (B (stv 0.9935064935064936 0.8020833333333335))) (|- ($p $tv) ((Implication (Product A B) Eligible) (stv 0.95 0.8)))))))

!(println! (C7PROBE product-antecedent-negative-B (collapse (let ($p $tv) (|- (A (stv 0.9935064935064936 0.8020833333333335)) (B (stv 0.0 0.8))) (|- ($p $tv) ((Implication (Product A B) Eligible) (stv 0.95 0.8)))))))

!(println! (C7PROBE product-antecedent-delete-A (collapse (let ($p $tv) (|- (A (stv 0.5 0.0)) (B (stv 0.9935064935064936 0.8020833333333335))) (|- ($p $tv) ((Implication (Product A B) Eligible) (stv 0.95 0.8)))))))

!(println! (C7PROBE product-antecedent-delete-B (collapse (let ($p $tv) (|- (A (stv 0.9935064935064936 0.8020833333333335)) (B (stv 0.5 0.0))) (|- ($p $tv) ((Implication (Product A B) Eligible) (stv 0.95 0.8)))))))

!(println! (C7PROBE product-antecedent-reverse (collapse (let ($p $tv) (|- (A (stv 0.9935064935064936 0.8020833333333335)) (B (stv 0.9935064935064936 0.8020833333333335))) (|- ($p $tv) ((Implication (Product A B) Eligible) (stv 0.95 0.8)))))))

!(println! (C7PROBE product-antecedent-contradict-B (collapse (let ($p $tv) (|- (A (stv 0.9935064935064936 0.8020833333333335)) (B (stv 0.5 0.8))) (|- ($p $tv) ((Implication (Product A B) Eligible) (stv 0.95 0.8)))))))

!(println! (C7PROBE product-antecedent-host-joint-control (collapse (|- ((Product A B) (stv 0.9935064935064936 0.8020833333333335)) ((Implication (Product A B) Eligible) (stv 0.95 0.8))))))

!(println! (C7PROBE product-antecedent-explicit-And-antecedent (collapse (|- (A (stv 0.9935064935064936 0.8020833333333335)) ((Implication (And A B) Eligible) (stv 0.95 0.8))))))

!(println! (C7PROBE product-antecedent-premise-reversal (collapse (|- (B (stv 0.9935064935064936 0.8020833333333335)) (A (stv 0.9935064935064936 0.8020833333333335))))))

!(println! (C7PROBE product-antecedent-correlated-duplicate (collapse (if (StampDisjoint (A shared) (B shared)) (collapse (let ($p $tv) (|- (A (stv 0.9935064935064936 0.8020833333333335)) (B (stv 0.9935064935064936 0.8020833333333335))) (|- ($p $tv) ((Implication (Product A B) Eligible) (stv 0.95 0.8))))) (empty)))))

!(println! (C7PROBE product-antecedent-duplicate-revision-unguarded (Truth_Revision (stv 0.9935064935064936 0.8020833333333335) (stv 0.9935064935064936 0.8020833333333335))))

!(println! (C7PROBE product-antecedent-duplicate-revision-guarded (collapse (if (StampDisjoint (A) (A)) (Truth_Revision (stv 0.9935064935064936 0.8020833333333335) (stv 0.9935064935064936 0.8020833333333335)) (empty)))))

!(println! (C7PROBE conditional-inheritance-A-only (collapse (|- ((Inheritance (Concept Candidate) (Concept KnightStep)) (stv 0.9935064935064936 0.8020833333333335)) ((Evaluation (Predicate Eligible) (List (Concept OpponentDestination))) (stv 0.5 0.0))))))

!(println! (C7PROBE conditional-inheritance-B-only (collapse (|- ((Inheritance (Concept Candidate) (Concept KnightStep)) (stv 0.5 0.0)) ((Evaluation (Predicate Eligible) (List (Concept OpponentDestination))) (stv 0.9935064935064936 0.8020833333333335))))))

!(println! (C7PROBE conditional-inheritance-A+B (collapse (|- ((Inheritance (Concept Candidate) (Concept KnightStep)) (stv 0.9935064935064936 0.8020833333333335)) ((Evaluation (Predicate Eligible) (List (Concept OpponentDestination))) (stv 0.9935064935064936 0.8020833333333335))))))

!(println! (C7PROBE conditional-inheritance-negative-B (collapse (|- ((Inheritance (Concept Candidate) (Concept KnightStep)) (stv 0.9935064935064936 0.8020833333333335)) ((Evaluation (Predicate Eligible) (List (Concept OpponentDestination))) (stv 0.0 0.8))))))

!(println! (C7PROBE conditional-inheritance-delete-A (collapse (|- ((Inheritance (Concept Candidate) (Concept KnightStep)) (stv 0.5 0.0)) ((Evaluation (Predicate Eligible) (List (Concept OpponentDestination))) (stv 0.9935064935064936 0.8020833333333335))))))

!(println! (C7PROBE conditional-inheritance-delete-B (collapse (|- ((Inheritance (Concept Candidate) (Concept KnightStep)) (stv 0.9935064935064936 0.8020833333333335)) ((Evaluation (Predicate Eligible) (List (Concept OpponentDestination))) (stv 0.5 0.0))))))

!(println! (C7PROBE conditional-inheritance-reverse (collapse (|- ((Inheritance (Concept Candidate) (Concept KnightStep)) (stv 0.9935064935064936 0.8020833333333335)) ((Evaluation (Predicate Eligible) (List (Concept OpponentDestination))) (stv 0.9935064935064936 0.8020833333333335))))))

!(println! (C7PROBE conditional-inheritance-contradict-B (collapse (|- ((Inheritance (Concept Candidate) (Concept KnightStep)) (stv 0.9935064935064936 0.8020833333333335)) ((Evaluation (Predicate Eligible) (List (Concept OpponentDestination))) (stv 0.5 0.8))))))

!(println! (C7PROBE conditional-inheritance-aligned-type-control (collapse (|- ((Evaluation (Predicate Eligible) (List (Concept KnightStep))) (stv 0.9935064935064936 0.8020833333333335)) ((Inheritance (Concept Candidate) (Concept KnightStep)) (stv 0.9935064935064936 0.8020833333333335))))))

!(println! (C7PROBE conditional-inheritance-premise-reversal (collapse (|- ((Evaluation (Predicate Eligible) (List (Concept OpponentDestination))) (stv 0.9935064935064936 0.8020833333333335)) ((Inheritance (Concept Candidate) (Concept KnightStep)) (stv 0.9935064935064936 0.8020833333333335))))))

!(println! (C7PROBE conditional-inheritance-correlated-duplicate (collapse (if (StampDisjoint (A shared) (B shared)) (collapse (|- ((Inheritance (Concept Candidate) (Concept KnightStep)) (stv 0.9935064935064936 0.8020833333333335)) ((Evaluation (Predicate Eligible) (List (Concept OpponentDestination))) (stv 0.9935064935064936 0.8020833333333335)))) (empty)))))

!(println! (C7PROBE conditional-inheritance-duplicate-revision-unguarded (Truth_Revision (stv 0.9935064935064936 0.8020833333333335) (stv 0.9935064935064936 0.8020833333333335))))

!(println! (C7PROBE conditional-inheritance-duplicate-revision-guarded (collapse (if (StampDisjoint (A) (A)) (Truth_Revision (stv 0.9935064935064936 0.8020833333333335) (stv 0.9935064935064936 0.8020833333333335)) (empty)))))