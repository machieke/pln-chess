!(import! &self "/data/pln-chess-cycle6-delivery/vendor/pln/lib_pln.metta")

!(println! (C7PROBE nested-implication-correlated-duplicate (collapse (if (StampDisjoint (A shared) (B shared)) (collapse (let ($p $tv) (|- (A (stv 0.9935064935064936 0.8020833333333335)) ((Implication A (Implication B Eligible)) (stv 0.95 0.8))) (|- (B (stv 0.9935064935064936 0.8020833333333335)) ($p $tv)))) (empty)))))
