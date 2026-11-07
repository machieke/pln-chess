"""Offline active learning only; independent game/family splits, native revision."""
import copy
import random
from collections import Counter
from pathlib import Path
import chess
from pln_chess.common import ROOT, read_json, write_json, digest
from pln_chess.domain import Position
from pln_chess.hypotheses import candidates
from pln_chess.cycle4.ontology import descriptors
from pln_chess.cycle4.model import observe_example
from pln_chess.cycle7.model import BackoffModel, key, projection
from pln_chess.pln import TV
from pln_chess.learning import PRIOR
from training.cycle4 import symmetry_key, enrich4

OPENINGS={
 'queens-pawn':['d2d4','d7d5','c2c4','e7e6'],
 'sicilian':['e2e4','c7c5','g1f3','d7d6'],
 'french':['e2e4','e7e6','d2d4','d7d5'],
}

def generate(output=None):
    config=read_json(ROOT/'configs/cycle7.json');positions=[];games=[]
    historical=[read_json(ROOT/p) for p in ('fixtures/dataset.json','artifacts/cycle2/dataset.json','artifacts/cycle3/dataset.json','artifacts/cycle4/datasets/dataset.json','artifacts/cycle5/datasets/dataset.json','artifacts/cycle6/datasets/dataset.json')]
    old={symmetry_key(p['fen']) for d in historical for p in d['positions']};seen=set(old)
    oldgames={g['id'] for d in historical for g in d.get('games',[])}
    for family in OPENINGS:
        split='train' if family=='queens-pawn' else 'independent-games'
        for index in range(config['train_games'] if split=='train' else config['test_games_per_family']):
            seed=config['seed']+1000*list(OPENINGS).index(family)+index;rng=random.Random(seed);b=chess.Board();history=[]
            gid=f'c7-{family}-{seed}'
            assert gid not in oldgames
            for ply in range(1,161):
                legal=sorted(b.legal_moves,key=lambda m:m.uci())
                if not legal:break
                m=chess.Move.from_uci(OPENINGS[family][ply-1]) if ply<=len(OPENINGS[family]) else rng.choice(legal)
                assert m in legal;history.append(m.uci());b.push(m)
                if ply in config['sample_plies']:
                    sym=symmetry_key(b.fen());assert sym not in seen;seen.add(sym)
                    pos=Position.from_fen(b.fen());grammar={m.notation for m in candidates(pos)}
                    assert {m.uci() for m in b.legal_moves}<=grammar
                    positions.append({'id':gid+f'-ply-{ply}','fen':b.fen(),'family':family,'source_game':gid,'split':split,'focus_move':None,
                        'dependence_group':gid,'transformation_lineage':[],'candidate_count':len(grammar)})
            games.append({'id':gid,'seed':seed,'family':family,'split':split,'moves':history,'initial_fen':chess.STARTING_FEN,'final_fen':b.fen()})
    data={'schema':7,'registration_hash':digest(config),'positions':positions,'games':games,'oracle_version':chess.__version__,
        'leakage':{'position_symmetry_overlap':[],'source_game_overlap':[],'transformation_lineage_overlap':[],
            'train_opening_families':['queens-pawn'],'test_opening_families':['sicilian','french'],
            'scope':'Synthetic independent games with disjoint seeded opening families, not external human games. Shared relative submotifs are measured, not asserted disjoint.'}}
    data['hash']=digest(data)
    if output:write_json(output,data)
    return data

def select(data,frozen):
    """Rank using model coverage and structure only; labels added after selection."""
    config=read_json(ROOT/'configs/cycle7.json');base=frozen.source_model().source['base']['hypotheses'];bygame={};selected=[];audit=[]
    for f in data['positions']:
        if f['split']!='train':continue
        p=Position.from_fen(f['fen'])
        for m in candidates(p):
            rel=next(r for r in descriptors(p,m)['relations'] if r['target']=='LocalAdmissibility')
            h=base.get(rel['id']);rank=0 if h is None else 1 if min(h['positive']['confidence'],h['negative']['confidence'])<.25 else 2
            item={'fen':f['fen'],'move':m.notation,'source_game':f['source_game'],'family':f['family'],
                'descriptor':rel['descriptor'],'relative_key':rel['id'],'rank':rank,'fixture':f['id']}
            bygame.setdefault(f['source_game'],[]).append(item)
    for gid,rows in sorted(bygame.items()):
        chosen=[];seen=set()
        for r in sorted(rows,key=lambda r:(r['rank'],digest([r['relative_key'],r['fixture'],r['move']]))):
            if r['relative_key'] in seen:continue
            seen.add(r['relative_key']);chosen.append(r)
            if len(chosen)>=config['active_examples_per_game']:break
        for r in chosen:
            b=chess.Board(r['fen'])
            # Off-board notation is outside python-chess's UCI grammar.
            try:label=chess.Move.from_uci(r['move']) in b.legal_moves
            except ValueError:label=False
            row=enrich4({'fen':r['fen'],'move':r['move'],'label':label,'source':'C7-offline-active-'+gid,
                'dependence_group':gid,'split':'train','confidence':.5,'transformation_lineage':[]})
            selected.append(row)
        audit.append({'game':gid,'pool':len(rows),'selected':chosen})
    return selected,{'label_blind_ranking':True,'policy':config['selection'],'games':audit,'selected_examples':len(selected),
        'independent_evidence_groups':len(bygame),'selection_hash':digest(audit)}

def train(frozen,rows,runtime,out,budget,dependence=True):
    """Replay labels per independent group. Existing C6 rules are never revised."""
    historical=read_json(ROOT/'artifacts/cycle4/datasets/dataset.json')['examples']
    groups=sorted({r['dependence_group'] for r in rows});chosen=set(groups[:budget]);states={};ledger=[];jobs=[];excluded=[]
    for new,records in ((False,[r for r in historical if r['split']=='train']),(True,[r for r in rows if r['dependence_group'] in chosen])):
        for r in records:
            p=observe_example(r['fen'],r['move'],r['label'],r['source'],r['dependence_group'],None,runtime,
                transformation_lineage=r.get('transformation_lineage'),movement_label=r.get('movement_label'),_payload_only=True,
                observation_confidence=r.get('confidence',.5))
            ev=digest(p);ledger.append({'evidence_id':ev,'payload':p,'new_training':new})
            local=next((t for t in p['targets'] if t['target']=='LocalAdmissibility'),None)
            if local is None:continue
            provenance={p['dependence_group'],*p.get('transformation_lineage',[])}
            for level in range(3):
                k=key(local['descriptor'],level)
                state=states.setdefault(k,{'id':k,'level':level,'descriptor':projection(local['descriptor'],level),'groups':set(),
                    'refs':[PRIOR.metta(),PRIOR.metta()],'ids':[],'positive_ids':[],'negative_ids':[],'new_training':False})
                if dependence and provenance&state['groups']:
                    excluded.append([ev,k]);continue
                state['groups'].update(provenance);state['ids'].append(ev);state['positive_ids' if local['label'] else 'negative_ids'].append(ev)
                state['new_training']|=new
                for index,label in enumerate((local['label'],not local['label'])):
                    name=f'c7train{len(jobs)}';jobs.append((name,f'(Truth_Revision {state["refs"][index]} {TV(float(label),p["observation_tv"]["confidence"]).metta()})'));state['refs'][index]=f'({name})'
    values=runtime.batch(jobs);model=copy.deepcopy(frozen);model.variant=f'C7-learned-{budget}'+('' if dependence else '-no-dependence')
    for k,s in states.items():
        model.hypotheses[k]={'id':k,'level':s['level'],'descriptor':s['descriptor'],'target':'LocalAdmissibility','tier':4,
            'positive':values[s['refs'][0][1:-1]].json(),'negative':values[s['refs'][1][1:-1]].json(),
            'evidence_ids':s['ids'],'dependence_groups':sorted(s['groups']),'supporting_evidence':s['positive_ids'],
            'contradicting_evidence':s['negative_ids'],'new_training':s['new_training'],'origin':'native-revision-of-host-joint-observations'}
    model.training_report={'new_evidence_budget':budget,'new_groups':sorted(chosen),'dependence_aware':dependence,
        'records':len(ledger),'revision_nodes':len(jobs),'excluded_duplicates':len(excluded),'excluded_digest':digest(excluded),
        'ledger_digest':digest(ledger),'hypotheses':len(model.hypotheses),'scope':'Partial local conditional, never a native conjunction or global legality theorem.'}
    if out:
        from evaluation.cycle7_io import pack
        out=Path(out);model.export(out/f'model/{model.variant}.json');pack(out/f'training/{model.variant}-ledger.json.xz',{'records':ledger,'native_revision_expressions':jobs})
    return model

def structural_audit(data):
    families={}
    for f in data['positions']:
        target=families.setdefault(f['split'],Counter())
        p=Position.from_fen(f['fen'])
        for m in candidates(p):
            local=descriptors(p,m)['local_context']
            target[digest(local)]+=1
    a,b=set(families['train']),set(families['independent-games'])
    return {'train_keys':len(a),'independent_game_keys':len(b),'shared_relative_categories':len(a&b),'heldout_relative_categories':sorted(b-a),
        'claim':'Opening families, full positions, games and transformation lineages are disjoint. Transferable relative structural submotifs intentionally overlap.'}

if __name__=='__main__':
    import sys
    generate(sys.argv[1])
