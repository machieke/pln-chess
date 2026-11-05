"""Cycle 3 full-set scoring and provenance. Oracle access is evaluation-only."""
import gzip,json,lzma,hashlib,resource,time
from pathlib import Path
import chess
from pln_chess.common import ROOT,digest,read_json,write_json
from pln_chess.domain import Position,inside
from pln_chess.hypotheses import candidates
from pln_chess.inference import infer_moves,Options
from pln_chess.cycle2.native import NativeSession
from evaluation.experiments import summarize
from evaluation.cycle2 import uncertainty


def write_gzip(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('wb') as handle:
        with gzip.GzipFile(fileobj=handle,mode='wb',filename='',mtime=0) as out:
            out.write(json.dumps(value,sort_keys=True,separators=(',',':')).encode())


def read_gzip(path):
    path=Path(path)
    if not path.exists() and path.suffix=='.gz':path=path.with_suffix('.xz')
    opener=lzma.open if path.suffix=='.xz' else gzip.open
    with opener(path,'rt') as handle:return json.load(handle)


def pack_reports(directory):
    """Lossless long-dictionary encoding of repetitive proof/evidence JSON.

    Reproduction writes gzip during execution; final delivery uses XZ to avoid
    committing duplicate evidence identifiers repeatedly across many reports.
    """
    directory=Path(directory);receipts=[]
    for source in sorted(directory.glob('*.json.gz')):
        raw=gzip.decompress(source.read_bytes());target=source.with_suffix('.xz')
        target.write_bytes(lzma.compress(raw,preset=6))
        if lzma.decompress(target.read_bytes())!=raw:raise RuntimeError('Artifact encoding mismatch')
        receipts.append({'logical_path':source.name,'stored_path':target.name,'json_sha256':hashlib.sha256(raw).hexdigest(),
                         'gzip_bytes':source.stat().st_size,'xz_bytes':target.stat().st_size,'lossless':True})
        source.unlink()  # Only the verified redundant generated encoding is removed.
    index=directory/'comparison.json'
    if index.exists():
        data=read_json(index)
        for variants in data.values():
            for report in variants.values():
                if report.get('artifact','').endswith('.gz') and (directory/Path(report['artifact']).name).with_suffix('.xz').exists():
                    report['artifact']=str(Path(report['artifact']).with_suffix('.xz'))
        write_json(index,data)
    write_json(directory/'artifact-encoding.json',{'format':'XZ compressed JSON; read_gzip accepts both encodings and legacy .gz logical names',
                                                 'files':receipts,'lossless':all(r['lossless'] for r in receipts)})
    return receipts


def infer(position,model,runtime,session=None,selected_moves=None,optimized=True,options=None):
    if model.schema==3:
        from pln_chess.cycle3.inference import infer_moves as run
    elif model.schema==2:
        from pln_chess.cycle2.inference import infer_moves as run
    else:return infer_moves(position,model,options,runtime,selected_moves)
    return run(position,model,options,runtime,selected_moves,session,optimized)


def tags(position,move,label):
    board=chess.Board(position.fen());after=position.successor(move);result=[]
    if not inside(move.end):result.append('boundary')
    if move.effect=='castle':result.append('castling')
    if move.effect=='en-passant':result.extend(['en-passant','history'])
    if move.promotion:result.append('promotion')
    if after:
        successor=chess.Board(after.fen());king=successor.king(position.turn=='White')
        if king is not None and successor.is_attacked_by(position.turn!='White',king):result.append('self-check')
    if not label:
        try:
            if not board.is_pseudo_legal(chess.Move.from_uci(move.notation)):result.append('illegal-capture-or-occupancy')
        except ValueError:pass
    return result or ([] if label else ['other'])


def evaluate(dataset,model,split,runtime,output=None):
    rows=[];positions=[];session=NativeSession(runtime);proofs={}
    options=None
    if model.schema==3:
        from pln_chess.cycle3.native import NativeSession as ScopedSession
        from pln_chess.cycle3.inference import Cycle3Options
        session=ScopedSession(runtime)
        options=Cycle3Options(max_proof_bytes=1024*1024*1024 if not model.training_report.get('dependence_aware',True) else 64*1024*1024)
    for fixture in dataset['positions']:
        if fixture['split']!=split:continue
        pos=Position.from_fen(fixture['fen']);moves={m.notation:m for m in candidates(pos)}
        result=infer(pos,model,runtime,session,options=options);expected={m.uci() for m in chess.Board(pos.fen()).legal_moves}
        for item in result['candidates']:
            move=moves[item['move']];label=move.notation in expected;categories=tags(pos,move,label)
            trace=item['proof_trace'];proof=digest(trace)
            row={'fixture':fixture['id'],'family':fixture['family'],'split':split,'fen':fixture['fen'],
                 'move':move.notation,'piece':item['piece'],'label':label,'classification':item['classification'],
                 'truth_value':item['legal_move_truth_value'],'self_check':'self-check' in categories,
                 'tags':categories,'root_cause':'self-check' if 'self-check' in categories else (categories[0] if categories else None),
                 'destination_exists':inside(move.end),'matched_hypotheses':[h['id'] for h in item.get('matched_hypotheses',[])],
                 'rule_ids':item.get('matched_rule_ids',[]),'proof_id':proof,'proof_node_ids':[t['id'] for t in trace],
                 'evidence_ids':item.get('evidence_ids',[]),'abstention_reason':item['gaps'] if item['classification'] in ('unknown','incomplete') else [],
                 'chosen_hypothesis':item.get('chosen_hypothesis_id'),
                 'attack_beliefs':[{k:a[k] for k in ('id','attacker_id','phase','truth_value','exposure_truth_value','negative_legality_truth_value','origin') if k in a} for a in item.get('attack_beliefs',[])],
                 'status':item['status']}
            rows.append(row)
            if not label and item['classification']=='supported':proofs[proof]=trace
        predicted={i['move'] for i in result['candidates'] if i['classification']=='supported'}
        positions.append({'fixture':fixture['id'],'family':fixture['family'],'exact':expected==predicted,'expected':sorted(expected),'predicted':sorted(predicted),
                          'elapsed':result['elapsed_seconds'],'native_invocations':result['native_invocations'],'grounded_atoms':result['grounded_atoms'],
                          'truncated':result['truncated'],'error':result['error']})
    metrics=summarize(rows,positions)
    metrics['per_piece']={p:summarize([r for r in rows if r['piece']==p],[]) for p in sorted({r['piece'] for r in rows})}
    metrics['per_family']={p:summarize([r for r in rows if r['family']==p],[]) for p in sorted({r['family'] for r in rows})}
    metrics['in_board']=summarize([r for r in rows if r['destination_exists']],positions)
    metrics['uncertainty']=uncertainty(rows,positions)
    metrics['peak_process_rss_kib']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    report={'dataset_hash':dataset['hash'],'model_version':model.version,'split':split,'thresholds':vars(Options()),
            'evaluation_budget':vars(options or Options()),
            'metrics':metrics,'rows':rows,'positions':positions,'error_proofs':proofs}
    if output:write_gzip(output,report)
    return report
