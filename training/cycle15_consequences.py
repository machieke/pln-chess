"""Training-only evidence admission and native revision of supplied templates."""
from pathlib import Path
import json
from pln_chess.common import digest, write_json
from pln_chess.pln import TV
from research.cycle15.knowledge import templates
from research.cycle15.native_reasoner import NativeReasoner, parse, save_result

LEARNED=('rook-attack','bishop-attack','queen-orthogonal','queen-diagonal','obstruction')


def evidence(roots):
    from evaluation.cycle15_corpus import episode, reference, registration
    registered={r['id']:r for r in registration() if r['split']=='train'}
    rows=[]
    for root in roots:
        if root['split']!='train' or registered.get(root['id'])!=root:
            raise ValueError('Only exact preregistered training roots may supply evidence')
        e=episode(root);kind=root['family']['kind'];direction=root['family']['direction']
        rule=kind+'-attack' if kind!='queen' else 'queen-'+('orthogonal' if 0 in direction else 'diagonal')
        for endpoint in ('state','after'):
            ref=reference(e[endpoint],e['query'])
            # Offline admission checks the exact conditional target. Occupied
            # before-states cannot contradict a rule conditioned on clearance.
            rows.append(dict(root=root['id'],ancestry=root['source_ancestry'],split=root['split'],
                endpoint=endpoint,rule=rule,observed_attack=ref['label'],
                label=ref['label'] if endpoint=='after' else None,
                admitted=endpoint=='after',reason='all declared terminal premises reference-verified' if endpoint=='after'
                else 'clearance antecedent not satisfied; negative observation retained without miscredit'))
            if endpoint=='state':rows.append(dict(root=root['id'],ancestry=root['source_ancestry'],split='train',
                endpoint=endpoint,rule='obstruction',observed_attack=ref['label'],label=not ref['label'],admitted=True,
                reason='occupied intervening cell and exact negative attack target reference-verified'))
        rows.append(dict(root=root['id'],ancestry=root['source_ancestry'],split='train',endpoint='unknown-control',
            rule=rule,observed_attack=None,label=None,admitted=False,reason='missing occupancy observation'))
    return rows


def fit(rows, out, *, exclude_ancestry=(), reasoner=None):
    reasoner=reasoner or NativeReasoner();out=Path(out);out.mkdir(parents=True,exist_ok=True)
    from evaluation.cycle15_corpus import registration
    admitted_records={digest(row) for row in evidence([r for r in registration() if r['split']=='train'])}
    rules={name:dict(truth_value=TV(.5,0).json(),ancestry=[],evidence=[]) for name in LEARNED}
    ledger=[];seen=set()
    for row in rows:
        if row.get('split')!='train':raise ValueError('Development/test labels cannot update rules')
        if digest(row) not in admitted_records:
            raise ValueError('Evidence is not an exact registered training observation')
        if row['rule'] not in rules:raise ValueError('Unknown learned template')
        item=dict(row)
        key=(row['rule'],row['ancestry'])
        if not row['admitted'] or row['label'] is None:
            item['action']='unadmitted';ledger.append(item);continue
        if row['ancestry'] in exclude_ancestry:
            item['action']='ancestry-excluded';ledger.append(item);continue
        if key in seen:
            item['action']='duplicate-ancestry-rejected';ledger.append(item);continue
        seen.add(key)
        current=rules[row['rule']];before=TV(**current['truth_value']);sample=TV(float(row['label']),.5)
        expression=f'(|- (LearnedBelief {before.metta()}) (LearnedBelief {sample.metta()}))'
        program=f'!(import! &self "{reasoner.runtime.library}")\n!(println! (REVISION {expression}))\n'
        receipt=reasoner.execute_program(program,10)
        if receipt['incomplete']:raise RuntimeError('Native training revision failed')
        lines=[parse(line) for line in receipt['stdout'].splitlines() if line.startswith('(REVISION ')]
        if len(lines)!=1:raise RuntimeError('Ambiguous native revision')
        tv=lines[0][1][1];after=TV(float(tv[1]),float(tv[2]))
        proof=save_result(receipt,out/'raw')
        item.update(action='native-revision',before=before.json(),after=after.json(),expression=expression,evidence=proof)
        current['truth_value']=after.json();current['ancestry'].append(row['ancestry'])
        current['evidence'].append(digest(row));ledger.append(item)
    model=dict(schema='cycle15-consequence-rules-v1',runtime_version=reasoner.runtime.version,
        structure_hash=digest(templates()),rules=rules,ledger_hash=digest(ledger),
        logical_structure_origin='supplied domain templates; only truth values learned',
        evidence_policy='one admitted observation per root ancestry and template; unknowns excluded')
    model['version']=digest(model)
    write_json(out/'model.json',model);write_json(out/'ledger.json',ledger)
    return model,ledger


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--out',required=True)
    args=parser.parse_args()
    from evaluation.cycle15_corpus import registration
    fit(evidence([r for r in registration() if r['split']=='train']),args.out)
