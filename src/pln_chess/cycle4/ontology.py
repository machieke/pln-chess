"""Typed relative observations. No legality, obstruction or attack adjudication."""
from pln_chess.common import digest
from pln_chess.cycle2.descriptors import motion
from pln_chess.cycle3.descriptors import descriptors as previous
from pln_chess.cycle4 import SCHEMA


def relation(target,descriptor,tier=0):
    return {'id':'c4:'+digest([SCHEMA,target,descriptor])[:24],'target':target,'descriptor':descriptor,'tier':tier,
            'provenance':'host-grounded','derivation':'Typed relative projection; never a native conjunction.'}


def descriptors(position,move,variant='C4-full'):
    raw=previous(position,move);c=raw['context'];piece=raw['piece']
    base={'piece':piece,'motion':motion(piece,c['geometry']),'effect':move.effect,'promotion':move.promotion}
    # A pooled joint observation, retained explicitly as a non-compositional baseline.
    # Victim identity and empty-ray length are not causal movement categories.
    local={**base,'destination':c['destination'],'ray_contents':raw['ray_motifs']['content_classes']}
    if piece=='Pawn' and c['geometry']['offset']==[0,2]:local['start_edge_distance']=c['pawn_start_edge_distance']
    if move.promotion:local['end_edge_distance']=c['pawn_end_edge_distance']
    if move.effect=='en-passant':local['ep_offset']=c['ep_offset']
    if move.effect=='castle':
        local.update({k:c[k] for k in ('castle_rights','castle_rook','castle_rook_kind','castle_rook_path','castle_king_edge_distance','rights_known')})
    relations=[relation('LocalAdmissibility',local,4),relation('GeometryObserved',base,1),
               relation('DestinationConflict',{'occupancy':c['destination'],'kind':c['destination_kind']},2),
               relation('BoundaryConflict',{'exists':c['destination_exists']},2)]
    cells=[]
    for cell in raw['ray_motifs']['cells']:
        r=relation('Obstruction',{'piece':piece,'motion':base['motion'],'occupancy':cell['occupancy']},2)
        cells.append({'step':cell['step'],'relation':r})
    relations.extend({r['relation']['id']:r['relation'] for r in cells}.values())
    attacks=[]
    for a in raw['attack_relations']:
        attacks.append({**a,'relation':relation('Attack',a['relation']['descriptor'],3)})
    # The schema addresses facts independently even when no learned rule matches.
    facts=[{'predicate':'PieceClass','roles':{'mover':piece}},
           {'predicate':'Displacement','roles':{'source':'source','target':'destination','offset':c['geometry']['offset']}},
           {'predicate':'DestinationRelation','roles':{'occupancy':c['destination'],'kind':c['destination_kind']}},
           {'predicate':'BoundaryRelation','roles':{'destination_exists':c['destination_exists']}},
           {'predicate':'TemporalObservation','roles':raw['temporal_observations']},
           {'predicate':'CandidateSuccessor','roles':{'operation':move.effect,'promotion':move.promotion}}]
    facts.extend({'predicate':'RayCell','roles':{'step':x['step'],'occupancy':x['occupancy']}} for x in raw['ray_motifs']['cells'])
    for fact in facts:fact['provenance']='sensed' if fact['predicate'] not in ('Displacement','CandidateSuccessor') else 'host-grounded'
    raw.update(schema=SCHEMA,variant=variant,relations=relations,attack_relations=attacks,cell_relations=cells,
               local_context=local,factored_premises=facts,
               composition='Unary native constraint chains; pooled local observation is explicitly non-compositional.')
    return raw
