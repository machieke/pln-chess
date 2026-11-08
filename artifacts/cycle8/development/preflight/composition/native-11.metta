!(import! &self "/data/pln-chess-cycle6-delivery/vendor/pln/lib_pln.metta")

!(println! (C7PROBE shared-evidence (PLN.Query ((Sentence (A (stv 0.9935064935064936 0.8020833333333335)) (shared)) (Sentence (B (stv 0.9935064935064936 0.8020833333333335)) (shared)) (Sentence ((Implication A (Implication B C)) (stv 0.95 0.8)) (supplied-rule))) C 12 30 60)))
