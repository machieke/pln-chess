"""Public source acquisition, explicit rights and immutable download receipts."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
from pathlib import Path
import urllib.request

from pln_chess.common import ROOT, read_json, write_json, digest
from scripts.cycle9_baseline import sha

TCEC = read_json(ROOT/'configs/cycle10.json')['source_commit_tcec']
SOURCES = [
    dict(id='lichess-rated-2013-01',population='Online rated human games, January 2013; mixed ratings and time controls',
         url='https://database.lichess.org/standard/lichess_db_standard_rated_2013-01.pgn.zst',
         filename='lichess-rated-2013-01.pgn.zst',license='CC0-1.0',
         license_url='https://creativecommons.org/publicdomain/zero/1.0/',publisher='Lichess',
         terms_url='https://database.lichess.org/',checksum_url='https://database.lichess.org/standard/sha256sums.txt'),
    dict(id='lichess-broadcast-2024-01',population='Official tournament broadcasts, January 2024; tournament participants, not Lichess rated server games',
         url='https://database.lichess.org/broadcast/lichess_db_broadcast_2024-01.pgn.zst',
         filename='lichess-broadcast-2024-01.pgn.zst',license='CC-BY-SA-4.0',
         license_url='https://creativecommons.org/licenses/by-sa/4.0/',publisher='Lichess and credited tournament broadcasters',
         terms_url='https://database.lichess.org/',checksum_url='https://database.lichess.org/broadcast/sha256sums.txt'),
    dict(id='tcec-season26-divisionp',population='TCEC Season 26 Premier Division; engine tournament with paired book openings',
         url=f'https://raw.githubusercontent.com/TCEC-Chess/tcecgames/{TCEC}/master-archive/TCEC_Season_26_-_Division_P.pgn',
         filename='tcec-season26-divisionp.pgn',license='CC-BY-SA-3.0',
         license_url='https://creativecommons.org/licenses/by-sa/3.0/',publisher='Top Chess Engine Championship organization',
         terms_url=f'https://raw.githubusercontent.com/TCEC-Chess/tcecgames/{TCEC}/README.md',upstream_commit=TCEC),
]


def fetch(url, path, limit=80_000_000):
    request=urllib.request.Request(url,headers={'User-Agent':'PLN-Chess-Cycle10-research/1.0'})
    started=datetime.now(timezone.utc).isoformat();path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    temporary=path.with_suffix(path.suffix+'.part');size=0
    with urllib.request.urlopen(request,timeout=90) as response, temporary.open('wb') as stream:
        headers=dict(response.headers); final=response.geturl()
        while block:=response.read(1024*1024):
            size+=len(block)
            if size>limit:raise ValueError('Registered download size guard exceeded')
            stream.write(block)
    temporary.replace(path)
    return dict(requested_url=url,final_url=final,acquired_utc=started,sha256=sha(path),bytes=size,
                headers={k:v for k,v in headers.items() if k.lower() in ('content-length','last-modified','etag','content-type')})


def acquire(out):
    out=Path(out);base=out/'sources';base.mkdir(parents=True,exist_ok=True)
    def one(source):
        folder=base/source['id'];folder.mkdir(exist_ok=True);receipt=folder/'receipt.json'
        if receipt.exists():
            old=read_json(receipt)
            assert old['source']==source
            assert all(sha(folder/r['file'])==r['sha256'] for r in old['downloads'].values())
            return old
        downloads={}
        for role,url,name in [('terms',source['terms_url'],'publisher-terms.txt'),('license',source['license_url'],'license.html'),('data',source['url'],source['filename'])]:
            downloads[role]={**fetch(url,folder/name),'file':name}
        terms=(folder/'publisher-terms.txt').read_text()
        if source['license']=='CC0-1.0':assert 'CC0' in terms
        elif source['license']=='CC-BY-SA-4.0':assert 'by-sa/4.0' in terms
        else:assert 'BY-SA 3.0' in terms
        integrity={'local_sha256_verified':True,'publisher_checksum_verified':False}
        if source.get('checksum_url'):
            try:
                downloads['checksums']={**fetch(source['checksum_url'],folder/'sha256sums.txt'),'file':'sha256sums.txt'}
                name=source['url'].rsplit('/',1)[-1]
                expected=next(line.split()[0] for line in (folder/'sha256sums.txt').read_text().splitlines() if line.split()[-1].lstrip('*').rsplit('/',1)[-1]==name)
                assert expected==downloads['data']['sha256'];integrity['publisher_checksum_verified']=True
            except (urllib.error.HTTPError,StopIteration) as error:
                integrity['publisher_checksum_unavailable']=str(error)
        result=dict(source=source,downloads=downloads,integrity=integrity,
                    permitted_use='Research, modification and redistribution under the recorded license; attribution and ShareAlike retained.',
                    attribution=f"{source['publisher']}; {source['url']}; {source['license']}")
        result['id']=digest(result);write_json(receipt,result);return result
    with ThreadPoolExecutor(max_workers=3) as pool:records=list(pool.map(one,SOURCES))
    write_json(base/'manifest.json',dict(schema=10,sources=records,independence='Three underlying game collections, two publishing organizations. Shared publisher alone is neither proof nor disproof of game independence; content audits follow.',
        rejected_alternatives={'FICS':'No explicit redistribution license verified; not acquired.','Caissabase':'Mixed archive ancestry and no explicit reusable license verified; not acquired.'}))
    (base/'ATTRIBUTION.txt').write_text('\n\n'.join(r['attribution']+'\nLicense: '+r['source']['license_url'] for r in records)+'\n\nOriginal source files retain their licenses. Derived combined evaluation corpus: CC BY-SA 4.0. Code licensing is unchanged. PGN metadata and complete move sequences retained; comments/variations excluded from derived records.\n')
    print([(r['source']['id'],r['downloads']['data']['sha256']) for r in records])


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);acquire(p.parse_args().out)
