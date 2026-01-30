# ============================================================
# Stage 1: Downloading Iowa Election Data
# R version using RSelenium
# ============================================================
#
# This script downloads precinct-level election results from
# Iowa's Secretary of State website for 2016, 2018, and 2020.
#
# WHY RSelenium?
# The website blocks simple download requests (you get "403 Forbidden").
# RSelenium controls a real browser, so the website can't tell
# it's not a human clicking around.
#
# ============================================================

# --- Install packages (run once) ---
# Uncomment these lines if you haven't installed the packages:
#
# install.packages("RSelenium")
# install.packages("here")       # for file paths


# --- Load libraries ---
library(RSelenium)


# ============================================================
# CONFIGURATION
# ============================================================

# Iowa's 99 counties
iowa_counties <- c(
  "Adair", "Adams", "Allamakee", "Appanoose", "Audubon",
 "Benton", "Black Hawk", "Boone", "Bremer", "Buchanan",
  "Buena Vista", "Butler", "Calhoun", "Carroll", "Cass",
  "Cedar", "Cerro Gordo", "Cherokee", "Chickasaw", "Clarke",
  "Clay", "Clayton", "Clinton", "Crawford", "Dallas",
  "Davis", "Decatur", "Delaware", "Des Moines", "Dickinson",
  "Dubuque", "Emmet", "Fayette", "Floyd", "Franklin",
  "Fremont", "Greene", "Grundy", "Guthrie", "Hamilton",
  "Hancock", "Hardin", "Harrison", "Henry", "Howard",
  "Humboldt", "Ida", "Iowa", "Jackson", "Jasper",
  "Jefferson", "Johnson", "Jones", "Keokuk", "Kossuth",
  "Lee", "Linn", "Louisa", "Lucas", "Lyon",
  "Madison", "Mahaska", "Marion", "Marshall", "Mills",
  "Mitchell", "Monona", "Monroe", "Montgomery", "Muscatine",
  "O'Brien", "Osceola", "Page", "Palo Alto", "Plymouth",
  "Pocahontas", "Polk", "Pottawattamie", "Poweshiek", "Ringgold",
  "Sac", "Scott", "Shelby", "Sioux", "Story",
  "Tama", "Taylor", "Union", "Van Buren", "Wapello",
  "Warren", "Washington", "Wayne", "Webster", "Winnebago",
  "Winneshiek", "Woodbury", "Worth", "Wright"
)

# Output folder - will be created if it doesn't exist
output_dir <- "./iowa_election_results"
if (!dir.exists(output_dir)) {
  dir.create(output_dir)
}

cat("Files will be saved to:", normalizePath(output_dir), "\n\n")


# ============================================================
# START THE BROWSER
# ============================================================
#
# RSelenium needs a "Selenium server" running. The rsDriver()
# function starts both the server and the browser.
#
# Common issues:
# - If Chrome doesn't work, try browser = "firefox"
# - You may need to install Java (Selenium server needs it)
# - First run may download driver files (takes a minute)

cat("Starting browser (this may take a moment)...\n")

# Start Chrome (change to "firefox" if Chrome doesn't work)
rD <- rsDriver(
  browser = "chrome",
  chromever = "latest",
  verbose = FALSE
)

# Get the browser client (this is what we use to control the browser)
driver <- rD$client

cat("Browser started!\n\n")


# ============================================================
# HELPER FUNCTION: Wait for download to complete
# ============================================================
#
# When you click a download link, it takes time to finish.
# This function checks the download folder repeatedly until
# the file appears (or we give up after a timeout).

wait_for_download <- function(folder, timeout = 60) {
  start_time <- Sys.time()

  while (difftime(Sys.time(), start_time, units = "secs") < timeout) {
    files <- list.files(folder, full.names = TRUE)

    # Check for partial downloads (Chrome uses .crdownload)
    partial <- files[grepl("\\.(crdownload|tmp|part)$", files)]
    excel <- files[grepl("\\.(xls|xlsx)$", files, ignore.case = TRUE)]

    if (length(excel) > 0 && length(partial) == 0) {
      Sys.sleep(0.5)  # Brief pause to ensure file is complete
      return(excel[1])
    }

    Sys.sleep(0.5)
  }

  return(NULL)  # Timed out
}


# ============================================================
# HELPER FUNCTION: Clear folder
# ============================================================

clear_folder <- function(folder) {
  files <- list.files(folder, full.names = TRUE)
  if (length(files) > 0) {
    file.remove(files)
  }
}


# ============================================================
# HELPER FUNCTION: Convert county name for URL
# ============================================================
# "O'Brien" -> "obrien"
# "Black Hawk" -> "blackhawk"

make_url_name <- function(county) {
  name <- tolower(county)
  name <- gsub(" ", "", name)   # Remove spaces
  name <- gsub("'", "", name)   # Remove apostrophes
  return(name)
}


# ============================================================
# CREATE TEMP FOLDER FOR DOWNLOADS
# ============================================================

temp_dir <- file.path(output_dir, "_temp")
if (!dir.exists(temp_dir)) {
  dir.create(temp_dir)
}


# ============================================================
# DOWNLOAD 2016 FILES (.xlsx)
# ============================================================

cat("==================================================\n")
cat("Downloading 2016 files...\n")
cat("==================================================\n")

for (county in iowa_counties) {
  county_url <- make_url_name(county)
  url <- paste0("https://sos.iowa.gov/elections/pdf/precinctresults/2016general/",
                county_url, ".xlsx")

  cat("  ", county, "... ", sep = "")

  clear_folder(temp_dir)
  driver$navigate(url)

  downloaded <- wait_for_download(temp_dir)

  if (!is.null(downloaded)) {
    new_name <- paste0(county, "_2016.xlsx")
    file.rename(downloaded, file.path(output_dir, new_name))
    cat("done\n")
  } else {
    cat("FAILED\n")
  }

  Sys.sleep(0.5)  # Pause between downloads
}


# ============================================================
# DOWNLOAD 2018 FILES (.xls)
# ============================================================

cat("\n==================================================\n")
cat("Downloading 2018 files...\n")
cat("==================================================\n")

for (county in iowa_counties) {
  county_url <- make_url_name(county)
  url <- paste0("https://sos.iowa.gov/elections/pdf/precinctresults/2018general/",
                county_url, ".xls")

  cat("  ", county, "... ", sep = "")

  clear_folder(temp_dir)
  driver$navigate(url)

  downloaded <- wait_for_download(temp_dir)

  if (!is.null(downloaded)) {
    new_name <- paste0(county, "_2018.xls")
    file.rename(downloaded, file.path(output_dir, new_name))
    cat("done\n")
  } else {
    cat("FAILED\n")
  }

  Sys.sleep(0.5)
}


# ============================================================
# DOWNLOAD 2020 FILES (.xlsx)
# ============================================================

cat("\n==================================================\n")
cat("Downloading 2020 files...\n")
cat("==================================================\n")

for (county in iowa_counties) {
  county_url <- make_url_name(county)
  url <- paste0("https://sos.iowa.gov/elections/pdf/precinctresults/2020general/",
                county_url, ".xlsx")

  cat("  ", county, "... ", sep = "")

  clear_folder(temp_dir)
  driver$navigate(url)

  downloaded <- wait_for_download(temp_dir)

  if (!is.null(downloaded)) {
    new_name <- paste0(county, "_2020.xlsx")
    file.rename(downloaded, file.path(output_dir, new_name))
    cat("done\n")
  } else {
    cat("FAILED\n")
  }

  Sys.sleep(0.5)
}


# ============================================================
# CLEANUP
# ============================================================

cat("\nClosing browser...\n")
driver$close()
rD$server$stop()

# Remove temp folder
unlink(temp_dir, recursive = TRUE)

cat("\n==================================================\n")
cat("DONE!\n")
cat("Files saved to:", normalizePath(output_dir), "\n")
cat("==================================================\n")
