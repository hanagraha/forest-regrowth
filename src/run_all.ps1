# run_all.ps1 - Run the main data processing workflow in order.
#
# Lives in src/, but runs every script from the project root so that
# relative paths like data/samples/... resolve correctly.
#
# Usage (from anywhere): .\src\run_all.ps1

$ErrorActionPreference = "Stop"

# Move to the project root (the parent of the folder this script is in)
Set-Location (Join-Path $PSScriptRoot "..")

# Python: use the active venv's python, unbuffered so prints show immediately
$Python = "python"

# Rscript: use PATH if available, else the default Windows install
$cmd = Get-Command Rscript -ErrorAction SilentlyContinue
if ($cmd) {
    $Rscript = $cmd.Source
} else {
    $Rscript = "C:\Program Files\R\R-4.5.2\bin\Rscript.exe"
}

function Run-Step {
    param(
        [string]$Label,
        [string]$Exe,
        [string[]]$ScriptArgs
    )
    Write-Host ""
    Write-Host "=== [$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Running $Label ==="
    & $Exe @ScriptArgs
    if ($LASTEXITCODE -ne 0) {
        Write-Host "!!! $Label failed with exit code $LASTEXITCODE" -ForegroundColor Red
        exit $LASTEXITCODE
    }
    Write-Host "=== Finished $Label ==="
}

Run-Step "a1_process_interpretations.py" $Python @("-u", "src/a1_process_interpretations.py")
Run-Step "a2_stehman_statistics.R"       $Rscript @("src/a2_stehman_statistics.R")
Run-Step "a3_spatial_agreement.py"       $Python @("-u", "src/a3_spatial_agreement.py")
Run-Step "a4_regrowth_extent.py"         $Python @("-u", "src/a4_regrowth_extent.py")
Run-Step "a5_regrowth_timing.py"         $Python @("-u", "src/a5_regrowth_timing.py")
Run-Step "a6_area_estimation.py"         $Python @("-u", "src/a6_area_estimation.py")

Write-Host ""
Write-Host "=== All steps completed successfully ===" -ForegroundColor Green