import json
import pandas as pd


CSV_PATH = "iowa_2014_precinct_database.csv"

OUT_RSHARE = "precinct_rshare_state_senate.json"
OUT_DISTRICT = "results_district_state_senate.json"
OUT_PRECINCT = "results_precinct_state_senate.json"


def main() -> None:
    # ------------------------------------------------------------
    # Step 1: Load data
    # ------------------------------------------------------------
    df = pd.read_csv(CSV_PATH)

    # ------------------------------------------------------------
    # Step 2: Filter to State Senate races
    # ------------------------------------------------------------
    # We select any race title that contains "State Senator"
    senate = df[df["RaceTitle"].str.contains("State Senator", na=False)].copy()

    # ------------------------------------------------------------
    # Step 3: Standardize party labels
    # ------------------------------------------------------------
    # Dashboard expects exactly: Republican, Democratic, Libertarian, Other
    party_map = {
        "Republican Party": "Republican",
        "Democratic Party": "Democratic",
        "Libertarian Party": "Libertarian",
    }
    senate["party"] = senate["PoliticalPartyName"].map(party_map).fillna("Other")

    # ------------------------------------------------------------
    # Step 4: Parse district number from RaceTitle (authoritative)
    # ------------------------------------------------------------
    # Typical format: "State Senator Dist. 1"
    # (We don't rely on senate_district column because it contains a few bad values)
    extracted = senate["RaceTitle"].str.extract(r"State Senator\s+Dist\.\s*(\d+)", expand=False)
    senate = senate[extracted.notna()].copy()
    senate["district"] = extracted.astype(int)

    # Keep only the 25 odd-numbered districts with races: 1,3,...,49
    odd_districts = set(range(1, 50, 2))
    senate = senate[senate["district"].isin(odd_districts)].copy()

    # ------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------
    print(f"State Senate rows: {len(senate)}")
    print(f"Unique precincts: {senate['shp_idx'].nunique()}")
    print(f"Unique districts: {senate['district'].nunique()}")
    print(f"District list: {sorted(senate['district'].unique())}")

    # ------------------------------------------------------------
    # Step 5: Build precinct_rshare_state_senate.json
    # ------------------------------------------------------------
    # One entry per precinct (shp_idx as string):
    #   r_share     = R votes / total votes * 100
    #   r_twoparty  = R votes / (R + D votes) * 100   <-- map color
    #   total_votes = sum of all votes
    precinct_rshare = {}

    for shp_idx, group in senate.groupby("shp_idx"):
        total = group["votes"].sum()
        r_votes = group.loc[group["party"] == "Republican", "votes"].sum()
        d_votes = group.loc[group["party"] == "Democratic", "votes"].sum()

        r_share = round(float(r_votes / total * 100), 1) if total > 0 else 0.0
        r_twoparty = (
            round(float(r_votes / (r_votes + d_votes) * 100), 1)
            if (r_votes + d_votes) > 0
            else 0.0
        )

        precinct_rshare[str(shp_idx)] = {
            "r_share": r_share,
            "r_twoparty": r_twoparty,
            "total_votes": int(total),
        }

    with open(OUT_RSHARE, "w") as f:
        json.dump(precinct_rshare, f, indent=2)

    print(f"Wrote {OUT_RSHARE}: {len(precinct_rshare)} precincts")

    # ------------------------------------------------------------
    # Step 6: Build results_district_state_senate.json
    # ------------------------------------------------------------
    # One entry per district (district number as string):
    # value = list of candidates with total votes + share within district
    results_district = {}

    for district, group in senate.groupby("district"):
        totals = (
            group.groupby(["CandidateName", "party"])["votes"]
            .sum()
            .reset_index()
            .sort_values("votes", ascending=False)
        )
        total_votes = totals["votes"].sum()

        candidate_list = []
        for _, row in totals.iterrows():
            candidate_list.append(
                {
                    "CandidateName": row["CandidateName"],
                    "party": row["party"],
                    "votes": int(row["votes"]),
                    "share": round(float(row["votes"] / total_votes * 100), 1)
                    if total_votes > 0
                    else 0.0,
                }
            )

        results_district[str(int(district))] = candidate_list

    with open(OUT_DISTRICT, "w") as f:
        json.dump(results_district, f, indent=2)

    print(f"Wrote {OUT_DISTRICT}: {len(results_district)} districts")

    # ------------------------------------------------------------
    # Step 7: Build results_precinct_state_senate.json
    # ------------------------------------------------------------
    # One entry per precinct (shp_idx as string):
    # value = list of candidates with votes + share within precinct
    results_precinct = {}

    for shp_idx, group in senate.groupby("shp_idx"):
        total = group["votes"].sum()

        candidates = []
        for _, row in group.sort_values("votes", ascending=False).iterrows():
            candidates.append(
                {
                    "CandidateName": row["CandidateName"],
                    "party": row["party"],
                    "votes": int(row["votes"]),
                    "share": round(float(row["votes"] / total * 100), 1) if total > 0 else 0.0,
                }
            )

        results_precinct[str(shp_idx)] = candidates

    with open(OUT_PRECINCT, "w") as f:
        json.dump(results_precinct, f, indent=2)

    print(f"Wrote {OUT_PRECINCT}: {len(results_precinct)} precincts")


if __name__ == "__main__":
    main()
