#!/usr/bin/env python3
"""
Merge Iowa county-level election data files into single files for each year.
Organizes data in the same format as statewide_2014_cleaned.csv.
"""

import pandas as pd
import openpyxl
import glob
import os
from pathlib import Path

def filter_races(df):
    """Filter dataframe to only include specified races."""
    # Define race patterns to keep
    race_patterns = [
        'President',  # President and Vice President
        'US Senator',  # US Senate (2016 format)
        'United States Senator',  # US Senate (2018/2020 format)
        'US Rep',  # US House (2016 format)
        'United States Representative',  # US House (2018/2020 format)
        'State Rep',  # State House (all years)
        'Governor',  # Governor (all years, includes "Governor/Lieutenant Governor")
    ]
    
    # Filter rows where RaceTitle contains any of the patterns
    mask = df['RaceTitle'].str.contains('|'.join(race_patterns), case=False, na=False)
    return df[mask].copy()

def process_2016_file(filepath):
    """Process a 2016 county file (single sheet format)."""
    county_name = Path(filepath).stem.split('_')[0]
    
    df = pd.read_excel(filepath)
    
    # Handle column name with or without space
    candidate_col = ' CandidateName' if ' CandidateName' in df.columns else 'CandidateName'
    
    # Extract race info and candidate info
    race_candidate_party = df[['RaceTitle', candidate_col]].copy()
    race_candidate_party.columns = ['RaceTitle', 'CandidateName']
    
    # Filter for only the races we need
    race_candidate_party = filter_races(race_candidate_party)
    
    if len(race_candidate_party) == 0:
        return None
    
    # Get the filtered row indices
    filtered_indices = race_candidate_party.index
    
    # Extract precinct data - all columns that don't end with "Total" or "Absentee" or "Polling"
    precinct_cols = [col for col in df.columns if not any(x in col for x in ['Total', 'Absentee', 'Polling', 'RaceTitle', 'CandidateName'])]
    
    # Get only the "Total" columns for each precinct
    total_cols = [col for col in df.columns if col.strip().endswith('Total') and not col.strip().endswith('Adair Total')]
    
    # Extract precinct vote data
    precinct_data = {}
    for col in total_cols:
        # Extract precinct name (e.g., " Adair-1NW Total" -> "Adair-1NW")
        precinct_name = col.strip().replace(' Total', '').strip()
        # Only get values for filtered rows
        precinct_data[precinct_name] = df.loc[filtered_indices, col].values
    
    # Combine with race/candidate info
    result_df = race_candidate_party.reset_index(drop=True)
    for precinct, votes in precinct_data.items():
        result_df[precinct] = votes
    
    return result_df

def process_2018_2020_file(filepath):
    """Process a 2018 or 2020 county file (multi-sheet format)."""
    county_name = Path(filepath).stem.split('_')[0]
    
    wb = openpyxl.load_workbook(filepath, data_only=True)
    
    # Skip 'Table of Contents' and 'Registered Voters' sheets
    data_sheets = [sheet for sheet in wb.sheetnames 
                   if sheet not in ['Table of Contents', 'Registered Voters']]
    
    all_races = []
    
    for sheet_name in data_sheets:
        df = pd.read_excel(filepath, sheet_name=sheet_name, header=None)
        
        # Extract race title from first row, first column
        race_title = df.iloc[0, 0]
        if pd.isna(race_title):
            continue
        
        # Candidate names are in row 1 (index 1)
        # Precinct names are in column 0, starting from row 3
        # Data starts at row 3
        
        # Find the header row structure
        # Row 2 has "Registered Voters", "Election Day", "Absentee", "Total Votes" pattern
        
        # Get precinct names (column 0, rows 3 onwards, excluding "Total:")
        precinct_start_row = 3
        precinct_names = []
        precinct_rows = []
        
        for idx, val in enumerate(df.iloc[precinct_start_row:, 0]):
            if val == "Total:" or pd.isna(val):
                break
            precinct_names.append(val)
            precinct_rows.append(precinct_start_row + idx)
        
        if len(precinct_names) == 0:
            continue
        
        # Parse candidate structure from rows 1 and 2
        candidates = []
        candidate_cols = []
        
        col_idx = 1  # Start after precinct name column
        while col_idx < len(df.columns):
            candidate_name = df.iloc[1, col_idx]
            if pd.isna(candidate_name):
                col_idx += 1
                continue
            
            # Find the "Total Votes" column for this candidate
            # It's typically the third column in the pattern: Election Day, Absentee, Total Votes
            total_col_idx = None
            for offset in range(5):  # Look ahead up to 5 columns
                if col_idx + offset < len(df.columns):
                    header = df.iloc[2, col_idx + offset]
                    if header == "Total Votes" or header == "Total":
                        total_col_idx = col_idx + offset
                        break
            
            if total_col_idx is not None:
                candidates.append(candidate_name)
                candidate_cols.append(total_col_idx)
                col_idx = total_col_idx + 1
            else:
                col_idx += 1
        
        # Extract votes for each candidate at each precinct
        for candidate, col_idx in zip(candidates, candidate_cols):
            for precinct_name, row_idx in zip(precinct_names, precinct_rows):
                votes = df.iloc[row_idx, col_idx]
                
                # Clean precinct name to match format: "CountyName-PrecinctName"
                clean_precinct = f"{county_name}-{precinct_name}"
                
                all_races.append({
                    'RaceTitle': race_title,
                    'CandidateName': candidate,
                    'PrecinctName': clean_precinct,
                    'Votes': votes if not pd.isna(votes) else 0
                })
    
    # Convert to DataFrame and pivot to match target format
    if len(all_races) == 0:
        return None
    
    races_df = pd.DataFrame(all_races)
    
    # Filter for only the races we need
    races_df = filter_races(races_df)
    
    if len(races_df) == 0:
        return None
    
    # Pivot: rows are race/candidate combinations, columns are precincts
    pivot_df = races_df.pivot_table(
        index=['RaceTitle', 'CandidateName'],
        columns='PrecinctName',
        values='Votes',
        aggfunc='first'
    ).reset_index()
    
    return pivot_df

def merge_county_files(year, input_pattern, output_file):
    """Merge all county files for a given year into a single file."""
    print(f"\n{'='*60}")
    print(f"Processing {year} files...")
    print(f"{'='*60}")
    
    county_files = sorted(glob.glob(input_pattern))
    
    if len(county_files) == 0:
        print(f"No files found matching pattern: {input_pattern}")
        return
    
    print(f"Found {len(county_files)} county files")
    
    all_data = []
    
    for filepath in county_files:
        county_name = Path(filepath).stem.split('_')[0]
        print(f"Processing {county_name}...", end=' ')
        
        try:
            if year == 2016:
                df = process_2016_file(filepath)
            else:  # 2018 or 2020
                df = process_2018_2020_file(filepath)
            
            if df is not None:
                all_data.append(df)
                print("✓")
            else:
                print("⚠ (no data)")
        except Exception as e:
            print(f"✗ Error: {e}")
    
    if len(all_data) == 0:
        print(f"No data extracted for {year}")
        return
    
    # Merge all county dataframes
    print("\nMerging data...")
    
    # Get all unique race/candidate combinations
    all_races_candidates = pd.concat([df[['RaceTitle', 'CandidateName']] for df in all_data]).drop_duplicates()
    
    # Start with race/candidate columns
    merged_df = all_races_candidates.copy()
    
    # Add all precinct columns from all counties
    for df in all_data:
        # Get precinct columns (all columns except RaceTitle and CandidateName)
        precinct_cols = [col for col in df.columns if col not in ['RaceTitle', 'CandidateName']]
        
        # Merge on RaceTitle and CandidateName
        merged_df = merged_df.merge(
            df[['RaceTitle', 'CandidateName'] + precinct_cols],
            on=['RaceTitle', 'CandidateName'],
            how='left'
        )
    
    # Add PoliticalPartyName column (empty for now - can be populated if available)
    merged_df.insert(2, 'PoliticalPartyName', '')
    
    # Sort by RaceTitle and CandidateName
    merged_df = merged_df.sort_values(['RaceTitle', 'CandidateName']).reset_index(drop=True)
    
    # Save to CSV
    merged_df.to_csv(output_file, index=False)
    print(f"\n✓ Saved to: {output_file}")
    print(f"  Shape: {merged_df.shape}")
    print(f"  Races: {merged_df['RaceTitle'].nunique()}")
    print(f"  Candidates: {len(merged_df)}")
    print(f"  Precincts: {len([col for col in merged_df.columns if col not in ['RaceTitle', 'CandidateName', 'PoliticalPartyName']])}")

def main():
    """Main processing function."""
    
    # Define file patterns and output files
    # Using the full path provided by user
    input_dir = r"C:\Users\18607\OneDrive - University of Connecticut\26 Spring\DSDA 4815\iowa-dashboard\iowa_election_results"
    output_dir = r"C:\Users\18607\OneDrive - University of Connecticut\26 Spring\DSDA 4815\iowa-dashboard\outputs"
    
    # Check if input directory exists
    if not os.path.exists(input_dir):
        print(f"\n{'='*70}")
        print("ERROR: Input directory not found!")
        print(f"{'='*70}")
        print(f"Looking for: {input_dir}")
        print("\nPlease verify the directory path and that all county files are there.")
        print(f"{'='*70}\n")
        return
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    years_config = [
        {
            'year': 2016,
            'pattern': f"{input_dir}/*_2016.xlsx",
            'output': f"{output_dir}/statewide_2016_cleaned.csv"
        },
        {
            'year': 2018,
            'pattern': f"{input_dir}/*_2018.xlsx",
            'output': f"{output_dir}/statewide_2018_cleaned.csv"
        },
        {
            'year': 2020,
            'pattern': f"{input_dir}/*_2020.xlsx",
            'output': f"{output_dir}/statewide_2020_cleaned.csv"
        }
    ]
    
    for config in years_config:
        merge_county_files(config['year'], config['pattern'], config['output'])
    
    print("\n" + "="*60)
    print("Processing complete!")
    print("="*60)

if __name__ == "__main__":
    main()
