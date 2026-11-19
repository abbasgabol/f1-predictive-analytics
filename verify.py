"""Verify original snapshots; optionally replay all forecasts in an isolated copy."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from run import ROOT, RACES

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--replay', action='store_true', help='Reproduce all five prediction JSON files in an ignored temporary copy.')
    args = parser.parse_args()
    manifest = json.loads((ROOT/'snapshot_manifest.json').read_text(encoding='utf-8'))['files']
    for relative, expected in manifest.items():
        path = ROOT/relative
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise RuntimeError(f'Original snapshot changed or missing: {relative}')
    print(f'PASS: {len(manifest)} original files match their recorded SHA-256 hashes.', flush=True)
    if not args.replay:
        return
    work = ROOT/'.verification'
    work.mkdir(exist_ok=True)
    replay = Path(tempfile.mkdtemp(prefix='replay-', dir=work))
    shutil.copytree(ROOT/'races', replay/'races', ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '.deps', 'f1-cleanroom-*'))
    guard = replay/'offline.py'
    guard.write_text('''import runpy,sys
from pathlib import Path
sys.path.insert(0,str(Path(sys.argv[1]).resolve().parent))
def no_network(event,args):
    if event in ('socket.connect','socket.getaddrinfo','socket.bind'):
        raise RuntimeError('Network disabled for snapshot reproduction')
sys.addaudithook(no_network)
runpy.run_path(sys.argv[1],run_name='__main__')
''', encoding='utf-8')
    results = []
    for race,(folder,script) in RACES.items():
        original = ROOT/'races'/folder/'outputs/prediction.json'
        expected = json.loads(original.read_text(encoding='utf-8'))
        copied = replay/'races'/folder
        result = subprocess.run([sys.executable,str(guard),script],cwd=copied,capture_output=True,text=True,timeout=300)
        (replay/f'{race}.log').write_text(result.stdout+'\n'+result.stderr,encoding='utf-8')
        if result.returncode:
            raise RuntimeError(f'{race} replay failed: {result.stderr}')
        actual = json.loads((copied/'outputs/prediction.json').read_text(encoding='utf-8'))
        if actual != expected:
            raise RuntimeError(f'{race} replay differs from the original prediction JSON')
        results.append({'race':race,'status':'PASS','comparison':'Full prediction JSON exactly reproduced'})
        print(f'PASS: {race} forecast reproduced exactly with network disabled.',flush=True)
    # Confirm that verification itself never overwrote the tracked originals.
    for relative, expected in manifest.items():
        assert hashlib.sha256((ROOT/relative).read_bytes()).hexdigest()==expected
    (work/'latest.json').write_text(json.dumps({'results':results,'original_files_unchanged':True},indent=2),encoding='utf-8')
    print('All five forecasts reproduced; original snapshots unchanged.',flush=True)

if __name__ == '__main__':
    main()
