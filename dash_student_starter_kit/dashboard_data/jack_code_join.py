# ---------------------------------------------
# Renewable Energy Projects -> Iowa Precincts
# Spatial Join Script
# ---------------------------------------------

import json
import pandas as pd
import geopandas as gpd

# ---------------------------------------------
# File paths
# ---------------------------------------------

RENEWABLE_FILE = "renewables16.json"
PRECINCT_FILE = "precincts.geojson"
OUTPUT_FILE = "renewables_precinct_join.csv"

# ---------------------------------------------
# 1. Load and parse the JSON
# ---------------------------------------------

with open(RENEWABLE_FILE, "r", encoding="utf-8") as f:
    raw = json.load(f)

# The plant records are nested here:
# raw["response"]["data"]
plants = pd.DataFrame(raw["response"]["data"])

print("Total plants in JSON:", len(plants))
print("Plant columns:")
print(plants.columns.tolist())

# ---------------------------------------------
# 2. Prepare plant data for spatial join
# ---------------------------------------------

# Convert coordinates to numeric
plants["latitude"] = pd.to_numeric(plants["latitude"], errors="coerce")
plants["longitude"] = pd.to_numeric(plants["longitude"], errors="coerce")

# Convert capacity to numeric
plants["nameplate-capacity-mw"] = pd.to_numeric(
    plants["nameplate-capacity-mw"],
    errors="coerce"
)

# Drop rows missing coordinates, if any
plants = plants.dropna(subset=["latitude", "longitude"]).copy()

# Create point geometry from longitude (x) and latitude (y)
plants_gdf = gpd.GeoDataFrame(
    plants,
    geometry=gpd.points_from_xy(plants["longitude"], plants["latitude"]),
    crs="EPSG:4326"
)

# ---------------------------------------------
# 3. Load precinct polygons
# ---------------------------------------------

precincts = gpd.read_file(PRECINCT_FILE)

print("\nPrecinct columns:")
print(precincts.columns.tolist())

# Make sure precincts are also in EPSG:4326
if precincts.crs is None:
    precincts = precincts.set_crs("EPSG:4326")
else:
    precincts = precincts.to_crs("EPSG:4326")

# ---------------------------------------------
# 4. Spatial join
# ---------------------------------------------

# Keep all plants, even if one does not match a precinct
joined = gpd.sjoin(
    plants_gdf,
    precincts,
    how="left",
    predicate="within"
)

print("\nRows after spatial join:", len(joined))

# ---------------------------------------------
# 5. Build final output table
# ---------------------------------------------

# In precincts.geojson, the precinct name column is:
# name
final_df = joined[
    [
        "plantName",
        "technology",
        "nameplate-capacity-mw",
        "county",
        "name",
        "congress_dist",
        "senate_dist",
        "house_dist"
    ]
].rename(columns={
    "plantName": "plant_name",
    "technology": "technology",
    "nameplate-capacity-mw": "capacity_mw",
    "county": "county",
    "name": "precinct_name",
    "congress_dist": "us_house_district",
    "senate_dist": "state_senate_district",
    "house_dist": "state_house_district"
})

# Optional: sort for easier reading
final_df = final_df.sort_values(
    by=["plant_name", "technology"],
    ascending=[True, True]
).reset_index(drop=True)

# ---------------------------------------------
# 6. Export CSV
# ---------------------------------------------

final_df.to_csv(OUTPUT_FILE, index=False)

print("\nCSV written to:", OUTPUT_FILE)
print("Final row count:", len(final_df))
print("\nPreview:")
print(final_df.head())