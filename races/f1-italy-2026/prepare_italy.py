"""Fetch only Italian qualifying. Import prior race data from local snapshots/workbook."""
from pathlib import Path
import sys, json, hashlib
ROOT = Path(__file__).resolve().parent
PRIOR = ROOT.parent/'f1-dutch-2026'
sys.path.insert(0,str(PRIOR))
import prepare_data as source

URL = 'https://www.formula1.com/en/results/2026/races/1293/italy/qualifying'

def main():
    history=json.loads((PRIOR/'data/history.json').read_text())
    dutch=json.loads((PRIOR/'data/target_qualifying.json').read_text())
    source.TARGET=13
    results={r['driver']:r for r in source.local_history(ROOT.parent/'f1_2026_final_dataset.xlsx') if int(r['round'])==12}
    actual=sorted(results,key=lambda d:int(results[d]['finish_position']))[:3]
    assert actual==['NOR','ANT','RUS'], 'Local Dutch labels disagree with user-supplied podium'
    for row in dutch:
        history.append({**row,'finish_position':int(results[row['driver']]['finish_position'])})
    target=source.table(source.get_page(URL),13,'Italy')
    assert len(target)==22
    data=ROOT/'data'; data.mkdir(exist_ok=True)
    for name,rows in [('history.json',history),('target_qualifying.json',target)]:
        (data/name).write_text(json.dumps(rows,indent=2),encoding='utf-8')
    manifest={
        'cutoff':'End of Italian GP qualifying, 5 September 2026',
        'target_source':URL,
        'historical_sources':['../f1-dutch-2026/data/history.json','../f1-dutch-2026/data/target_qualifying.json','../f1_2026_final_dataset.xlsx (round 12 only)'],
        'training_rounds':list(range(1,13)),
        'target_race_outcomes_in_model_data':False,
        'disclosure':'A web qualifying search incidentally exposed a race-result snippet to the assistant. It is not in the model data. Existing model architecture, features, regularization and evaluation protocol were retained unchanged. This is not claimed to be a fully blind assistant forecast.',
        'snapshot_limitation':'Retrospective qualifying classifications; exact as-of publication state not certified.',
        'sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in data.glob('*.json') if p.name!='provenance.json'}}
    (data/'provenance.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print(f'Saved {len(history)} historical rows and {len(target)} qualifying-only target rows.')

if __name__=='__main__': main()
