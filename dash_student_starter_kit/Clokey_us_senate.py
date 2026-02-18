import pandas as pd
# pandas is used for reading and manipulating the data
import json
# json exports the results into JSON files

df = pd.read_csv('C:/Users/18607/OneDrive - University of Connecticut/26 Spring/DSDA 4815/iowa-dashboard/iowa_2014_precinct_database.csv')
#loads the cleaned 2014 precinct-level database into the working environment as a data frame

senate = df[df['RaceTitle'] == 'U.S. Senator'].copy()
#this command filders to the US Senate race specifically, only keeping rows where the RaceTitle is "U.S. Senator"

print(f"US Senate rows: {len(senate)}")
#prints how many total rows exist in the data frame

print(f"Unique precincts: {senate['shp_idx'].nunique()}")
#prints the number of unique precincts

print(f"Candidates: {senate['CandidateName'].unique()}")
#prints the unique candidates in the data frame

party_map = {
    'Republican Party': 'Republican',
    'Democratic Party': 'Democratic',
    'Libertarian Party': 'Libertarian',
}
#changes the labels from the data frame to shorter, one-word party names

senate['party'] = senate['PoliticalPartyName'].map(party_map).fillna('Other')
#converts to the shorter party labels, labels those not in the party_map as "Other"

print(f"\nParty mapping:")
for orig, mapped in zip(senate['PoliticalPartyName'], senate['party']):
    pass  
print(senate.groupby(['PoliticalPartyName', 'party']).size().to_string())
#verifies the party mapping by printing the number of rows that fall under each mapped party name

precinct_rshare = {}

for shp_idx, group in senate.groupby('shp_idx'):
    total = group['votes'].sum()
    r_votes = group.loc[group['party'] == 'Republican', 'votes'].sum()
    d_votes = group.loc[group['party'] == 'Democratic', 'votes'].sum()

    r_share = round(float(r_votes / total * 100), 1) if total > 0 else 0.0
    r_twoparty = round(float(r_votes / (r_votes + d_votes) * 100), 1) if (r_votes + d_votes) > 0 else 0.0

    precinct_rshare[str(shp_idx)] = {
        'r_share': r_share,
        'r_twoparty': r_twoparty,
        'total_votes': int(total)
    }

print(f"\nprecinct_rshare: {len(precinct_rshare)} precincts")
#This code creates a dictionary that loops over each precinct
#For each precinct, total votes, Republican votes, and Democratic votes are tallied
#Republican share of all votes is calculated from r_share
#Republican share when only considering Republican and Democratic votes is calculated from r_twoparty
#Results are stored in the initial dictionary with their corresponding titles

print(f"Example (shp_idx '0'): {precinct_rshare.get('0')}")

district_totals = senate.groupby(['CandidateName', 'party'])['votes'].sum().reset_index()
district_totals = district_totals.sort_values('votes', ascending=False)
total_all = district_totals['votes'].sum()
#district_totals sums votes for each US Senate candidate and sorts them descendingly
#total_all provides total statewide votes

results_district_list = []
for _, row in district_totals.iterrows():
    results_district_list.append({
        'CandidateName': row['CandidateName'],
        'party': row['party'],
        'votes': int(row['votes']),
        'share': round(float(row['votes'] / total_all * 100), 1)
    })
#This builds a statewide results list including candidate name, party, votes, and vote share

results_district = {'statewide': results_district_list}
#This creates a dictionary for the district results

print(f"\nresults_district:")
for c in results_district_list:
    print(f"  {c['CandidateName']} ({c['party']}): {c['votes']:,} votes ({c['share']}%)")
#This prints a summary for each candidate from the district results

results_precinct = {}
#creates dictionary for candidate results per precinct

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
#loops through precincts, sorting candidates by vote count, computing vote share within each precinct, and storing a list of candidate results

print(f"\nresults_precinct: {len(results_precinct)} precincts")
print(f"Example (shp_idx '0'): {results_precinct.get('0')}")
#prints how many precincts were looped through and an example set of precinct data

office_name = 'us_senate'
# sets the office name for future use

with open(f'C:/Users/18607/OneDrive - University of Connecticut/26 Spring/DSDA 4815/iowa-dashboard/precinct_rshare_{office_name}.json', 'w') as f:
    json.dump(precinct_rshare, f)

with open(f'C:/Users/18607/OneDrive - University of Connecticut/26 Spring/DSDA 4815/iowa-dashboard/results_district_{office_name}.json', 'w') as f:
    json.dump(results_district, f)

with open(f'C:/Users/18607/OneDrive - University of Connecticut/26 Spring/DSDA 4815/iowa-dashboard/results_precinct_{office_name}.json', 'w') as f:
    json.dump(results_precinct, f)
#creates the JSON files using the 3 dictionaries written in the above code, storing them in a designated directory on my computer
#these JSON files control map colors, create the sidebar summary, and populate the sidebar detail view for specific precincts

print(f"\nJSON files created:")
print(f"  dashboard_data/precinct_rshare_{office_name}.json")
print(f"  dashboard_data/results_district_{office_name}.json")
print(f"  dashboard_data/results_precinct_{office_name}.json")
print(f"\nOpen the dashboard and select 'US Senate' from the dropdown to test.")
#These printed statements verify the creation of the JSON files