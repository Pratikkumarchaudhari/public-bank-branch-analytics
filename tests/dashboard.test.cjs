const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'..'),api=require(path.join(root,'dashboard.js'));
const s=JSON.parse(fs.readFileSync(path.join(root,'outputs/summary.json'),'utf8'));
test('Cohort counts and source-row filters reconcile',()=>{
 assert.equal(api.filterBranches(s).length,179);assert.equal(api.filterBranches(s,{cohort:'matched'}).length,162);
 assert.equal(api.filterBranches(s,{cohort:'entering'}).length,9);assert.equal(api.filterBranches(s,{cohort:'exiting'}).length,8);
 assert.equal(api.filterBranches(s,{cohort:'matched',search:'SYN0001'})[0].prior_deposits_thousands,42919);
});
test('Combined filters and missing-period values stay explicit',()=>{
 const rows=api.filterBranches(s,{cohort:'matched',state:'NY',bank:'BANK01'});
 assert.ok(rows.length>0);assert.ok(rows.every(r=>r.latest_state==='NY'&&r.latest_bank_id==='BANK01'));
 const entering=api.filterBranches(s,{cohort:'entering'});assert.ok(entering.every(r=>r.prior_deposits_thousands===null&&r.branch_growth_pct===null));
});
test('Filtered CSV includes headers and neutralizes formula-like text',()=>{
 const csv=api.csv([{branch_id:'=1+1',cohort:'matched'}]);assert.ok(csv.includes('"\'=1+1"'));assert.equal(api.csv([]).split('\r\n').length,1);
});
