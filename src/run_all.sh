#!/usr/bin/env bash
#
# run_all.sh - Run the main data processing workflow in order.
#
# Lives in src/, but runs every script from the project root so that
# relative paths like data/samples/... resolve correctly.
#
# Usage (from anywhere): bash src/run_all.sh
#
# Steps:
#   1. a1_process_interpretations.py
#   2. a2_stehman_statistics.R
#   3. a3_spatial_agreement.py
#   4. a4_regrowth_extent.py
#   5. a5_regrowth_timing.py
#   6. a6_area_estimation.py

set -euo pipefail

# Move to the project root (the parent of the folder this script is in)
cd "$(dirname "${BASH_SOURCE[0]}")/.."

# Use unbuffered Python so print output appears immediately
PYTHON="${PYTHON:-python}"
PYTHON_FLAGS="-u"

# Find Rscript: use $RSCRIPT if set, else PATH, else the default Windows install
if [ -n "${RSCRIPT:-}" ]; then
    :
elif command -v Rscript >/dev/null 2>&1; then
    RSCRIPT="Rscript"
else
    RSCRIPT="/c/Program Files/R/R-4.5.2/bin/Rscript.exe"
fi

run_step() {
    local label="$1"
    shift
    echo
    echo "=== [$(date '+%Y-%m-%d %H:%M:%S')] Running ${label} ==="
    if "$@"; then
        echo "=== Finished ${label} ==="
    else
        local status=$?
        echo "!!! ${label} failed with exit code ${status}" >&2
        exit "${status}"
    fi
}

run_step "a1_process_interpretations.py" "$PYTHON" $PYTHON_FLAGS src/a1_process_interpretations.py
run_step "a2_stehman_statistics.R"       "$RSCRIPT" src/a2_stehman_statistics.R
run_step "a3_spatial_agreement.py"       "$PYTHON" $PYTHON_FLAGS src/a3_spatial_agreement.py
run_step "a4_regrowth_extent.py"         "$PYTHON" $PYTHON_FLAGS src/a4_regrowth_extent.py
run_step "a5_regrowth_timing.py"         "$PYTHON" $PYTHON_FLAGS src/a5_regrowth_timing.py
run_step "a6_area_estimation.py"         "$PYTHON" $PYTHON_FLAGS src/a6_area_estimation.py

echo
echo "=== All steps completed successfully ==="