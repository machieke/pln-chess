"""Offline UCI evidence with record-local bounds and original-actor perspective.

No production module imports this adapter. Search scores label research only.
"""
import queue
import subprocess
import threading
import time

import chess

from pln_chess.common import digest


def parse_info(line, *, side_to_move, actor):
    """Parse one independent UCI record; never retain fields from older records."""
    words=line.split()
    if not words or words[0]!='info' or 'score' not in words or 'pv' not in words:return None
    try:
        start=words.index('score');kind=words[start+1];value=int(words[start+2])
        if kind not in ('cp','mate'):return None
        bound='lower' if 'lowerbound' in words else 'upper' if 'upperbound' in words else 'unflagged'
        if 'lowerbound' in words and 'upperbound' in words:raise ValueError('Conflicting bound flags')
        sign=1 if side_to_move==actor else -1
        outcome=None if kind=='cp' else ('win' if value>0 else 'loss')
        if sign<0:
            bound={'lower':'upper','upper':'lower','unflagged':'unflagged'}[bound]
            if outcome is not None:outcome='loss' if outcome=='win' else 'win'
        numeric={}
        for key in ('depth','seldepth','nodes','time','multipv'):
            numeric[key]=int(words[words.index(key)+1]) if key in words else None
        pv=words[words.index('pv')+1:]
        if not pv:return None
        return dict(score=dict(kind=kind,value=sign*value,mate_outcome=outcome,bound=bound),
            raw_score=dict(kind=kind,value=value,bound='lower' if 'lowerbound' in words else 'upper' if 'upperbound' in words else 'unflagged'),
            actor='White' if actor else 'Black',side_to_move='White' if side_to_move else 'Black',
            perspective_reversed=sign<0,pv=pv,candidate=pv[0],**numeric)
    except (ValueError,IndexError) as error:
        raise ValueError('Malformed score-bearing UCI info record: '+line) from error


def ordinary_interval(score):
    if score['kind']!='cp':raise ValueError('Mate values cannot become centipawn intervals')
    value=score['value'];bound=score['bound']
    return (value if bound!='upper' else None,value if bound!='lower' else None)


def direction(a,b,margin=80):
    """Operational reference comparison, not a probability or native calculus."""
    if a['kind']==b['kind']=='cp':
        lo_a,hi_a=ordinary_interval(a);lo_b,hi_b=ordinary_interval(b)
        if lo_a is not None and hi_b is not None and lo_a-hi_b>=margin:return 'A'
        if lo_b is not None and hi_a is not None and lo_b-hi_a>=margin:return 'B'
        return None
    if a['bound']!='unflagged' or b['bound']!='unflagged':return None
    def category(score):
        return 0 if score['kind']=='cp' else 1 if score['mate_outcome']=='win' else -1
    first,second=category(a),category(b)
    if first!=second:return 'A' if first>second else 'B'
    if a['value']==b['value']:return None
    return 'A' if a['value']<b['value'] else 'B'


def classify_tier(evaluations, margin=80, nondirectional_margin=20):
    """Require the same registered operational result at both budgets."""
    if len(evaluations)!=2:return 'unknown','missing-budget-analysis'
    directions=[];near=[]
    for evaluation in evaluations:
        candidates=evaluation.get('candidates',{})
        if set(candidates)!={'A','B'} or any(candidates[k] is None for k in ('A','B')):
            return 'unknown','missing-candidate-analysis'
        if evaluation.get('termination')!='completed':return 'unknown','interrupted-search'
        if not evaluation.get('history_verified',False):return 'unknown','history-or-perspective-mismatch'
        a,b=(candidates[k]['score'] for k in ('A','B'))
        directions.append(direction(a,b,margin))
        near.append(a['kind']==b['kind']=='cp' and a['bound']==b['bound']=='unflagged'
            and abs(a['value']-b['value'])<=nondirectional_margin)
    if directions[0] is not None and directions[0]==directions[1]:
        return directions[0],'stable-operational-direction'
    if all(near):return 'no-demonstrated-preference','stable-no-demonstrated-direction'
    if any(d is not None for d in directions) and directions[0]!=directions[1]:return 'unknown','budget-disagreement'
    scores=[c['score'] for e in evaluations for c in e['candidates'].values()]
    if any(s['bound']!='unflagged' for s in scores):return 'unknown','overlapping-or-one-sided-bounds'
    if any(s['kind']=='mate' for s in scores):return 'unknown','mate-order-ambiguity'
    return 'unknown','insufficient-margin'


def board_from_history(history, expected_fen=None):
    board=chess.Board(history['initial_fen'])
    if not board.is_valid():raise ValueError('Invalid initial reference position')
    for notation in history['moves']:
        move=chess.Move.from_uci(notation)
        if move not in board.legal_moves:raise ValueError('Illegal supplied reference history')
        board.push(move)
    if expected_fen is not None and board.fen(en_passant='fen')!=expected_fen:
        raise ValueError('Reference history does not reconstruct the requested root')
    return board


class RawEngine:
    """One pinned teacher process; every search has explicit reset and transcript."""
    def __init__(self,binary,*,threads=1,hash_mib=32,timeout=120):
        self.timeout=timeout;self.transcript=[];self.lines=queue.Queue()
        self.process=subprocess.Popen([str(binary)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,text=True,bufsize=1)
        def reader():
            try:
                for line in self.process.stdout:self.lines.put(line.rstrip('\r\n'))
            finally:self.lines.put(None)
        self.reader=threading.Thread(target=reader,daemon=True);self.reader.start()
        try:
            self.send('uci');self.until('uciok')
            self.options=dict(Threads=threads,Hash=hash_mib,UCI_ShowWDL='true',MultiPV=1)
            for name,value in self.options.items():self.send(f'setoption name {name} value {value}')
            self.send('isready');self.until('readyok')
            self.initialization=list(self.transcript)
        except BaseException:
            self.close();raise

    def send(self,line):
        if '\n' in line or '\r' in line:raise ValueError('UCI command must be one line')
        self.transcript.append(dict(direction='sent',line=line))
        self.process.stdin.write(line+'\n');self.process.stdin.flush()

    def until(self,prefix,timeout=None):
        deadline=time.monotonic()+(self.timeout if timeout is None else timeout);received=[]
        while True:
            remaining=deadline-time.monotonic()
            if remaining<=0:raise TimeoutError('UCI did not return '+prefix)
            try:line=self.lines.get(timeout=remaining)
            except queue.Empty as error:raise TimeoutError('UCI did not return '+prefix) from error
            if line is None:raise RuntimeError('Reference engine terminated before '+prefix)
            self.transcript.append(dict(direction='received',line=line));received.append(line)
            if line==prefix or line.startswith(prefix+' '):return received

    def analyze(self,history,*,roots,nodes,actor,expected_fen=None,multipv=1):
        board=board_from_history(history,expected_fen)
        if type(nodes) is not int or nodes<=0:raise ValueError('Positive registered node budget required')
        if not roots or len(set(roots))!=len(roots):raise ValueError('Explicit distinct candidate roots required')
        for notation in roots:
            if chess.Move.from_uci(notation) not in board.legal_moves:raise ValueError('Illegal candidate root')
        began=time.perf_counter();offset=len(self.transcript)
        self.send(f'setoption name MultiPV value {multipv}')
        self.send('ucinewgame');self.send('setoption name Clear Hash');self.send('isready');self.until('readyok')
        command='position fen '+history['initial_fen']
        if history['moves']:command+=' moves '+' '.join(history['moves'])
        self.send(command);self.send('go nodes '+str(nodes)+' searchmoves '+' '.join(sorted(roots)))
        termination='completed'
        try:lines=self.until('bestmove')
        except TimeoutError:
            termination='interrupted';self.send('stop');lines=self.until('bestmove',timeout=10)
        raw=self.transcript[offset:];iterations=[];latest={};completed={}
        for event in raw:
            if event['direction']!='received':continue
            info=parse_info(event['line'],side_to_move=board.turn,actor=actor)
            if info is None:continue
            check=board.copy()
            try:
                for notation in info['pv']:
                    move=chess.Move.from_uci(notation)
                    if move not in check.legal_moves:raise ValueError('Illegal teacher PV')
                    check.push(move)
            except ValueError as error:
                raise ValueError('Reference PV does not replay legally') from error
            if info['candidate'] not in roots:raise ValueError('Teacher ignored candidate restriction')
            iterations.append(info);latest[info['candidate']]=info
            if info['score']['bound']=='unflagged':completed[info['candidate']]=info.get('depth')
        best=next((line.split()[1] for line in reversed(lines) if line.startswith('bestmove ')),None)
        if best not in roots:termination='missing-or-inconsistent-candidate'
        return dict(schema='c14-raw-search-v1',root_fen=board.fen(en_passant='fen'),
            root_identity=digest([history,board.fen(en_passant='fen')]),history=history,
            original_actor='White' if actor else 'Black',root_turn='White' if board.turn else 'Black',
            requested_roots=list(roots),node_budget=nodes,multipv=multipv,termination=termination,
            bestmove=best,candidates=latest,completed_unflagged_depths=completed,iterations=iterations,
            actual_reported_nodes=max((i['nodes'] or 0 for i in iterations),default=0),
            transcript=raw,transcript_sha256=digest(raw),options={**self.options,'MultiPV':multipv},
            reset_policy='ucinewgame; Clear Hash; isready before every search',history_verified=True,
            elapsed_seconds=time.perf_counter()-began,
            score_scope='Original decision-maker search estimate/bound; no game-theoretic certainty claim')

    def close(self):
        if self.process.poll() is None:
            try:self.send('quit');self.process.wait(timeout=5)
            except (BrokenPipeError,subprocess.TimeoutExpired):self.process.kill();self.process.wait()
        if self.process.stdin:self.process.stdin.close()
        self.reader.join(timeout=5)
        if self.process.stdout:self.process.stdout.close()

    def __enter__(self):return self
    def __exit__(self,*args):self.close()
