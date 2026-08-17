import hashlib
import pandas as pd

# Columns the week 8-10 dashboards need, grouped by what they drive.
GEO = ['City', 'CountyOrParish', 'PostalCode', 'StateOrProvince',
       'Latitude', 'Longitude', 'DistrictName']
PROPERTY = ['PropertyType', 'PropertySubType', 'LivingArea', 'BedroomsTotal',
            'BathroomsTotalInteger', 'YearBuilt']
PRICE = ['ClosePrice', 'ListPrice', 'OriginalListPrice', 'PricePerSqFt',
         'PriceRatio', 'CloseToOriginalListRatio']
TIMING = ['CloseDate', 'ListingContractDate', 'PurchaseContractDate',
          'DaysOnMarket', 'ListingToContractDays', 'ContractToCloseDays',
          'Year', 'Month', 'YrMo']
COMPETITIVE = ['ListAgentFullName', 'AgentKey',
               'ListOfficeName', 'OfficeKey']
STATUS = ['MlsStatus']
FLAGS = ['ClosePrice_outlier_flag', 'LivingArea_outlier_flag',
         'DaysOnMarket_outlier_flag', 'any_outlier_flag',
         'ratio_implausible_flag']

KEEP = GEO + PROPERTY + PRICE + TIMING + COMPETITIVE + STATUS + FLAGS


def clean_zip(df, name):
    """PostalCode arrives as ZIP or ZIP+4, sometimes numeric. Tableau's
    geographic role only matches 5-digit strings, so normalize to that."""
    if 'PostalCode' not in df.columns:
        print(f'  [{name}] PostalCode not present, skipped')
        return df
    zips = df['PostalCode'].astype('string').str.strip()
    df['PostalCode'] = zips.str.extract(r'^(\d{5})', expand=False)
    bad = zips.notna().sum() - df['PostalCode'].notna().sum()
    print(f"  [{name}] PostalCode: {df['PostalCode'].notna().sum():,} valid "
          f"5-digit ({bad:,} unparseable)")
    return df


def add_listing_month(df, name):
    """YrMo is CloseDate-derived, so it is null for anything not closed.
    New-listing counts need their own month key off ListingContractDate."""
    if 'ListingContractDate' not in df.columns:
        print(f'  [{name}] ListingContractDate not present, skipped')
        return df
    lcd = pd.to_datetime(df['ListingContractDate'], errors='coerce')
    df['ListYear'] = lcd.dt.year
    df['ListMonth'] = lcd.dt.month
    df['ListYrMo'] = lcd.dt.to_period('M').astype('string')
    print(f"  [{name}] ListYrMo: {df['ListYrMo'].notna().sum():,} populated "
          f"({df['ListYrMo'].notna().mean():.1%})")
    return df


def select_columns(df, name):
    """Keep only dashboard columns. Reports anything missing rather than
    raising, so a renamed upstream column surfaces instead of silently
    dropping a dashboard field."""
    present = [c for c in KEEP if c in df.columns]
    missing = [c for c in KEEP if c not in df.columns]
    if missing:
        print(f'  [{name}] NOT FOUND (check before proceeding): {missing}')
    extra = [c for c in ['ListYear', 'ListMonth', 'ListYrMo'] if c in df.columns]
    print(f'  [{name}] Keeping {len(present) + len(extra)} of {len(df.columns)} columns')
    return df[present + extra]

def add_agent_key(df, name):
    """Build a per-agent grouping key for the top-100 agent dashboards."""
    if 'ListAgentEmail' not in df.columns:
        print(f'  [{name}] ListAgentEmail not present, skipped')
        return df

    email = df['ListAgentEmail'].astype('string').str.strip().str.lower()

    # Propagate each name's known email onto its blank rows before hashing.
    email = email.groupby(df['ListAgentFullName']).transform(
        lambda s: s.ffill().bfill())
    n_filled = email.notna().sum() - df['ListAgentEmail'].notna().sum()
    print(f'  [{name}] Backfilled {n_filled:,} emails within name groups')

    df['AgentKey'] = email.map(
        lambda e: hashlib.sha1(e.encode()).hexdigest()[:12] if pd.notna(e) else pd.NA
    )

    # Report keys and names over the same rows -- comparing keys on emailed
    # rows against names on all rows is not a valid comparison.
    sub = df[df['AgentKey'].notna()]
    print(f"  [{name}] AgentKey: {len(sub):,} keyed by email "
          f"({sub['AgentKey'].nunique():,} distinct agents vs "
          f"{sub['ListAgentFullName'].nunique():,} distinct names)")

    n_missing = df['AgentKey'].isna().sum()
    df['AgentKey'] = df['AgentKey'].fillna(
        'name:' + df['ListAgentFullName'].astype('string').str.lower().str.strip())
    print(f"  [{name}] Fallback: {n_missing:,} rows name-keyed "
          f"({df['AgentKey'].notna().sum():,} of {len(df):,} now keyed)")
    return df

def add_office_key(df, name):
    """No office ID in the feed. Normalize the name — casefold, strip
    punctuation and suffixes, collapse whitespace — so 'Compass, Inc.' and
    'COMPASS INC' group together. Imperfect; document it."""
    if 'ListOfficeName' not in df.columns:
        return df
    s = (df['ListOfficeName'].astype('string')
         .str.lower()
         .str.replace(r'[.,]', '', regex=True)
         .str.replace(r'\b(inc|llc|corp|co)\b', '', regex=True)
         .str.replace(r'\s+', ' ', regex=True)
         .str.strip())
    df['OfficeKey'] = s
    print(f"  [{name}] OfficeKey: {df['OfficeKey'].nunique():,} distinct vs "
          f"{df['ListOfficeName'].nunique():,} raw names")
    return df

def flag_implausible_ratio(df, name, threshold=5):
    """Flag (not null) rows where OriginalListPrice is wrong — placeholders,
    dropped zeros, and entry errors push PriceRatio far past the p99 of 1.28,
    which would wreck the required average close-to-original-list dashboard."""
    if 'PriceRatio' not in df.columns:
        return df
    df['ratio_implausible_flag'] = df['PriceRatio'] > threshold
    n = df['ratio_implausible_flag'].sum()
    print(f'  [{name}] ratio_implausible_flag (>{threshold}): {n:,} ({n / len(df):.3%})')
    return df

def process(path, name, out_path):
    print(f'\n{"=" * 60}\n{name} ({path})\n{"=" * 60}')
    df = pd.read_csv(path, low_memory=False)
    print(f'Loaded: {df.shape[0]:,} rows x {df.shape[1]} columns')

    df = clean_zip(df, name)
    df = add_listing_month(df, name)
    df = add_agent_key(df, name)
    df = add_office_key(df, name)
    df = flag_implausible_ratio(df, name)
    df = select_columns(df, name)

    df.to_csv(out_path, index=False)
    print(f'Saved: {out_path} ({df.shape[0]:,} rows x {df.shape[1]} columns)')
    return df


if __name__ == '__main__':
    process('data/sold_flagged.csv', 'SOLD', 'data/tableau_sold.csv')
    process('data/listings_flagged.csv', 'LISTINGS', 'data/tableau_listings.csv')