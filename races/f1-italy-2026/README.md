# Italian Grand Prix 2026 forecast

Run `python model.py` to reproduce the forecast from the saved offline datasets.
Read `outputs/REPORT.md` for the result, probabilities and chronological validation.
Run `python -m unittest -v test_model.py` for leakage and probability checks.

The model is the previous Dutch GP model, with identical four features,
Plackett-Luce top-three likelihood, optimizer and L2 regularization (0.03).
Only the historical dataset and target event were advanced by one race.
No tuning was performed to match Italy's race result.

## Cutoff and sources

- Target: Italy round 13, end of qualifying on 5 September 2026.
- Target data: official qualifying classification only; no race labels or final grid.
- History: 264 driver entries across rounds 1–12, including the Dutch race.
- Dutch podium in the local workbook agrees with the user's supplied result.
- Every historical form feature uses strictly earlier rounds.
- Six expanding-window validation races: rounds 7–12. The Dutch race is now
  historical data for Italy, while the original Dutch forecast remains unchanged.
- Target URL and file hashes are recorded in `data/provenance.json`.

## Integrity disclosure

A qualifying-focused web search unexpectedly exposed an Italian race-result
snippet to the assistant. Therefore this is not presented as a fully blind
assistant forecast. The snippet is excluded from all model data and code.
The already-existing modeling method was retained unchanged. The script trains
only on rounds 1–12 and loads a strictly qualifying-only target JSON.
No Italian race-result endpoint was directly requested and no target scoring
or result comparison is performed.

The data is retrospectively retrieved, not timestamped archival snapshots from
the qualifying flag. Later qualifying classification corrections cannot be
ruled out. Historical labels originate in the existing local workbook and were
not fully independently verified. Probabilities are uncalibrated small-data estimates.

## Installation elsewhere

Python 3.10 or newer:

```powershell
python -m pip install -r requirements.txt
python model.py
python -m unittest -v test_model.py
```

On this machine the script uses the dependencies in the sibling Dutch project.
`prepare_italy.py` is an optional network refresh utility requiring the sibling
Dutch project and the parent-directory original workbook. It is not needed to
run predictions from the included JSON snapshots.
