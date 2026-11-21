"""Load event snapshots without opening the target race's result file."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUALIFYING_FIELDS = {"round", "gp", "driver", "name", "team", "qualifying_position", "q1", "q2", "q3"}


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def catalog(root: Path = ROOT) -> dict:
    return read_json(root / "data/catalog.json")


def validate(history: list[dict], target: list[dict], target_round: int) -> None:
    """Fail closed; checks remain enabled under python -O."""
    if {r.get("round") for r in history} != set(range(1, target_round)):
        raise ValueError("History must contain every earlier round and no target/future round")
    if any(set(r) - QUALIFYING_FIELDS for r in target):
        raise ValueError("Target contains fields outside the qualifying allowlist")
    if any(r.get("round") != target_round for r in target):
        raise ValueError("Target round mismatch")
    for rnd in range(1, target_round + 1):
        rows = target if rnd == target_round else [r for r in history if r["round"] == rnd]
        if len(rows) != 22 or len({r["driver"] for r in rows}) != 22:
            raise ValueError(f"Round {rnd} must contain 22 distinct entrants")
        if any(type(r["qualifying_position"]) is not int or not 1 <= r["qualifying_position"] <= 22 for r in rows):
            raise ValueError(f"Invalid qualifying rank in round {rnd}")
        if rnd < target_round and sorted(r["finish_position"] for r in rows) != list(range(1, 23)):
            raise ValueError(f"Incomplete finishing classification in round {rnd}")


def load_race(slug: str, root: Path = ROOT) -> tuple[dict, list[dict], list[dict]]:
    config = catalog(root)[slug]
    history = []
    for rnd in range(1, config["round"]):
        event = root / "data/events" / f"{rnd:02d}"
        qualifiers = read_json(event / "qualifying.json")
        results = read_json(event / "results.json")
        positions = {r["driver"]: r["finish_position"] for r in results}
        if len(results) != 22 or len(positions) != 22 or set(positions) != {r["driver"] for r in qualifiers}:
            raise ValueError(f"Qualifying/result driver mismatch in round {rnd}")
        history.extend({**r, "finish_position": positions[r["driver"]]} for r in qualifiers)
    target = read_json(root / "data/events" / f"{config['round']:02d}" / "qualifying.json")
    validate(history, target, config["round"])
    semantic_hash = hashlib.sha256(json.dumps([history, target], sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    if semantic_hash != config["input_semantic_sha256"]:
        raise ValueError("Inputs differ from the recorded forecast snapshot")
    return config, history, target


def verify_integrity(root: Path = ROOT) -> int:
    manifest = read_json(root / "data/manifest.json")
    for name, expected in manifest.items():
        path = root / name
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError(f"Snapshot changed or missing: {name}")
    return len(manifest)
