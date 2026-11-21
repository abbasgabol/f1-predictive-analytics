import copy
import io
import itertools
import unittest
from contextlib import redirect_stderr
from unittest.mock import patch

import numpy as np
from scipy.optimize import check_grad

from f1predictor import data
from f1predictor.cli import main
from f1predictor.features import features
from f1predictor.pipeline import compare_reference, predict
from f1predictor.ranking import FULL_MODEL, objective, podium_distribution
from f1predictor.validation import Trainer


class DataTests(unittest.TestCase):
    def test_all_cutoffs_reconstruct_original_inputs(self):
        for slug in data.catalog():
            config, history, target = data.load_race(slug)
            self.assertEqual(len(history), 22 * (config["round"] - 1))
            self.assertEqual(len(target), 22)

    def test_loader_never_opens_target_or_future_results(self):
        original = data.read_json
        accessed = []

        def spy(path):
            accessed.append(path)
            return original(path)

        with patch.object(data, "read_json", side_effect=spy):
            data.load_race("dutch")
        result_rounds = [int(p.parent.name) for p in accessed if p.name == "results.json"]
        self.assertEqual(result_rounds, list(range(1, 12)))

    def test_target_outcome_columns_rejected(self):
        config, history, target = data.load_race("las-vegas")
        for name in ("finish_position", "points", "status", "race_time", "final_grid"):
            poisoned = copy.deepcopy(target)
            poisoned[0][name] = 1
            with self.subTest(name=name), self.assertRaises(ValueError):
                data.validate(history, poisoned, config["round"])

    def test_target_race_in_training_rejected(self):
        config, history, target = data.load_race("las-vegas")
        history += [dict(r, finish_position=i + 1) for i, r in enumerate(target)]
        with self.assertRaises(ValueError):
            data.validate(history, target, config["round"])

    def test_duplicate_entrants_rejected(self):
        config, history, target = data.load_race("las-vegas")
        target[0] = target[1].copy()
        with self.assertRaises(ValueError):
            data.validate(history, target, config["round"])

    def test_snapshot_hashes(self):
        self.assertGreater(data.verify_integrity(), 80)


class FeatureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _, cls.history, cls.target = data.load_race("las-vegas")

    def test_current_and_future_outcomes_do_not_change_features(self):
        for rnd in range(1, 21):
            field = [r for r in self.history if r["round"] == rnd]
            poisoned = copy.deepcopy(self.history)
            for row in poisoned:
                if row["round"] >= rnd:
                    row["finish_position"] = 23 - row["finish_position"]
            np.testing.assert_array_equal(features(field, self.history), features(field, poisoned))

    def test_new_driver_uses_neutral_prior(self):
        newcomer = dict(self.target[0], driver="NEW", team="NEW_TEAM")
        x = features([newcomer], self.history)[0]
        np.testing.assert_allclose(x[1:], [.5, 3 / 22, .5])

    def test_names_are_not_model_inputs(self):
        renamed = [dict(r, driver="driver_" + r["driver"], team="team_" + r["team"]) for r in self.history]
        target = [dict(r, driver="driver_" + r["driver"], team="team_" + r["team"]) for r in self.target]
        np.testing.assert_array_equal(features(self.target, self.history), features(target, renamed))


class RankingTests(unittest.TestCase):
    def test_analytic_gradient_against_finite_difference(self):
        rng = np.random.default_rng(19)
        groups = [(rng.normal(size=(6, 4)), [0, 2, 3]), (rng.normal(size=(6, 4)), [1, 3, 0])]
        w = rng.normal(size=4)
        error = check_grad(lambda v: objective(v, groups, .1)[0], lambda v: objective(v, groups, .1)[1], w)
        self.assertLess(error, 1e-6)

    def test_vectorized_distribution_matches_independent_enumeration(self):
        rng = np.random.default_rng(5)
        x, w = rng.normal(size=(6, 4)), rng.normal(size=4)
        scores = x @ w
        strengths = np.exp(scores - scores.max())
        expected = np.zeros((6, 3))
        orders = []
        for order in itertools.permutations(range(6), 3):
            remaining = strengths.sum()
            p = 1.
            for i in order:
                p *= strengths[i] / remaining
                remaining -= strengths[i]
            orders.append((p, order))
            for slot, i in enumerate(order):
                expected[i, slot] += p
        actual, order, joint = podium_distribution(x, w)
        np.testing.assert_allclose(actual, expected, atol=1e-12)
        self.assertEqual(order, max(orders)[1])
        self.assertAlmostEqual(joint, max(orders)[0])
        np.testing.assert_allclose(actual.sum(axis=0), np.ones(3), atol=1e-12)
        self.assertTrue(np.all(actual.sum(axis=1) <= 1 + 1e-12))

    def test_field_requires_three_drivers(self):
        with self.assertRaises(ValueError):
            podium_distribution(np.ones((2, 4)), np.zeros(4))


class SelectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _, cls.history, _ = data.load_race("dutch")

    def test_fit_cache_is_defensive_and_reuses_work(self):
        trainer = Trainer(self.history)
        a = trainer.fit(7, FULL_MODEL)
        a[:] = 999
        b = trainer.fit(7, FULL_MODEL)
        self.assertFalse(np.any(b == 999))
        self.assertEqual(trainer.fit_count, 1)

    def test_future_poisoning_cannot_change_earlier_selection(self):
        original = Trainer(self.history)
        poisoned = copy.deepcopy(self.history)
        for row in poisoned:
            if row["round"] >= 7:
                row["finish_position"] = 23 - row["finish_position"]
        altered = Trainer(poisoned)
        candidate = original.choose(7)
        self.assertEqual(candidate, altered.choose(7))
        np.testing.assert_array_equal(original.fit(7, candidate), altered.fit(7, candidate))
        self.assertEqual(original.score(7, candidate)["prediction"], altered.score(7, candidate)["prediction"])

    def test_training_snapshot_isolated_from_caller_mutation(self):
        rows = copy.deepcopy(self.history)
        trainer = Trainer(rows)
        a = trainer.fit(7, FULL_MODEL)
        rows[0]["finish_position"] = 22
        np.testing.assert_array_equal(a, trainer.fit(7, FULL_MODEL))


class RegressionTests(unittest.TestCase):
    def test_latest_forecast_and_backtest_match_frozen_reference(self):
        compare_reference("las-vegas", predict("las-vegas", backtest=True))

    def test_cli_protects_frozen_forecasts(self):
        with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
            main(["predict", "las-vegas", "--output", str(data.ROOT / "forecasts/las-vegas/prediction.json")])
        self.assertEqual(error.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
