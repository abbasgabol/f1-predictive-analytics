import copy, json, unittest
import selection as g
import numpy as np

class GeneralizationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.history=json.loads((g.m.ROOT/'data/history.json').read_text())

    def test_held_out_labels_cannot_change_selection_or_prediction(self):
        original=g.predict_fold(self.history,7)
        poisoned=copy.deepcopy(self.history)
        for row in poisoned:
            if row['round']>=7: row['finish_position']=23-row['finish_position']
        changed=g.predict_fold(poisoned,7)
        self.assertEqual(original['selected'],changed['selected'])
        self.assertEqual(original['prediction'],changed['prediction'])
        self.assertEqual(original['inner_validation'],changed['inner_validation'])
        np.testing.assert_array_equal(original['coefficients'],changed['coefficients'])

    def test_original_candidate_reproduces_existing_fit(self):
        history=[r for r in self.history if r['round']<7]
        np.testing.assert_allclose(g.fit(history,g.CANDIDATES[3]),g.m.fit(history),atol=1e-10)

if __name__=='__main__': unittest.main()
