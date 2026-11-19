"""Run any saved race model from one repository, independent of current directory."""
from pathlib import Path
import argparse
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
RACES = {
    'dutch': ('f1-dutch-2026', 'model.py'),
    'italy': ('f1-italy-2026', 'model.py'),
    'spain': ('f1-spain-2026', 'predict.py'),
    'azerbaijan': ('f1-azerbaijan-2026', 'predict.py'),
    'bahrain': ('f1-bahrain-2026', 'predict.py'),
}

def run_race(race, tests=False):
    folder, script = RACES[race]
    command = [sys.executable, '-m', 'unittest', 'discover', '-p', 'test_*.py', '-v'] if tests else [sys.executable, script]
    print(f"{'Testing' if tests else 'Running'} {race}...", flush=True)
    return subprocess.call(command, cwd=ROOT/'races'/folder)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('race', choices=[*RACES, 'all'])
    parser.add_argument('--test', action='store_true', help='Run existing leakage and model-selection tests.')
    args = parser.parse_args()
    races = RACES if args.race == 'all' else [args.race]
    for race in races:
        code = run_race(race, args.test)
        if code:
            return code
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
