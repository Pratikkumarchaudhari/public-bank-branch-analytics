import unittest
from decimal import Decimal
import json
from pathlib import Path
import csv
import pandas as pd
from analysis import analyze,sample

class GrowthAuditTests(unittest.TestCase):
    def test_sample_totals_match_independent_decimal_csv_sums(self):
        with (Path(__file__).resolve().parents[1]/'data/branches.csv').open() as f:rows=list(csv.DictReader(f))
        old={r['branch_id']:Decimal(r['deposits_thousands']) for r in rows if r['year']=='2024'}
        new={r['branch_id']:Decimal(r['deposits_thousands']) for r in rows if r['year']=='2025'}
        matched=old.keys()&new.keys();prior=sum(old[i] for i in matched);latest=sum(new[i] for i in matched)
        s=analyze(sample());a=s['growth_audit']
        self.assertEqual(len(matched),162)
        self.assertEqual(prior,Decimal('21756069.00'))
        self.assertEqual(latest,Decimal('23182213.20'))
        self.assertAlmostEqual(a['unrounded_matched_growth_pct'],float(100*(latest/prior-1)),places=10)
        self.assertEqual(s['cohort']['matched_growth_pct'],6.56)
    def test_aggregate_growth_is_not_average_individual_growth(self):
        df=pd.DataFrame([
            [2024,'A','BANK','NY',100],[2024,'B','BANK','NY',900],
            [2025,'A','BANK','NY',200],[2025,'B','BANK','NY',900]],
            columns=['year','branch_id','bank_id','state','deposits_thousands'])
        s=analyze(df)
        self.assertEqual(s['cohort']['matched_growth_pct'],10)
        individual=[r['branch_growth_pct'] for r in s['branch_comparison']]
        self.assertEqual(sum(individual)/len(individual),50)
    def test_cohorts_bridge_and_breakdowns_reconcile(self):
        s=analyze(sample());a=s['growth_audit'];rows=s['branch_comparison']
        self.assertEqual(len(rows),179)
        self.assertEqual(sum(r['cohort']=='entering' for r in rows),9)
        self.assertEqual(sum(r['cohort']=='exiting' for r in rows),8)
        self.assertAlmostEqual(a['prior_total_deposits_thousands']+a['matched_change_thousands']+a['entering_deposits_thousands']-a['exiting_deposits_thousands'],a['latest_total_deposits_thousands'])
        self.assertEqual(a['bridge_residual_thousands'],0)
        for key in ['matched_by_state','matched_by_bank']:
            self.assertEqual(sum(r['branches'] for r in a[key]),162)
            self.assertAlmostEqual(sum(r['prior_deposits_thousands'] for r in a[key]),a['prior_matched_deposits_thousands'])
    def test_zero_denominator_and_single_year_are_explicit(self):
        df=sample();df['deposits_thousands']=0
        s=analyze(df);self.assertIsNone(s['growth_audit']['unrounded_matched_growth_pct'])
        self.assertTrue(all(r['branch_growth_pct'] is None for r in s['branch_comparison']))
        json.dumps(s,allow_nan=False)
        single=analyze(df[df.year==2025]);self.assertIsNone(single['growth_audit']);self.assertEqual(single['branch_comparison'],[])
    def test_nonconsecutive_years_and_latest_group_assignment(self):
        df=sample();df.loc[df.year==2025,'year']=2026
        df.loc[df.year==2026,'state']='CA'
        s=analyze(df);a=s['growth_audit']
        self.assertEqual((a['prior_year'],a['latest_year']),(2024,2026))
        self.assertEqual(a['matched_by_state'][0]['group'],'CA')
        self.assertEqual(a['matched_by_state'][0]['branches'],162)

if __name__=='__main__':unittest.main()
