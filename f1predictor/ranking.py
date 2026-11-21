"""Plackett-Luce likelihood with analytic gradients and exact podium probabilities."""
from dataclasses import dataclass

import numpy as np
from scipy.optimize import minimize
from scipy.special import logsumexp


@dataclass(frozen=True)
class Candidate:
    columns: tuple[int, ...] = (0, 1, 2, 3)
    l2: float = 0.03

    @property
    def name(self):
        return f"{'qualifying' if len(self.columns) == 1 else 'form'}_l2_{self.l2}"


FULL_MODEL = Candidate()
CANDIDATES = tuple(Candidate(columns, penalty) for columns in ((0,), (0, 1, 2, 3)) for penalty in (0.03, 0.1, 0.3))


def objective(w: np.ndarray, groups: list[tuple], penalty: float):
    loss, gradient = 0.0, np.zeros_like(w)
    for x, podium in groups:
        remaining = list(range(len(x)))
        for winner in podium:
            scores = x[remaining] @ w
            normalizer = logsumexp(scores)
            loss += normalizer - x[winner] @ w
            gradient += np.exp(scores - normalizer) @ x[remaining] - x[winner]
            remaining.remove(winner)
    return loss / len(groups) + penalty * np.sum(w * w), gradient / len(groups) + 2 * penalty * w


def fit(groups: list[tuple], candidate: Candidate, *, legacy: bool = False) -> np.ndarray:
    options = {"maxiter": 1000, "ftol": 1e-12, "gtol": 1e-8}
    if not legacy:
        options["maxls"] = 50
    result = minimize(objective, np.zeros(len(candidate.columns)), args=(groups, candidate.l2),
                      jac=True, method="L-BFGS-B", options=options)
    if not result.success:
        raise RuntimeError(f"Optimizer did not converge: {result.message}")
    return result.x


def podium_distribution(x: np.ndarray, w: np.ndarray):
    """Enumerate all n*(n-1)*(n-2) podiums with vectorized NumPy operations."""
    scores = x @ w
    strengths = np.exp(scores - scores.max())
    n = len(strengths)
    if n < 3:
        raise ValueError("At least three entrants are required")
    total = strengths.sum()
    a, b, c = np.indices((n, n, n))
    valid = (a != b) & (a != c) & (b != c)
    a, b, c = a[valid], b[valid], c[valid]
    p = strengths[a] / total * strengths[b] / (total - strengths[a]) * strengths[c] / (total - strengths[a] - strengths[b])
    marginals = np.column_stack([np.bincount(idx, weights=p, minlength=n) for idx in (a, b, c)])
    best = int(p.argmax())
    return marginals, (int(a[best]), int(b[best]), int(c[best])), float(p[best])
