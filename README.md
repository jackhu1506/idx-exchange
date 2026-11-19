# idx-exchange

Data analyst internship project at IDX Exchange. Housing market analytics
pipeline built on CRMLS (California Regional Multiple Listing Service) data,
Jan 2024 – present: aggregation, cleaning, feature engineering, outlier
flagging, Tableau dashboards, and a San Diego market report.

## Deliverables

- [Market Analysis dashboard](https://public.tableau.com/app/profile/jack.hu1001/viz/market_analysis_17881435915340/market_analysis)
  – median close price, days on market, close-to-original-list ratio, closed
  sales, new listings, and mortgage rates vs. market activity (year-over-year)
- [Competitive Analysis dashboard](https://public.tableau.com/app/profile/jack.hu1001/viz/competitive_analysis_17881454950150/heatmaps)
  – top agents and brokerages by volume and units
- San Diego Residential Market Intelligence Report – 1-page market report
  covering price trends, market activity, and competitive landscape
  (`src/week11-12_report.py`). Not included in the repo because it contains
  agent-level names and figures.

## Structure

- `src/` – Python scripts, run in week order
- `figures/` – EDA and distribution charts, by week
- `summary_week*.md` – per-week method notes, results, and limitations
- Data (CSV), Tableau workbooks (`.twbx`), the market report, and program
  documents are local only (excluded via .gitignore) per program
  confidentiality requirements

## Pipeline

| Stage | Script | Output | Notes |
|---|---|---|---|
| Aggregate monthly files, filter to Residential | `week1_aggregate.py` | `combined_{sold,listings}_residential.csv` | [Week 1](summary_week1.md) |
| Structure & missingness EDA | `week2-3_eda.py` | missing / distribution reports | [Weeks 2–3](summary_week2-3.md) |
| Merge FRED 30-yr mortgage rate | `week2-3_mortgage.py` | `{sold,listings}_with_rates.csv` | [Weeks 2–3](summary_week2-3.md) |
| Clean: remove invalid rows, flag quality issues | `week4-5_cleaning.py` | `{sold,listings}_cleaned.csv` | [Weeks 4–5](summary_week4-5.md) |
| Engineer metrics, school-district spatial join | `week6_inspect.py`, `week6_features.py` | +10 columns per dataset | [Week 6](summary_week6.md) |
| IQR outlier flags | `week7_iqr.py` | `{sold,listings}_flagged.csv`, `{sold,listings}_analysis.csv` | [Week 7](summary_week7.md) |
| Tableau export: agent/office keys, format fixes | `week8_tableau.py` | `tableau_{sold,listings}.csv` | [Week 8](summary_week8.md) |
| Dashboards | Tableau | [Market](https://public.tableau.com/app/profile/jack.hu1001/viz/market_analysis_17881435915340/market_analysis), [Competitive](https://public.tableau.com/app/profile/jack.hu1001/viz/competitive_analysis_17881454950150/heatmaps) | [Weeks 9–10](summary_week9-10.md) |
| San Diego market report | `week11-12_report.py` | 1-page report (local only) | [Weeks 11–12](summary_week11-12.md) |

All CSV outputs are local only.

## Design decisions

- **Flag, don't delete.** Only always-invalid rows are removed (non-positive
  price or area, negative DOM). Data-quality issues and outliers become
  boolean flags; each analysis chooses which to apply.
- **Sold and listings are separate extracts.** Never unioned (listings holds
  only ~39% of closed sales); closed-sale metrics come from sold only.
- **Filter by statistic.** Averages exclude the relevant outlier flags;
  medians and counts use all rows.
- **Agents keyed by hashed email**, with emails backfilled within each name
  first. Names merge different agents. Offices have no identifier, so they
  are keyed by normalized name and their rankings are approximate.
- **Spatial join uses Unified districts only** to avoid duplicate matches.
  A null `DistrictName` doesn't always mean bad coordinates.
- **Rates vs. activity uses year-over-year change**, so seasonality doesn't
  appear as a false correlation.

## Known limitations

- IQR fences are statewide, so high-cost counties are flagged more heavily
- Shared brokerage inboxes merge unrelated agents under one key
- Dashboard filters don't reach New Listings (a separate data source)

## Running

Requires pandas and geopandas (see `requirements.txt`). Place the CRMLS
monthly CSVs in `data/` and run the scripts in `src/` in week order from the
repo root.