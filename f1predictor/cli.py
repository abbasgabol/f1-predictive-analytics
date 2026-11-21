"""Command-line access to predictions, chronological evaluation and integrity checks."""
import argparse
import json
from pathlib import Path

from .data import ROOT, catalog, load_race, verify_integrity
from .pipeline import compare_reference, predict
from .validation import Trainer


def main(argv=None):
    parser = argparse.ArgumentParser(prog="python -m f1predictor", description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("list", help="List the ten available forecast snapshots")
    forecast = commands.add_parser("predict", help="Fit and predict one race from qualifying-cutoff inputs")
    forecast.add_argument("race", choices=list(catalog()))
    forecast.add_argument("--output", type=Path, help="Optional JSON output; data/ and forecasts/ are protected")
    backtest = commands.add_parser("backtest", help="Evaluate on whole earlier races in chronological order")
    backtest.add_argument("race", choices=list(catalog()))
    integrity = commands.add_parser("verify", help="Verify data and frozen-artifact hashes")
    integrity.add_argument("--replay", action="store_true", help="Recompute and compare forecasts and backtests")
    integrity.add_argument("--race", choices=list(catalog()), help="Replay just one race")
    args = parser.parse_args(argv)
    if args.command == "list":
        for slug, config in catalog().items():
            print(f"{slug:15} round {config['round']:2} | {config['selection']:6} | {config['cutoff']}")
    elif args.command == "predict":
        if args.output:
            resolved = args.output.resolve()
            if any(resolved.is_relative_to(ROOT / folder) for folder in ("data", "forecasts")):
                parser.error("Immutable data and forecast folders cannot be output destinations")
        result = predict(args.race)
        for row in result["prediction"]:
            print(f"P{row['position']}  {row['name']}")
        print(f"Model: {result['selected_model']} | Training: {result['training_races']} prior races")
        print("Probabilities are uncalibrated; this is a forecast, not a guarantee.")
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    elif args.command == "backtest":
        config, history, _ = load_race(args.race)
        print(json.dumps(Trainer(history).backtest(config["round"], config["selection"]), indent=2))
    else:
        print(f"PASS: {verify_integrity()} snapshot hashes", flush=True)
        if args.replay:
            for slug in ([args.race] if args.race else catalog()):
                result = predict(slug, backtest=True)
                compare_reference(slug, result)
                print(f"PASS: {slug} — coefficients, all 22 probabilities, podium and backtest reproduce", flush=True)
    return 0
