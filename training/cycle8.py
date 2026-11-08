"""Offline promotion supervision; all belief updates use native revision."""
from collections import defaultdict
from pathlib import Path
import argparse
from pln_chess.common import ROOT, read_json, write_json, digest
from pln_chess.domain import Position
from pln_chess.api import find_move
from pln_chess.learning import PRIOR
from pln_chess.pln import Runtime, TV
from pln_chess.cycle7.model import BackoffModel
from pln_chess.cycle8.model import PromotionModel
from pln_chess.cycle8.ontology import observe, project, key
from evaluation.cycle7_io import pack


def train(data, source, runtime, variant='C8-promotion-relative', out=None, retract_groups=()):
    projection=variant if variant in ('no-destination-context','no-choice-context') else 'C8-promotion-relative'
    model=PromotionModel.wrap(source,variant='C8-'+variant if not variant.startswith('C8-') else variant)
    model.projection_variant=projection
    if variant=='no-promotion-training':
        model.training_report={'records':0,'new_training':False,'scope':'C7 exact learned categories only'}
        if out:model.export(Path(out)/f'model/{model.variant}.json')
        return model
    ledger=[];observations=defaultdict(list);skipped=[]
    for row in data['examples']:
        if row['split']!='train' or row['dependence_group'] in retract_groups:continue
        pos=Position.from_fen(row['fen'],unknown_squares=tuple(tuple(s) for s in row.get('unknown_squares',[])))
        move=find_move(pos,row['move']);obs=observe(pos,move)
        if obs is None:continue
        descriptor=project(obs['descriptor'],projection);identifier=key(descriptor,projection)
        payload={'input':{'fen':row['fen'],'move':row['move'],'unknown_squares':row.get('unknown_squares',[])},
            'position_fixture':row['position_fixture'],'structural_family':row['family'],
            'global_label':row['label'],'local_transition_label':row['movement_label'],
            'exposure_labels':row['attack_labels'],'descriptor':descriptor,'complete_descriptor':obs['descriptor'],
            'typed_observations':obs['propositions'],'dependence_group':row['dependence_group'],
            'transformation_lineage':row.get('transformation_lineage',[]),'source':row['source'],
            'observation_tv':TV(float(row['movement_label']),row['confidence'] if obs['complete'] else 0).json(),
            'runtime_version':runtime.version,'hypothesis_id':identifier,
            'scope':'Offline pseudo-legal transition label; king exposure is not folded into this target.'}
        evidence_id=digest(payload);ledger.append({'evidence_id':evidence_id,'payload':payload})
        if not payload['observation_tv']['confidence']:
            skipped.append({'evidence_id':evidence_id,'reason':'incomplete observation / zero evidence'});continue
        observations[identifier].append((evidence_id,payload))
    jobs=[];states={}
    for identifier,rows in sorted(observations.items()):
        bygroup=defaultdict(list)
        for evidence,p in rows:bygroup[p['dependence_group']].append((evidence,p))
        chosen=[];seen_ancestors=set()
        for group,records in sorted(bygroup.items()):
            if variant=='no-dependence':
                chosen.extend(records);continue
            labels={p['local_transition_label'] for _,p in records}
            if len(labels)>1:
                skipped.extend({'evidence_id':e,'reason':'ambiguous labels in the same source group'} for e,_ in records);continue
            evidence,p=records[0];ancestry={group,*p['transformation_lineage']}
            if ancestry&seen_ancestors:
                skipped.extend({'evidence_id':e,'reason':'shared transformation ancestry'} for e,_ in records);continue
            seen_ancestors.update(ancestry);chosen.append((evidence,p))
            skipped.extend({'evidence_id':e,'reason':'same source group already counted'} for e,_ in records[1:])
        if not chosen:continue
        refs=[PRIOR.metta(),PRIOR.metta()];ids=[];positive=[];negative=[];groups=set()
        for evidence,p in chosen:
            ids.append(evidence);groups.update([p['dependence_group'],*p['transformation_lineage']])
            (positive if p['local_transition_label'] else negative).append(evidence)
            for channel,label in enumerate((p['local_transition_label'],not p['local_transition_label'])):
                name=f'c8train{len(jobs)}'
                jobs.append((name,f'(Truth_Revision {refs[channel]} {TV(float(label),p["observation_tv"]["confidence"]).metta()})'))
                refs[channel]=f'({name})'
        states[identifier]={'id':identifier,'descriptor':chosen[0][1]['descriptor'],'target':'LocalAdmissibility','tier':4,
            'evidence_ids':ids,'supporting_evidence':positive,'contradicting_evidence':negative,
            'dependence_groups':sorted(groups),'refs':refs,'origin':'native-revision-of-relative-promotion-observations'}
    values=runtime.batch(jobs)
    for identifier,h in states.items():
        refs=h.pop('refs');model.hypotheses[identifier]={**h,'positive':values[refs[0][1:-1]].json(),'negative':values[refs[1][1:-1]].json()}
    model.training_report={'records':len(ledger),'native_revision_nodes':len(jobs),'hypotheses':len(model.hypotheses),
        'ledger_digest':digest(ledger),'skipped_records':len(skipped),'skipped_digest':digest(skipped),
        'dependence_aware':variant!='no-dependence','retracted_groups':sorted(retract_groups),
        'dataset_hash':data['hash'],'projection_variant':projection,
        'scope':'Local promotion eligibility, not a complete legality or safety theorem. No historical checkpoint is revised.'}
    if out:
        out=Path(out);model.export(out/f'model/{model.variant}.json')
        pack(out/f'training/{model.variant}-ledger.json.xz',{'records':ledger,'excluded':skipped,
            'native_revision_expressions':jobs,'native_revision_outputs':{k:v.json() for k,v in values.items()}})
    return model


def run(out):
    out=Path(out);rt=Runtime(timeout=600);data=read_json(out/'datasets/dataset.json')
    source=BackoffModel.load(ROOT/'artifacts/cycle7/model/C7-learned-8.json',rt)
    frozen=PromotionModel.wrap(BackoffModel.load(ROOT/'artifacts/cycle7/model/C7-frozen.json',rt),'C8-frozen')
    frozen.export(out/'model/C8-frozen.json')
    for variant in ('C8-promotion-relative',*read_json(ROOT/'configs/cycle8.json')['ablations']):
        model=train(data,source,rt,variant,out);print(model.variant,model.training_report,flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',required=True);run(parser.parse_args().out)
