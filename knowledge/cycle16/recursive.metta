; Declarative domain templates only. These are parsed as data, never definitions
; of native inference operators. Stable rule stamps survive every firing.
(Rule empty-tail (Implication (State $s) (PathEmpty Nil $s)))
(Rule extend-empty (Implication (Empty $c $s) (Implication (PathEmpty $tail $s) (PathEmpty (Cons $c $tail) $s))))
(Rule clear-path (Implication (RayPath $a $t $path $shape $s) (Implication (PathEmpty $path $s) (Clear $a $t $shape $s))))
(Rule clear-one (Implication (RayPath $a $t (Cons $c Nil) $shape $s) (Implication (Empty $c $s) (Clear $a $t $shape $s))))
(Rule rook-attack (Implication (PieceKind $a rook $s) (Implication (Clear $a $t orthogonal $s) (Attack $a $t $s))))
(Rule bishop-attack (Implication (PieceKind $a bishop $s) (Implication (Clear $a $t diagonal $s) (Attack $a $t $s))))
(Rule queen-orthogonal (Implication (PieceKind $a queen $s) (Implication (Clear $a $t orthogonal $s) (Attack $a $t $s))))
(Rule queen-diagonal (Implication (PieceKind $a queen $s) (Implication (Clear $a $t diagonal $s) (Attack $a $t $s))))
(Rule obstruction (Implication (RayMember $a $t $c $s) (Implication (Occupied $c $s) (NoAttack $a $t $s))))
(Rule exposure-white (Implication (OriginalActor $s white) (Implication (Owner $a black $s) (Implication (Owner $t white $s) (Implication (PieceKind $t king $s) (Implication (Attack $a $t $s) (KingExposed $t white $s)))))))
(Rule exposure-black (Implication (OriginalActor $s black) (Implication (Owner $a white $s) (Implication (Owner $t black $s) (Implication (PieceKind $t king $s) (Implication (Attack $a $t $s) (KingExposed $t black $s)))))))
