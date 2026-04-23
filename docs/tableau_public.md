## Tableau Public Dashboard Pipeline

This repo includes a pipeline that turns Kaggle datasets into a single, curated CSV optimized for Tableau Public. All calculated fields are created in Python so Tableau only needs filters and standard aggregations.

### Run The Pipeline

1) Download the raw CSVs (Kaggle account required):
`python etl/download.py --dataset store-sales`
`python etl/download.py --dataset walmart`

2) Build the Tableau extract:
`python etl/tableau_pipeline.py`

By default, the pipeline reads from `DATA_DIR/csv/<dataset>` (or `./data/csv/<dataset>` if `DATA_DIR` is not set) and writes to `DATA_DIR/tableau` (or `./data/tableau`).

Optional flags:
- `--input-dir`: override the CSV input folder
- `--output-dir`: override the output folder
- `--dataset store-sales|walmart`: select dataset
- `--top-families 10`: flag top families for filtering (store-sales only)
- `--min-date 2014-01-01`, `--max-date 2017-08-15`: date filtering

### Output Files

The pipeline produces one Tableau-friendly dataset plus metadata:
- `tableau_unified.csv`: store-sales unified extract
- `tableau_unified_walmart.csv`: Walmart unified extract
- `metadata.json`: extract lineage + top family list

### Suggested Tableau Public Dashboards

#### 1) Executive Overview
Recommended data source: `tableau_unified.csv` (store-sales) or `tableau_unified_walmart.csv`
- KPI tiles: total sales, avg sales, total promotions, total transactions
- Line chart: `date` vs `total_sales`
- Dual-axis line: `total_sales` and `dcoilwtico`
- Highlight table: `is_holiday` vs `avg_sales`

Filters:
- Date range
- Holiday indicator

#### 2) Store Performance
Recommended data source: `tableau_unified.csv` (store-sales) or `tableau_unified_walmart.csv`
- Map or bar: `state` (from store metadata) vs `total_sales`
- Scatter: `avg_daily_sales` vs `avg_daily_transactions` (size by `promo_rate`)
- Top N table: `store_nbr` by `total_sales`

Filters:
- State
- Store type
- Cluster

#### 3) Category & Promo Trends
Recommended data source: `tableau_unified.csv` (store-sales) or `tableau_unified_walmart.csv`
- Line chart: `date` vs `total_sales` with `family` color
- Bar: `family` vs `total_sales`
- Heatmap: `family` vs `promo_rate`

Filters:
- Family
- Date range

### Publishing To Tableau Public

1) Open Tableau Public and connect to the unified CSV for your dataset.
2) Build the dashboards with shared filters where relevant.
3) Publish to Tableau Public and add the URLs to your project README.

See `docs/tableau_dashboard_spec.md` for store-sales and
`docs/tableau_walmart_spec.md` for Walmart.

