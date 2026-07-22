# Weeks 4–5 Cleaning Summary

_Generated from `src/week4-5_cleaning.py` run on 2024 Jan–present CRMLS data._

## Row and column totals

| Dataset | Rows loaded | Rows removed | Rows final | Cols loaded | Cols final |
|---|--:|--:|--:|--:|--:|
| Sold | 448,253 | 217 | 448,036 | 86 | 85 |
| Listings | 607,724 | 425 | 607,299 | 86 | 74 |

_Final column counts include the 7 flag columns added during cleaning._

## Columns dropped

| Dataset | Duplicate (`.1`) | Fully empty | High-null (>90%) kept |
|---|--:|--:|--:|
| Sold | 0 | 8 | 7 |
| Listings | 11 | 8 | 5 |

Fully-empty columns (both datasets): FireplacesTotal, AboveGradeFinishedArea, TaxAnnualAmount, TaxYear, ElementarySchoolDistrict, BusinessType, CoveredSpaces, MiddleOrJuniorSchoolDistrict.

Duplicate columns appear only in the listing exports (source header duplication, renamed `.1` on load, verified identical before removal).

## Rows removed by business rule (always-invalid)

| Rule | Sold | Listings |
|---|--:|--:|
| ClosePrice ≤ 0 | 1 | 0 |
| LivingArea ≤ 0 | 165 | 393 |
| DaysOnMarket < 0 | 51 | 32 |
| BedroomsTotal < 0 | 0 | 0 |
| BathroomsTotalInteger < 0 | 0 | 0 |
| **Total** | **217** | **425** |

Nulls preserved (missing treated as missing, not invalid). Removals are 0.05% (sold) and 0.07% (listings).

## Date consistency flags (kept, not removed)

| Flag | Sold | Listings |
|---|--:|--:|
| listing_after_close | 70 | 85 |
| purchase_after_close | 239 | 266 |
| negative_timeline | 294 | 304 |

## Geographic quality flags (kept, not removed)

| Flag | Sold | Listings |
|---|--:|--:|
| Missing coordinates | 4,385 | 80,801 |
| Zero (0,0) sentinel | 37 | 75 |
| Positive longitude | 31 | 92 |
| Out-of-state / implausible | 63 | 251 |

## Notes

- **Listings coordinate gap:** 80,801 rows (~13%) lack coordinates vs ~1% for sold, because geocode-backfilled `_filled` variants exist only for sold months. Blocks the week 6 school-district join on those rows — confirm plan before starting week 6.
- Statistical (IQR) outlier handling deferred to week 7 by design; raw distributions preserved.
- Conservative by design: removes only always-invalid rows and flags the rest,
  since aggressive cleaning risks discarding valuable data for a marginally
  cleaner dataset