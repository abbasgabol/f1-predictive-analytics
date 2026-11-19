import copy, json, unittest
import model as m
import numpy as np

class LeakageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.history=json.loads((m.ROOT/'data/history.json').read_text())
        cls.target=json.loads((m.ROOT/'data/target_qualifying.json').read_text())

    def test_clean_target_and_complete_races(self):
        m.check_data(self.history,self.target)

    def test_current_and_future_outcomes_cannot_change_features(self):
        field=[r for r in self.history if r['round']==7]
        altered=copy.deepcopy(self.history)
        for row in altered:
            if row['round']>=7:
                row['finish_position']=23-row['finish_position']
                row['points']=99999
                row['status']='invented future outcome'
        np.testing.assert_array_equal(m.features(field,self.history),m.features(field,altered))

    def test_poisoned_target_labels_rejected(self):
        target=copy.deepcopy(self.target)
        target[0]['finish_position']=1
        with self.assertRaises(AssertionError): m.check_data(self.history,target)

    def test_target_outcomes_cannot_change_predictions(self):
        clean=m.features(self.target,self.history)
        poison=[dict(r,finish_position=i+1) for i,r in enumerate(self.target)]
        np.testing.assert_array_equal(clean,m.features(self.target,self.history+poison))

    def test_exact_probability_constraints(self):
        w=m.fit(self.history)
        probs,order,joint=m.distribution(m.features(self.target,self.history),w)
        np.testing.assert_allclose(probs.sum(axis=0),np.ones(3),atol=1e-10)
        self.assertTrue(np.all(probs>=0))
        self.assertTrue(np.all(probs.sum(axis=1)<=1+1e-10))
        self.assertEqual(len(set(order)),3)
        self.assertTrue(0<joint<1)

if __name__=='__main__': unittest.main()
