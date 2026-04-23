## Dashboard Spec: Walmart Sales Command Center

Use this spec to build a Tableau Public dashboard from the Walmart dataset
using the single extract:
`/Users/akhil/Projects/Inventory-Forecasting-and-Modeling/data/tableau/tableau_unified_walmart.csv`.

All calculated fields are created in Python. In Tableau, only use standard
aggregations (SUM, MIN, MAX, AVG) and filters.

### 1) Data Source

Connect to:
- `tableau_unified_walmart.csv`

### 2) Aggregation Rules (Important)

Use these rules to avoid double counting:
- Row-level metrics (safe to SUM):
  - `total_sales`, `total_markdown`
- Store-date metrics (safe to SUM at store/date grain):
  - `store_date_sales`
- Date-level metrics (repeat per row, use MIN or MAX):
  - `date_total_sales`, `date_total_markdown`, `date_sales_7d_avg`,
    `date_sales_28d_avg`, `date_sales_7d_std`, `date_sales_28d_std`,
    `date_sales_7d_upper`, `date_sales_7d_lower`, `date_sales_28d_upper`,
    `date_sales_28d_lower`, `date_avg_sales_per_store`, `date_avg_sales_per_dept`
- Safe-to-SUM date metrics (already divided by date row count):
  - `date_total_sales_safe_sum`, `date_total_markdown_safe_sum`
- Overall metrics (constants, use MAX):
  - `overall_total_sales`, `overall_avg_weekly_sales`,
    `overall_sales_per_store`, `overall_sales_per_dept`, `overall_markdown_rate`

### 3) Field Types and Formatting

- `date`, `month`, `week_start` -> Date
- `store_nbr`, `dept`, `week`, `day_of_week_num`, `day_of_month`,
  `month_num`, `iso_year` -> Whole Number
- `total_sales`, `store_date_sales`, `date_total_sales` -> Currency (0-2 decimals)
- `total_markdown`, `date_total_markdown` -> Currency (0-2 decimals)
- `fuel_price`, `temperature`, `cpi`, `unemployment` -> Number (1-2 decimals)
- `date_markdown_rate`, `overall_markdown_rate` -> Percent (1-2 decimals)

### 4) Worksheet Build Steps

#### 4.1 KPI Tiles
Data source: `tableau_unified_walmart.csv`

Create:
- `01 - KPI Total Sales` -> `MAX([overall_total_sales])`
- `02 - KPI Avg Weekly Sales` -> `MAX([overall_avg_weekly_sales])`
- `03 - KPI Markdown Total` -> `MAX([overall_total_markdown])`
- `04 - KPI Markdown Rate` -> `MAX([overall_markdown_rate])`

#### 4.2 Sales Trend + Rolling Avg (Advanced)
Sheet: `05 - Sales Trend + Rolling Avg`
- Columns: `date` (Exact Date, continuous)
- Rows: `MIN([date_total_sales])`
- Add `MIN([date_sales_7d_avg])` and `MIN([date_sales_28d_avg])` to Rows.
- Dual Axis each, synchronize axes.

#### 4.3 Sales Volatility Bands (Advanced)
Sheet: `06 - Sales Volatility Bands`
- Columns: `date` (Exact Date, continuous)
- Rows: `MIN([date_total_sales])`
- Add `MIN([date_sales_7d_upper])` and `MIN([date_sales_7d_lower])` to Rows.
- Dual Axis each, synchronize axes.
- Use light gray for upper/lower band lines.

#### 4.4 Calendar Heatmap (Advanced)
Sheet: `07 - Calendar Heatmap`
- Filters: `iso_year` (single select), `month_num` (single select)
- Columns: `week` (Discrete)
- Rows: `day_of_week` (Discrete, order Mon → Sun)
- Marks: Square
- Color: `MIN([date_total_sales])`
- Label: `MIN([day_of_month])`
- Tooltip: date, date_total_sales, date_sales_7d_avg, is_holiday.

#### 4.5 Markdown Impact Scatter (Advanced)
Sheet: `08 - Markdown Impact`
- Columns: `total_markdown`
- Rows: `total_sales`
- Marks: Circle
- Color: `store_type`
- Detail: `dept`
- Size: `store_date_sales`
- Add Analytics -> Trend Line (Linear).

#### 4.6 Store Ranking
Sheet: `09 - Top Stores`
- Rows: `store_nbr`
- Columns: `SUM([total_sales])`
- Sort descending.
- Filter: Top 10 by SUM(total_sales).

### 5) Dashboard Assembly

Create dashboard: `Walmart Sales Command Center`
Canvas: 1400 x 900, Tiled.

Row 1: KPI strip
- `01 - KPI Total Sales`, `02 - KPI Avg Weekly Sales`,
  `03 - KPI Markdown Total`, `04 - KPI Markdown Rate`

Row 2:
- Left (60%): `05 - Sales Trend + Rolling Avg`
- Right (40%): `06 - Sales Volatility Bands`

Row 3:
- Left (50%): `07 - Calendar Heatmap`
- Right (50%): `08 - Markdown Impact`

Row 4:
- Full width: `09 - Top Stores`

### 6) Filters

Show filters on dashboard:
- Date range (`date`)
- Store Type (`store_type`)
- Dept (`dept`)
- Holiday Flag (`is_holiday`)

### 7) Styling

- Palette: Sales #163A70, Rolling Avg #1E8F8D, Markdown #D9822B
- Remove gridlines and zero lines.
- Titles in 14-16 pt bold.
- Subtitle: "Walmart Weekly Sales | Kaggle".

