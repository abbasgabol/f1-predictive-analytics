"""Compare the frozen forecasts and chronological baselines on whole races."""

import sys
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from f1predictor.data import load_race, read_json
from f1predictor.ranking import CANDIDATES, Candidate
from f1predictor.validation import Trainer


def forecast_comparison():
    races = read_json(ROOT / "website/races.json")
    model_hits = qualifying_hits = model_wins = qualifying_wins = 0
    added_hits = dropped_hits = replacements = 0
    print("Frozen forecasts with recorded outcomes")
    print("Race                Forecast    Qualifying   Podium-pick gain")
    scored = [race for race in races if race["actual"]]
    for race in scored:
        grid = sorted(race["field"], key=lambda driver: driver["qualifying"])
        qualifying = [driver["code"] for driver in grid[:3]]
        forecast = race["prediction"]
        actual = set(race["actual"])
        predicted = set(forecast)
        top_qualifiers = set(qualifying)
        model = len(predicted & actual)
        baseline = len(top_qualifiers & actual)
        model_hits += model
        qualifying_hits += baseline
        model_wins += forecast[0] == race["actual"][0]
        qualifying_wins += qualifying[0] == race["actual"][0]
        added = predicted - top_qualifiers
        replacements += len(added)
        added_hits += len(added & actual)
        dropped_hits += len((top_qualifiers - predicted) & actual)
        print(f"{race['name']:19} {model:>2}/3        {baseline:>2}/3         {model - baseline:+}")
    slots = 3 * len(scored)
    print(f"Podium picks: forecast {model_hits}/{slots}, qualifying {qualifying_hits}/{slots}")
    print(f"Winners: forecast {model_wins}/{len(scored)}, qualifying {qualifying_wins}/{len(scored)}")
    print(f"Of {replacements} replacements, {added_hits} additions reached the podium and {dropped_hits} omissions reached it.")


def chronological_comparison():
    config, history, _ = load_race("las-vegas", ROOT)
    trainer = Trainer(history)
    rounds = [round_no for round_no in trainer.rounds if 7 <= round_no < config["round"]]
    family_tests = {
        "Qualifying only": tuple(candidate for candidate in CANDIDATES if candidate.columns == (0,)),
        "Form only": tuple(Candidate((1, 2, 3), penalty) for penalty in (0.03, 0.1, 0.3)),
        "Qualifying + form": tuple(candidate for candidate in CANDIDATES if len(candidate.columns) == 4),
        "Current selection": CANDIDATES,
    }
    print(f"\nRetrospective walk-forward test, rounds {rounds[0]}–{rounds[-1]}")
    print("Model                 Podium picks   Winners   Exact order   Mean log loss")
    for name, candidates in family_tests.items():
        selected = [trainer.choose(round_no, candidates=candidates) for round_no in rounds]
        scores = [trainer.score(round_no, model) for round_no, model in zip(rounds, selected)]
        hits = sum(score["hits"] for score in scores)
        wins = sum(score["winner_correct"] for score in scores)
        orders = sum(score["exact_order"] for score in scores)
        loss = mean(score["nll"] for score in scores)
        print(f"{name:22} {hits:>2}/{3 * len(rounds):<12} {wins:>2}/{len(rounds):<5} {orders:>2}/{len(rounds):<10} {loss:.3f}")
        if name == "Current selection":
            qualifying = sum(model.columns == (0,) for model in selected)
            print(f"The current policy selected qualifying alone in {qualifying}/{len(rounds)} tests.")


if __name__ == "__main__":
    forecast_comparison()
    chronological_comparison()
