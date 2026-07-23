import geopandas as gpd

gdf = gpd.read_file('data/DistrictAreas2526_-284845464123469011.geojson')
print("shape:", gdf.shape)
print("crs:", gdf.crs)
print("columns:", gdf.columns.tolist())

for c in gdf.columns:
    if 'district' in c.lower() or 'name' in c.lower() or 'type' in c.lower():
        print(f"\n{c} unique values (first 10):")
        print(gdf[c].unique()[:10])