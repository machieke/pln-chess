"""Evidence-linked Cycle 10 reports; measurements are read from delivered artifacts."""
import argparse
from collections import Counter
from pathlib import Path
import statistics
from pln_chess.common import ROOT,read_json,write_json
from scripts.cycle9_baseline import sha


def architecture(out):
    out=Path(out)
    write_json(out/'architecture/decision.json',dict(schema=10,production_composition_extension='no-go',
        new_operator_enabled=False,upstream_modified=False,strategic_selector_enabled=False,handcoded_evaluation_score_enabled=False,
        isolated_prototype_enabled=False,prior_decision='docs/cycle9/architecture-decision.md',
        prior_decision_sha256=sha(ROOT/'docs/cycle9/architecture-decision.md'),
        prior_composition_review_sha256=sha(ROOT/'artifacts/cycle9/composition/review.json'),
        new_requirements=['Transport event identity, trust, dependence and state scope without creating missing historical facts.',
                          'Measure external calibration drift separately from raw native truth values.',
                          'Future relational fields require target-specific evidence and dependence-preserving successor comparisons.'],
        calculus_conclusion='These requirements do not supply a joint probabilistic model or native proof certificates. No new operator is authorized.',
        classification='Architecture recommendation grounded in existing native boundaries, not an executed new composition experiment.'))
    write_json(out/'architecture/strategic-readiness.json',dict(schema='strategic-proposal-v10',implemented=False,
        fields=['spatial-interaction','attack-defense','mobility','king-exposure','strategic-influence','successor-change'],
        available=['piece-relative observation grammar','native revision','scoped conditional evidence','negative exposure chains','source/evidence lineage'],
        missing=['general non-king defense semantics','joint uncertain-premise composition','universal positive safety proof',
                 'validated influence targets','dependence-preserving strategic successor comparison'],
        position_tables=False,move_selection=False,report='docs/cycle10/strategic-readiness.md',
        report_sha256=sha(ROOT/'docs/cycle10/strategic-readiness.md')))


def provenance(out):
    out=Path(out);data=read_json(out/'datasets/dataset.json');sources=read_json(out/'sources/manifest.json')
    lines=['# External dataset provenance','',
        'The corpus contains **1,308 external positions from 150 complete published game records**, plus **112 separately labelled synthetic adversarial positions**. The final external test has 1,020 positions from 102 games; adaptation and calibration each have 144 positions from 24 different games. [Dataset manifest](../../artifacts/cycle10/datasets/manifest.json).','',
        'Three underlying collections are represented, published by two organizations. The Lichess online-rated and official broadcast collections are distinct populations, not independent merely because they have different download paths. Complete move-sequence hashes and position audits test actual overlap. Player, opening and engine-pair dependence remains possible. [Overlap audit](../../artifacts/cycle10/datasets/overlap-audit.json).','',
        '| Collection | Publisher reuse terms | Download provenance |','|---|---|---|']
    for entry in sources['sources']:
        s=entry['source'];lines.append(f"| {s['id']} | [{s['license']}]({s['license_url']}); [publisher statement]({s['terms_url']}) | [Original download]({s['url']}), [local receipt](../../artifacts/cycle10/sources/{s['id']}/receipt.json) |")
    lines+=['','Original source bytes retain their original licenses. The combined derived corpus is distributed under CC BY-SA 4.0 with [source attribution](../../artifacts/cycle10/sources/ATTRIBUTION.txt); code licensing is unchanged. Original PGNs, terms and license documents are retained, with acquisition timestamps and local SHA-256 hashes. The two Lichess files match publisher checksum lists. The TCEC file additionally matches the Git blob at its pinned commit. [Git-object verification](../../artifacts/cycle10/sources/tcec-git-object-verification.json).','',
        '| Selected source games | Games | Published date range | Recorded rating range / median | Recorded time controls |','|---|---:|---|---|---|']
    for entry in sources['sources']:
        source=entry['source']['id'];games=[g for g in data['games'] if g['source_collection']==source]
        dates=sorted(g['headers'].get('Date','unknown') for g in games);ratings=[]
        for game in games:
            for key in ('WhiteElo','BlackElo'):
                try:ratings.append(int(game['headers'].get(key,'')))
                except ValueError:pass
        rating=f'{min(ratings)}–{max(ratings)} / {statistics.median(ratings):g}' if ratings else 'not recorded'
        controls=Counter(g['headers'].get('TimeControl','not recorded') for g in games)
        lines.append(f"| {source} | {len(games)} | {dates[0]} – {dates[-1]} | {rating} | "+'; '.join(f'{k} ({v})' for k,v in controls.most_common())+' |')
    lines+=['','Ratings across online players and engines are source metadata, not comparable measures of human playing strength. Account type is not independently authenticated, so the online collection is not certified free of bots or other automation. Tournament broadcasts and engine games are not relabelled as online human play.','',
        'The registered sampler takes the first 1,000 valid complete records per source, or the whole archive if smaller, then selects games by content hash within global opening-family partitions. It does not sample uniformly across the complete monthly archive. Source time windows, tournaments, engine opponents and special-move enrichment constrain external validity. The complete record includes resignation or adjudication; it need not end in a rules-terminal position. [Protocol](study-protocol.md), [raw game records and sampled prefixes](../../artifacts/cycle10/datasets/dataset.json).','',
        'All games are replayed by the offline reference library before selection; parse errors, invalid games, short games and unfinished records are counted in the source audit. Headers and archive ordinals supplement original game links, whose Site header can identify a tournament rather than a unique game. Complete move-sequence content hashes provide stable game identities. Neither model predictions nor model errors participate in acquisition, eligibility or sampling.','',
        'The overlap audit checks exact FENs, canonical four-field states, complete game contents and whole-board relative transformations against historical training, validation and evaluation datasets. A supplemental audit covers all eight plane symmetries, owner swaps and translation normalization. It found no historical or repeated equivalents among the 1,420 selected positions. Geometry-equivalent boards are conservatively excluded even if turn or historical eligibility differs. [All-symmetry audit](../../artifacts/cycle10/datasets/all-symmetry-audit.json).','',
        'Opening families are partitioned globally across sources, and games never cross adaptation/calibration/test splits. Recurring exact local descriptors are measured separately; they are expected transferable knowledge, not a claim that every substructure is independent. [Relative-transfer audit](../../artifacts/cycle10/datasets/relative-transfer-audit.json).','',
        'The corpus includes opening, early-middlegame, middlegame and reduced-material endgame positions, including pawn, rook and minor-piece endings. Castling, en-passant, all promotion choices, pin contexts, multiple attackers and discovered-check opportunities are recorded as offline structural strata. Coverage counts and any absent strata remain visible in the [diversity manifest](../../artifacts/cycle10/datasets/manifest.json).','',
        'FICS and Caissabase were considered but not acquired because explicit reusable redistribution terms were not established during the source search. Their absence is not a claim that their data cannot lawfully be used under other circumstances. No private credentials, paid access or network-unavailable fallback was used.','']
    target=ROOT/'docs/cycle10/dataset-provenance.md';target.parent.mkdir(parents=True,exist_ok=True);target.write_text('\n'.join(lines))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);a=p.parse_args();provenance(a.out);architecture(a.out)
