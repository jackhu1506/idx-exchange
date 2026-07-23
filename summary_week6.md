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