# idx-exchange

Data analyst internship project at IDX Exchange. Housing market analytics
pipeline built on CRMLS(California Regional Multiple Listing Service) 
MLS data (Jan 2024 - present), covering data aggregation, cleaning, 
feature engineering, and Tableau dashboards.

## Structure

- `src/` - Python scripts
- `figures/` - distribution charts and EDA visuals, organized by week
- Data files (CSV) and documents are local only and excluded via .gitignore,
  per program confidentiality requirements

## Progress

### Week 1 - Monthly Dataset Aggregation (`week1_aggregate.py`)
- Concatenates ~30 monthly CRMLS Listing and Sold CSV files into two combined
  datasets (Jan 2024 through the most recent completed month)
- Handles `_filled` file variants (coordinate-enriched versions), preferring
  them per month to avoid gaps and double-counting
- Filters both datasets to PropertyType == 'Residential'
- Sold: 448,253 rows | Listings: 607,724 rows (post-filter)
- Outputs: `combined_sold_residential.csv`, `combined_listings_residential.csv` (local only)

### Weeks 2-3 - Dataset Structuring & Validation (`week2-3_eda.py`)
- Structure report: dimensions, dtypes, property type composition
- Missing value analysis: per-column null counts/percentages, flags columns
  >90% null (15 in sold, 13 in listings; several fields 100% unpopulated in
  the CRMLS feed)
- Numeric distribution summaries (percentile tables) for ClosePrice,
  LivingArea, DaysOnMarket and other key fields
- Distribution figures: raw and 99th-percentile-clipped histograms/boxplots
  documenting extreme outliers 
- Outputs: `missing_report_sold.csv`, `missing_report_listings.csv`,
  `distribution_summary_sold.csv`, `distribution_summary_listings.csv`
  (all local only)