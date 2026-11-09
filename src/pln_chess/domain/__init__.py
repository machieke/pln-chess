"""FEN I/O and structural state changes. No legality decisions."""
from __future__ import annotations
from dataclasses import dataclass, replace
from functools import cached_property
from pln_chess.common import digest

Square = tuple[int, int]
PIECES = {"p":"Pawn", "n":"Knight", "b":"Bishop", "r":"Rook", "q":"Queen", "k":"King"}

def inside(square):
    return all(0 <= n < 8 for n in square)

def square_name(square):
    if not inside(square):
        return f"({square[0]},{square[1]})"
    return chr(97+square[0]) + str(square[1]+1)

def parse_square(value):
    if len(value) != 2 or value[0] not in "abcdefgh" or value[1] not in "12345678":
        raise ValueError(f"Invalid square: {value}")
    return ord(value[0])-97, int(value[1])-1

@dataclass(frozen=True)
class Piece:
    id: str
    kind: str
    owner: str
    square: Square

    def __post_init__(self):
        object.__setattr__(self, 'square', tuple(self.square))

    @cached_property
    def symbol(self):
        letter = next(k for k,v in PIECES.items() if v == self.kind)
        return letter.upper() if self.owner == "White" else letter

@dataclass(frozen=True)
class Move:
    start: Square
    end: Square
    promotion: str | None = None
    effect: str = "ordinary"

    def __post_init__(self):
        object.__setattr__(self, 'start', tuple(self.start))
        object.__setattr__(self, 'end', tuple(self.end))

    @cached_property
    def notation(self):
        return square_name(self.start)+square_name(self.end)+(self.promotion or "")

    @cached_property
    def id(self):
        return "m"+digest([self.start,self.end,self.promotion,self.effect])[:16]

@dataclass(frozen=True)
class Position:
    pieces: tuple[Piece, ...]
    turn: str
    rights: str = "-"
    ep: Square | None = None
    halfmove: int = 0
    fullmove: int = 1
    unknown_squares: tuple[Square, ...] = ()
    history_known: bool = False
    rights_known: bool = True

    def __post_init__(self):
        # Keep frozen state transitively immutable before memoizing its identity.
        object.__setattr__(self, 'pieces', tuple(self.pieces))
        object.__setattr__(self, 'unknown_squares', tuple(tuple(s) for s in self.unknown_squares))
        if self.ep is not None:
            object.__setattr__(self, 'ep', tuple(self.ep))

    @classmethod
    def from_fen(cls, fen, **kwargs):
        fields = fen.split()
        if len(fields) != 6:
            raise ValueError("Expected six FEN fields; unknown history must be supplied explicitly")
        board, turn, rights, ep, half, full = fields
        rows = board.split('/')
        if len(rows) != 8 or turn not in ('w','b') or any(c not in 'KQkq-' for c in rights):
            raise ValueError("Invalid FEN board, turn, or castling rights")
        if rights != '-' and ('-' in rights or len(set(rights)) != len(rights)):
            raise ValueError("Invalid castling rights")
        pieces = []
        for y,row in zip(range(7,-1,-1),rows):
            x=0
            for c in row:
                if c in '12345678':
                    x += int(c)
                elif c.lower() in PIECES:
                    if x >= 8:
                        raise ValueError("FEN rank overflow")
                    pieces.append(Piece(f"p{len(pieces)}",PIECES[c.lower()], 'White' if c.isupper() else 'Black',(x,y)))
                    x += 1
                else:
                    raise ValueError(f"Invalid FEN character {c}")
            if x != 8:
                raise ValueError("Each FEN rank must contain eight cells")
        half,full=int(half),int(full)
        if half < 0 or full < 1:
            raise ValueError("Invalid FEN counters")
        return cls(tuple(pieces),'White' if turn == 'w' else 'Black',rights,
                   None if ep=='-' else parse_square(ep),half,full,**kwargs)

    @cached_property
    def _by_square(self):
        # Preserve the original first-piece behavior even for duplicate squares.
        return {p.square: p for p in reversed(self.pieces)}

    def at(self, square):
        try:
            return self._by_square.get(square)
        except TypeError:
            return next((p for p in self.pieces if p.square == square),None)

    def fen(self):
        return self._fen

    @cached_property
    def _fen(self):
        rows=[]
        for y in range(7,-1,-1):
            row=''; empty=0
            for x in range(8):
                p=self.at((x,y))
                if p:
                    if empty: row+=str(empty); empty=0
                    row+=p.symbol
                else: empty+=1
            if empty: row+=str(empty)
            rows.append(row)
        return ' '.join(('/'.join(rows),'w' if self.turn=='White' else 'b',self.rights or '-',
                         square_name(self.ep) if self.ep else '-',str(self.halfmove),str(self.fullmove)))

    @cached_property
    def id(self):
        return 's'+digest([self.fen(),self.unknown_squares,self.history_known,self.rights_known])[:16]

    def board_text(self):
        return '\n'.join(str(y+1)+' '+' '.join(self.at((x,y)).symbol if self.at((x,y)) else '.' for x in range(8))
                         for y in range(7,-1,-1))+'\n  a b c d e f g h'

    def successor(self, move):
        """Apply a proposed edit, including illegal moves. Never validate chess.

        Castle relocates a boundary rook; EP removes the adjacent pawn cell;
        promotion replaces the moved piece type. Missing pieces are left absent.
        """
        mover=self.at(move.start)
        if mover is None or not inside(move.end):
            return None  # A structural state cannot be formed outside its board.
        removed={move.start,move.end}
        if move.effect=='en-passant':
            removed.add((move.end[0],move.start[1]))
        pieces=[p for p in self.pieces if p.square not in removed]
        promoted=PIECES[move.promotion] if move.promotion else mover.kind
        pieces.append(replace(mover,square=move.end,kind=promoted))
        if move.effect=='castle':
            step=1 if move.end[0]>move.start[0] else -1
            rook_square=(7 if step==1 else 0,move.start[1])
            rook=self.at(rook_square)
            if rook and rook.id != mover.id:
                pieces=[p for p in pieces if p.id != rook.id and p.square != (move.end[0]-step,move.end[1])]
                pieces.append(replace(rook,square=(move.end[0]-step,move.end[1])))
        rights=self.rights.replace('-','')
        # Rights updates are structural history bookkeeping, never an acceptance gate.
        if mover.kind=='King':
            for r in ('KQ' if mover.owner=='White' else 'kq'): rights=rights.replace(r,'')
        for sq,flag in (((0,0),'Q'),((7,0),'K'),((0,7),'q'),((7,7),'k')):
            if sq in (move.start,move.end): rights=rights.replace(flag,'')
        ep=None
        if mover.kind=='Pawn' and abs(move.end[1]-move.start[1])==2:
            ep=(move.start[0],(move.start[1]+move.end[1])//2)
        return replace(self,pieces=tuple(pieces),turn='Black' if self.turn=='White' else 'White',
                       rights=rights or '-',ep=ep,halfmove=0 if mover.kind=='Pawn' or self.at(move.end) else self.halfmove+1,
                       fullmove=self.fullmove+(self.turn=='Black'))
