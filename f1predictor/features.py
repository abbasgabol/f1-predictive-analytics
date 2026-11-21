"""Four numerical features, each available by the qualifying cutoff."""
import numpy as np

FEATURES = (
    "qualifying_quality",
    "driver_last3_finish_quality",
    "driver_prior_podium_rate",
    "team_last3_races_finish_quality",
)


def features(field: list[dict], history: list[dict]) -> np.ndarray:
    values = []
    for row in field:
        prior = [r for r in history if r["round"] < row["round"]]
        driver = sorted([r for r in prior if r["driver"] == row["driver"]], key=lambda r: r["round"])
        team = [r for r in prior if r["team"] == row["team"]]
        recent_rounds = sorted({r["round"] for r in team})[-3:]
        team_recent = [r for r in team if r["round"] in recent_rounds]

        def quality(rows):
            return np.mean([(23 - r["finish_position"]) / 22 for r in rows]) if rows else 0.5

        podium_rate = (sum(r["finish_position"] <= 3 for r in driver) + 2 * 3 / 22) / (len(driver) + 2)
        values.append([(23 - row["qualifying_position"]) / 22, quality(driver[-3:]), podium_rate, quality(team_recent)])
    return np.asarray(values, dtype=float)
