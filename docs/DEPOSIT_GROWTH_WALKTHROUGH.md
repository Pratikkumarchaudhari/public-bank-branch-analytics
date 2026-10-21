# Exactly where 6.56% comes from

[Open the granular dashboard](https://pratikkumar-data-ai-portfolio.woollydog11.chatgpt.site/demos/public-bank-branch-analytics.html) · [Source CSV](../data/branches.csv) · [Branch comparison CSV](../outputs/branch_comparison.csv)

## What question does the percentage answer?

**How much did deposits change for the same branches present in both years?** It measures aggregate growth for a fixed set of branch IDs. It does not combine that growth with entering or exiting records.

The dataset is generated synthetic data, not a real FDIC download. The 6.56% is calculated from the generated values; it is not evidence about actual banks or an employer result.

## Step 1: define the grain and the join

Each source row is one branch ID in one observation year, with a fictional bank, state, and deposit value. The source has 341 rows: 170 in 2024 and 171 in 2025. A unique record key is `(year, branch_id)`.

The pipeline validates keys and numeric values, then outer-joins the two periods on branch_id. Each ID is classified once:

| Classification | Rule | IDs | Used in matched growth? |
|---|---|---:|---|
| Matched | Present in 2024 and 2025 | 162 | Yes |
| Entering | Present only in 2025 | 9 | No |
| Exiting | Present only in 2024 | 8 | No |

Reconciliation: 162 + 8 = 170 prior-year IDs, and 162 + 9 = 171 latest-year IDs. The union has 179 IDs, not 341 distinct branches.

Entering IDs are SYN0172 through SYN0180. Exiting IDs are SYN0019, SYN0038, SYN0057, SYN0076, SYN0095, SYN0114, SYN0133, and SYN0152. SYN0171 is absent in both periods because of the sample construction; it is not a matched or entering ID.

In real data, entering/exiting records are not automatically proven branch openings/closures. Source coverage changes, identifier changes, and corrections can cause the same pattern.

## Step 2: sum deposits for only the 162 matched IDs

**All deposit amounts in the tables and formula are in thousands of dollars ($000).** Multiply by 1,000 to express them in dollars. Using the same units in numerator and denominator leaves the percentage unchanged.

| Quantity | Amount ($000) |
|---|---:|
| Prior deposits for the 162 matched IDs | 21,756,069.00 |
| Latest deposits for those same 162 IDs | 23,182,213.20 |
| Increase for the matched cohort | 1,426,144.20 |

## Step 3: divide the increase by the prior matched deposits

```text
Matched growth (%) =
100 × (latest matched deposits − prior matched deposits) / prior matched deposits

= 100 × (23,182,213.20 − 21,756,069.00) / 21,756,069.00
= 100 × 1,426,144.20 / 21,756,069.00
= 6.5551557131...%
≈ 6.56%
```

The pipeline rounds the final percentage to two decimal places for the headline. It also saves the unrounded ratio and its numerator/denominator in `outputs/summary.json` under `growth_audit`.

If prior matched deposits are zero, the percentage is undefined and the application returns null, displayed as a dash. It does not manufacture a 0% result.

## Step 4: inspect individual branches

| Branch | Prior deposits ($000) | Latest deposits ($000) | Increase ($000) | Individual growth |
|---|---:|---:|---:|---:|
| SYN0001 | 42,919.00 | 44,421.16 | 1,502.16 | 3.50% |
| SYN0002 | 50,838.00 | 53,125.71 | 2,287.71 | 4.50% |
| SYN0003 | 58,757.00 | 61,988.63 | 3,231.63 | 5.50% |

These three examples are part of the 162-row matched cohort. The export contains every matched, entering, and exiting ID, with period-specific bank/state values.

**The headline is not the simple average of individual percentages.** It is aggregate deposit growth, equivalently a prior-deposit-weighted average when all included branches have positive prior deposits. A branch with a larger starting balance contributes more to the aggregate result.

For example, one branch growing from 100 to 200 and another staying at 900 have individual rates of 100% and 0%. Their simple average is 50%, but their combined deposits grow from 1,000 to 1,100: aggregate growth is 10%. A test in this repository checks this distinction.

## Step 5: reconcile matched growth with total growth

| Bridge step | Change ($000) | Running deposits ($000) |
|---|---:|---:|
| Start with all 2024 deposits | — | 22,652,665.00 |
| Remove the 8 exiting IDs' prior deposits | −896,596.00 | 21,756,069.00 |
| Add matched-branch deposit growth | +1,426,144.20 | 23,182,213.20 |
| Add the 9 entering IDs' latest deposits | +1,332,411.78 | 24,514,624.98 |

```text
All-branch total growth (%)
= 100 × (24,514,624.98 − 22,652,665.00) / 22,652,665.00
= 8.2196067438...%
≈ 8.22%
```

Therefore, **6.56% answers the fixed-cohort question** and **8.22% answers the total-included-network question**. Neither number substitutes for the other. The bridge demonstrates that the change is fully accounted for, with a zero reconciliation residual in the sample.

## More granular outputs

| File | What it lets you inspect |
|---|---|
| [branch_comparison.csv](../outputs/branch_comparison.csv) | Every ID's cohort, period-specific bank/state, deposits, delta, and individual matched-growth rate |
| [matched_by_state.csv](../outputs/matched_by_state.csv) | Matched branch counts and aggregate growth grouped by latest state |
| [matched_by_bank.csv](../outputs/matched_by_bank.csv) | The same breakdown grouped by latest bank |
| [summary.json](../outputs/summary.json) | Exact cohort totals, unrounded growth, bridge, and headline metrics |

State/bank breakdowns assign matched IDs to their latest-period group. If a branch moves between states or banks, those are not automatically same-state or same-bank cohorts. Preserve prior/latest classifications when interpreting real data. Filtering the dashboard ledger selects evidence rows; it does not change the headline calculation.

## How this relates to the project's purpose

The project goes beyond reporting a single percentage:

1. **Validate the data:** avoid duplicate branch-year rows or invalid deposit values changing the answer.
2. **Explain network change:** show entering, exiting, and matched IDs instead of relying only on a net count.
3. **Isolate comparable growth:** use the same branch set for numerator and denominator.
4. **Locate contributions:** inspect state/bank cohorts and individual branches.
5. **Reconcile totals:** connect the fixed-cohort finding to the complete network change.
6. **Make the work auditable:** publish the input, formulas, comparison rows, tests, and limitations.

This demonstrates analytical judgment and traceability. Synthetic data demonstrates the method, not real-world banking conclusions.

## Reproduce it

```bash
python analysis.py
python -m unittest discover -s tests -v
node --test tests/dashboard.test.cjs
```

After dependency setup, the first command recreates the sample, detailed outputs, and report.html. Use `--input` to analyze a compatible CSV instead. `python render_report.py` rebuilds the HTML from a saved summary. Hosted results update only when the regenerated report is published.

Ten Python tests and three Node dashboard-logic tests passed in the build workspace. Tests include independent decimal arithmetic over the source CSV, aggregate-versus-average growth, bridge/cohort reconciliation, zero denominators, missing comparison years, latest-group assignment, filters, and export handling. Browser interaction remains unverified in that workspace.
