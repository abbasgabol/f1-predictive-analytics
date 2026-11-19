# F1: 2026 Dutch Grand Prix podium model

Run `python model.py` to train, validate, and reproduce the prediction offline.
Read `outputs/REPORT.md` for the podium, probability estimates, and validation.

The model is regularized Plackett–Luce ranking, fitted with SciPy. It learns one
strength score per driver from pre-race features and a likelihood for the ordered
top three. The next podium place is selected from the drivers remaining, so a
driver cannot occupy two places. We enumerate all 9,240 possible ordered podiums
to obtain exact model probabilities and the most likely ordered podium.

## Run

On this machine, dependencies are available in `.deps`, loaded automatically.
On another machine (Python 3.10 or newer):

```powershell
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
.venv/Scripts/python model.py
.venv/Scripts/python -m unittest -v test_model.py
```

## Leakage protection

- `data/history.json` contains rounds 1–11 only. `data/target_qualifying.json`
  contains only Dutch qualifying fields; no target race results are exported.
- Every form feature filters strictly to `historical_round < prediction_round`.
- Inputs use an explicit four-feature allowlist. Current results, points and
  status never enter X. Historical finish positions are legitimate training labels.
- Entire races are held out chronologically: train 1–6/test 7, through
  train 1–10/test 11. No random driver-row split and no tuning on the target.
- Regularization is fixed at 0.03. The qualifying-only comparison learns the same
  likelihood from qualifying rank alone. It is evaluated on identical folds.
- No current-race grid is used; official qualifying rank replaces the local grid.
- Tests mutate future results, inject target labels, and check exact probability
  normalization. Run `python -m unittest -v test_model.py`.

## Sources and reproducibility

`prepare_data.py` rebuilds the snapshots using the existing parent-directory
`f1_2026_final_dataset.xlsx` and only official Formula 1 qualifying URLs.
It requires network access. It filters out round 12 before decoding its outcome
cells. Historical qualifying omissions are retained at tied rank 22, using the
local historical entrant list. The target field must contain all 22 qualifiers.

`data/provenance.json` records source URLs and SHA-256 hashes. `outputs/model.json`
contains the fitted coefficients, feature names, regularization, and input hashes.
`outputs/prediction.json` contains all probabilities and per-race backtest results.
Input workbooks remain unchanged. Reruns use the saved snapshots by default.

These are retrospectively retrieved classifications, not archived snapshots at
the qualifying flag. Later classification corrections cannot be ruled out.
Historical race labels come from the existing workbook and were not fully
independently checked. Only 11 races are available; treat probabilities as
model estimates, not calibrated confidence. No target race-result comparison
is included, and no Dutch race-result endpoint is fetched.
