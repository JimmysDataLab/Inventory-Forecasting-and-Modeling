## Project Setup

1) Create and activate the environment:
`conda env create -f env.yaml`
`conda activate ts-analysis`

2) Configure your data directory (optional but recommended):
`export DATA_DIR="/path/to/data"`

3) Download the Kaggle dataset (requires Kaggle credentials):
`python etl/download.py`

4) Build Tableau-ready extracts:
`python etl/tableau_pipeline.py --dataset store-sales`
`python etl/tableau_pipeline.py --dataset walmart`

See `docs/tableau_public.md` for dashboard guidance and publishing steps.
