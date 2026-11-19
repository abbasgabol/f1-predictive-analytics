"""Build a clean dataset. Never requests the target race result or starting grid."""
from pathlib import Path
import json, hashlib, re, sys, zipfile, xml.etree.ElementTree as ET
import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'data'
TARGET = 12
BASE = 'https://www.formula1.com'
TARGET_URL = BASE + '/en/results/2026/races/1292/netherlands/qualifying'

def local_history(path):
    ns = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    with zipfile.ZipFile(path) as z:
        root = ET.fromstring(z.read('xl/worksheets/sheet1.xml'))
    rows = root.find('m:sheetData', ns)
    def value(cell):
        return ''.join(cell.itertext())
    headers = [value(c) for c in rows[0]]
    history = []
    for row in rows[1:]:
        # Read round first; target outcomes are never decoded or copied.
        if int(value(row[0])) >= TARGET:
            continue
        item = dict(zip(headers, map(value, row)))
        history.append({k: item[k] for k in ('round','gp','driver','team','finish_position')})
    return history

def get_page(url):
    if not url.endswith('/qualifying'):
        raise ValueError('Only qualifying endpoints permitted')
    r = requests.get(url, timeout=40)
    r.raise_for_status()
    return BeautifulSoup(r.text, 'html.parser')

def table(soup, rnd, gp):
    rows = []
    for tr in soup.select('table tbody tr'):
        cells = [c.get_text(' ', strip=True).replace('\xa0',' ') for c in tr.select('td')]
        if len(cells) < 7:
            continue
        code = re.search(r'\b([A-Z]{3})\b\s*$', cells[2])
        if not code:
            raise ValueError(cells)
        pos = int(cells[0]) if cells[0].isdigit() else None
        rows.append(dict(round=rnd, gp=gp, driver=code.group(1),
                         name=cells[2][:code.start()].strip(), team=cells[3],
                         qualifying_position=pos, q1=cells[4], q2=cells[5], q3=cells[6]))
    if not 18 <= len(rows) <= 22 or len({r['driver'] for r in rows}) != len(rows):
        raise ValueError(f'Unexpected qualifying field: round {rnd}, {len(rows)} rows')
    # Unclassified qualifying entrants stay in the field, tied behind classified drivers.
    for r in rows:
        if r['qualifying_position'] is None:
            r['qualifying_position'] = 22
    return rows

def main():
    DATA.mkdir(parents=True, exist_ok=True)
    hist = local_history(ROOT.parent / 'f1_2026_final_dataset.xlsx')
    soup = get_page(TARGET_URL)
    links = {}
    for a in soup.select('a[href]'):
        href = a['href']
        match = re.search(r'/en/results/2026/races/(\d+)/([^/]+)/race-result', href)
        if match:
            links[match.group(2)] = BASE + match.group(0).replace('/race-result','/qualifying')
    aliases = {'Great Britain':'great-britain','Barcelona':'barcelona-catalunya'}
    qualifying = []
    sources = []
    for rnd, gp in sorted({(int(r['round']), r['gp']) for r in hist}):
        slug = aliases.get(gp, gp.lower())
        if slug not in links:
            raise ValueError(f'Missing official URL for {gp}; available: {links}')
        url = links[slug]
        classified = table(get_page(url), rnd, gp)
        seen = {r['driver'] for r in classified}
        for h in hist:
            if int(h['round']) == rnd and h['driver'] not in seen:
                classified.append(dict(round=rnd, gp=gp, driver=h['driver'], name=h['driver'],
                    team=h['team'], qualifying_position=22, q1='', q2='', q3=''))
        qualifying.extend(classified)
        sources.append({'round':rnd, 'url':url, 'session':'qualifying'})
        print(f'Fetched round {rnd}: {gp}', flush=True)
    target = table(soup, TARGET, 'Netherlands')
    assert len(target) == 22
    sources.append({'round':TARGET,'url':TARGET_URL,'session':'qualifying'})
    by_key = {(int(r['round']),r['driver']):r for r in hist}
    train = []
    for q in qualifying:
        h = by_key[(q['round'],q['driver'])]
        p = h['finish_position']
        train.append({**q, 'finish_position':int(float(p))})
    for name, obj in [('history.json',train),('target_qualifying.json',target)]:
        (DATA/name).write_text(json.dumps(obj, indent=2), encoding='utf-8')
    manifest = {'cutoff':'End of Dutch GP qualifying, 22 August 2026',
                'historical_labels':'G:/f1_2026_final_dataset.xlsx, Full Dataset, rounds 1-11 only; not independently fully verified',
                'target_outcomes_in_export':False,'sources':sources,
                'sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in DATA.glob('*.json')}}
    (DATA/'provenance.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print('Saved clean training and target qualifying data.')

if __name__ == '__main__':
    main()
