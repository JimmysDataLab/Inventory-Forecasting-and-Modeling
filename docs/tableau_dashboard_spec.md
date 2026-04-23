## Dashboard Spec: Inventory Sales Command Center

Use this spec to build a Tableau Public dashboard from a single extract:
`/Users/akhil/Projects/Inventory-Forecasting-and-Modeling/data/tableau/tableau_unified.csv`.

All calculated fields are created in Python. In Tableau, only use standard
aggregations (SUM, MAX, MIN, AVG) and filters.

### 1) Data Source

Connect to:
- `tableau_unified.csv`

### 2) Aggregation Rules (Important)

Use these rules to avoid double counting:
- Row-level metrics (safe for SUM):
  - `total_sales`, `total_onpromotion`, `transactions_allocated`
- Store-day metrics (safe for SUM at store/day grain):
  - `store_day_sales`, `store_day_transactions`
- Date-level metrics (repeat per row, use MIN or MAX):
  - `date_total_sales`, `date_total_transactions`, `date_sales_7d_avg`,
    `date_sales_28d_avg`, `date_sales_7d_std`, `date_sales_28d_std`,
    `date_sales_7d_upper`, `date_sales_7d_lower`, `date_sales_28d_upper`,
    `date_sales_28d_lower`, `date_promo_rate`, `date_sales_per_transaction`
- Safe-to-SUM date metrics (already divided by date row count):
  - `date_total_sales_safe_sum`, `date_total_transactions_safe_sum`,
    `date_total_onpromotion_safe_sum`
- Overall metrics (constants, use MAX):
  - `overall_total_sales`, `overall_total_transactions`,
    `overall_avg_daily_sales`, `overall_sales_per_transaction`

If totals look inflated (e.g., tens of billions), you're likely summing a
date-level field such as `date_total_sales`. Use MIN/MAX for date-level fields.

### 3) Field Types and Formatting

- `date`, `month` -> Date
- `store_nbr`, `family_rank`, `week`, `day_of_week_num`, `day_of_month`,
  `month_num`, `iso_year` -> Whole Number
- `total_sales`, `store_day_sales`, `date_total_sales` -> Currency (0-2 decimals)
- `transactions_allocated`, `date_total_transactions` -> Number (0 decimals)
- `dcoilwtico` -> Number (1-2 decimals)
- `date_promo_rate`, `overall_promo_rate` -> Percent (1-2 decimals)

### 4) Worksheet Build Steps

Use naming convention: `01 - KPI Total Sales`, `02 - KPI Avg Daily Sales`, etc.

#### 4.1 KPI Tiles (4 sheets)
Data source: `tableau_unified.csv`

Sheet: `01 - KPI Total Sales`
- Marks: Text
- Text: `MAX([overall_total_sales])`
- Format: Currency, 0 decimals
- Title: `Total Sales`
- Remove all gridlines and axes.

Repeat for:
- `02 - KPI Avg Daily Sales` -> `MAX([overall_avg_daily_sales])`
- `03 - KPI Total Transactions` -> `MAX([overall_total_transactions])`
- `04 - KPI Sales per Transaction` -> `MAX([overall_sales_per_transaction])`

#### 4.2 Sales Trend With Rolling Averages (Complex)
Sheet: `05 - Sales Trend + Rolling Avg`
- Columns: `date` (Exact Date, continuous)
- Rows: `MIN([date_total_sales])`
- Marks: Line
- Add `MIN([date_sales_7d_avg])` and `MIN([date_sales_28d_avg])` to Rows.
- Right click each -> Dual Axis, then Synchronize Axis.
- Color: Sales (dark blue), 7D (teal), 28D (amber).
- Tooltip: date, date_total_sales, date_sales_7d_avg, date_sales_28d_avg.

#### 4.3 Sales Volatility Bands (Advanced)
Sheet: `06 - Sales Volatility Bands`
- Columns: `date` (Exact Date, continuous)
- Rows: `MIN([date_total_sales])`
- Marks: Line
- Add `MIN([date_sales_7d_upper])` and `MIN([date_sales_7d_lower])` to Rows.
- Dual Axis each and synchronize axes.
- Set upper/lower to light gray, and move them behind the main line.
- Tooltip: date, date_total_sales, date_sales_7d_avg, date_sales_7d_std.

#### 4.4 Calendar Heatmap (Advanced)
Sheet: `07 - Calendar Heatmap`
- Filters: `iso_year` (single select), `month_num` (single select)
- Columns: `week` (Discrete)
- Rows: `day_of_week` (Discrete, order Mon → Sun)
- Marks: Square
- Color: `MIN([date_total_sales])`
- Label: `MIN([day_of_month])`
- Tooltip: date, date_total_sales, date_sales_7d_avg, is_holiday.
- Hide headers for `week` if you want a cleaner calendar look.

#### 4.5 Sales vs Oil (Dual Axis)
Sheet: `08 - Sales vs Oil`
- Columns: `date` (Exact Date, continuous)
- Rows: `MIN([date_total_sales])`
- Add `MIN([dcoilwtico])` to Rows.
- Dual Axis, synchronize axes.
- Color: Sales in dark blue, Oil in amber.

#### 4.6 Promo Impact Scatter (Complex)
Sheet: `09 - Promo Impact`
- Columns: `total_onpromotion`
- Rows: `total_sales`
- Marks: Circle
- Detail: `family`
- Color: `state`
- Size: `transactions_allocated`
- Add Analytics -> Trend Line (Linear) to show promo vs sales lift.
- Tooltip: family, state, total_sales, total_onpromotion, transactions_allocated.

#### 4.7 State x Family Heatmap (Complex)
Sheet: `10 - State Family Heatmap`
- Filters: `family_rank` (set to <= 10)
- Rows: `state`
- Columns: `family`
- Marks: Square
- Color: `SUM([total_sales])`
- Add label: `SUM([total_sales])` (optional, small font)

#### 4.8 Top Stores
Sheet: `11 - Top Stores`
- Rows: `store_nbr`
- Columns: `SUM([total_sales])`
- Sort descending by total sales.
- Filter: `store_nbr` -> Top 10 by `SUM(total_sales)`

### 5) Dashboard Assembly

Create dashboard: `Inventory Sales Command Center`
Canvas: 1400 x 900, Tiled.

Row 1: KPI strip
- `01 - KPI Total Sales`, `02 - KPI Avg Daily Sales`,
  `03 - KPI Total Transactions`, `04 - KPI Sales per Transaction`

Row 2:
- Left (60%): `05 - Sales Trend + Rolling Avg`
- Right (40%): `06 - Sales Volatility Bands`

Row 3:
- Left (50%): `07 - Calendar Heatmap`
- Right (50%): `09 - Promo Impact`

Row 4:
- Left (50%): `08 - Sales vs Oil`
- Right (50%): `10 - State Family Heatmap`

Row 5:
- Left (50%): `11 - Top Stores`

### 6) Workbook Template Outline (Sheet List + Layout)

Sheets:
- `01 - KPI Total Sales`
- `02 - KPI Avg Daily Sales`
- `03 - KPI Total Transactions`
- `04 - KPI Sales per Transaction`
- `05 - Sales Trend + Rolling Avg`
- `06 - Sales Volatility Bands`
- `07 - Calendar Heatmap`
- `08 - Sales vs Oil`
- `09 - Promo Impact`
- `10 - State Family Heatmap`
- `11 - Top Stores`

Dashboard:
- `Inventory Sales Command Center` (uses the layout in section 5)

### 7) Filters and Interactions

Show filters on dashboard:
- Date range (`date`)
- State (`state`)
- Family (`family`)
- `is_top_family` (toggle)

Apply filters to all sheets unless noted.

### 8) Styling

- Palette: Sales #163A70, Rolling Avg #1E8F8D, Oil #D9822B
- Remove gridlines and zero lines.
- Titles in 14-16 pt bold.
- Subtitle: "Kaggle Store Sales | 2013-2017".

### 9) Publishing Checklist

- Verify totals using `overall_*` KPIs.
- Confirm rolling averages align with sales trend.
- Ensure heatmap and scatter remain legible at default size.
- Publish to Tableau Public and copy the URL into README.
