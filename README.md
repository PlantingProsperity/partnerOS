# Pinneo OS Scripts

![Tests](https://github.com/<OWNER>/<REPO>/actions/workflows/tests.yml/badge.svg)

Small workflow scripts for lead triage, scouting, and underwriting.

## Setup

1. Create a virtual environment and install dependencies:
   - `bash scripts/bootstrap_venv.sh`

2. Activate the environment:
   - `source .venv/bin/activate`

## Running

- Manager (lead triage): `python scripts/manager_triage.py`
- Scout (GIS lookup): `python scripts/scout_scrape.py "123 Main St, Vancouver, WA"`
- Underwriter (analysis): `python scripts/underwriter_calc.py "123-main-st"`

## Testing

- Run tests: `bash scripts/run_tests.sh`

## Environment

- `PINNEO_QUIET=1` suppresses script log output (useful for tests/automation).
