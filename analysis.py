"""Branch footprint, deposit concentration and year-over-year cohort analysis."""
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parent
REQUIRED={'year','branch_id','bank_id','state','deposits_thousands'}
FDIC={'YEAR':'year','UNINUMBR':'branch_id','CERT':'bank_id','STALPBR':'state','DEPSUMBR':'deposits_thousands'}

def sample():
    rng=np.random.default_rng(42);rows=[]
    for year in [2024,2025]:
        for i in range(1,181):
            if year==2025 and i%19==0:continue
            if year==2024 and i>170:continue
            deposits=round((35000+(i*7919)%200000)*(1+(year-2024)*(.025+(i%9)/100)),2)
            rows.append(dict(year=year,branch_id=f'SYN{i:04}',bank_id=f'BANK{(i%12)+1:02}',
                state=['NY','NJ','CT','PA','MA'][i%5],deposits_thousands=deposits))
    return pd.DataFrame(rows)

def validate(df):
    missing=REQUIRED-set(df.columns)
    if missing:raise ValueError(f'Missing columns: {sorted(missing)}')
    if df.empty:raise ValueError('No branch records')
    df=df.copy()
    for c in ['branch_id','bank_id','state']:
        if df[c].isna().any() or df[c].astype(str).str.strip().eq('').any():raise ValueError(f'Blank {c}')
        df[c]=df[c].astype(str).str.strip()
    for c in ['year','deposits_thousands']:df[c]=pd.to_numeric(df[c],errors='raise')
    if not np.isfinite(df[['year','deposits_thousands']].to_numpy()).all():raise ValueError('Nonfinite values')
    if (df.year%1!=0).any():raise ValueError('Year must be an integer')
    df['year']=df.year.astype(int)
    if (df.deposits_thousands<0).any():raise ValueError('Negative deposits')
    if df.duplicated(['year','branch_id']).any():raise ValueError('Duplicate branch-year keys')
    return df

def analyze(df):
    df=validate(df);year=int(df.year.max());latest=df[df.year==year]
    total=float(latest.deposits_thousands.sum())
    state=latest.groupby('state').agg(branches=('branch_id','size'),
        deposits_thousands=('deposits_thousands','sum')).reset_index()
    state['deposit_share_pct']=0.0 if total==0 else 100*state.deposits_thousands/total
    bank_state=latest.groupby(['state','bank_id']).deposits_thousands.sum().reset_index()
    totals=bank_state.groupby('state').deposits_thousands.transform('sum')
    bank_state['share_sq']=(bank_state.deposits_thousands.div(totals.replace(0,np.nan))*100)**2
    state=state.merge(bank_state.groupby('state').share_sq.sum(min_count=1).rename('hhi'),on='state')
    state=state.where(state.notna(),None)
    yearly=df.groupby('year').agg(branches=('branch_id','size'),deposits_thousands=('deposits_thousands','sum')).reset_index()
    years=sorted(df.year.unique());cohort=dict(prior_year=None,net_change=None,added=None,removed=None,matched_growth_pct=None)
    if len(years)>1:
        prior=int(years[-2]);old=df[df.year==prior].set_index('branch_id');new=latest.set_index('branch_id')
        matched=old.index.intersection(new.index);base=float(old.loc[matched,'deposits_thousands'].sum())
        cohort=dict(prior_year=prior,net_change=len(new)-len(old),added=len(new.index.difference(old.index)),
            removed=len(old.index.difference(new.index)),matched_growth_pct=None if base==0 else round(100*(float(new.loc[matched,'deposits_thousands'].sum())/base-1),2))
    return dict(data_type='Synthetic demonstration',latest_year=year,total_deposits_thousands=round(total,2),
        branches=len(latest),states=state.round(2).astype(object).where(state.notna(),None).to_dict('records'),yearly=yearly.to_dict('records'),cohort=cohort)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--input',type=Path);p.add_argument('--fdic',action='store_true')
    a=p.parse_args()
    if a.fdic and not a.input:p.error('--fdic requires --input')
    df=pd.read_csv(a.input,dtype=str,keep_default_na=False) if a.input else sample()
    if a.fdic:df=df.rename(columns=FDIC)
    result=analyze(df)
    if a.input:result['data_type']='User-supplied FDIC export' if a.fdic else 'User-supplied input'
    out=ROOT/'outputs';out.mkdir(exist_ok=True)
    (out/'summary.json').write_text(json.dumps(result,indent=2,allow_nan=False))
    pd.DataFrame(result['states']).to_csv(out/'state_metrics.csv',index=False)
    if not a.input:
        (ROOT/'data').mkdir(exist_ok=True);df.to_csv(ROOT/'data/branches.csv',index=False)
    print(json.dumps(result,indent=2,allow_nan=False))
if __name__=='__main__':main()
