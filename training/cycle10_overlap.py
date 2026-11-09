"""Additional all-dihedral exclusion and local-feature transfer accounting."""
import argparse
from collections import Counter,defaultdict
from pathlib import Path
import chess
from pln_chess.common import ROOT,read_json,write_json,digest
from pln_chess.domain import Position
from pln_chess.hypotheses import candidates
from pln_chess.cycle4.ontology import descriptors
from pln_chess.cycle7.model import key as local_key
from pln_chess.cycle8.ontology import observe as promotion_observe,key as promotion_key
from scripts.cycle9_baseline import sha


def all_symmetry_key(fen):
    pieces=[(p.symbol(),chess.square_file(s),chess.square_rank(s)) for s,p in chess.Board(fen).piece_map().items()]
    forms=[]
    for swap in (False,True):
        for transpose in (False,True):
            for sx,sy in ((1,1),(1,-1),(-1,1),(-1,-1)):
                transformed=[(symbol.swapcase() if swap else symbol,sx*(y if transpose else x),sy*(x if transpose else y)) for symbol,x,y in pieces]
                minx=min(x for _,x,_ in transformed);miny=min(y for _,_,y in transformed)
                forms.append(tuple(sorted((symbol,x-minx,y-miny) for symbol,x,y in transformed)))
    return digest(min(forms))


def run(out):
    out=Path(out);data=read_json(out/'datasets/dataset.json');old=defaultdict(set);historical_files={}
    paths=[ROOT/'fixtures/dataset.json']
    for cycle in range(2,10):paths.extend(p for p in (ROOT/f'artifacts/cycle{cycle}/dataset.json',ROOT/f'artifacts/cycle{cycle}/datasets/dataset.json') if p.exists())
    for path in paths:
        previous=read_json(path);historical_files[str(path.relative_to(ROOT))]=sha(path)
        for fen in {r['fen'] for r in previous.get('positions',[])+previous.get('examples',[]) if r.get('fen')}:
            old[all_symmetry_key(fen)].add(str(path.relative_to(ROOT)))
    seen={};cross=[];historical=[];byfixture={}
    for f in data['positions']:
        key=all_symmetry_key(f['fen']);byfixture[f['id']]=key
        if key in old:historical.append(dict(fixture=f['id'],historical_datasets=sorted(old[key])))
        if key in seen:cross.append(dict(fixture=f['id'],other=seen[key]))
        seen[key]=f['id']
    report=dict(dataset_hash=data['hash'],method='All eight plane symmetries with and without owner swap, translation normalized; clocks, side and historical flags deliberately ignored for conservative exclusion.',
        historical_files=historical_files,historical_keys=len(old),positions=len(byfixture),historical_overlaps=historical,
        repeated_or_transformed_positions=cross,fixture_keys=byfixture,passed=not historical and not cross)
    write_json(out/'datasets/all-symmetry-audit.json',report)
    assert report['passed'],'Broader symmetry audit found overlaps; stop before external inference'
    checkpoint=read_json(ROOT/'artifacts/cycle8/model/C8-promotion-relative.json')
    local=checkpoint['source']['source']['source']['base']['hypotheses'];learned=checkpoint['source']['hypotheses'];promotion=checkpoint['hypotheses']
    keys=defaultdict(set);counts=defaultdict(Counter);novel=defaultdict(list)
    for f in data['positions']:
        p=Position.from_fen(f['fen'])
        for m in candidates(p):
            relation=next(r for r in descriptors(p,m)['relations'] if r['target']=='LocalAdmissibility')
            identifier=local_key(relation['descriptor'],0);known=relation['id'] in local or identifier in learned
            if m.promotion:
                obs=promotion_observe(p,m);identifier=promotion_key(obs['descriptor']);known|=identifier in promotion
            keys[f['split']].add(identifier);counts[f['split']]['known' if known else 'unseen']+=1
            if not known:novel[f['id']].append(m.notation)
    sets={k:sorted(v) for k,v in keys.items()};adapt=keys['external-adaptation'];test=keys['external-test']
    write_json(out/'datasets/relative-transfer-audit.json',dict(dataset_hash=data['hash'],per_split_counts={k:dict(v) for k,v in counts.items()},
        per_split_keys=sets,shared_adaptation_test_keys=len(adapt&test),test_only_keys=len(test-adapt),unseen_candidates_by_fixture=dict(novel),
        scope='Exact learned local/promotion descriptor availability, not predictions or legal labels. Recurring local features are intentional transfer. An unseen descriptor can be valid geometry; missing knowledge is distinct from a candidate-generation failure.'))
    print('All-symmetry exclusion passed;',len(byfixture),'positions;',len(test-adapt),'test-only relative keys',flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);run(p.parse_args().out)
