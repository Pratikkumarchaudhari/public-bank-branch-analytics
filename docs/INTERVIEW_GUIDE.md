# Interview walkthrough: Bank Branch Network & Deposit Analysis

See [analysis methodology and platforms](ANALYSIS_METHOD.md) and [data provenance](../data/README.md) for the underlying dataset and calculations.

See the [exact deposit growth walkthrough](DEPOSIT_GROWTH_WALKTHROUGH.md) to explain the 6.56% numerator, denominator, matched IDs, and deposit bridge.

## 60-second explanation

“This is an independent portfolio project connecting my data stewardship experience with hands-on Python analysis. The question is: how to distinguish changes in a branch network from deposit growth? I used synthetic data so the work is reproducible and shareable. The synthetic sample contains 170 branches in 2024 and 171 in 2025: nine entering IDs and eight exiting IDs. Matched-branch deposit growth is 6.56%. All deposit values remain in thousands of dollars. I would validate the assumptions and outputs with a business owner before applying the method to real data.”

## Demonstrate it in five minutes

1. Show the business question and data dictionary in the README.
2. Open `report.html`; use the filter and explain the denominator or model threshold.
3. Trace one row through the executable Python code into the CSV/JSON output.
4. Run the tests and explain one edge case that could change the conclusion.
5. Discuss a limitation below and propose a measured next experiment.

## Architecture and tradeoffs

Require unique (year, branch_id) keys and finite, nonnegative deposits. Aggregate the latest year by state and bank; compute state shares and within-state HHI = sum of squared bank deposit shares (percentage points squared, range up to 10,000). Match IDs across the two latest available years to separate cohort growth from footprint changes. The prior period may not be the immediately preceding calendar year; its year is reported explicitly.

Use `python analysis.py --input local_data/SOD.csv --fdic` for a downloaded FDIC export. Expected FDIC headers: YEAR, UNINUMBR, CERT, STALPBR, DEPSUMBR. Download those fields through [FDIC BankFind](https://banks.data.fdic.gov/bankfind-suite/SOD/customDownload). Check the current field definitions and deposit units before importing. Combine annual exports if you need a two-period comparison. A real FDIC dataset was not downloaded or tested in this session.

## What I would change for production

Add source contracts, versioned datasets, access control, approved retention, source-to-report lineage, observed business SLAs, independent review, and monitoring for changing inputs. Current implementation stays local and has no enterprise deployment. SQL examples in analytics projects can be adapted to a governed Snowflake/dbt pipeline; they are not deployed Snowflake integrations.

## Strong questions to be ready for

- How did you prevent bad keys or missing values from changing the result?
- What is the denominator of each published metric?
- Which design choice is policy rather than an empirical finding?
- Which result would make you choose a simpler approach?
- What did you verify locally, and what remains untested?

## Honest resume wording after reviewing the code

“Implemented and evaluated an independent bank branch network & deposit analysis project using Python, reproducible synthetic data, automated validation, and an interactive results report.”

## Limits

The checked-in dataset is generated, not FDIC data. HHI is a descriptive concentration measure, not a regulatory or competitive finding. Deposit growth is nominal, not inflation-adjusted. Export coverage, branch identifier changes, and restatements can affect cohort matching. State share refers only to the included sample.
