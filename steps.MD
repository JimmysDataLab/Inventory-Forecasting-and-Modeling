## Quickstart (macOS/Linux)

1) Create and activate the environment:
`conda env create -f env.yaml`
`conda activate ts-analysis`

2) Install Kaggle CLI if needed:
`pip install kaggle`

3) Download data:
`python etl/download.py --dataset store-sales`
`python etl/download.py --dataset walmart`

4) Build Tableau extracts:
`python etl/tableau_pipeline.py --dataset store-sales`
`python etl/tableau_pipeline.py --dataset walmart`

Output locations:
- Raw CSVs: `data/csv/<dataset>/`
- Unified extracts: `data/tableau/`

---

## Windows (PowerShell)

1) Create and activate the environment:
`conda env create -f env.yaml`
`conda activate ts-analysis`

2) Install Kaggle CLI if needed:
`pip install kaggle`

3) Set Kaggle credentials (if not already configured):
`$env:KAGGLE_USERNAME="your_username"`
`$env:KAGGLE_KEY="your_key"`

4) Download data:
`python etl/download.py --dataset store-sales`
`python etl/download.py --dataset walmart`

5) Build Tableau extracts:
`python etl/tableau_pipeline.py --dataset store-sales`
`python etl/tableau_pipeline.py --dataset walmart`

Output locations:
- Raw CSVs: `data/csv/<dataset>/`
- Unified extracts: `data/tableau/`