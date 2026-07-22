import pandas as pd

DATE_FIELDS = [
    'CloseDate',
    'PurchaseContractDate',
    'ListingContractDate',
    'ContractStatusChangeDate',
]

NUMERIC_FIELDS = [
    'ClosePrice',
    'ListPrice',
    'OriginalListPrice',
    'LivingArea',
    'LotSizeAcres',
    'BedroomsTotal',
    'BathroomsTotalInteger',
    'DaysOnMarket',
    'YearBuilt',
    'Latitude',
    'Longitude',
]

# Rough bounding box for California (used to flag implausible coordinates)
CA_LAT_MIN, CA_LAT_MAX = 32.0, 42.5
CA_LON_MIN, CA_LON_MAX = -125.0, -113.5

def convert_dates(df, name):
    """Step 1: convert date fields (where present) to datetime."""
    print(f'\n--- [{name}] Date conversion ---')
    for col in DATE_FIELDS:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
            print(f'  {col}: converted, dtype = {df[col].dtype}')
        else:
            print(f'  {col}: not present, skipped')
    return df


def drop_duplicate_columns(df, name):
    """Step 2a: drop redundant '.1' duplicate columns created by pandas
    auto-renaming during the Week 1 concat. Each duplicate is verified
    against its base column before removal; mismatches are kept and reported."""
    print(f'\n--- [{name}] Redundant column removal ---')
    dup_cols = [c for c in df.columns if c.endswith('.1') and c[:-2] in df.columns]

    dropped, kept = [], []
    for col in dup_cols:
        base = col[:-2]
        # .equals treats NaN == NaN as True, which is what we want here
        if df[col].equals(df[base]):
            dropped.append(col)
        else:
            kept.append(col)

    df = df.drop(columns=dropped)
    print(f'  Dropped {len(dropped)} verified duplicates:')
    for col in dropped:
        print(f'    - {col} (identical to {col[:-2]})')
    if kept:
        print(f'  WARNING: {len(kept)} .1 columns differ from base and were KEPT:')
        for col in kept:
            print(f'    - {col}')
    return df


def drop_empty_columns(df, name):
    """Step 2: drop 100%-empty columns; report columns >90% null but keep them."""
    print(f'\n--- [{name}] Column pruning ---')
    null_pct = df.isnull().mean()

    fully_empty = null_pct[null_pct == 1.0].index.tolist()
    high_null = null_pct[(null_pct > 0.9) & (null_pct < 1.0)].index.tolist()

    print(f'  Columns before: {df.shape[1]}')
    print(f'  Dropping {len(fully_empty)} fully empty (100% null) columns:')
    for col in fully_empty:
        print(f'    - {col}')
    df = df.drop(columns=fully_empty)
    print(f'  Columns after: {df.shape[1]}')

    print(f'  Retained {len(high_null)} columns with >90% (but <100%) nulls:')
    for col in high_null:
        print(f'    - {col} ({null_pct[col]:.1%} null)')
    return df


def coerce_numeric(df, name):
    """Step 3: ensure key numeric fields are properly typed."""
    print(f'\n--- [{name}] Numeric type coercion ---')
    for col in NUMERIC_FIELDS:
        if col in df.columns:
            before_nulls = df[col].isnull().sum()
            df[col] = pd.to_numeric(df[col], errors='coerce')
            new_nulls = df[col].isnull().sum() - before_nulls
            note = f' ({new_nulls} values coerced to NaN)' if new_nulls > 0 else ''
            print(f'  {col}: dtype = {df[col].dtype}{note}')
    return df


def remove_invalid_records(df, name):
    """Step 4: business-rule removal of always-invalid records."""
    print(f'\n--- [{name}] Business rule filtering ---')
    start = len(df)
    print(f'  Rows before: {start:,}')

    rules = []
    if 'ClosePrice' in df.columns:
        rules.append(('ClosePrice <= 0', df['ClosePrice'] <= 0))
    if 'LivingArea' in df.columns:
        rules.append(('LivingArea <= 0', df['LivingArea'] <= 0))
    if 'DaysOnMarket' in df.columns:
        rules.append(('DaysOnMarket < 0', df['DaysOnMarket'] < 0))
    if 'BedroomsTotal' in df.columns:
        rules.append(('BedroomsTotal < 0', df['BedroomsTotal'] < 0))
    if 'BathroomsTotalInteger' in df.columns:
        rules.append(('BathroomsTotalInteger < 0', df['BathroomsTotalInteger'] < 0))

    invalid_mask = pd.Series(False, index=df.index)
    for label, mask in rules:
        # NaN comparisons evaluate False, so nulls are retained (handled as missing, not invalid)
        count = mask.sum()
        print(f'  {label}: {count:,} rows removed')
        invalid_mask |= mask.fillna(False)

    df = df[~invalid_mask]
    print(f'  Rows after: {len(df):,} (removed {start - len(df):,})')
    return df


def add_date_consistency_flags(df, name):
    """Step 5: flag (not remove) records with illogical date ordering."""
    print(f'\n--- [{name}] Date consistency flags ---')

    has_listing = 'ListingContractDate' in df.columns
    has_purchase = 'PurchaseContractDate' in df.columns
    has_close = 'CloseDate' in df.columns

    if has_listing and has_close:
        df['listing_after_close_flag'] = df['ListingContractDate'] > df['CloseDate']
        print(f"  listing_after_close_flag: {df['listing_after_close_flag'].sum():,}")
    if has_purchase and has_close:
        df['purchase_after_close_flag'] = df['PurchaseContractDate'] > df['CloseDate']
        print(f"  purchase_after_close_flag: {df['purchase_after_close_flag'].sum():,}")
    if has_listing and has_purchase:
        # Negative timeline: purchase agreement signed before the listing agreement
        df['negative_timeline_flag'] = df['PurchaseContractDate'] < df['ListingContractDate']
        print(f"  negative_timeline_flag: {df['negative_timeline_flag'].sum():,}")

    if not (has_close or has_purchase):
        print('  No transaction date fields present, skipped (expected for listings dataset)')
    return df


def add_geo_flags(df, name):
    """Step 6: flag (not remove) geographic data quality issues."""
    print(f'\n--- [{name}] Geographic data quality ---')

    if 'Latitude' not in df.columns or 'Longitude' not in df.columns:
        print('  Latitude/Longitude not present, skipped')
        return df

    lat, lon = df['Latitude'], df['Longitude']

    df['geo_missing_flag'] = lat.isnull() | lon.isnull()
    df['geo_zero_flag'] = (lat == 0) | (lon == 0)
    df['geo_positive_lon_flag'] = lon > 0
    df['geo_out_of_state_flag'] = (
        ~df['geo_missing_flag']
        & ~df['geo_zero_flag']
        & (
            (lat < CA_LAT_MIN) | (lat > CA_LAT_MAX)
            | (lon < CA_LON_MIN) | (lon > CA_LON_MAX)
        )
    )

    print(f"  Missing coordinates: {df['geo_missing_flag'].sum():,}")
    print(f"  Zero (sentinel) coords: {df['geo_zero_flag'].sum():,}")
    print(f"  Positive longitude errors: {df['geo_positive_lon_flag'].sum():,}")
    print(f"  Out-of-state/implausible: {df['geo_out_of_state_flag'].sum():,}")
    return df


def clean_dataset(path, name, out_path):
    print(f'\n{"=" * 60}')
    print(f'Cleaning {name} ({path})')
    print(f'{"=" * 60}')

    df = pd.read_csv(path, low_memory=False)
    print(f'Loaded: {df.shape[0]:,} rows x {df.shape[1]} columns')

    df = drop_duplicate_columns(df, name)
    df = convert_dates(df, name)
    df = drop_empty_columns(df, name)
    df = coerce_numeric(df, name)
    df = remove_invalid_records(df, name)
    df = add_date_consistency_flags(df, name)
    df = add_geo_flags(df, name)

    df.to_csv(out_path, index=False)
    print(f'\nSaved cleaned dataset: {out_path}')
    print(f'Final shape: {df.shape[0]:,} rows x {df.shape[1]} columns')
    return df


if __name__ == '__main__':
    sold = clean_dataset(
        'csv/sold_with_rates.csv', 'SOLD', 'csv/sold_cleaned.csv'
    )
    listings = clean_dataset(
        'csv/listings_with_rates.csv', 'LISTINGS', 'csv/listings_cleaned.csv'
    )