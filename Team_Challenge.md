Your challenge is to set up a dashboard that provides information about precinct level elections for different elected offices in several states between 2014-2020. 

You will get information about state election results for general elections in 2014-2020 in several states and information about the  location of large wind and solar projects during this same period.
Your job is to build a dataset that can summarize at the state, district and precinct level

a) votes and vote shares for candidates in each election
b) the incumbent party in the district (and precinct)

c) changes in votes and vote share for the incumbent party compared to the previous election (if there was one)

d) whether the candidate for election is the incumbent office holder

e) whether a renewable project was built in the precincts between elections (and how many and their cumulative size)

f) whether the district had prior renewable energy facilities (and how many and their cumulative size)

g) (possibly) several demographic features in the district (like average income, % of minority voters, etc

This project requires you to do several important data collection and managment tasks, drawing data from several sources (to be named), use spatial (shapefile) data, and provide a presentation laying out your results. 

Step 1 (due 1/29) Write the code to dowload all the IOWA election results files at precinct level for 2014-2020 general elections (even years), run it to get all the files in your team folder.

Step 2 retain the election contests of interest, and eliminate others

Step 3 merge and reshape data for each county to a standardized form :  precinct, county, year, office1, office1_d_votes_p, office1_d_candidate_p, office1_r_votes_p, office1_r_candidate_p, office 1_other_votes_p, office1_total_precinct_votes_p, office2, office2_d_votes_p, office2_d_candidate_p office2_r_votes_p, office2_r_candidate_p, office2_other_votes_p, office2_total_votes_p, office3 office1_d_votes_p, office3_d_candidate_p, office3_r_votes_p, office3_r_candidate_p, office3_other_votes_p, office3_total_votes_p, ... etc for each office of interest in county 

  Step 3 can be broken into steps to simplify and verify that certain changes are made. Code for those steps might be developed simultaneously. In most cases, it probably makes sense to take just 2 -3 county files for a paticular year, develop code to transform those, and then loop over all the county files. Some years, the data is already somewhat structured where candidates are the columns and year-county-precinct is the row. In the files are structured differently, but can be "reshaped."  For all years,  columns are subtypes of votes that are not needed and should be deleted. For many offices, there may be more than 3 "candidates", so some vote totals should go into "other"

  Here are challenges:  How do you delete the polling and absentee votes for each candidate without deleting total vote for them.
                        How do you find and delete some tabs/pages while retaining others based on the ToC in each file
                        How do you merge columns when different offices are in different tabs (or when offices are the rows and precincts are the columns)?
                        
