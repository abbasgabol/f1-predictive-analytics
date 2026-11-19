"""Offline adversarial audit; original forecasts and data remain untouched."""
import copy, hashlib, json, os, shutil, subprocess, sys, tempfile
from pathlib import Path
import model as m
import selection as s
import numpy as np

ROOT=m.ROOT

def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def independent_features(field,history):
    values=[]
    for row in field:
        earlier=[r for r in history if int(r['round'])<int(row['round'])]
        starts=sorted([r for r in earlier if r['driver']==row['driver']],key=lambda r:r['round'])
        teammates=[r for r in earlier if r['team']==row['team']]
        rounds=sorted(set(r['round'] for r in teammates))[-3:]
        form=starts[-3:]
        team=[r for r in teammates if r['round'] in rounds]
        values.append([(23-row['qualifying_position'])/22,
            sum(23-r['finish_position'] for r in form)/(22*len(form)) if form else .5,
            (sum(r['finish_position']<=3 for r in starts)+6/22)/(len(starts)+2),
            sum(23-r['finish_position'] for r in team)/(22*len(team)) if team else .5])
    return np.array(values)

def main():
    out=ROOT/'audit'; out.mkdir(exist_ok=True)
    protected=[*sorted((ROOT/'data').glob('*.json')),*sorted((ROOT/'outputs').glob('*')),
               ROOT/'model.py',ROOT/'selection.py',ROOT/'predict.py']
    before={str(p):digest(p) for p in protected}
    history=json.loads((ROOT/'data/history.json').read_text())
    target=json.loads((ROOT/'data/target_qualifying.json').read_text())
    frozen=json.loads((ROOT/'outputs/model.json').read_text())
    forecast=json.loads((ROOT/'outputs/prediction.json').read_text())
    checks=[]
    def passed(name,detail):
        checks.append(dict(check=name,status='PASS',detail=detail)); print('PASS:',name,flush=True)

    m.check_data(history,target)
    assert len(history)==330 and max(r['round'] for r in history)==15
    assert {r['gp'] for r in target}=={'Bahrain'}
    passed('Training cutoff and target field allowlist','330 rows from rounds 1–15; 22 Bahrain qualifying rows, no target outcome fields.')
    for name,sha in frozen['sha256'].items(): assert digest(ROOT/'data'/name)==sha
    for name,sha in frozen['implementation_sha256'].items(): assert digest(ROOT/name)==sha
    passed('Frozen input and implementation hashes','Every recorded data/code SHA-256 matches the original forecast artifact.')

    # Rebuild every historical and target feature independently; no input feature cache.
    for rnd in range(1,17):
        field=[r for r in history+target if r['round']==rnd]
        np.testing.assert_allclose(m.features(field,history),independent_features(field,history),atol=1e-14)
    passed('Independent feature reconstruction','All 352 driver rows agree with independently calculated strictly-prior-race features.')

    for rnd in range(1,16):
        field=[r for r in history if r['round']==rnd]
        poison=copy.deepcopy(history)
        for row in poison:
            if row['round']>=rnd:
                row['finish_position']=23-row['finish_position']
                row['points']=100000
                row['status']='POISON'
        np.testing.assert_array_equal(m.features(field,history),m.features(field,poison))
    passed('Every-race future-label poisoning','Changing current/future outcomes cannot change the features for any of rounds 1–15.')

    for key in ['finish_position','podium','points','status','race_time','final_grid']:
        poison=copy.deepcopy(target); poison[0][key]=999
        try: m.check_data(history,poison)
        except AssertionError: pass
        else: raise AssertionError('Target leak accepted: '+key)
    poison_history=history+[dict(r,finish_position=i+1) for i,r in enumerate(target)]
    try: m.check_data(poison_history,target)
    except AssertionError: pass
    else: raise AssertionError('Target race accepted as training history')
    passed('Target contamination rejected','Six prohibited field types and Bahrain rows injected into training are rejected by production validation.')

    candidate=frozen['selected_model']; w=s.fit(history,candidate)
    np.testing.assert_allclose(w,frozen['coefficients'],atol=1e-12)
    shuffled=copy.deepcopy(history); np.random.default_rng(12).shuffle(shuffled)
    np.testing.assert_allclose(s.fit(shuffled,candidate),w,atol=1e-12)
    drivers={d:f'driver_{i:02d}' for i,d in enumerate(sorted({r['driver'] for r in history+target}))}
    teams={d:f'team_{i:02d}' for i,d in enumerate(sorted({r['team'] for r in history+target}))}
    renamed=[dict(r,driver=drivers[r['driver']],team=teams[r['team']]) for r in history]
    renamed_target=[dict(r,driver=drivers[r['driver']],team=teams[r['team']]) for r in target]
    np.testing.assert_allclose(s.fit(renamed,candidate),w,atol=1e-10)
    np.testing.assert_allclose(m.features(renamed_target,renamed),m.features(target,history),atol=1e-12)
    passed('Row-order and identity controls','Training-row shuffling and consistent driver/team anonymization preserve fitted coefficients and target features.')

    # Replay actual production entry point with only code and cutoff-safe data.
    # Use a separate folder beside project so dependency lookup still resolves.
    clean=Path(tempfile.mkdtemp(prefix='f1-cleanroom-',dir=ROOT.parent))
    (clean/'data').mkdir()
    for name in ['model.py','selection.py','predict.py']: shutil.copyfile(ROOT/name,clean/name)
    for p in (ROOT/'data').glob('*.json'): shutil.copyfile(p,clean/'data'/p.name)
    runner='''import sys,runpy
from pathlib import Path
original=Path(sys.argv[1]).resolve()
def guard(event,args):
    if event in ('socket.connect','socket.getaddrinfo','socket.bind'):
        raise RuntimeError('Network forbidden during clean-room replay')
    if event=='open' and isinstance(args[0],(str,bytes)):
        path=Path(args[0]).resolve()
        if path==original or original in path.parents or path.suffix.lower()=='.xlsx':
            raise RuntimeError('Original project/workbook read forbidden')
sys.addaudithook(guard)
runpy.run_path('predict.py',run_name='__main__')
'''
    (clean/'replay.py').write_text(runner,encoding='utf-8')
    run=subprocess.run([sys.executable,'replay.py',str(ROOT)],cwd=clean,capture_output=True,text=True,timeout=180)
    (out/'cleanroom.log').write_text(run.stdout+'\n'+run.stderr,encoding='utf-8')
    if run.returncode: raise RuntimeError(run.stderr)
    replay=json.loads((clean/'outputs/prediction.json').read_text())
    assert replay==forecast, 'Clean-room replay differs from frozen forecast'
    passed('Offline clean-room production replay','Entire prediction JSON reproduced exactly, including selection, probabilities and validation; original project/workbooks and network access blocked.')

    # Descriptive negative control, not a significance test: fixed existing four-feature
    # model, no retuning. Rebuild form features after permuting outcome labels per race.
    rng=np.random.default_rng(20261109)
    def performance(rows):
        hits=[]
        for rnd in range(7,16):
            train=[r for r in rows if r['round']<rnd]
            test=[r for r in rows if r['round']==rnd]
            hits.append(s.score(test,train,candidate,s.fit(train,candidate))['hits'])
        return float(np.mean(hits))
    real_hits=performance(history); shuffled_hits=[]
    for trial in range(30):
        rows=copy.deepcopy(history)
        for rnd in range(1,16):
            group=[r for r in rows if r['round']==rnd]
            labels=rng.permutation([r['finish_position'] for r in group])
            for row,label in zip(group,labels): row['finish_position']=int(label)
        shuffled_hits.append(performance(rows))
    negative=dict(protocol='30 within-race label permutations; fixed original four-feature model, chronological held-outs 7–15; form recomputed. Descriptive control, not a calibrated significance test.',
        real_labels_mean_hits=real_hits,shuffled_mean_hits=float(np.mean(shuffled_hits)),
        shuffled_min=float(min(shuffled_hits)),shuffled_max=float(max(shuffled_hits)),
        uniform_random_expected_hits=9/22,all_shuffled_means=shuffled_hits)
    passed('Random-label negative control completed',f"Real labels: {real_hits:.3f}/3 mean hits; shuffled labels: {np.mean(shuffled_hits):.3f}/3. See caveats; this is supporting evidence, not proof.")
    assert before=={str(p):digest(p) for p in protected}
    result=dict(conclusion='No evidence of target-result leakage in the saved Bahrain modeling pipeline under these tests.',
        checks=checks,negative_control=negative,cleanroom_directory=str(clean),
        original_files_unchanged=True,
        limitations=['Cannot certify upstream workbook labels or the exact historical publication state of qualifying pages.',
            'Hashes demonstrate consistency with saved artifacts, not independently timestamped provenance.',
            'Italian forecast had incidental assistant search exposure; code audit cannot make the full conversation blind.',
            'Repeated model development on known history and a small sample limit claims about generalization.',
            'No Bahrain actual outcome is used in these tests or model fitting.'])
    (out/'AUDIT.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    lines=['# Bahrain model leakage audit','',result['conclusion'],'',
        '## Executed checks','']+[f"- **{r['status']} — {r['check']}:** {r['detail']}" for r in checks]
    lines += ['', '## Interpretation','',
        'Correct podium names alone do not establish leakage. The model can reproduce the forecast from only earlier race results and qualifying inputs. It does not need to read Bahrain race labels, saved predictions, or a network service to compute its prediction.',
        'A random-label control disrupts the real relationship between features and outcomes. Losing useful predictive signal under this control is reassuring, but is not an exhaustive proof of no leakage.',
        'The 80% podium-driver hit rate previously quoted came from five sequential chat forecasts, not a large independent benchmark. It does not imply 80% probability of an exact ordered podium.',
        '', '## What this cannot prove','']+['- '+r for r in result['limitations']]
    (out/'REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps(negative,indent=2))

if __name__=='__main__': main()
