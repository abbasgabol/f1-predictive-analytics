# Azerbaijan Grand Prix 2026 podium forecast

Event: Baku City Circuit. Cutoff: end of qualifying, 25 September 2026.

```powershell
python predict.py
python -m unittest -v test_model.py test_selection.py
```

Read `outputs/REPORT.md` for the podium, probabilities and validation.
`outputs/prediction.json` contains the detailed forecast and historical folds.
`outputs/model.json` records coefficients, settings, and input/code hashes.

The selection procedure is unchanged from the Spanish forecast: compare six
regularized ranking candidates using inner chronological validation; prefer
fewer features and stronger regularization within one standard error of the
best inner score. Every outer race is evaluated using only earlier races.
No target outcome is involved in selection. Original forecasts remain untouched.

Training includes 14 preceding races (308 driver entries), including Spain.
Target inputs contain only Azerbaijan qualifying fields. All 22 entrants have
qualifying classifications, with teams taken from this event. Azerbaijan race
results, final grid, race weather, telemetry and later standings are excluded.
The data builder permits only two exact URLs: Azerbaijan qualifying and the
previous Spanish race classification. It refuses redirects.

The small dataset cannot establish better future performance or guarantee
absence of overfitting. Historical validation is retrospective; probabilities
are uncalibrated. Qualifying classifications were retrieved retrospectively,
so later corrections cannot be ruled out without an archived as-of snapshot.

On another Python 3.10+ machine, run `python -m pip install -r requirements.txt`
first. Locally, dependencies from the sibling Dutch project are used.
Prediction is fully offline using the included JSON snapshots.
Optional `prepare_data.py` refresh requires network access and the sibling
Spanish project snapshots. It does not request Azerbaijan's race result.
