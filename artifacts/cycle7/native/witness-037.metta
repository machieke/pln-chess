!(import! &self "/data/pln-chess-cycle7-clean-0eab14c/vendor/pln/lib_pln.metta")

!(println! (C7PROBE nested-implication-A+B (collapse (let ($p $tv) (|- (A (stv 0.9935064935064936 0.8020833333333335)) ((Implication A (Implication B Eligible)) (stv 0.95 0.8))) (|- (B (stv 0.9935064935064936 0.8020833333333335)) ($p $tv))))))
