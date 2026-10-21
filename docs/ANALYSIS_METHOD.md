# How the branch network and deposit analysis works

[Dataset and provenance](../data/README.md) · [Static CSV](../data/branches.csv) · [Executable analysis](../analysis.py)

For the exact 6.56% calculation and the expanded cohort outputs, see the [Deposit growth walkthrough](DEPOSIT_GROWTH_WALKTHROUGH.md).

## Platforms actually used

| Purpose | Implementation |
|---|---|
| Data source | Synthetic CSV generated locally by Python |
| Main analysis | Python with Pandas: validation, group-by aggregation, joins, and cohort matching |
| Numerical validation | NumPy: finite-number checks and handling zero-denominator cases |
| Result files | CSV and JSON committed to GitHub |
| Report | Static HTML/CSS/JavaScript; its state selector displays the saved metrics |
| SQL examples | SQLite-compatible reference queries in sql/branch_analysis.sql |
| Automated verification | Python unittest and GitHub Actions |
| Hosting | Portfolio demonstration published through ChatGPT Sites |

The main results were computed by `analysis.py`, not by SQL, Snowflake, Tableau, Power BI, or a hosted database. The SQL file illustrates related queries; it is not called by the Python pipeline.

## 1. Load and validate

Without `--input`, the script generates the deterministic sample. With `--input`, Pandas loads a CSV. The `--fdic` flag renames supported FDIC columns to this project's schema.

The validator requires all five columns and nonempty input. It trims branch/bank/state values, rejects blank identifiers or state labels, converts year/deposits to numbers, rejects nonfinite values and negative deposits, requires integer years, and rejects duplicate (year, branch_id) keys.

It does not verify real bank identity, source completeness, or whether a state label is an officially valid jurisdiction. Validation is not a claim of real-world accuracy.

## 2. Summarize each year

Group by year and calculate:

- Number of branch records, equal to unique branch IDs within a validated year.
- Sum of deposits, retaining the source unit of thousands of dollars.

The current sample has 170 records in 2024 and 171 in 2025. Both years together contain 341 branch-year records; that is not 341 distinct branches.

## 3. Calculate latest-year state metrics

Select the maximum observation year: 2025 for the sample. Group its rows by state to obtain branch count and deposit total.

```text
state deposit share (%) =
100 × state deposits / deposits across all included latest-year rows
```

These are shares of the included synthetic sample, not a state's share of all US deposits. The saved sample's NY share is 21.93%. The dashboard state filter selects rows for display; it does not recalculate shares against a newly filtered denominator.

## 4. Calculate within-state concentration

First sum deposits by (state, bank_id). Within each state, calculate each included bank's deposit share in percentage points, square each share, and sum:

```text
HHI = sum((100 × bank deposits in state / total state deposits)²)
```

A one-bank state would have HHI 10,000. A zero-deposit state has an undefined HHI and is represented as null. The result is descriptive for the included sample, not a market-definition study or regulatory conclusion.

## 5. Separate footprint change from matched-branch growth

Compare IDs in the two latest available years. The code reports the prior year explicitly; it does not require the two years to be consecutive.

| Cohort calculation | Sample result |
|---|---:|
| IDs in latest year but absent from prior year | 9 entering IDs |
| IDs in prior year but absent from latest year | 8 exiting IDs |
| IDs present in both years | 162 matched IDs |
| Latest count minus prior count | +1 net change |

```text
matched-branch growth (%) =
100 × (latest deposits for matched IDs / prior deposits for those same IDs − 1)
```

The sample result is **6.56%**. This is growth in the matched cohort's aggregate deposits, not the average of individual branch growth percentages. If prior matched deposits are zero, growth is undefined and returned as null.

Entering/exiting IDs are not automatically proven openings/closures. Source coverage changes, identifier changes, and corrections can create the same pattern. In this sample those differences are deliberately constructed.

## 6. Save and present

- [outputs/summary.json](../outputs/summary.json): yearly metrics, latest-year state metrics, and cohort summary.
- [outputs/state_metrics.csv](../outputs/state_metrics.csv): latest-year state aggregates.
- [report.html](../report.html): saved interactive sample report.

Running the analysis now refreshes CSV/JSON outputs and the standalone HTML together. The additional outputs are `branch_comparison.csv`, `matched_by_state.csv`, and `matched_by_bank.csv`; `summary.json` also contains `growth_audit` and row-level comparison data. Publishing remains a separate step.

## Reproduce the calculation

```bash
python -m pip install -r requirements.txt
python analysis.py
python analysis.py --input data/branches.csv
python -m unittest discover -s tests -v
```

Use the virtual environment and Windows instructions in the main README when applicable. Ten Python tests cover key and numeric validation, HHI, independent source-CSV growth arithmetic, aggregate-versus-average growth, cohort and bridge reconciliation, zero denominators, single-year inputs, and latest-period group assignment. Three Node tests cover ledger filtering and CSV handling.

## What to say in an interview

> “I used a reproducible synthetic branch-year dataset and analyzed it with Python/Pandas. I validated keys and deposit values, aggregated geographic deposit shares, calculated within-state bank concentration, and matched branch IDs across two years to separate footprint change from cohort growth. I published the input CSV, code, and output files so the results can be inspected. The FDIC adapter is available for a future real-data analysis, but the published findings use synthetic data.”
