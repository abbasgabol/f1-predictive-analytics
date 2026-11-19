"""Strict URL allowlist: Spanish qualifying/practice and preceding Italian result."""
from pathlib import Path
import sys, json, hashlib, re
import requests
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parent
PRIOR=ROOT.parent/'f1-italy-2026'
QUAL='https://www.formula1.com/en/results/2026/races/1294/spain/qualifying'
PRACTICE='https://www.formula1.com/en/results/2026/races/1294/spain/practice/3'
ITALY='https://www.formula1.com/en/results/2026/races/1293/italy/race-result'
ALLOWED={QUAL,PRACTICE,ITALY}

def fetch(url):
    if url not in ALLOWED: raise ValueError('URL outside cutoff allowlist')
    response=requests.get(url,timeout=40,allow_redirects=False)
    response.raise_for_status()
    if response.status_code!=200: raise ValueError('Redirects are not allowed')
    soup=BeautifulSoup(response.text,'html.parser')
    rows=[]
    for tr in soup.select('table tbody tr'):
        cells=[c.get_text(' ',strip=True).replace('\xa0',' ') for c in tr.select('td')]
        if not cells: continue
        match=re.search(r'\b([A-Z]{3})\b\s*$',cells[2])
        if not match: raise ValueError('Unrecognized driver')
        rows.append((match.group(1),cells[2][:match.start()].strip(),cells))
    return rows

def main():
    history=json.loads((PRIOR/'data/history.json').read_text())
    italy_qual=json.loads((PRIOR/'data/target_qualifying.json').read_text())
    result=fetch(ITALY)
    assert len(result)==22
    assert [r[0] for r in result[:3]]==['ANT','RUS','VER']
    # Official classification table order assigns distinct trailing ranks to NC entries.
    positions={row[0]:i+1 for i,row in enumerate(result)}
    history += [{**r,'finish_position':positions[r['driver']]} for r in italy_qual]
    target=[]
    for driver,name,c in fetch(QUAL):
        target.append(dict(round=14,gp='Spain',driver=driver,name=name,team=c[3],
            qualifying_position=int(c[0]) if c[0].isdigit() else 22,q1=c[4],q2=c[5],q3=c[6]))
    seen={r['driver'] for r in target}; missing=[]
    practice=fetch(PRACTICE)
    for driver,name,c in practice:
        if driver not in seen:
            target.append(dict(round=14,gp='Spain',driver=driver,name=name,team=c[3],
                qualifying_position=22,q1='',q2='',q3=''))
            missing.append(driver)
    assert len(target)==22 and len({r['driver'] for r in target})==22
    data=ROOT/'data'
    for name,obj in [('history.json',history),('target_qualifying.json',target)]:
        (data/name).write_text(json.dumps(obj,indent=2),encoding='utf-8')
    manifest=dict(cutoff='End of Spanish Grand Prix qualifying, 12 September 2026',
        event='Spanish Grand Prix at Madring, Madrid; not the earlier Barcelona-Catalunya GP',
        requested_urls=sorted(ALLOWED),target_race_result_requested=False,
        missing_qualifying_drivers=missing,
        missing_qualifying_handling='Entrants confirmed in practice 3 receive tied qualifying rank 22, consistent with the historical preprocessing rule.',
        historical_labels='Prior local snapshots through Netherlands; official Italian GP race classification for round 13.',
        historical_nc_handling='Italian NC entries receive ranks from official table order, consistent with full-field training ranks.',
        snapshot_limitation='Retrospective classifications, not archived as-of publication snapshots.',
        sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in data.glob('*.json') if p.name!='provenance.json'})
    (data/'provenance.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print(f'Saved {len(history)} prior-race rows and {len(target)} target entrants. Missing qualifying ranks: {missing}')

if __name__=='__main__': main()
