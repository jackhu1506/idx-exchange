# Weeks 2–3 Structuring & Validation Summary

_Generated from `src/week2-3_eda.py` and `src/week2-3_mortgage.py` on 2024 Jan–present CRMLS data. Read-only analysis; no records modified._

## Dataset dimensions

| Dataset | Rows | Columns | Columns >90% null |
|---|--:|--:|--:|
| Sold | 448,253 | 84 | 15 |
| Listings | 607,724 | 84 | 13 |

8 fields are 100% unpopulated in both feeds (AboveGradeFinishedArea, CoveredSpaces, TaxAnnualAmount, TaxYear, ElementarySchoolDistrict, FireplacesTotal, MiddleOrJuniorSchoolDistrict, BusinessType).

## Property composition

Both datasets filtered to `PropertyType == 'Residential'` (validated: only value remaining). SingleFamilyResidence dominates (~75% sold, ~73% listings), followed by Condominium and Townhouse.

## Key field distributions — Sold

| Field | Min | Median | 99th pct | Max |
|---|--:|--:|--:|--:|
| ClosePrice | 0 | 825,000 | 5,600,000 | 989,500,000 |
| LivingArea | 0 | 1,646 | 5,287 | 17,021,320 |
| DaysOnMarket | −288 | 18 | 233 | 12,430 |

## Key field distributions — Listings

| Field | Min | Median | 99th pct | Max |
|---|--:|--:|--:|--:|
| ClosePrice | 525 | 860,000 | 5,500,000 | 820,000,000 |
| LivingArea | 0 | 1,671 | 6,307 | 17,021,320 |
| DaysOnMarket | −58 | 11 | 134 | 1,063 |

Extreme min/max values (zero prices/areas, negative days on market, implausibly large maxes) confirm the presence of invalid records and outliers — motivating the business-rule cleaning in weeks 4–5 and IQR flagging in week 7. Raw distributions preserved here by design.

## Mortgage rate enrichment

- FRED MORTGAGE30US series (30-yr fixed, weekly) averaged to monthly rates
- Merged onto both datasets via `year_month` key (CloseDate for sold, ListingContractDate for listings)
- Validated: 0 unmatched rows in either dataset

## Outputs (local only)

`missing_report_sold.csv`, `missing_report_listings.csv`, `distribution_summary_sold.csv`, `distribution_summary_listings.csv`, `sold_with_rates.csv`, `listings_with_rates.csv`, plus distribution figures in `figures/week2-3/`.