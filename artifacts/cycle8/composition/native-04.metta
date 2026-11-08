!(import! &self "/data/pln-chess-cycle8-clean-40548dd/vendor/pln/lib_pln.metta")
!(let* (($learn (Truth_Revision (stv 0.5 0.05) (stv 1.0 0.5)))) (progn (println! (RESULT learn $learn))))
