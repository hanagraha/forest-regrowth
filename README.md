# forest-regrowth
Code repository for processing FD30Ref data, conducting accuracy assessments of remote sensing based maps, and calculating sample-based area estimates of forest trajectories

## Dependencies

Project dependencies are listed in [`requirements.txt`](requirements.txt). A virtual nvironment can be created using any package manager; an example using `venv` is provided below.

### Example: venv

**Windows (PowerShell)**
```powershell
python -m venv .regrvenv
.regrvenv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**macOS / Linux**
```bash
python3 -m venv .regrvenv
source .regrvenv/bin/activate
pip install -r requirements.txt
```

## Running the workflow

Run the scripts in `src/` in this order:

1. `a1_process_interpretations.py`
2. `a2_stehman_statistics.R`
3. `a3_spatial_agreement.py`
4. `a4_regrowth_extent.py`
5. `a5_regrowth_timing.py`
6. `a6_area_estimation.py`

Run all six at once from the project root with either wrapper script.

### Git Bash

```bash
source .regrvenv/Scripts/activate
bash src/run_all.sh
```

### PowerShell

```powershell
.regrvenv\Scripts\Activate.ps1
.\src\run_all.ps1
```