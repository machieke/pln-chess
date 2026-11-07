!(import! &self "/data/pln-chess-cycle7-clean-0eab14c/vendor/pln/lib_pln.metta")

!(println! (C7PROBE choice (let ($tv $e) (BestConfidenceCandidate (((stv 0.9 0.7) (sourceA)) ((stv 0.1 0.8) (sourceB)))) $tv)))
