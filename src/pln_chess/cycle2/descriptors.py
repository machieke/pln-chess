"""Host sensing/indexing only. No attack, movement, or legality adjudicator."""
from pln_chess.common import digest
from pln_chess.observations import observe


def relation(tier, descriptor, target='LegalMove'):
    return {'id':'c2:'+digest([target,tier,descriptor])[:24], 'tier':tier,
            'descriptor':descriptor, 'target':target, 'provenance':'host-derived',
            'derivation':'Projection of directly observed relative geometry/occupancy; not a PLN conjunction.'}


def occupancy_motifs(sequence):
    cells=[{'step':i,'occupancy':cell} for i,cell in enumerate(sequence,1)]
    occupied=[cell for cell in cells if cell['occupancy'] not in ('Empty','Boundary')]
    # These are observations of contents, never a judgment that a move is blocked.
    return {'cells':cells,'content_classes':sorted(set(sequence)-{'Empty'}),
            'first_nonempty':next((c for c in cells if c['occupancy']!='Empty'),None),
            'prefix_empty_count':next((i for i,c in enumerate(sequence) if c!='Empty'),len(sequence)),
            'suffix_empty_count':next((i for i,c in enumerate(reversed(sequence)) if c!='Empty'),len(sequence)),
            'occupied_count':len(occupied)}


def motion(piece, geo):
    dx,dy=geo['offset']
    if piece in ('Pawn','King','Knight'):
        # Owner-relative displacement, reflection symmetric in files. No label seeded.
        return [abs(dx),dy] if piece=='Pawn' else sorted([abs(dx),abs(dy)])
    return geo['family']


def descriptors(position, move, variant='hierarchical'):
    raw=observe(position,move)
    c=raw['context']; piece=raw['piece']; ray=occupancy_motifs(c['intermediate'])
    base={'piece':piece,'motion':motion(piece,c['geometry']),'effect':c['effect'],'promotion':c['promotion']}
    occupancy={'ray_contents':ray['content_classes']}
    dest={'destination':c['destination'],'destination_kind':c['destination_kind']}
    temporal={k:c[k] for k in ('pawn_start_edge_distance','pawn_end_edge_distance','ep_offset','castle_rights',
                  'castle_rook','castle_rook_kind','castle_rook_path','castle_king_edge_distance','rights_known') if c[k] is not None and c[k]!=[]}
    local={**base,**dest,**temporal}
    if variant!='no-obstruction': local.update(occupancy)
    relations=[relation(0,{'piece':piece},'MovementPatternSupported'),
               relation(1,base,'MovementPatternSupported'),
               relation(2,{**base,**occupancy},'MovementPatternSupported'),
               relation(3,{**base,**dest},'MovementPatternSupported'),
               relation(4,local),
               relation(5,{**local,'distance':c['geometry']['distance'],'first_nonempty':ray['first_nonempty']})]
    if variant=='no-obstruction':
        relations=[r for r in relations if r['tier'] not in (2,5)]
        relations.append(relation(5,{**local,'distance':c['geometry']['distance']}))
    if variant not in ('no-exact','no-obstruction'):
        exact={k:v for k,v in c.items() if variant!='no-exposure' or k not in ('postmove_opponents','castle_transit')}
        relations.append(relation(6,exact))
    if variant=='geometry-only': relations=[relation(4,base)]
    attacks=[]
    if variant!='no-exposure':
        for a in raw['attacks']:
            d=a['descriptor']; aray=occupancy_motifs(d['intermediate'])
            shape={'piece':d['piece'],'motion':motion(d['piece'],d['geometry']),'ray_contents':aray['content_classes']}
            attacks.append({**a,'relation':relation(4,shape,'Attack'),'raw_ray':aray})
    complete=raw['complete'] and sum(p.owner==position.turn and p.kind=='King' for p in position.pieces)==1
    return {**raw,'schema':'hierarchical-relative-v2','complete':complete,'local_context':local,'relations':relations,
            'ray_motifs':ray,'attack_relations':attacks,'variant':variant,
            'boundary':'Movement keys exclude opponent-to-king frames. Exposure is separately indexed.'}
