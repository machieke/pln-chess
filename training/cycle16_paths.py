"""Exact conditional admission, native revision, stable source-game ancestry."""
import argparse
from pathlib import Path
from pln_chess.common import ROOT,digest,write_json
from pln_chess.pln import TV
from research.cycle15.knowledge import templates
from research.cycle15.native_reasoner import NativeReasoner,parse,save_result
from research.cycle16.corpus import roots,variant,reference,OCCUPANCIES
from research.cycle16.records import record

PATH=ROOT/'knowledge/cycle16/finite_two.metta'
TERMINAL=('rook-attack','bishop-attack','queen-orthogonal','queen-diagonal')


def evidence():
    rows=[]
    for root in roots():
        if root['split']!='train':continue
        kind=next(p['kind'] for p in root['state']['pieces'] if p['id']==root['attacker'])
        terminal=kind+'-attack' if kind!='queen' else 'queen-'+root['coarse_geometry'].split('-')[0]
        for occupancy in OCCUPANCIES:
            state=variant(root,occupancy);ref=reference(state,root['attacker'],root['target'])
            for rule in ('clear-two',terminal):
                rows.append(dict(root=root['id'],ancestry=root['source_ancestry'],split='train',rule=rule,
                    occupancy=occupancy,state_identity=digest(state),observation_identity=digest([state,root['attacker'],root['target']]),
                    admitted=occupancy=='EE',label=ref['label'] if occupancy=='EE' else None,
                    observed_attack=ref['label'],reference=ref,conditional='Exact two-cell ray and both emptiness premises' if rule=='clear-two' else 'Kind and reference-verified clearance',
                    reason='all declared antecedents satisfied' if occupancy=='EE' else 'unknown antecedent excluded' if 'U' in occupancy else 'blocked antecedent excluded'))
    return rows


def prior(learn_chain=False):
    structures=templates(PATH)
    learned=('clear-two',*TERMINAL) if learn_chain else ('clear-two',)
    return {name:dict(truth_value=TV(.5,0).json(),ancestry=[],evidence=[],declaration=structures[name],
        rule_identity='rule_'+name,source_checkpoint=None,origin='new Cycle 16 parameter; no inherited learned support') for name in learned}


def fit(rows,out,*,learn_chain=False,exclude_ancestry=(),untrained=False,reasoner=None):
    out=Path(out)
    if (out/'model.json').exists():raise ValueError('Choose a new checkpoint generation')
    reasoner=reasoner or NativeReasoner();allowed={digest(r) for r in evidence()}
    rules=prior(learn_chain);ledger=[];seen=set()
    for row in rows:
        if row.get('split')!='train' or digest(row) not in allowed:
            raise ValueError('Only exact frozen training evidence is admitted')
        item=dict(row)
        if row['rule'] not in rules:continue
        key=(row['rule'],row['ancestry'])
        if not row['admitted']:item['action']='unadmitted'
        elif untrained:item['action']='untrained-prior-control'
        elif row['ancestry'] in exclude_ancestry:item['action']='ancestry-excluded'
        elif key in seen:item['action']='duplicate-ancestry-rejected'
        else:
            seen.add(key);current=rules[row['rule']];before=TV(**current['truth_value'])
            expression=f'(|- (LearnedBelief {before.metta()}) (LearnedBelief {TV(float(row["label"]),.5).metta()}))'
            program=f'!(import! &self "{reasoner.runtime.library}")\n!(println! (C16REVISION {expression}))\n'
            receipt=reasoner.execute_program(program,15)
            if receipt['incomplete']:raise RuntimeError('Native revision incomplete: '+str(save_result(receipt,out/'raw')))
            values=[parse(line) for line in receipt['stdout'].splitlines() if line.startswith('(C16REVISION ')]
            if len(values)!=1:raise RuntimeError('Ambiguous native revision')
            tv=values[0][1][1];after=TV(float(tv[1]),float(tv[2]))
            item.update(action='native-revision',before=before.json(),after=after.json(),expression=expression,
                proof=save_result(receipt,out/'raw'))
            current['truth_value']=after.json();current['ancestry'].append(row['ancestry']);current['evidence'].append(digest(row))
        ledger.append(item)
    model=dict(schema='cycle16-finite-path-v1',runtime_version=reasoner.runtime.version,
        structure_hash=digest(templates(PATH)),rules=rules,ledger_hash=digest(ledger),
        corpus_hash=digest(roots()),logical_structure_origin='Supplied finite conditional; no structure discovery',
        evidence_policy='One exact training source-game ancestry per template; blocked/unknown antecedents excluded',
        learn_chain=learn_chain,untrained=untrained)
    model['version']=digest(model);record(out/'model.json',model);record(out/'ledger.json',ledger)
    return model,ledger


def run(out):
    out=Path(out);rows=evidence();record(out/'evidence.json',rows)
    models={}
    for name,kwargs in [('learned',{}),('prior',{'untrained':True}),('shared-chain',{'learn_chain':True}),
                        ('replay',{}),('leave-one',{'exclude_ancestry':(rows[0]['ancestry'],)})]:
        models[name],_=fit(rows+rows if name=='replay' else rows,out/name,**kwargs)
    assert models['learned']['rules']==models['replay']['rules']
    record(out/'summary.json',dict(models={n:m['version'] for n,m in models.items()},
        exact_replay_parameters_and_ancestry=True,removed_ancestry=rows[0]['ancestry'],
        supplied_structure_hash=digest(templates(PATH)),all_admitted_labels_positive=all(r['label'] for r in rows if r['admitted'])))
    return models


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);run(p.parse_args().out)
