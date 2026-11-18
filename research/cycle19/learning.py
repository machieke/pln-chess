"""Native revision of supplied rules from fresh, measured annotations."""
from pathlib import Path
from pln_chess.common import ROOT,digest
from pln_chess.pln import TV
from research.cycle15.knowledge import templates
from research.cycle15.native_reasoner import NativeReasoner,parse,save_result
from .records import record,sha

PATH=ROOT/'knowledge/cycle16/finite_two.metta'
PAIR=('clear-two','rook-attack')
ASSIGNMENTS={'D-AB':('A','B'),'D-BA':('B','A'),'S-AA':('A','A'),'S-BB':('B','B'),'P':(None,None)}


def fit(journal,annotations,out,arm,*,exclude=(),remove_support=(),reasoner=None):
    out=Path(out)
    if (out/'model.json').exists():raise ValueError('Generation already exists')
    if arm not in ASSIGNMENTS:raise ValueError('Unregistered learning arm')
    reasoner=reasoner or NativeReasoner();structures=templates(PATH)
    rules={name:dict(truth_value=TV(.5,0).json(),ancestry=[],evidence=[],declaration=structures[name],
        rule_identity='rule_'+name,origin='Supplied structure; Cycle19 native revision') for name in PAIR}
    admitted=[];ledger=[];seen={}
    for ident in annotations:
        node=journal.require(ident)
        if node['kind']!='annotation':raise ValueError('Expected measured annotation')
        row=node['payload'];rule=row['rule'];action='excluded'
        component=journal.require(row['component'])
        env=journal.require(row['environment'])
        if (component['kind']!='measurement' or row['component'] not in node['parents']
            or component['payload']['target']!=row['target']
            or component['payload']['result']['value']!=row['label']
            or component['payload']['parent_event']!=row['environment']
            or env['kind']!='environment' or env['payload']['ancestry']!=row['ancestry']):
            raise ValueError('Annotation does not match its measured component and environment')
        if rule not in PAIR:raise ValueError('Unknown component')
        eligible=(row['admitted'] and row['split']==ASSIGNMENTS[arm][PAIR.index(rule)]
            and row['ancestry'] not in exclude and rule not in remove_support)
        key=(rule,row['ancestry'])
        if eligible and key in seen:
            # Identical delivery is idempotent. A conflicting active payload
            # from the same source must be resolved by explicit supersession.
            if seen[key]!=digest(row):raise ValueError('Conflicting current evidence from same source')
            action='duplicate-source-rejected'
        elif eligible:
            seen[key]=digest(row);current=rules[rule];before=TV(**current['truth_value'])
            expression=f'(|- (LearnedBelief {before.metta()}) (LearnedBelief {TV(float(row["label"]),.5).metta()}))'
            program=f'!(import! &self "{reasoner.runtime.library}")\n!(println! (C19REVISION {expression}))\n'
            receipt=reasoner.execute_program(program,15);proof=save_result(receipt,out/'raw')
            if receipt['incomplete']:raise RuntimeError('Incomplete revision: '+str(proof))
            values=[parse(line) for line in receipt['stdout'].splitlines() if line.startswith('(C19REVISION ')]
            if len(values)!=1:raise RuntimeError('Ambiguous native revision')
            tv=values[0][1][1];current['truth_value']=TV(float(tv[1]),float(tv[2])).json()
            current['ancestry'].append(row['ancestry']);current['evidence'].append(ident)
            admitted.append(ident);action='native-revision'
            ledger.append(dict(annotation=ident,action=action,before=before.json(),after=current['truth_value'],expression=expression,proof=proof))
            continue
        ledger.append(dict(annotation=ident,action=action))
    for value in rules.values():
        value['ancestry'].sort();value['evidence'].sort()
    model=dict(schema='cycle19-learned-pair-v1',arm=arm,runtime_version=reasoner.runtime.version,
        structure_hash=digest(structures),rules=rules,learner_identity=sha(Path(__file__)),
        admitted_components={k:journal.node(k) for k in sorted(admitted)},
        assumptions=dict(observation_confidence=.5,prior_strength=.5,prior_confidence=0,
            evidence_policy='one-current-measurement-per-rule-source',structure='supplied'),
        exclusions=sorted(exclude),removed_support=sorted(remove_support))
    model['version']=digest(model)
    generation=journal.add('generation',model,admitted)
    record(out/'model.json',model);record(out/'ledger.json',ledger)
    return dict(model=model,generation=generation)
