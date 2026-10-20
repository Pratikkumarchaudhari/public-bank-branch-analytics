-- SQLite-compatible reference. Deposits remain in thousands of dollars.
WITH totals AS (
  SELECT year, state, SUM(deposits_thousands) AS deposits, COUNT(*) AS branches
  FROM branches GROUP BY year, state
)
SELECT *, ROUND(100.0 * deposits / NULLIF(SUM(deposits) OVER (PARTITION BY year),0),2) AS state_share_pct
FROM totals ORDER BY year, deposits DESC;

-- Matched-branch growth avoids mixing openings/closures into growth.
SELECT current.branch_id,
       100.0 * (current.deposits_thousands-prior.deposits_thousands)
       / NULLIF(prior.deposits_thousands,0) AS growth_pct
FROM branches current JOIN branches prior
ON current.branch_id=prior.branch_id AND current.year=prior.year+1;
