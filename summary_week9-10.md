# Weeks 9–10 – Tableau Dashboard Development

_Workbooks: `market_analysis.twbx` (built), `competitive_analysis.twbx`
(in progress). Sources: `tableau_sold.csv` (465,089 × 43),
`tableau_listings.csv` (631,564 × 43), separate extracts, not unioned._

## market_analysis.twbx

Six worksheets. Five required, one of my own design.

| Sheet | Source | Measure | Row filter |
|---|---|---|---|
| Median Close Price | sold | `MEDIAN(ClosePrice)` | none |
| Avg Days on Market | sold | `AVG(DaysOnMarket)` | `DaysOnMarket_outlier_flag = False` |
| Avg Close-to-Orig Ratio | sold | `AVG(CloseToOriginalListRatio)` | `ratio_implausible_flag = False` |
| Closed Sales | sold | `COUNT` | none |
| New Listings | listings | `COUNT` | none |
| Rates vs. Activity | sold | dual axis | none |

All time series use `MONTH(CloseDate)` as a continuous axis, so new months
appear automatically on refresh rather than requiring axis edits.

**Filter policy.** Averages exclude the week 7 outlier flags; medians and
counts do not. Median is robust to the tail by construction and a count is
indifferent to magnitude, so filtering those would discard valid sales for
no benefit. The two average dashboards are the only ones where a handful of
extreme rows move the number.

**Validation.** Median close price was checked against a pandas groupby
before any other sheet was built: January 2024 reads 749,000 in both, and
the axis carries 31 months (Jan 2024 – Jul 2026). Since every other sheet
inherits the same date grain and extract, one validated sheet confirms the
plumbing for all of them.

## Self-designed dashboard: mortgage rates vs. market activity

Uses `rate_30yr_fixed`, merged from FRED in weeks 2–3 and unused by any
required dashboard. It was not in the week 8 `KEEP` list — that list was
scoped to the required deliverables — so `week8_tableau.py` was widened to
carry it through.

**First version was misleading.** Monthly closed sales against the 30-year
fixed rate on a dual axis appeared to show the two series moving together.
That reading does not hold: closed sales carry strong seasonality (spring
peak, December trough, every year), and two seasonal series rescaled to fill
the same plot area will appear correlated whether or not they are related.
The chart could not distinguish a rate effect from coincident seasonality,
and the apparent relationship was partly an artifact of the axis bounds.

**Fix: year-over-year change.** Sales were converted to percent difference
against the same month one year prior. Seasonality is present in both the
numerator and denominator and cancels. This requires discrete
`YEAR` + `MONTH` date parts rather than a truncated month — Tableau needs a
year level to step across — and costs the first twelve months, since 2024
has no prior year. Nineteen usable months remain.

**Result.** The relationship inverts as theory predicts.

The unadjusted version is kept as a separate worksheet, off the dashboard,
for the week 11 presentation.

**Caveat.** `CloseDate` is escrow completion, typically 30–45 days after a
buyer locks a rate, so the visual alignment understates the true lag.

## AgentKey display normalization

The top-100 agent chart rendered multiple rows per key: `AgentKey` groups by
hashed email, but `ListAgentFullName` varies row to row, and Tableau makes one
row per unique dimension combination. One key showed nine.

Two distinct causes, quantified:

| | Keys affected | Share |
|---|--:|--:|
| >1 raw name per key | 1,457 | 1.70% |
| >1 name after casefold | 898 | 1.05% |

So ~560 were casing only (`Melissa Westfall` / `MELISSA WESTFALL`), and 898
genuinely carry multiple people under one email.

**Fix.** `add_display_name()` in `week8_tableau.py` sets `AgentDisplayName` to
the modal name variant per key, broadcast back to every row via `transform`.
One label per key, so the chart renders one row per agent.

**Limitation — this hides a real problem.** Of the top 100 by volume, five
keys carry more than one name. Four are correct behavior:

| Key | Names | Assessment |
|---|---|---|
| `3799878b11f8` | Brady Sandahl / Brady Sandah Real Estate Group | same agent, individual and team brand |
| `4e8b1d6eeec0` | Enrique Valdez / Henry Valdez | same agent, name variant |
| `68f6916b0a40` | Karen Myatt / Todd Myatt | partner team |
| `aa8d07fe2da6` | David Berg / F. Ron Smith | partner team |

The fifth, `4673f2497157`, merges Alexis Schlattman, Charmaine Frank, Gabriel
Valdez, and Melissa Westfall — unrelated agents sharing a brokerage inbox.
Their combined volume places the key in the top 100, and normalization now
labels that combined total with a single name. This is worse than the stacked
display, which at least looked wrong. Not corrected: hardcoding one hash is
brittle and would not generalize to future months.

This also qualifies the week 8 claim that email is one-per-agent. It holds for
~99% of keys; shared team addresses are the exception.

## Open items

- Cross-data-source filtering: City / County / Zip / PropertySubType filters
  reach the five sold-based sheets but not New Listings, which reads from the
  listings source. Options are per-source parameters, a blend relationship, or
  moving New Listings to its own dashboard. Unresolved.
- `.twbx` packages the full extract — 465,089 rows with coordinates, addresses,
  and agent names. Required as a deliverable but should not be committed
  without direction from Aidan.
- Week 7 IQR fence and week 8 counts shifted when July 2026 was added;
  `summary_week7.md` and `summary_week8.md` carry stale figures.