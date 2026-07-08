import os
import pandas as pd

CSV_DIR = 'csv'

# Step 1: Fetch mortgage rate data from FRED (no API key needed)
url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=MORTGAGE30US"
mortgage = pd.read_csv(url, parse_dates=['observation_date'])
mortgage.columns = ['date', 'rate_30yr_fixed']
print(f'FRED MORTGAGE30US: {len(mortgage):,} weekly observations, '
      f'{mortgage["date"].min().date()} to {mortgage["date"].max().date()}')

# Step 2: Resample weekly rates to monthly averages
mortgage['year_month'] = mortgage['date'].dt.to_period('M')
mortgage_monthly = (
    mortgage.groupby('year_month')['rate_30yr_fixed']
    .mean()
    .reset_index()
)
print(f'Resampled to {len(mortgage_monthly):,} monthly averages')

# Step 3: Load combined datasets and create matching keys
sold = pd.read_csv(os.path.join(CSV_DIR, 'combined_sold_residential.csv'),
                   low_memory=False)
listings = pd.read_csv(os.path.join(CSV_DIR, 'combined_listings_residential.csv'),
                       low_memory=False)

sold['year_month'] = pd.to_datetime(sold['CloseDate']).dt.to_period('M')
listings['year_month'] = pd.to_datetime(
    listings['ListingContractDate']).dt.to_period('M')

# Step 4: Merge
sold_with_rates = sold.merge(mortgage_monthly, on='year_month', how='left')
listings_with_rates = listings.merge(mortgage_monthly, on='year_month', how='left')

# Step 5: Validate
sold_nulls = sold_with_rates['rate_30yr_fixed'].isnull().sum()
listing_nulls = listings_with_rates['rate_30yr_fixed'].isnull().sum()
print(f'\nValidation - rows with no rate after merge:')
print(f'  sold:     {sold_nulls:,}')
print(f'  listings: {listing_nulls:,}')

if sold_nulls or listing_nulls:
    print('\nWARNING: unmatched rows found. Sample of unmatched year_month values:')
    if sold_nulls:
        print('  sold:', sold_with_rates.loc[
            sold_with_rates['rate_30yr_fixed'].isnull(), 'year_month'
        ].value_counts().head())
    if listing_nulls:
        print('  listings:', listings_with_rates.loc[
            listings_with_rates['rate_30yr_fixed'].isnull(), 'year_month'
        ].value_counts().head())

# Preview
print('\nPreview:')
print(sold_with_rates[
    ['CloseDate', 'year_month', 'ClosePrice', 'rate_30yr_fixed']
].head().to_string())

# Step 6: Save enriched datasets
sold_with_rates.to_csv(
    os.path.join(CSV_DIR, 'sold_with_rates.csv'), index=False)
listings_with_rates.to_csv(
    os.path.join(CSV_DIR, 'listings_with_rates.csv'), index=False)
print('\nSaved sold_with_rates.csv and listings_with_rates.csv')