!(import! &self "/data/pln-chess-cycle6-delivery/vendor/pln/lib_pln.metta")

!(println! (C7PROBE nested-implication-premise-reversal (collapse (let ($p $tv) (|- (B (stv 0.9935064935064936 0.8020833333333335)) ((Implication A (Implication B Eligible)) (stv 0.95 0.8))) (|- (A (stv 0.9935064935064936 0.8020833333333335)) ($p $tv))))))
