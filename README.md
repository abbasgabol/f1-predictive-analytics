# F1 podium predictor — 2026

Five reproducible race forecasts in one project. Each race uses only earlier race
results and its own qualifying inputs. Start with a race-named Python file, or use
the shared runner. Saved inputs make prediction fully offline.

## Folder layout

```text
f1-podium-predictor/
├── dutch_grand_prix.py
├── italian_grand_prix.py
├── spanish_grand_prix.py
├── azerbaijan_grand_prix.py
├── bahrain_grand_prix.py
├── run.py
├── verify.py
├── requirements.txt
├── snapshot_manifest.json
└── races/
    ├── f1-dutch-2026/
    ├── f1-italy-2026/
    ├── f1-spain-2026/
    ├── f1-azerbaijan-2026/
    └── f1-bahrain-2026/
```

Each race folder contains its original source code, tests, `data/`, and `outputs/`.
The Dutch post-race evaluation, Italian generalization experiments, and Bahrain
leakage audit are retained in their respective race folders. Race-specific files
were copied byte-for-byte so their original hashes and audit history remain valid.

## Setup

Python 3.10 or newer. In this folder:

```powershell
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
.venv/Scripts/python bahrain_grand_prix.py
```

On macOS/Linux use `.venv/bin/python` instead of `.venv/Scripts/python`.
With dependencies already installed, `python bahrain_grand_prix.py` is sufficient.
No packages from the original machine's project folders are required.

## Run and test

```powershell
python dutch_grand_prix.py
python italian_grand_prix.py
python spanish_grand_prix.py
python azerbaijan_grand_prix.py
python bahrain_grand_prix.py

# Equivalent shared runner:
python run.py bahrain
python run.py all

# All existing leakage and model-selection tests:
python run.py all --test

# Check preserved snapshot hashes:
python verify.py

# Reproduce every forecast in an isolated copy, with network disabled:
python verify.py --replay
```

Normal prediction runs regenerate that race's `outputs/` using the saved inputs.
Verification runs in ignored `.verification/` copies and leaves recorded forecasts
unchanged. It compares the complete prediction JSON, not only the podium names.
Use the pinned NumPy/SciPy versions in `requirements.txt` for reproducibility;
different platforms can still introduce small floating-point differences.

## Saved forecasts

| Race | Predicted P1 | Predicted P2 | Predicted P3 | Report |
|---|---|---|---|---|
| Dutch | Kimi Antonelli | George Russell | Lando Norris | [Report](races/f1-dutch-2026/outputs/REPORT.md) |
| Italian | George Russell | Kimi Antonelli | Charles Leclerc | [Report](races/f1-italy-2026/outputs/REPORT.md) |
| Spanish | Kimi Antonelli | Lando Norris | Max Verstappen | [Report](races/f1-spain-2026/outputs/REPORT.md) |
| Azerbaijan | George Russell | Charles Leclerc | Lando Norris | [Report](races/f1-azerbaijan-2026/outputs/REPORT.md) |
| Bahrain | Kimi Antonelli | Max Verstappen | Lewis Hamilton | [Report](races/f1-bahrain-2026/outputs/REPORT.md) |

These are the original forecasts, not revised predictions after seeing outcomes.
Post-race evaluation files stay separate from training/qualifying snapshots.
The historical event labels are preserved from the source pages: Spain at Madrid,
and the event labeled Bahrain Grand Prix in Malaysia at Sepang.

## Method and limitations

The model is regularized Plackett–Luce ranking. It estimates driver strength from
qualifying position and strictly earlier driver/team form. The Spanish and later
projects use nested chronological selection over six small candidates; the
earlier projects retain their original fixed-model method. Entire races are kept
together in validation.

No claim of guaranteed accuracy or absence of overfitting is made. Data is limited,
probabilities are uncalibrated, and retrospectively retrieved classifications may
include later corrections. The Italian forecast had incidental assistant exposure
to a race-result search snippet; that result was excluded from model inputs, but
the forecast is not described as fully blind.

Read the [Bahrain leakage audit](races/f1-bahrain-2026/audit/REPORT.md) and
[generalization review](races/f1-italy-2026/generalization/REPORT.md).
Audit files and subproject READMEs preserve historical paths and descriptions from
the original run. This root README gives the current portable run instructions.

## Data refresh

Predictions require no downloads or Excel workbook. Optional original `prepare*.py`
scripts are retained for provenance, but fetching again can change retrospective
source data. Do not refresh snapshots to reproduce the recorded forecasts.

The Dutch and Italian preparation scripts additionally expect the original local
workbook at `races/f1_2026_final_dataset.xlsx`; it is not bundled and is ignored by
Git. Later preparation scripts use included sibling snapshots plus their explicitly
allowed source URLs. Source URLs and hashes are recorded in each `data/provenance.json`.

## Push to GitHub

Create an empty GitHub repository, then run from this folder:

```powershell
git init -b main
git add .
git commit -m "Organize F1 podium models by race"
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
git push -u origin main
```

Replace the example remote with your repository URL. `.gitignore` excludes
environments, installed dependencies, caches, temporary replays, credentials and
duplicate ZIPs. `.gitattributes` preserves original snapshot bytes across systems.
