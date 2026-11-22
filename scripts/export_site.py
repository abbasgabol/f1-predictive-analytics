"""Export saved forecasts and separate evaluation labels for the static dashboard."""

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "website" / "races.json"


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def export():
    catalog = read(ROOT / "data/catalog.json")
    supplied = {
        row["event"]: row["actual"]
        for row in read(ROOT / "docs/audits/chat-baseline.json")["races"]
    }
    reported = read(ROOT / "data/evaluation/podiums.json")
    races = []
    for slug, config in sorted(catalog.items(), key=lambda pair: pair[1]["round"]):
        number = config["round"]
        event = ROOT / f"data/events/{number:02}"
        forecast = read(ROOT / f"forecasts/{slug}/prediction.json")
        qualifying = {row["driver"]: row for row in read(event / "qualifying.json")}
        field = [
            {
                "code": row["driver"],
                "name": row["name"],
                "team": qualifying[row["driver"]]["team"],
                "qualifying": qualifying[row["driver"]]["qualifying_position"],
                "win": row.get("win_probability", row.get("p1")),
                "podium": row.get("podium_probability", row.get("podium")),
            }
            for row in forecast["field"]
        ]
        actual, source = None, None
        podium_details = reported.get(slug)
        if podium_details is not None:
            actual = [row["driver"] for row in podium_details]
            source = "User-supplied race classification"
        elif slug in supplied:
            actual, source = supplied[slug], "Reader supplied classification"
        elif (event / "results.json").exists():
            results = read(event / "results.json")
            actual = [row["driver"] for row in sorted(results, key=lambda row: row["finish_position"])[:3]]
            source = "Archived race classification"
        prediction = [row["driver"] for row in forecast["prediction"]]
        known = {row["code"] for row in field}
        for lineup in (prediction, actual):
            if lineup is not None and (len(lineup) != 3 or len(set(lineup)) != 3 or not set(lineup) <= known):
                raise ValueError(f"Invalid podium for {slug}: {lineup}")
        races.append({
            "slug": slug,
            "name": config["name"],
            "round": number,
            "cutoff": forecast["cutoff"],
            "prediction": prediction,
            "actual": actual,
            "source": source,
            "joint": forecast["ordered_podium_probability"],
            "field": field,
            **({"actualDetails": podium_details} if podium_details is not None else {}),
        })
    return json.dumps(races, ensure_ascii=False, separators=(",", ":")) + "\n"


def export_backtest():
    forecast = read(ROOT / "forecasts/las-vegas/prediction.json")
    summary = forecast["historical_validation"]
    data = {
        "folds": [{"round": fold["round"], "hits": fold["hits"]} for fold in forecast["outer_folds"]],
        "mean": summary["mean_podium_hits"],
        "winners": summary["winners_correct"],
    }
    return json.dumps(data, separators=(",", ":")) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Check the committed export")
    args = parser.parse_args()
    outputs = {OUTPUT: export(), OUTPUT.with_name("backtest.json"): export_backtest()}
    for path, content in outputs.items():
        if args.check:
            if not path.is_file() or path.read_text(encoding="utf-8") != content:
                parser.exit(1, f"{path.name} is outdated. Run python scripts/export_site.py.\n")
        else:
            path.write_text(content, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
