# Week 7 Outlier Detection Summary

_Generated from `src/week7_outliers.py` run on the week 6 enriched datasets._

## Approach

IQR flagging (Tukey fences, Q1 − 1.5×IQR to Q3 + 1.5×IQR) on `ClosePrice`,
`LivingArea`, and `DaysOnMarket`. Four boolean columns added per dataset: one
flag per field plus a combined `any_outlier_flag`. No records deleted.

The handbook snippet filters rows directly, but its surrounding text and the
deliverable spec both call for flagging first and building a separate filtered
dataset. The prose is followed here, consistent with weeks 4-5. Missing values
are not treated as outliers; flag rates are reported against valued rows.

## IQR bounds and flag rates

| Dataset | Field | Bounds | 99th pct | Flagged |
|---|---|--:|--:|--:|
| Sold | ClosePrice | −512,500 – 2,387,500 | 5,575,000 | 33,464 (7.47%) |
| Sold | LivingArea | −216 – 3,688 | 5,288 | 19,578 (4.37%) |
| Sold | DaysOnMarket | −52 – 108 | 233 | 34,204 (7.63%) |
| Listings | ClosePrice | −532,500 – 2,487,500 | 5,500,000 | 12,764 (7.26%) |
| Listings | LivingArea | −333 – 3,883 | 6,309 | 29,923 (4.93%) |
| Listings | DaysOnMarket | −21 – 51 | 134 | 57,915 (9.54%) |

`any_outlier_flag`: 70,344 sold (15.70%), 92,084 listings (15.16%).

## Before vs. after filtering

| Field | Sold before | Sold after | Listings before | Listings after |
|---|--:|--:|--:|--:|
| Rows | 448,036 | 377,692 | 607,299 | 515,215 |
| ClosePrice | 825,000 | 787,500 | 860,000 | 828,800 |
| LivingArea | 1,646 | 1,572 | 1,672 | 1,611 |
| DaysOnMarket | 18 | 16 | 11 | 10 |
| PricePerSqFt | 537.19 | 526.75 | 563.98 | 554.17 |
| PriceRatio | 1.00 | 1.00 | 1.00 | 1.00 |

Largest median shift is DaysOnMarket (−11.1% sold, −9.1% listings); price and
PPSF move under 5%.

## Notes

- **IQR is one-sided here.** All lower bounds are negative and all three fields
  are positive by construction (non-positive values removed in week 4-5), so
  every flag is high-side. Expected for right-skewed distributions.
- **Fences sit well below the 99th percentile.** Sold ClosePrice cuts at 2.39M
  vs. a 99th percentile of 5.58M — this removes the top 7.5% of the market, not
  a thin tail of implausible values.
- **Filtered dataset is geographically biased.** A single statewide fence hits
  high-cost counties hardest: Santa Clara (median 1.60M) and San Mateo (1.70M)
  sit near the cut, Kern (370K) is barely affected.
- **Filtering costs 15.7% of rows and moves medians under 5%.** Medians are
  robust to tails by construction, so the tradeoff is poor for median-based
  reporting. Would matter more for mean-based metrics.
- **DaysOnMarket is the most defensible field to filter** — largest median
  shift, and a genuine long tail of stale and relisted listings.
- **Recommendation:** treat the flagged dataset as primary and apply flags per
  analysis; `any_outlier_flag` is the most aggressive option and rarely the
  right one, since an unusual DOM does not invalidate a price.

## Limitations

- Global fences, not per-county — computed statewide per the spec snippet.
  Per-county or per-PropertySubType fences would remove the geographic bias
  above; worth revisiting before the week 8-10 dashboards.
- Listings filtering is driven mainly by LivingArea and DaysOnMarket, since
  ClosePrice is 71% null and most rows pass the price check by default.
- IQR assumes roughly symmetric distributions; none of the three fields
  qualifies. Percentile cutoffs are reported above as a reference point.

## Outputs (local only)

`sold_flagged.csv` (448,036), `sold_analysis.csv` (377,692),
`listings_flagged.csv` (607,299), `listings_analysis.csv` (515,215).