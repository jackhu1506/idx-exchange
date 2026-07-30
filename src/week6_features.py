import pandas as pd
import geopandas as gpd

DISTRICT_FILE = 'data/DistrictAreas2526_-284845464123469011.geojson'
WGS84 = 'EPSG:4326'   # plain lat/lon, the CRS of our property coordinates

def add_market_metrics(df, name):
    """Add the seven handbook metrics. Each is computed only where its inputs
    exist; rows missing an input get NaN for that metric (not an error)."""
    print(f'\n--- [{name}] Market metrics ---')

    # Guard against divide-by-zero: replace 0 denominators with NaN first.
    olp = df['OriginalListPrice'].where(df['OriginalListPrice'] > 0)
    living = df['LivingArea'].where(df['LivingArea'] > 0)

    # Price Ratio = ClosePrice / OriginalListPrice
    df['PriceRatio'] = df['ClosePrice'] / olp

    # Close-to-Original-List Ratio (same formula, kept as its own column)
    df['CloseToOrigListRatio'] = df['ClosePrice'] / olp
    df['PricePerSqFt'] = df['ClosePrice'] / living
    df['DaysOnMarketMetric'] = df['DaysOnMarket']

    # Year / Month / YrMo from CloseDate
    close = pd.to_datetime(df['CloseDate'], errors='coerce')
    df['Year'] = close.dt.year
    df['Month'] = close.dt.month
    df['YrMo'] = close.dt.to_period('M').astype('string')  # e.g. "2024-05"

    # Listing to Contract Days = PurchaseContractDate - ListingContractDate
    lcd = pd.to_datetime(df['ListingContractDate'], errors='coerce')
    pcd = pd.to_datetime(df['PurchaseContractDate'], errors='coerce')
    df['ListingToContractDays'] = (pcd - lcd).dt.days

    # Contract to Close Days = CloseDate - PurchaseContractDate
    df['ContractToCloseDays'] = (close - pcd).dt.days

    metrics = ['PriceRatio', 'CloseToOrigListRatio', 'PricePerSqFt',
               'DaysOnMarketMetric', 'Year', 'Month', 'YrMo',
               'ListingToContractDays', 'ContractToCloseDays']
    for m in metrics:
        populated = df[m].notna().sum()
        print(f'  {m}: {populated:,} populated ({populated / len(df):.1%})')
    return df

def add_school_district(df, name, districts_4326):
    """Point-in-polygon join: assign each property the Unified district whose
    polygon contains it. Only rows with valid coordinates are joined; all other
    rows are retained with a null DistrictName."""
    print(f'\n--- [{name}] School district spatial join ---')

    # Only join rows with usable coordinates (reuse week 4-5 flags).
    valid_mask = ~df['geo_missing_flag'] & ~df['geo_zero_flag']
    valid = df[valid_mask].copy()
    print(f'  Joinable rows (valid coords): {len(valid):,} of {len(df):,} '
          f'({len(valid) / len(df):.1%})')

    # Build points in lat/lon, then reproject to match the districts.
    points = gpd.GeoDataFrame(
        valid,
        geometry=gpd.points_from_xy(valid['Longitude'], valid['Latitude']),
        crs=WGS84,
    )

    joined = gpd.sjoin(
        points, districts_4326[['DistrictName', 'geometry']],
        how='left', predicate='within',
    )
    # sjoin can duplicate a point if district polygons overlap; keep first match.
    joined = joined[~joined.index.duplicated(keep='first')]

    # Merge the district result back onto the full frame by index so that
    # non-joined rows (missing/zero coords) keep a null district.
    df['DistrictName'] = joined['DistrictName']

    matched = df['DistrictName'].notna().sum()
    print(f'  Matched to a Unified district: {matched:,} ({matched / len(df):.1%})')
    unmatched_valid = valid_mask.sum() - matched
    print(f'  Valid coords but no district match: {unmatched_valid:,} '
          f'(out-of-state, or inside a non-Unified area)')
    return df

def print_sample_and_summary(df, name):
    """Deliverable output: a sample of new columns, plus a segmented summary."""
    print(f'\n--- [{name}] Sample of engineered columns ---')
    sample_cols = ['ClosePrice', 'OriginalListPrice', 'LivingArea',
                   'PriceRatio', 'PricePerSqFt', 'DaysOnMarketMetric',
                   'YrMo', 'ListingToContractDays', 'ContractToCloseDays',
                   'DistrictName']
    sample_cols = [c for c in sample_cols if c in df.columns]
    # Sample from rows where the transaction metrics are populated so the table
    # actually shows the new columns filled in.
    populated = df[df['PriceRatio'].notna()]
    show = populated.sample(10, random_state=42) if len(populated) >= 10 else populated
    with pd.option_context('display.max_columns', None, 'display.width', 200):
        print(show[sample_cols].to_string(index=False))

    print(f'\n--- [{name}] Segmented summary by CountyOrParish ---')
    if 'CountyOrParish' in df.columns:
        summary = df.groupby('CountyOrParish').agg(
            n=('ClosePrice', 'size'),
            n_priced=('ClosePrice', 'count'),
            median_close=('ClosePrice', 'median'),
            median_ppsf=('PricePerSqFt', 'median'),
            median_dom=('DaysOnMarket', 'median'),
            median_price_ratio=('PriceRatio', 'median'),
        ).sort_values('n', ascending=False)
        with pd.option_context('display.max_rows', 20, 'display.width', 200):
            print(summary.head(15).round(2).to_string())
    else:
        print('  CountyOrParish not present, skipped')

def load_districts():
    """Load CA school districts, keep only Unified, reproject to lat/lon."""
    gdf = gpd.read_file(DISTRICT_FILE)
    unified = gdf[gdf['DistrictType'] == 'Unified'].copy()
    unified_4326 = unified.to_crs(WGS84)
    return unified_4326


def process(path, name, out_path, districts_4326):
    print(f'\n{"=" * 60}')
    print(f'Processing {name} ({path})')
    print(f'{"=" * 60}')
    df = pd.read_csv(path, low_memory=False)
    print(f'Loaded: {df.shape[0]:,} rows x {df.shape[1]} columns')

    df = add_market_metrics(df, name)
    df = add_school_district(df, name, districts_4326)
    print_sample_and_summary(df, name)

    df.to_csv(out_path, index=False)
    print(f'\nSaved enriched dataset: {out_path}')
    print(f'Final shape: {df.shape[0]:,} rows x {df.shape[1]} columns')
    return df


if __name__ == '__main__':
    districts_4326 = load_districts()

    process('data/sold_cleaned.csv', 'SOLD',
            'data/sold_enriched.csv', districts_4326)
    process('data/listings_cleaned.csv', 'LISTINGS',
            'data/listings_enriched.csv', districts_4326)