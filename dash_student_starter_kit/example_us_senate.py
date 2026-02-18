"""
Example: Building dashboard JSON data for US Senate
====================================================
This script shows the complete pipeline from raw CSV to the three
JSON files needed by the election dashboard. Students should adapt
this for their assigned office.

US Senate is a statewide race, so the structure is simple:
- Every matched precinct has data
- There is one "statewide" district (no district numbers)

Usage:
    python example_us_senate.py
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
# Check the RaceTitle column to find the right filter string.
# For US Senate, the title is exactly "U.S. Senator"
senate = df[df['RaceTitle'] == 'U.S. Senator'].copy()

print(f"US Senate rows: {len(senate)}")
print(f"Unique precincts: {senate['shp_idx'].nunique()}")
print(f"Candidates: {senate['CandidateName'].unique()}")

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
senate['party'] = senate['PoliticalPartyName'].map(party_map).fillna('Other')

print(f"\nParty mapping:")
for orig, mapped in zip(senate['PoliticalPartyName'], senate['party']):
    pass  # just applying the map
print(senate.groupby(['PoliticalPartyName', 'party']).size().to_string())

# ---------------------------------------------------------------
# Step 4: Build precinct_rshare — R share per precinct
# ---------------------------------------------------------------
# For each precinct (shp_idx), we need:
#   r_share:     Republican votes / total votes * 100
#   r_twoparty:  Republican votes / (Republican + Democratic) * 100
#   total_votes: sum of all votes

precinct_rshare = {}

for shp_idx, group in senate.groupby('shp_idx'):
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
# US Senate is statewide, so the key is "statewide" (not a number)
# For Congress, Senate, House: keys would be district numbers as strings

district_totals = senate.groupby(['CandidateName', 'party'])['votes'].sum().reset_index()
district_totals = district_totals.sort_values('votes', ascending=False)
total_all = district_totals['votes'].sum()

results_district_list = []
for _, row in district_totals.iterrows():
    results_district_list.append({
        'CandidateName': row['CandidateName'],
        'party': row['party'],
        'votes': int(row['votes']),
        'share': round(float(row['votes'] / total_all * 100), 1)
    })

results_district = {'statewide': results_district_list}

print(f"\nresults_district:")
for c in results_district_list:
    print(f"  {c['CandidateName']} ({c['party']}): {c['votes']:,} votes ({c['share']}%)")

# ---------------------------------------------------------------
# Step 6: Build results_precinct — candidate totals per precinct
# ---------------------------------------------------------------
# Same structure as results_district, but keyed by shp_idx

results_precinct = {}

for shp_idx, group in senate.groupby('shp_idx'):
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
# Each team creates 3 files named with their office suffix.
# The dashboard fetches: precinct_rshare_OFFICE.json,
#   results_district_OFFICE.json, results_precinct_OFFICE.json
#
# For US Senate, the files are:
#   precinct_rshare_us_senate.json
#   results_district_us_senate.json
#   results_precinct_us_senate.json

office_name = 'us_senate'

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
print(f"\nOpen the dashboard and select 'US Senate' from the dropdown to test.")
