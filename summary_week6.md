convert file's native EPSG:3857 to EPSG:4326
# Week 6 – School District Boundary File Inspection

_Source: `data/DistrictAreas2526_-284845464123469011.geojson` (California School District Areas 2025-26, data.ca.gov). Inspection only; no data modified._

## File structure

| Property | Value |
|---|--:|
| Districts (rows) | 936 |
| Columns | 51 |
| CRS | EPSG:3857 (Web Mercator) |

## Key fields for the join

| Column | Purpose | Sample values |
|---|---|---|
| `DistrictName` | Becomes the new column on the property data | Alameda Unified, Berkeley Unified, Fremont Unified |
| `DistrictType` | Filter field — join uses `Unified` only | Unified, Elementary, High |
| `CountyName` | Available for cross-checking against `CountyOrParish` | Alameda, Fresno, Contra Costa |
| `geometry` | District boundary polygons used for point-in-polygon matching | — |

## Notes

- **CRS mismatch requires reprojection.** The boundary file is EPSG:3857 (meters, Web Mercator); property coordinates are EPSG:4326 (degrees, lat/lon). The districts are reprojected to EPSG:4326 before joining — without this the spatial join returns no matches.
- **Filtering to `DistrictType == 'Unified'`** avoids duplicate matches. Elementary and High districts can overlap the same geographic area, so joining against all three types would return multiple districts per property and multiply rows.
- **Tradeoff of the unified filter:** properties in areas served only by separate Elementary and High districts (no unified district) will return a null `DistrictName` despite having valid coordinates. Null district therefore means either invalid/missing coordinates, out-of-state location, or a non-unified area.
- The boundary file is a static geographic reference with no time dimension, so its school-year edition (2025-26) does not need to align with the property data's date range (Jan 2024–present). District boundaries change rarely.
- Only `DistrictName` and `geometry` are carried into the join; the remaining 49 columns (enrollment, demographics, locale codes) are not used.

# Week 6 – Feature Engineering and Market Metrics

_Source: `src/week6_features.py`. Inputs `data/sold_cleaned.csv` (448,036 × 85) and
`data/listings_cleaned.csv` (607,299 × 74). Outputs add 10 columns to each._

## Engineered columns

| Handbook metric | Column | Formula |
|---|---|---|
| Price Ratio | `PriceRatio` | ClosePrice / OriginalListPrice |
| Close to Original List Ratio | `CloseToOriginalListRatio` | ClosePrice / OriginalListPrice |
| Price Per Sq Ft | `PricePerSqFt` | ClosePrice / LivingArea |
| Days on Market | `DaysOnMarket` | raw field, unchanged |
| Year / Month / YrMo | `Year`, `Month`, `YrMo` | derived from CloseDate |
| Listing to Contract Days | `ListingToContractDays` | PurchaseContractDate − ListingContractDate |
| Contract to Close Days | `ContractToCloseDays` | CloseDate − PurchaseContractDate |
| (spatial join) | `DistrictName` | point-in-polygon vs. Unified districts |

## Coverage

| Column | Sold | Listings |
|---|--:|--:|
| PriceRatio | 99.8% | 28.8% |
| PricePerSqFt | 99.9% | 28.9% |
| DaysOnMarket | 100.0% | 100.0% |
| Year / Month / YrMo | 100.0% | 32.5% |
| ListingToContractDays | 100.0% | 50.5% |
| ContractToCloseDays | 100.0% | 32.5% |
| DistrictName | 74.9% | 66.8% |

Close-dependent metrics are sparse on listings by design: only closed records have
a `ClosePrice` or `CloseDate`. Both datasets run the same code path with no
dataset-specific branching, so coverage percentages surface the difference rather
than the script hardcoding it.

## Spatial join results

| | Sold | Listings |
|---|--:|--:|
| Valid coordinates | 443,614 (99.0%) | 526,423 (86.7%) |
| Matched to a Unified district | 335,408 (74.9%) | 405,841 (66.8%) |
| Valid coords, no district match | 108,206 | 120,582 |

The listings coordinate gap (13.3%) reflects that geocode-backfilled `_filled`
file variants exist only for the sold feed. Unmatched-but-valid rows are expected
from the Unified-only filter documented above; roughly a third of California
territory is served by separate Elementary and High districts with no Unified
district. No rows are dropped, they carry a null `DistrictName`.

## Method notes

- **Divide-by-zero guard.** Denominators pass through `.where(x > 0)` before
  division, converting zeros and negatives to NaN. Pandas otherwise returns
  `inf`, which passes `.notna()` and silently corrupts medians.
- **Date parsing** uses `errors='coerce'`; unparseable values become NaT and
  propagate as NaN