"""
Weeks 2-3 - Dataset Structuring and Validation (EDA)
Runs on the combined residential datasets produced by week1_aggregate.py.
Outputs: console report (structure, property types, nulls, distributions),
missing value report CSV, distribution figures, filtered dataset CSV.
"""

import os
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

CSV_DIR = 'csv'
FIG_DIR = 'figures/week2-3'
os.makedirs(FIG_DIR, exist_ok=True)

NUMERIC_FIELDS = ['ClosePrice', 'ListPrice', 'OriginalListPrice', 'LivingArea',
                  'LotSizeAcres', 'BedroomsTotal', 'BathroomsTotalInteger',
                  'DaysOnMarket', 'YearBuilt']
KEY_FIELDS = ['ClosePrice', 'LivingArea', 'DaysOnMarket']


def eda_report(df, name):
    print(f'\n{"="*60}\n{name.upper()} DATASET\n{"="*60}')

    # Structure
    print(f'Rows: {len(df):,}   Columns: {len(df.columns)}')
    print('\nDtypes summary:')
    print(df.dtypes.value_counts())

    # Property types
    if 'PropertyType' in df.columns:
        print('\nUnique PropertyType values:')
        print(df['PropertyType'].value_counts(dropna=False))
    if 'PropertySubType' in df.columns:
        print('\nTop PropertySubType values:')
        print(df['PropertySubType'].value_counts(dropna=False).head(15))

    # Missing value report
    nulls = df.isnull().sum()
    pct = (nulls / len(df) * 100).round(2)
    report = pd.DataFrame({'null_count': nulls, 'null_pct': pct})
    report = report.sort_values('null_pct', ascending=False)
    report.to_csv(os.path.join(CSV_DIR, f'missing_report_{name}.csv'))

    flagged = report[report['null_pct'] > 90]
    print(f'\nColumns >90% null ({len(flagged)}):')
    print(flagged.head(30).to_string())
    print(f'\nFull missing value report saved: missing_report_{name}.csv')

    # Numeric distributions 
    present = [c for c in NUMERIC_FIELDS if c in df.columns]
    if present:
        summary = df[present].describe(
            percentiles=[.01, .05, .25, .5, .75, .95, .99]).T
        summary.to_csv(os.path.join(CSV_DIR, f'distribution_summary_{name}.csv'))
        print('\nNumeric distribution summary:')
        print(summary.to_string())
        print(f'Saved: distribution_summary_{name}.csv')


    # Figures for the key deliverable fields
    # Two versions per field: raw (shows outlier impact) and clipped
    # (1st-99th percentile, outliers excluded FROM THE PLOT ONLY --
    # the underlying data is not modified).
    for col in KEY_FIELDS:
        if col not in df.columns:
            continue
        series = pd.to_numeric(df[col], errors='coerce').dropna()

        p01, p99 = series.quantile(0.01), series.quantile(0.99)
        clipped = series[(series >= p01) & (series <= p99)]
        n_excluded = len(series) - len(clipped)

        # RAW histogram
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.hist(series, bins=100)
        ax.set_title(f'{name}: {col} (raw, full range)')
        ax.set_xlabel(col); ax.set_ylabel('count')
        fig.tight_layout()
        fig.savefig(os.path.join(FIG_DIR, f'{name}_{col}_hist_raw.png'), dpi=120)
        plt.close(fig)

        # CLIPPED histogram
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.hist(clipped, bins=100)
        ax.set_title(f'{name}: {col} (1st-99th pctile, {n_excluded:,} rows excluded from plot)')
        ax.set_xlabel(col); ax.set_ylabel('count')
        fig.tight_layout()
        fig.savefig(os.path.join(FIG_DIR, f'{name}_{col}_hist_clipped.png'), dpi=120)
        plt.close(fig)

        # RAW boxplot
        fig, ax = plt.subplots(figsize=(8, 2.5))
        ax.boxplot(series, vert=False)
        ax.set_title(f'{name}: {col} boxplot (raw)')
        fig.tight_layout()
        fig.savefig(os.path.join(FIG_DIR, f'{name}_{col}_box_raw.png'), dpi=120)
        plt.close(fig)

        # CLIPPED boxplot
        fig, ax = plt.subplots(figsize=(8, 2.5))
        ax.boxplot(clipped, vert=False)
        ax.set_title(f'{name}: {col} boxplot (1st-99th pctile)')
        fig.tight_layout()
        fig.savefig(os.path.join(FIG_DIR, f'{name}_{col}_box_clipped.png'), dpi=120)
        plt.close(fig)

    print(f'Figures saved to {FIG_DIR}/ (raw + clipped versions)')


# Load combined datasets from week 1
sold = pd.read_csv(os.path.join(CSV_DIR, 'combined_sold_residential.csv'),
                   low_memory=False)
listings = pd.read_csv(os.path.join(CSV_DIR, 'combined_listings_residential.csv'),
                       low_memory=False)

eda_report(sold, 'sold')
eda_report(listings, 'listings')

# Datasets are already Residential-filtered from week 1; re-validate here.
print('\nValidation - PropertyType values remaining:')
print('sold:', sold['PropertyType'].unique())
print('listings:', listings['PropertyType'].unique())