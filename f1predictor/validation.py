"""Expanding-window selection with precomputed features and dataset-scoped caches."""
from copy import deepcopy

import numpy as np
from scipy.special import logsumexp

from .features import features
from .ranking import CANDIDATES, FULL_MODEL, Candidate, fit


class Trainer:
    """An immutable training snapshot; cached fits never cross datasets or cutoffs."""

    def __init__(self, history: list[dict]):
        self._history = deepcopy(history)
        self.rounds = sorted({r["round"] for r in history})
        self._groups = {}
        for rnd in self.rounds:
            field = sorted([r for r in self._history if r["round"] == rnd], key=lambda r: r["driver"])
            x = features(field, self._history)
            podium = sorted(range(len(field)), key=lambda i: field[i]["finish_position"])[:3]
            self._groups[rnd] = (field, x, podium)
        self._fits = {}
        self._scores = {}
        self.fit_count = 0

    def fit(self, cutoff: int, candidate: Candidate, *, legacy: bool = False):
        key = (cutoff, candidate, legacy)
        if key not in self._fits:
            groups = [(self._groups[r][1][:, candidate.columns], self._groups[r][2]) for r in self.rounds if r < cutoff]
            if not groups:
                raise ValueError("No training races before cutoff")
            self._fits[key] = fit(groups, candidate, legacy=legacy)
            self.fit_count += 1
        return self._fits[key].copy()

    def score(self, rnd: int, candidate: Candidate, *, legacy: bool = False):
        key = (rnd, candidate, legacy)
        if key not in self._scores:
            w = self.fit(rnd, candidate, legacy=legacy)
            field, x, actual = self._groups[rnd]
            scores = x[:, candidate.columns] @ w
            predicted = np.argsort(-scores, kind="stable")[:3].tolist()
            remaining = list(range(len(field)))
            nll = 0.0
            for idx in actual:
                nll += logsumexp(scores[remaining]) - scores[idx]
                remaining.remove(idx)
            self._scores[key] = dict(round=rnd, gp=field[0]["gp"], nll=float(nll),
                hits=len(set(actual) & set(predicted)), winner_correct=actual[0] == predicted[0],
                exact_order=actual == predicted, prediction=[field[i]["driver"] for i in predicted])
        return deepcopy(self._scores[key])

    def choose(self, cutoff: int):
        records = []
        for candidate in CANDIDATES:
            losses = [self.score(r, candidate)["nll"] for r in self.rounds if 4 <= r < cutoff]
            if len(losses) < 2:
                raise ValueError("Selection requires at least two earlier validation races")
            records.append(dict(candidate=candidate, mean_nll=float(np.mean(losses)),
                standard_error=float(np.std(losses, ddof=1) / np.sqrt(len(losses)))))
        best = min(records, key=lambda r: r["mean_nll"])
        threshold = best["mean_nll"] + best["standard_error"]
        eligible = [r for r in records if r["mean_nll"] <= threshold]
        chosen = min(eligible, key=lambda r: (len(r["candidate"].columns), -r["candidate"].l2))
        return chosen["candidate"]

    def backtest(self, cutoff: int, policy: str = "nested"):
        records = []
        for rnd in self.rounds:
            if 7 <= rnd < cutoff:
                candidate = self.choose(rnd) if policy == "nested" else FULL_MODEL
                records.append({**self.score(rnd, candidate, legacy=policy == "fixed"), "selected_model": candidate.name})
        if not records:
            raise ValueError("No backtest races")
        return dict(races=len(records), mean_podium_hits=float(np.mean([r["hits"] for r in records])),
            winners_correct=sum(r["winner_correct"] for r in records), exact_orders=sum(r["exact_order"] for r in records),
            mean_ordered_podium_nll=float(np.mean([r["nll"] for r in records])), folds=records)
