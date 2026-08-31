import pandas as pd

df = pd.read_csv('data/tableau_sold.csv', low_memory=False)
sd = df[(df['City'].str.strip().str.upper() == 'SAN DIEGO') &
        (df['StateOrProvince'] == 'CA')].copy()

# Price stats exclude IQR outliers and implausible-ratio rows.
sd_clean = sd[~sd['any_outlier_flag'].fillna(False) &
              ~sd['ratio_implausible_flag'].fillna(False)]

removed = len(sd) - len(sd_clean)
print(f'Total closed sales: {len(sd):,}')
print(f'After filtering:    {len(sd_clean):,}  ({removed:,} removed, {removed/len(sd):.1%})')

# --- Monthly: median ratio, not mean ---
monthly = sd_clean.groupby('YrMo').agg(
    median_price=('ClosePrice', 'median'),
    avg_dom=('DaysOnMarket', 'mean'),
    ppsf=('PricePerSqFt', 'median'),
    ratio_med=('CloseToOriginalListRatio', 'median'),
    ratio_mean=('CloseToOriginalListRatio', 'mean'),
    n=('ClosePrice', 'size'),
).round(3)
print('\n--- Monthly ---')
print(monthly.to_string())

# --- Why the mean blew up: what is above 1.5 in those months? ---
susp = sd_clean[sd_clean['CloseToOriginalListRatio'] > 1.5]
print(f'\n--- Ratio > 1.5: {len(susp)} rows ---')
print(susp.groupby('YrMo').size().to_string())
print(susp[['YrMo', 'ClosePrice', 'OriginalListPrice',
            'CloseToOriginalListRatio']].nlargest(10, 'CloseToOriginalListRatio').to_string())

# --- Yearly summary for the report narrative ---
sd_clean = sd_clean.copy()
sd_clean['Yr'] = sd_clean['YrMo'].str[:4]
print('\n--- By year ---')
print(sd_clean.groupby('Yr').agg(
    median_price=('ClosePrice', 'median'),
    avg_dom=('DaysOnMarket', 'mean'),
    ppsf=('PricePerSqFt', 'median'),
    ratio_med=('CloseToOriginalListRatio', 'median'),
    n=('ClosePrice', 'size'),
).round(3).to_string())

# --- Market Activity ---
lst = pd.read_csv('data/tableau_listings.csv', low_memory=False)
lst_sd = lst[lst['City'].str.strip().str.upper() == 'SAN DIEGO']
print('\n--- New listings by month ---')
print(lst_sd.groupby('ListYrMo').size().to_string())

# --- Competitive Landscape ---
by_agent = sd_clean.groupby('AgentKey').agg(
    name=('AgentDisplayName', 'first'),
    volume=('ClosePrice', 'sum'),
    units=('ClosePrice', 'size'),
)
by_agent['avg_sale'] = (by_agent['volume'] / by_agent['units']).round(0)
print('\n--- Top 10 agents by volume ---')
print(by_agent.nlargest(10, 'volume').to_string())
print('\n--- Top 10 agents by units ---')
print(by_agent.nlargest(10, 'units').to_string())

by_office = sd_clean.groupby('OfficeKey').agg(
    name=('OfficeDisplayName', 'first'),
    volume=('ClosePrice', 'sum'),
    units=('ClosePrice', 'size'),
)
top10 = by_office.nlargest(10, 'volume')
print('\n--- Top 10 offices by volume ---')
print(top10.to_string())
print(f"\nTop 10 office share of units: {top10['units'].sum() / len(sd_clean):.1%}")
print(f"Distinct offices: {len(by_office):,}  |  Distinct agents: {len(by_agent):,}")