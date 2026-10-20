import unittest
import pandas as pd
from analysis import analyze,sample,validate

class BranchTests(unittest.TestCase):
    def test_reconciliation(self):
        s=analyze(sample());self.assertAlmostEqual(sum(x['deposit_share_pct'] for x in s['states']),100,places=1)
        self.assertEqual(s['cohort']['net_change'],s['cohort']['added']-s['cohort']['removed'])
    def test_duplicate_rejected(self):
        df=sample();df=pd.concat([df,df.iloc[:1]])
        with self.assertRaises(ValueError):validate(df)
    def test_hhi_monopoly(self):
        df=sample();df['bank_id']='ONE'
        self.assertTrue(all(x['hhi']==10000 for x in analyze(df)['states']))
    def test_zero_and_negative_deposits(self):
        df=sample();df['deposits_thousands']=0
        s=analyze(df);self.assertEqual(s['total_deposits_thousands'],0)
        import json
        json.dumps(s,allow_nan=False)
        self.assertIsNone(s['cohort']['matched_growth_pct'])
        df.loc[0,'deposits_thousands']=-1
        with self.assertRaises(ValueError):validate(df)
    def test_blank_key(self):
        df=sample();df.loc[0,'branch_id']=' '
        with self.assertRaises(ValueError):validate(df)
if __name__=='__main__':unittest.main()
