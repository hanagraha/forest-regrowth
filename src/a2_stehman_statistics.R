# -------------------------------------------------------------------------
# IMPORT PACKAGES AND READ DATA
# -------------------------------------------------------------------------
# Install packages if missing
options(repos = c(CRAN = "https://cloud.r-project.org"))
for (pkg in c("terra", "mapaccuracy")) {
  if (!requireNamespace(pkg, quietly = TRUE)) install.packages(pkg)
}

# Load packages
library(terra)
library(mapaccuracy)

# Read reference data
sampledata <- read.csv("data/samples/fd30ref_SA_labels.csv")

# Read strata data
strata_area <- read.csv("data/map/areaha_strata.csv")
strata_counts <- strata_area$area
names(strata_counts) <- strata_area$class

# Create output folder if it doesn't exist
dir.create("data/stehman", showWarnings = FALSE, recursive = TRUE)


# -------------------------------------------------------------------------
# DEFINE KEY FUNCTIONS
# -------------------------------------------------------------------------
# Define function to calculate stehman statistics
stehstats <- function(strata, ref, map, folder, filename){
  
  # Calculate statistics
  stats <- stehman2014(strata, ref, map, strata_counts)
  
  # Create dataframe
  stats_df <- data.frame(
    class = names(stats$area),
    ua = as.numeric(stats$UA),
    ce = 1 - as.numeric(stats$UA),
    pa = as.numeric(stats$PA),
    oe = 1 - as.numeric(stats$PA), 
    area = as.numeric(stats$area),
    se_uace = as.numeric(stats$SEua),
    se_paoe = as.numeric(stats$SEpa),
    se_a = as.numeric(stats$SEa),
    oa = as.numeric(stats$OA),
    se_oa = as.numeric(stats$SEoa)
  )
  
  # Clean confusion matrix (remove rows and columns with only NA)
  cm <- stats$matrix
  cm <- cm[rowSums(!is.na(cm)) > 0 & rowSums(cm, na.rm=TRUE) != 0, 
           colSums(!is.na(cm)) > 0 & colSums(cm, na.rm=TRUE) != 0]
  
  # Create output folder if needed
  outdir <- file.path("data/stehman", folder)
  dir.create(outdir, showWarnings = FALSE, recursive = TRUE)
  prefix <- file.path(outdir, filename)
  
  # Export statistics and confusion matrix
  write.csv(stats_df, paste0(prefix, "_stats.csv"), row.names = FALSE)
  write.csv(cm, paste0(prefix, "_cm.csv"))
  
  message("Stehman statistics saved to ", prefix)
}


# -------------------------------------------------------------------------
# AREA ESTIMATION (WITH ORIGINAL LABELS)
# -------------------------------------------------------------------------
# Original trajectories
stehstats(sampledata$strata, sampledata$traj, sampledata$traj, "trajectory", "ae_traj")

# Original Zhang trajectories
stehstats(sampledata$strata, sampledata$traj, sampledata$zhang, "trajectory", "ae_zhang")

# Original Potapov trajectories
stehstats(sampledata$strata, sampledata$traj, sampledata$potapov, "trajectory", "ae_potapov")

# Original Mapbiomas trajectories
stehstats(sampledata$strata, sampledata$traj, sampledata$mapbiomas, "trajectory", "ae_mapbiomas")


# -------------------------------------------------------------------------
# TRAJECTORY VALIDATION (WITH MATCHED LABELS)
# -------------------------------------------------------------------------
# Zhang trajectories
stehstats(sampledata$strata, sampledata$ref_zhangtraj,
          sampledata$zhang, "trajectory", "zhang")

# Potapov trajectories
stehstats(sampledata$strata, sampledata$ref_pottraj,
          sampledata$potapov, "trajectory", "potapov")

# Mapbiomas trajectories
stehstats(sampledata$strata, sampledata$ref_mbtraj,
          sampledata$mapbiomas, "trajectory", "mapbiomas")


# -------------------------------------------------------------------------
# AREA ESTIMATION (COMBINED LABELS)
# -------------------------------------------------------------------------
# Trajectory - Disturbance year
stehstats(sampledata$strata, sampledata$traj_distperiod,
          sampledata$traj_distperiod, "timing", "ae_trajdistperiods")

# Trajectory - Regrowth year
stehstats(sampledata$strata, sampledata$traj_regrperiod,
          sampledata$traj_regrperiod, "timing", "ae_trajregrperiods")

# Combined disturbance and regrowth labels
stehstats(sampledata$strata, sampledata$traj_distregr,
          sampledata$traj_distregr, "timing", "ae_trajdistregr")

# Combined disturbance and regrowth labels (10 years)
stehstats(sampledata$strata, sampledata$traj_distregr10,
          sampledata$traj_distregr10, "timing", "ae_trajdistregr10")


# -------------------------------------------------------------------------
# AREA ESTIMATION (REGROWTH ERRORS)
# -------------------------------------------------------------------------
# Potapov regrowth period
stehstats(sampledata$strata, sampledata$potapov_errs,
          sampledata$potapov_errs, "timing", "ae_regrerrs_potapov")

# Zhang regrowth period
stehstats(sampledata$strata, sampledata$zhang_errs,
          sampledata$zhang_errs, "timing", "ae_regrerrs_zhang")

# Mapbiomas regrowth period
stehstats(sampledata$strata, sampledata$mapbiomas_errs,
          sampledata$mapbiomas_errs, "timing", "ae_regrerrs_mapbiomas")



