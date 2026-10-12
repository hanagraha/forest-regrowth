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