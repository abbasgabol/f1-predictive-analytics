"""Shared prediction pipeline; frozen forecasts are never overwritten."""
from pathlib import Path

import numpy as np

from .data import ROOT, load_race, read_json
from .features import FEATURES, features
from .ranking import FULL_MODEL, podium_distribution
from .validation import Trainer


def predict(slug: str, *, root: Path = ROOT, backtest: bool = False):
    config, history, target = load_race(slug, root)
    trainer = Trainer(history)
    cutoff = config["round"]
    fixed = config["selection"] == "fixed"
    chosen = FULL_MODEL if fixed else trainer.choose(cutoff)
    coefficients = trainer.fit(cutoff, chosen, legacy=fixed)
    target = sorted(target, key=lambda r: r["driver"])
    x = features(target, history)[:, chosen.columns]
    marginals, order, joint = podium_distribution(x, coefficients)
    result = dict(race=slug, cutoff=config["cutoff"], training_races=cutoff-1, training_rows=len(history),
        selected_model=chosen.name, features=[FEATURES[c] for c in chosen.columns], coefficients=coefficients.tolist(),
        prediction=[dict(position=slot+1, driver=target[i]["driver"], name=target[i]["name"]) for slot, i in enumerate(order)],
        ordered_podium_probability=joint,
        field=[dict(driver=r["driver"], name=r["name"], qualifying_position=r["qualifying_position"],
            win_probability=float(marginals[i, 0]), second_probability=float(marginals[i, 1]),
            third_probability=float(marginals[i, 2]), podium_probability=float(marginals[i].sum())) for i, r in enumerate(target)],
        probability_warning="Uncalibrated model estimates; retrospective data and small sample.")
    result["field"].sort(key=lambda r: -r["podium_probability"])
    if backtest:
        result["validation"] = trainer.backtest(cutoff, config["selection"])
    result["optimizer_calls"] = trainer.fit_count
    return result


def compare_reference(slug: str, result: dict, root: Path = ROOT):
    """Check every driver's probabilities, coefficients and ordered podium."""
    original = read_json(root / "forecasts" / slug / "prediction.json")
    model = read_json(root / "forecasts" / slug / "model.json")
    if result["prediction"] != original["prediction"]:
        raise AssertionError(f"{slug}: ordered prediction changed")
    np.testing.assert_allclose(result["coefficients"], model["coefficients"], rtol=1e-8, atol=1e-9)
    np.testing.assert_allclose(result["ordered_podium_probability"], original["ordered_podium_probability"], rtol=1e-8, atol=1e-10)
    expected_model = model.get("selected_model", {}).get("name", "form_l2_0.03")
    if result["selected_model"] != expected_model:
        raise AssertionError(f"{slug}: model selection changed")
    for row in result["field"]:
        old = next(r for r in original["field"] if r["driver"] == row["driver"])
        expected = [old.get("win_probability", old.get("p1")), old.get("podium_probability", old.get("podium"))]
        np.testing.assert_allclose([row["win_probability"], row["podium_probability"]], expected, rtol=1e-8, atol=1e-10)
    if "validation" in result:
        old = original.get("historical_validation")
        if old:
            for key, value in old.items():
                np.testing.assert_allclose(result["validation"][key], value, rtol=1e-8, atol=1e-9)
        else:
            old = original["validation_summary"]["form_and_qualifying"]
            for key, legacy in [("mean_podium_hits", "mean_podium_hits"), ("winners_correct", "winner_correct"),
                                ("exact_orders", "exact_order_correct"), ("mean_ordered_podium_nll", "mean_ordered_podium_nll")]:
                np.testing.assert_allclose(result["validation"][key], old[legacy], rtol=1e-8, atol=1e-9)
