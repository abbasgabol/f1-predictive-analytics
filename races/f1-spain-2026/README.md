# Spanish GP 2026 — pre-race podium forecast

Event: Spanish Grand Prix at Madring, Madrid (not Barcelona-Catalunya).
Cutoff: end of qualifying on 12 September 2026.

```powershell
python predict.py
python -m unittest -v test_model.py test_selection.py
```

`outputs/REPORT.md` explains the prediction, validation and limitations.
`outputs/prediction.json` contains probabilities and per-fold validation;
`outputs/model.json` records model settings, coefficients and input/code hashes.
The original Dutch and Italian forecasts remain untouched.

The model-selection rule was fixed before this forecast: six small candidates,
inner chronological validation, and a one-standard-error simplicity preference.
Outer races do not select their own model. This reduces opportunities for
overfitting; it cannot promise better unseen-race accuracy from just 13 races.

No Spanish race result is requested. The target JSON contains qualifying-only
fields, including imputed rank 22 for two entrants confirmed in pre-qualifying
practice. Previous races, including Italy, are legitimate historical inputs.
Retrospective source corrections cannot be excluded without timestamped archives.

On another Python 3.10+ machine, first run `python -m pip install -r requirements.txt`.
On this machine, the sibling Dutch project's dependency folder is used automatically.
Included snapshots make prediction fully offline. Optional `prepare_spain.py`
refresh requires network access and the sibling Italian project snapshots;
it enforces an exact three-URL allowlist and refuses redirects.
