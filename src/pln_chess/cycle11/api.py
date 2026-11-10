"""Bounded field-inspector contracts, independent of the operational legal API."""
import os
from pathlib import Path
from pln_chess.common import ROOT, read_json
from pln_chess.domain import Position, parse_square
from pln_chess.pln import Runtime
from .fields.model import FieldModel
from .fields.inference import FieldOptions, build_field
from .fields.ontology import FIELDS, TARGETS


def output_root():
    return Path(os.environ.get('C11_OUT',ROOT/'artifacts/cycle11'))


def inspect_fields(position,checkpoint=None,*,family=None,piece=None,candidate=None,history=None,
                   legal_mode='operational',runtime=None,options=None):
    options=options or FieldOptions()
    runtime=runtime or Runtime(timeout=options.timeout_seconds)
    position=Position.from_fen(position) if isinstance(position,str) else position
    checkpoint=checkpoint or output_root()/'model/C11-field-trained.json'
    model=FieldModel.load(checkpoint,runtime) if isinstance(checkpoint,(str,Path)) else checkpoint
    families=FIELDS if family in (None,'all') else (family,)
    if any(f not in TARGETS for f in families):raise ValueError('Unknown field family')
    selected=None
    if piece:
        entity=next((p for p in position.pieces if p.id==piece),None)
        if entity is None:entity=position.at(parse_square(piece))
        if entity is None:raise ValueError('Selected source square has no supplied entity')
        selected=[entity.id]
    if candidate:
        from .fields.comparison import compare_candidate
        return compare_candidate(position,candidate,model,history_input=history,options=options,runtime=runtime,
            families=families,source_ids=selected,legal_mode=legal_mode)
    return build_field(position,model,options=options,runtime=runtime,families=families,source_ids=selected)


def inspector_catalog():
    data=read_json(output_root()/'datasets/worked-controls.json')
    # Display inputs and provenance only. Offline labels are not inference input.
    return dict(examples=[{key:row[key] for key in ('id','description','fen','move','unknown_squares','history_input','selected_piece_square','selected_field') if key in row}
        for row in data['worked']],families=list(FIELDS),models=['trained','empty'],
        scope='Experimental influence relations; native conditional proofs do not establish strategic value.')


def inspector_fields(payload):
    if not isinstance(payload,dict):raise ValueError('Expected a field request object')
    selector=payload.get('model','trained')
    if selector not in ('trained','empty'):raise ValueError('Unknown field model selector')
    family=payload.get('family','all')
    if family not in (*TARGETS,'all'):raise ValueError('Unknown field family')
    mode=payload.get('legal_mode','operational')
    if mode not in ('operational','strict','experimental'):raise ValueError('Unknown legal proof mode')
    unknown=payload.get('unknown_squares',[])
    if not isinstance(unknown,list) or len(unknown)>64:raise ValueError('Invalid unknown cells')
    unknown=[parse_square(s) if isinstance(s,str) else s for s in unknown]
    position=Position.from_fen(payload['fen'],unknown_squares=unknown)
    options=FieldOptions(max_native_invocations=payload.get('max_invocations',100000),timeout_seconds=payload.get('timeout',180))
    return inspect_fields(position,output_root()/f'model/C11-field-{selector}.json',family=family,
        piece=payload.get('piece') or None,candidate=payload.get('candidate') or None,
        history=payload.get('history'),legal_mode=mode,options=options)
