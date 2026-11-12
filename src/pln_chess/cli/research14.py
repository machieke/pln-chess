"""Read-only offline reference disclosure, separate from inference requests."""
from pln_chess.common import read_json


def reference(identifier):
    from pln_chess.cycle14.inspector import catalog,output_root
    allowed={r['id'] for r in catalog()['examples']}
    if identifier not in allowed:raise ValueError('Reference disclosure is limited to registered development and historical observations')
    path=output_root()/'labels/immediate-g1/records'/(identifier+'.json')
    if not path.is_file():return dict(available=False,id=identifier,status='No registered offline reference',inference_input=False)
    record=read_json(path)
    return dict(available=True,id=identifier,label=record['label'],reason=record['reason'],
        generation=record['generation'],evidence_id=record['evidence_id'],original_actor=record['original_actor'],
        horizon=record['horizon'],inference_input=False,
        scope='Stored offline operational search evidence for the registered root pair; neither a PLN conclusion nor proof of optimal chess value.')
