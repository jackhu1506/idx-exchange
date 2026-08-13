import pandas as pd

FIELDS = ['ClosePrice', 'LivingArea', 'DaysOnMarket']


def flag_outliers(df, name):
    """Add an IQR outlier flag per field, plus a combined any_outlier_flag."""
    print(f'\n--- [{name}] IQR bounds and flags ---')
    flag_cols = []

    for col in FIELDS:
        q1, q3 = df[col].quantile(0.25), df[col].quantile(0.75)
        iqr = q3 - q1
        lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr

        # NaN stays False: missing is not an outlier.
        flag = ((df[col] < lower) | (df[col] > upper)).fillna(False)
        flag_col = f'{col}_outlier_flag'
        df[flag_col] = flag
        flag_cols.append(flag_col)

        n = int(flag.sum())
        n_valued = int(df[col].notna().sum())
        p01, p99 = df[col].quantile(0.01), df[col].quantile(0.99)
        print(f'  {col}: Q1={q1:,.1f} Q3={q3:,.1f} '
              f'bounds=[{lower:,.1f}, {upper:,.1f}]')
        print(f'    1st pct={p01:,.1f}  99th pct={p99:,.1f}')
        print(f'    flagged {n:,} of {n_valued:,} valued rows '
              f'({n / n_valued:.2%})')

    df['any_outlier_flag'] = df[flag_cols].any(axis=1)
    n_any = int(df['any_outlier_flag'].sum())
    print(f'  any_outlier_flag: {n_any:,} of {len(df):,} rows '
          f'({n_any / len(df):.2%})')
    return df


def compare(full, clean, name):
    """Written comparison: size and medians before vs. after filtering."""
    print(f'\n--- [{name}] Before vs. after filtering ---')
    rows = []
    for col in FIELDS + ['PricePerSqFt', 'PriceRatio']:
        rows.append({
            'field': col,
            'median_before': full[col].median(),
            'median_after': clean[col].median(),
        })
    out = pd.DataFrame(rows).set_index('field')
    out['pct_change'] = ((out['median_after'] / out['median_before'] - 1) * 100)
    print(f'  Rows: {len(full):,} -> {len(clean):,} '
          f'({(len(clean) / len(full) - 1) * 100:.2f}%)')
    print(out.round(2).to_string())


def process(path, name, flagged_path, clean_path):
    print(f'\n{"=" * 60}')
    print(f'Processing {name} ({path})')
    print(f'{"=" * 60}')
    df = pd.read_csv(path, low_memory=False)
    print(f'Loaded: {df.shape[0]:,} rows x {df.shape[1]} columns')

    df = flag_outliers(df, name)
    clean = df[~df['any_outlier_flag']].copy()
    compare(df, clean, name)

    df.to_csv(flagged_path, index=False)
    clean.to_csv(clean_path, index=False)
    print(f'\nSaved flagged dataset: {flagged_path} ({len(df):,} rows)')
    print(f'Saved filtered dataset: {clean_path} ({len(clean):,} rows)')


if __name__ == '__main__':
    process('data/sold_enriched.csv', 'SOLD',
            'data/sold_flagged.csv', 'data/sold_analysis.csv')
    process('data/listings_enriched.csv', 'LISTINGS',
            'data/listings_flagged.csv', 'data/listings_analysis.csv')