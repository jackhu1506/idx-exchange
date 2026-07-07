"""
Week 1 - Monthly Dataset Aggregation
Concatenates all monthly CRMLS Listing and Sold files (Jan 2024 through the
most recently completed month), filters to Residential, saves combined CSVs.

For Sold files, some months exist as a "_filled" variant (same data plus
latfilled/lonfilled flags from a coordinate-filling pass). Where both exist,
the _filled version is preferred; otherwise the plain file is used.
"""

import glob
import os
import pandas as pd

CSV_DIR = 'csv'

def pick_sold_files():
    """Return one Sold file per month, preferring the _filled variant."""
    all_sold = glob.glob(os.path.join(CSV_DIR, 'CRMLSSold2*.csv'))
    by_month = {}
    for path in all_sold:
        name = os.path.basename(path)
        # month key = YYYYMM regardless of suffix
        month = name.replace('CRMLSSold', '')[:6]
        is_filled = '_filled' in name
        if month not in by_month or is_filled:
            by_month[month] = path
    return [by_month[m] for m in sorted(by_month)]

def load_and_combine(files, label):
    frames = []
    for f in files:
        df = pd.read_csv(f, low_memory=False)
        print(f'{label}: {os.path.basename(f)} -> {len(df):,} rows')
        frames.append(df)
    combined = pd.concat(frames, ignore_index=True)
    return combined

# Sold
sold_files = pick_sold_files()
sold = load_and_combine(sold_files, 'Sold')
print(f'\nSold combined (before Residential filter): {len(sold):,} rows')

sold_res = sold[sold['PropertyType'] == 'Residential']
print(f'Sold combined (after Residential filter):  {len(sold_res):,} rows')

# Listings
listing_files = sorted(glob.glob(os.path.join(CSV_DIR, 'CRMLSListing2*.csv')))
listings = load_and_combine(listing_files, 'Listing')
print(f'\nListings combined (before Residential filter): {len(listings):,} rows')

listings_res = listings[listings['PropertyType'] == 'Residential']
print(f'Listings combined (after Residential filter):  {len(listings_res):,} rows')

sold_res.to_csv(os.path.join(CSV_DIR, 'combined_sold_residential.csv'), index=False)
listings_res.to_csv(os.path.join(CSV_DIR, 'combined_listings_residential.csv'), index=False)
print('\nSaved combined_sold_residential.csv and combined_listings_residential.csv')