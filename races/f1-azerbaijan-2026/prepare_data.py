"""Only target qualifying and the preceding Spanish race result are permitted."""
from pathlib import Path
import json, re, hashlib
import requests
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parent
PRIOR=ROOT.parent/'f1-spain-2026'
QUAL='https://www.formula1.com/en/results/2026/races/1295/azerbaijan/qualifying'
PREVIOUS='https://www.formula1.com/en/results/2026/races/1294/spain/race-result'
ALLOWED={QUAL,PREVIOUS}

def fetch(url):
    if url not in ALLOWED: raise ValueError('URL outside cutoff allowlist')
    response=requests.get(url,timeout=40,allow_redirects=False)
    response.raise_for_status()
    if response.status_code!=200: raise ValueError('Redirect refused')
    soup=BeautifulSoup(response.text,'html.parser')
    result=[]
    for tr in soup.select('table tbody tr'):
        c=[td.get_text(' ',strip=True).replace('\xa0',' ') for td in tr.select('td')]
        if not c: continue
        match=re.search(r'\b([A-Z]{3})\b\s*$',c[2])
        if not match: raise ValueError('Unrecognized driver')
        result.append((match.group(1),c[2][:match.start()].strip(),c))
    return result

def main():
    history=json.loads((PRIOR/'data/history.json').read_text())
    previous_qual=json.loads((PRIOR/'data/target_qualifying.json').read_text())
    previous_result=fetch(PREVIOUS)
    assert len(previous_result)==22
    assert [r[0] for r in previous_result[:3]]==['ANT','VER','NOR'], 'Disagrees with supplied Spanish podium'
    ranks={r[0]:i+1 for i,r in enumerate(previous_result)}
    history += [{**r,'finish_position':ranks[r['driver']]} for r in previous_qual]
    target=[]
    for driver,name,c in fetch(QUAL):
        target.append(dict(round=15,gp='Azerbaijan',driver=driver,name=name,team=c[3],
            qualifying_position=int(c[0]) if c[0].isdigit() else 22,q1=c[4],q2=c[5],q3=c[6]))
    assert len(target)==22 and len({r['driver'] for r in target})==22
    data=ROOT/'data'
    for name,obj in [('history.json',history),('target_qualifying.json',target)]:
        (data/name).write_text(json.dumps(obj,indent=2),encoding='utf-8')
    manifest=dict(event='Azerbaijan Grand Prix, Baku',cutoff='End of qualifying, 25 September 2026',
        requested_urls=sorted(ALLOWED),target_race_result_requested=False,
        historical_sources='Prior Spanish-project snapshots through Italy; official Spanish race classification for round 14.',
        missing_target_qualifying_drivers=[],
        historical_nc_handling='Official classification table order for trailing NC ranks, consistent with the existing preprocessing rule.',
        snapshot_limitation='Retrospective qualifying classifications; exact as-of publication snapshots unavailable.',
        sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in data.glob('*.json') if p.name!='provenance.json'})
    (data/'provenance.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print(f'Saved {len(history)} historical entries and {len(target)} target qualifiers.')

if __name__=='__main__': main()
