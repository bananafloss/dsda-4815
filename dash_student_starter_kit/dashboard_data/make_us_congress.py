"""

"""

import pandas as pd
import json

# ---------------------------------------------------------------
# Step 1: Load the raw election data
# ---------------------------------------------------------------
df = pd.read_csv('iowa_2014_precinct_database.csv')

# ---------------------------------------------------------------
# Step 2: Filter to US Senate races only
# ---------------------------------------------------------------
congress = df[df["RaceTitle"].str.startswith("U.S. Rep")].copy()

print(f"US Congress rows: {len(congress)}")
print(f"Unique precincts: {congress['shp_idx'].nunique()}")
print(f"Candidates: {congress['CandidateName'].unique()}")

# ---------------------------------------------------------------
# Step 3: Standardize party names
# ---------------------------------------------------------------
# The dashboard expects exactly: "Republican", "Democratic",
# "Libertarian", or "Other"
party_map = {
    'Republican Party': 'Republican',
    'Democratic Party': 'Democratic',
    'Libertarian Party': 'Libertarian',
}
# Anything not in the map becomes "Other"
# Check your data's exact party names — they may differ by state/year
congress['party'] = congress['PoliticalPartyName'].map(party_map).fillna('Other')

print(f"\nParty mapping:")
for orig, mapped in zip(congress['PoliticalPartyName'], congress['party']):
    pass  # just applying the map
print(congress.groupby(['PoliticalPartyName', 'party']).size().to_string())


# ---------------------------------------------------------------
# Step 4: Build precinct_rshare — R share per precinct
# ---------------------------------------------------------------


precinct_rshare = {}

for shp_idx, group in congress.groupby('shp_idx'):
    total = group['votes'].sum()
    r_votes = group.loc[group['party'] == 'Republican', 'votes'].sum()
    d_votes = group.loc[group['party'] == 'Democratic', 'votes'].sum()

    r_share = round(float(r_votes / total * 100), 1) if total > 0 else 0.0
    r_twoparty = round(float(r_votes / (r_votes + d_votes) * 100), 1) if (r_votes + d_votes) > 0 else 0.0

    # Keys must be strings; values must be plain Python types (not numpy)
    precinct_rshare[str(shp_idx)] = {
        'r_share': r_share,
        'r_twoparty': r_twoparty,
        'total_votes': int(total)
    }

print(f"\nprecinct_rshare: {len(precinct_rshare)} precincts")
# Show one example
print(f"Example (shp_idx '0'): {precinct_rshare.get('0')}")


# ---------------------------------------------------------------
# Step 5: Build results_district — candidate totals per district
# ---------------------------------------------------------------

results_district = {}

district_grouped = (
    congress
    .groupby(["congress_district", "CandidateName", "party"])["votes"]
    .sum()
    .reset_index()
)

for dist, g in district_grouped.groupby("congress_district"):
    g = g.sort_values("votes", ascending=False)
    total_all = g["votes"].sum()

    results_district[str(int(dist))] = [
        {
            "CandidateName": row["CandidateName"],
            "party": row["party"],
            "votes": int(row["votes"]),
            "share": round(float(row["votes"] / total_all * 100), 1) if total_all > 0 else 0.0
        }
        for _, row in g.iterrows()
    ]

print("\nresults_district:")
for d, cands in results_district.items():
    print(f"District {d}: {len(cands)} candidates")


# ---------------------------------------------------------------
# Step 6: Build results_precinct — candidate totals per precinct
# ---------------------------------------------------------------


results_precinct = {}

for shp_idx, group in congress.groupby('shp_idx'):
    total = group['votes'].sum()
    candidates = []
    for _, row in group.sort_values('votes', ascending=False).iterrows():
        candidates.append({
            'CandidateName': row['CandidateName'],
            'party': row['party'],
            'votes': int(row['votes']),
            'share': round(float(row['votes'] / total * 100), 1) if total > 0 else 0.0
        })
    results_precinct[str(shp_idx)] = candidates

print(f"\nresults_precinct: {len(results_precinct)} precincts")
print(f"Example (shp_idx '0'): {results_precinct.get('0')}")

# ---------------------------------------------------------------
# Step 7: Export to JSON
# ---------------------------------------------------------------


office_name = 'us_congress'

with open(f'dashboard_data/precinct_rshare_{office_name}.json', 'w') as f:
    json.dump(precinct_rshare, f)

with open(f'dashboard_data/results_district_{office_name}.json', 'w') as f:
    json.dump(results_district, f)

with open(f'dashboard_data/results_precinct_{office_name}.json', 'w') as f:
    json.dump(results_precinct, f)

print(f"\nJSON files created:")
print(f"  dashboard_data/precinct_rshare_{office_name}.json")
print(f"  dashboard_data/results_district_{office_name}.json")
print(f"  dashboard_data/results_precinct_{office_name}.json")
print(f"\nOpen the dashboard and select 'US Congress' from the dropdown to test.")
