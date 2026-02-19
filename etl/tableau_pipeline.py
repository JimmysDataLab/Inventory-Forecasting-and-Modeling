import argparse
import json
import logging
import os
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
from dotenv import load_dotenv

LOGGER = logging.getLogger(__name__)


def _resolve_paths(input_dir: str | None, output_dir: str | None) -> tuple[Path, Path]:
    load_dotenv()
    data_dir = Path(os.getenv("DATA_DIR") or "data")
    input_path = Path(input_dir) if input_dir else data_dir / "csv"
    output_path = Path(output_dir) if output_dir else data_dir / "tableau"
    return input_path, output_path


def _read_csv(path: Path, **kwargs) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Missing required file: {path}")
    return pd.read_csv(path, **kwargs)


def _normalize_dates(df: pd.DataFrame, column: str = "date") -> pd.DataFrame:
    df[column] = pd.to_datetime(df[column], errors="coerce")
    return df


def _stringify_date(df: pd.DataFrame, column: str) -> pd.DataFrame:
    df[column] = pd.to_datetime(df[column], errors="coerce").dt.strftime("%Y-%m-%d")
    return df


def _load_raw(input_dir: Path) -> dict[str, pd.DataFrame]:
    train = _read_csv(input_dir / "train.csv", parse_dates=["date"])
    stores = _read_csv(input_dir / "stores.csv")
    transactions = _read_csv(input_dir / "transactions.csv", parse_dates=["date"])
    oil = _read_csv(input_dir / "oil.csv", parse_dates=["date"])
    holidays = _read_csv(input_dir / "holidays_events.csv", parse_dates=["date"])

    train["sales"] = pd.to_numeric(train["sales"], errors="coerce").fillna(0.0)
    train["onpromotion"] = pd.to_numeric(train["onpromotion"], errors="coerce").fillna(0).astype("int64")
    train["store_nbr"] = pd.to_numeric(train["store_nbr"], errors="coerce").astype("int64")
    train["family"] = train["family"].astype("string")

    transactions["transactions"] = (
        pd.to_numeric(transactions["transactions"], errors="coerce").fillna(0).astype("int64")
    )
    transactions["store_nbr"] = pd.to_numeric(
        transactions["store_nbr"], errors="coerce"
    ).astype("int64")

    oil["dcoilwtico"] = pd.to_numeric(oil["dcoilwtico"], errors="coerce")
    oil = oil.sort_values("date")
    oil["dcoilwtico"] = oil["dcoilwtico"].ffill().bfill()

    holidays = _normalize_dates(holidays)
    holidays["transferred"] = holidays["transferred"].astype("string").str.lower()
    holidays = holidays[holidays["transferred"] != "true"]

    return {
        "train": train,
        "stores": stores,
        "transactions": transactions,
        "oil": oil,
        "holidays": holidays,
    }


def _load_walmart_raw(input_dir: Path) -> dict[str, pd.DataFrame]:
    train = _read_csv(input_dir / "train.csv", parse_dates=["Date"])
    features = _read_csv(input_dir / "features.csv", parse_dates=["Date"])
    stores = _read_csv(input_dir / "stores.csv")

    train = train.rename(
        columns={
            "Store": "store_nbr",
            "Dept": "dept",
            "Date": "date",
            "Weekly_Sales": "total_sales",
            "IsHoliday": "is_holiday",
        }
    )
    features = features.rename(
        columns={
            "Store": "store_nbr",
            "Date": "date",
            "Temperature": "temperature",
            "Fuel_Price": "fuel_price",
            "Markdown1": "markdown1",
            "Markdown2": "markdown2",
            "Markdown3": "markdown3",
            "Markdown4": "markdown4",
            "Markdown5": "markdown5",
            "CPI": "cpi",
            "Unemployment": "unemployment",
            "IsHoliday": "feature_is_holiday",
        }
    )
    stores = stores.rename(
        columns={
            "Store": "store_nbr",
            "Type": "store_type",
            "Size": "store_size",
        }
    )

    train["total_sales"] = pd.to_numeric(train["total_sales"], errors="coerce").fillna(0.0)
    train["store_nbr"] = pd.to_numeric(train["store_nbr"], errors="coerce").astype("int64")
    train["dept"] = pd.to_numeric(train["dept"], errors="coerce").astype("int64")
    train["is_holiday"] = train["is_holiday"].fillna(False).astype("int64")

    for column in ["temperature", "fuel_price", "cpi", "unemployment"]:
        if column in features.columns:
            features[column] = pd.to_numeric(features[column], errors="coerce")

    markdown_cols = ["markdown1", "markdown2", "markdown3", "markdown4", "markdown5"]
    for column in markdown_cols:
        if column in features.columns:
            features[column] = pd.to_numeric(features[column], errors="coerce").fillna(0.0)

    features["feature_is_holiday"] = features["feature_is_holiday"].fillna(False).astype("int64")

    return {
        "train": train,
        "features": features,
        "stores": stores,
    }


def _uniq_join(series: pd.Series) -> str | None:
    values = sorted({str(val).strip() for val in series.dropna().tolist() if str(val).strip()})
    return ", ".join(values) if values else None


def _build_holiday_daily(holidays: pd.DataFrame) -> pd.DataFrame:
    holiday_daily = holidays.groupby("date", as_index=False).agg(
        is_holiday=("description", "size"),
        holiday_types=("type", _uniq_join),
        holiday_locales=("locale", _uniq_join),
        holiday_names=("description", _uniq_join),
    )
    holiday_daily["is_holiday"] = np.where(holiday_daily["is_holiday"] > 0, 1, 0)
    return holiday_daily


def _add_family_rank(train: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    family_sales = train.groupby("family", as_index=False)["sales"].sum().sort_values(
        "sales", ascending=False
    )
    family_sales["family_rank"] = np.arange(1, len(family_sales) + 1)
    ranked = train.merge(family_sales[["family", "family_rank"]], on="family", how="left")
    return ranked, family_sales


def _build_unified_extract(
    train: pd.DataFrame,
    stores: pd.DataFrame,
    transactions: pd.DataFrame,
    oil: pd.DataFrame,
    holidays: pd.DataFrame,
    top_families: int,
) -> tuple[pd.DataFrame, list[str]]:
    train = train.merge(stores, on="store_nbr", how="left")

    train, family_sales = _add_family_rank(train)
    train["family_rank"] = train["family_rank"].fillna(0).astype("int64")
    train["is_top_family"] = np.where(train["family_rank"] <= top_families, 1, 0)

    date_row_count = (
        train.groupby("date")
        .size()
        .rename("date_row_count")
        .reset_index()
    )

    store_day_sales = train.groupby(["date", "store_nbr"], as_index=False).agg(
        store_day_sales=("sales", "sum"),
        store_day_family_count=("family", "nunique"),
    )
    store_day_transactions = transactions.groupby(["date", "store_nbr"], as_index=False).agg(
        store_day_transactions=("transactions", "sum"),
    )

    train = train.merge(store_day_sales, on=["date", "store_nbr"], how="left")
    train = train.merge(store_day_transactions, on=["date", "store_nbr"], how="left")

    train["store_day_sales"] = train["store_day_sales"].fillna(0.0)
    train["store_day_family_count"] = (
        train["store_day_family_count"].fillna(0).astype("int64")
    )
    train["store_day_transactions"] = (
        train["store_day_transactions"].fillna(0).astype("int64")
    )

    train["store_day_sales_share"] = np.where(
        train["store_day_sales"] > 0,
        train["sales"] / train["store_day_sales"],
        np.where(
            train["store_day_family_count"] > 0,
            1 / train["store_day_family_count"],
            0.0,
        ),
    )
    train["transactions_allocated"] = (
        train["store_day_transactions"] * train["store_day_sales_share"]
    )

    date_metrics = train.groupby("date", as_index=False).agg(
        date_total_sales=("sales", "sum"),
        date_total_onpromotion=("onpromotion", "sum"),
        date_store_count=("store_nbr", "nunique"),
        date_family_count=("family", "nunique"),
    )
    date_transactions = transactions.groupby("date", as_index=False).agg(
        date_total_transactions=("transactions", "sum"),
    )
    date_metrics = date_metrics.merge(date_transactions, on="date", how="left")
    date_metrics["date_total_transactions"] = (
        date_metrics["date_total_transactions"].fillna(0).astype("int64")
    )
    date_metrics = date_metrics.merge(date_row_count, on="date", how="left")
    date_metrics["date_row_count"] = (
        date_metrics["date_row_count"].fillna(0).astype("int64")
    )
    date_metrics["date_sales_per_transaction"] = np.where(
        date_metrics["date_total_transactions"] > 0,
        date_metrics["date_total_sales"] / date_metrics["date_total_transactions"],
        0.0,
    )
    date_metrics["date_avg_sales_per_store"] = np.where(
        date_metrics["date_store_count"] > 0,
        date_metrics["date_total_sales"] / date_metrics["date_store_count"],
        0.0,
    )
    date_metrics["date_promo_rate"] = np.where(
        date_metrics["date_store_count"] > 0,
        date_metrics["date_total_onpromotion"] / date_metrics["date_store_count"],
        0.0,
    )
    date_metrics["date_total_sales_safe_sum"] = np.where(
        date_metrics["date_row_count"] > 0,
        date_metrics["date_total_sales"] / date_metrics["date_row_count"],
        0.0,
    )
    date_metrics["date_total_transactions_safe_sum"] = np.where(
        date_metrics["date_row_count"] > 0,
        date_metrics["date_total_transactions"] / date_metrics["date_row_count"],
        0.0,
    )
    date_metrics["date_total_onpromotion_safe_sum"] = np.where(
        date_metrics["date_row_count"] > 0,
        date_metrics["date_total_onpromotion"] / date_metrics["date_row_count"],
        0.0,
    )

    date_metrics = date_metrics.sort_values("date")
    date_metrics["date_sales_7d_avg"] = (
        date_metrics["date_total_sales"].rolling(7, min_periods=1).mean()
    )
    date_metrics["date_sales_28d_avg"] = (
        date_metrics["date_total_sales"].rolling(28, min_periods=1).mean()
    )
    date_metrics["date_transactions_7d_avg"] = (
        date_metrics["date_total_transactions"].rolling(7, min_periods=1).mean()
    )
    date_metrics["date_sales_7d_std"] = (
        date_metrics["date_total_sales"].rolling(7, min_periods=1).std().fillna(0.0)
    )
    date_metrics["date_sales_28d_std"] = (
        date_metrics["date_total_sales"].rolling(28, min_periods=1).std().fillna(0.0)
    )
    date_metrics["date_sales_7d_upper"] = (
        date_metrics["date_sales_7d_avg"] + (2 * date_metrics["date_sales_7d_std"])
    )
    date_metrics["date_sales_7d_lower"] = (
        date_metrics["date_sales_7d_avg"] - (2 * date_metrics["date_sales_7d_std"])
    )
    date_metrics["date_sales_28d_upper"] = (
        date_metrics["date_sales_28d_avg"] + (2 * date_metrics["date_sales_28d_std"])
    )
    date_metrics["date_sales_28d_lower"] = (
        date_metrics["date_sales_28d_avg"] - (2 * date_metrics["date_sales_28d_std"])
    )

    date_metrics["year"] = date_metrics["date"].dt.year
    date_metrics["month"] = date_metrics["date"].dt.to_period("M").dt.to_timestamp()
    date_metrics["month_num"] = date_metrics["date"].dt.month.astype("int64")
    date_metrics["month_name"] = date_metrics["date"].dt.month_name()
    iso_calendar = date_metrics["date"].dt.isocalendar()
    date_metrics["iso_year"] = iso_calendar.year.astype("int64")
    date_metrics["week"] = iso_calendar.week.astype("int64")
    date_metrics["day_of_week"] = date_metrics["date"].dt.day_name()
    date_metrics["day_of_week_num"] = (date_metrics["date"].dt.dayofweek + 1).astype("int64")
    date_metrics["day_of_month"] = date_metrics["date"].dt.day.astype("int64")
    date_metrics["week_start"] = date_metrics["date"] - pd.to_timedelta(
        date_metrics["date"].dt.dayofweek, unit="D"
    )

    holiday_daily = _build_holiday_daily(holidays)
    date_metrics = date_metrics.merge(holiday_daily, on="date", how="left")
    date_metrics["is_holiday"] = date_metrics["is_holiday"].fillna(0).astype("int64")

    date_metrics = date_metrics.merge(oil[["date", "dcoilwtico"]], on="date", how="left")

    overall_total_sales = float(date_metrics["date_total_sales"].sum())
    overall_total_transactions = float(date_metrics["date_total_transactions"].sum())
    overall_avg_daily_sales = (
        float(date_metrics["date_total_sales"].mean()) if len(date_metrics) else 0.0
    )
    overall_avg_daily_transactions = (
        float(date_metrics["date_total_transactions"].mean()) if len(date_metrics) else 0.0
    )
    overall_sales_per_transaction = (
        overall_total_sales / overall_total_transactions
        if overall_total_transactions > 0
        else 0.0
    )
    overall_promo_rate = (
        float(date_metrics["date_total_onpromotion"].sum())
        / float(date_metrics["date_store_count"].sum())
        if float(date_metrics["date_store_count"].sum()) > 0
        else 0.0
    )

    unified = train.merge(date_metrics, on="date", how="left")
    unified = unified.rename(
        columns={
            "sales": "total_sales",
            "onpromotion": "total_onpromotion",
        }
    )
    unified["transactions_allocated"] = unified["transactions_allocated"].fillna(0.0)
    unified["sales_per_transaction_allocated"] = np.where(
        unified["transactions_allocated"] > 0,
        unified["total_sales"] / unified["transactions_allocated"],
        0.0,
    )

    unified["overall_total_sales"] = overall_total_sales
    unified["overall_total_transactions"] = overall_total_transactions
    unified["overall_avg_daily_sales"] = overall_avg_daily_sales
    unified["overall_avg_daily_transactions"] = overall_avg_daily_transactions
    unified["overall_sales_per_transaction"] = overall_sales_per_transaction
    unified["overall_promo_rate"] = overall_promo_rate

    unified = _stringify_date(unified, "date")
    unified = _stringify_date(unified, "month")
    unified = _stringify_date(unified, "week_start")

    for column in ["holiday_types", "holiday_locales", "holiday_names", "family", "state"]:
        if column in unified.columns:
            unified[column] = unified[column].astype("string")

    columns = [
        "date",
        "month",
        "year",
        "month_num",
        "month_name",
        "iso_year",
        "week",
        "week_start",
        "day_of_week",
        "day_of_week_num",
        "day_of_month",
        "store_nbr",
        "state",
        "city",
        "type",
        "cluster",
        "family",
        "family_rank",
        "is_top_family",
        "total_sales",
        "total_onpromotion",
        "transactions_allocated",
        "store_day_sales",
        "store_day_transactions",
        "store_day_family_count",
        "store_day_sales_share",
        "sales_per_transaction_allocated",
        "date_total_sales",
        "date_total_transactions",
        "date_total_onpromotion",
        "date_row_count",
        "date_total_sales_safe_sum",
        "date_total_transactions_safe_sum",
        "date_total_onpromotion_safe_sum",
        "date_store_count",
        "date_family_count",
        "date_sales_per_transaction",
        "date_avg_sales_per_store",
        "date_promo_rate",
        "date_sales_7d_avg",
        "date_sales_28d_avg",
        "date_transactions_7d_avg",
        "date_sales_7d_std",
        "date_sales_28d_std",
        "date_sales_7d_upper",
        "date_sales_7d_lower",
        "date_sales_28d_upper",
        "date_sales_28d_lower",
        "dcoilwtico",
        "is_holiday",
        "holiday_types",
        "holiday_locales",
        "holiday_names",
        "overall_total_sales",
        "overall_total_transactions",
        "overall_avg_daily_sales",
        "overall_avg_daily_transactions",
        "overall_sales_per_transaction",
        "overall_promo_rate",
    ]

    unified = unified[columns]
    top_family_list = family_sales.head(top_families)["family"].tolist()
    return unified, top_family_list


def _build_walmart_unified(
    train: pd.DataFrame,
    features: pd.DataFrame,
    stores: pd.DataFrame,
) -> pd.DataFrame:
    markdown_cols = ["markdown1", "markdown2", "markdown3", "markdown4", "markdown5"]

    train = train.merge(stores, on="store_nbr", how="left")
    train = train.merge(features, on=["store_nbr", "date"], how="left")

    for column in markdown_cols:
        if column not in train.columns:
            train[column] = 0.0

    train["total_markdown"] = train[markdown_cols].fillna(0.0).sum(axis=1)

    date_row_count = (
        train.groupby("date")
        .size()
        .rename("date_row_count")
        .reset_index()
    )

    store_date_sales = train.groupby(["date", "store_nbr"], as_index=False).agg(
        store_date_sales=("total_sales", "sum"),
        store_date_dept_count=("dept", "nunique"),
    )

    train = train.merge(store_date_sales, on=["date", "store_nbr"], how="left")
    train["store_date_sales"] = train["store_date_sales"].fillna(0.0)
    train["store_date_dept_count"] = (
        train["store_date_dept_count"].fillna(0).astype("int64")
    )
    train["store_date_sales_share"] = np.where(
        train["store_date_sales"] > 0,
        train["total_sales"] / train["store_date_sales"],
        np.where(train["store_date_dept_count"] > 0, 1 / train["store_date_dept_count"], 0.0),
    )

    date_metrics = train.groupby("date", as_index=False).agg(
        date_total_sales=("total_sales", "sum"),
        date_total_markdown=("total_markdown", "sum"),
        date_store_count=("store_nbr", "nunique"),
        date_dept_count=("dept", "nunique"),
    )
    date_metrics = date_metrics.merge(date_row_count, on="date", how="left")
    date_metrics["date_row_count"] = (
        date_metrics["date_row_count"].fillna(0).astype("int64")
    )
    date_metrics["date_avg_sales_per_store"] = np.where(
        date_metrics["date_store_count"] > 0,
        date_metrics["date_total_sales"] / date_metrics["date_store_count"],
        0.0,
    )
    date_metrics["date_avg_sales_per_dept"] = np.where(
        date_metrics["date_dept_count"] > 0,
        date_metrics["date_total_sales"] / date_metrics["date_dept_count"],
        0.0,
    )
    date_metrics["date_markdown_rate"] = np.where(
        date_metrics["date_total_sales"] > 0,
        date_metrics["date_total_markdown"] / date_metrics["date_total_sales"],
        0.0,
    )
    date_metrics["date_total_sales_safe_sum"] = np.where(
        date_metrics["date_row_count"] > 0,
        date_metrics["date_total_sales"] / date_metrics["date_row_count"],
        0.0,
    )
    date_metrics["date_total_markdown_safe_sum"] = np.where(
        date_metrics["date_row_count"] > 0,
        date_metrics["date_total_markdown"] / date_metrics["date_row_count"],
        0.0,
    )

    date_metrics = date_metrics.sort_values("date")
    date_metrics["date_sales_7d_avg"] = (
        date_metrics["date_total_sales"].rolling(7, min_periods=1).mean()
    )
    date_metrics["date_sales_28d_avg"] = (
        date_metrics["date_total_sales"].rolling(28, min_periods=1).mean()
    )
    date_metrics["date_sales_7d_std"] = (
        date_metrics["date_total_sales"].rolling(7, min_periods=1).std().fillna(0.0)
    )
    date_metrics["date_sales_28d_std"] = (
        date_metrics["date_total_sales"].rolling(28, min_periods=1).std().fillna(0.0)
    )
    date_metrics["date_sales_7d_upper"] = (
        date_metrics["date_sales_7d_avg"] + (2 * date_metrics["date_sales_7d_std"])
    )
    date_metrics["date_sales_7d_lower"] = (
        date_metrics["date_sales_7d_avg"] - (2 * date_metrics["date_sales_7d_std"])
    )
    date_metrics["date_sales_28d_upper"] = (
        date_metrics["date_sales_28d_avg"] + (2 * date_metrics["date_sales_28d_std"])
    )
    date_metrics["date_sales_28d_lower"] = (
        date_metrics["date_sales_28d_avg"] - (2 * date_metrics["date_sales_28d_std"])
    )

    date_metrics["year"] = date_metrics["date"].dt.year
    date_metrics["month"] = date_metrics["date"].dt.to_period("M").dt.to_timestamp()
    date_metrics["month_num"] = date_metrics["date"].dt.month.astype("int64")
    date_metrics["month_name"] = date_metrics["date"].dt.month_name()
    iso_calendar = date_metrics["date"].dt.isocalendar()
    date_metrics["iso_year"] = iso_calendar.year.astype("int64")
    date_metrics["week"] = iso_calendar.week.astype("int64")
    date_metrics["day_of_week"] = date_metrics["date"].dt.day_name()
    date_metrics["day_of_week_num"] = (date_metrics["date"].dt.dayofweek + 1).astype("int64")
    date_metrics["day_of_month"] = date_metrics["date"].dt.day.astype("int64")
    date_metrics["week_start"] = date_metrics["date"] - pd.to_timedelta(
        date_metrics["date"].dt.dayofweek, unit="D"
    )

    overall_total_sales = float(date_metrics["date_total_sales"].sum())
    overall_avg_weekly_sales = (
        float(date_metrics["date_total_sales"].mean()) if len(date_metrics) else 0.0
    )
    overall_sales_per_store = (
        overall_total_sales / float(date_metrics["date_store_count"].sum())
        if float(date_metrics["date_store_count"].sum()) > 0
        else 0.0
    )
    overall_sales_per_dept = (
        overall_total_sales / float(date_metrics["date_dept_count"].sum())
        if float(date_metrics["date_dept_count"].sum()) > 0
        else 0.0
    )
    overall_total_markdown = float(date_metrics["date_total_markdown"].sum())
    overall_markdown_rate = (
        overall_total_markdown / overall_total_sales if overall_total_sales > 0 else 0.0
    )

    unified = train.merge(date_metrics, on="date", how="left")
    unified["overall_total_sales"] = overall_total_sales
    unified["overall_avg_weekly_sales"] = overall_avg_weekly_sales
    unified["overall_sales_per_store"] = overall_sales_per_store
    unified["overall_sales_per_dept"] = overall_sales_per_dept
    unified["overall_total_markdown"] = overall_total_markdown
    unified["overall_markdown_rate"] = overall_markdown_rate

    unified = _stringify_date(unified, "date")
    unified = _stringify_date(unified, "month")
    unified = _stringify_date(unified, "week_start")

    for column in ["store_type", "month_name", "day_of_week"]:
        if column in unified.columns:
            unified[column] = unified[column].astype("string")

    columns = [
        "date",
        "month",
        "year",
        "month_num",
        "month_name",
        "iso_year",
        "week",
        "week_start",
        "day_of_week",
        "day_of_week_num",
        "day_of_month",
        "store_nbr",
        "dept",
        "store_type",
        "store_size",
        "is_holiday",
        "feature_is_holiday",
        "total_sales",
        "total_markdown",
        "store_date_sales",
        "store_date_dept_count",
        "store_date_sales_share",
        "date_total_sales",
        "date_total_markdown",
        "date_row_count",
        "date_total_sales_safe_sum",
        "date_total_markdown_safe_sum",
        "date_store_count",
        "date_dept_count",
        "date_avg_sales_per_store",
        "date_avg_sales_per_dept",
        "date_markdown_rate",
        "date_sales_7d_avg",
        "date_sales_28d_avg",
        "date_sales_7d_std",
        "date_sales_28d_std",
        "date_sales_7d_upper",
        "date_sales_7d_lower",
        "date_sales_28d_upper",
        "date_sales_28d_lower",
        "temperature",
        "fuel_price",
        "markdown1",
        "markdown2",
        "markdown3",
        "markdown4",
        "markdown5",
        "cpi",
        "unemployment",
        "overall_total_sales",
        "overall_avg_weekly_sales",
        "overall_sales_per_store",
        "overall_sales_per_dept",
        "overall_total_markdown",
        "overall_markdown_rate",
    ]

    unified = unified[columns]
    return unified


def _apply_date_filters(train: pd.DataFrame, min_date: str | None, max_date: str | None) -> pd.DataFrame:
    if min_date:
        train = train[train["date"] >= pd.to_datetime(min_date)]
    if max_date:
        train = train[train["date"] <= pd.to_datetime(max_date)]
    return train


def run_pipeline(
    input_dir: str | None = None,
    output_dir: str | None = None,
    dataset: str = "store-sales",
    top_families: int = 10,
    min_date: str | None = None,
    max_date: str | None = None,
) -> dict[str, Path]:
    input_path, output_path = _resolve_paths(input_dir, output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    LOGGER.info("Loading raw CSVs from %s", input_path)
    dataset = dataset.strip().lower()
    if input_dir is None:
        dataset_path = input_path / dataset
        if dataset_path.exists():
            input_path = dataset_path
            LOGGER.info("Using dataset subfolder %s", input_path)

    family_list: list[str] | None = None

    if dataset == "walmart":
        raw = _load_walmart_raw(input_path)
        train = _apply_date_filters(raw["train"], min_date, max_date)
        LOGGER.info("Building unified Walmart Tableau extract")
        unified = _build_walmart_unified(
            train,
            raw["features"],
            raw["stores"],
        )
        outputs = {
            "tableau_unified": output_path / "tableau_unified_walmart.csv",
        }
        unified.to_csv(outputs["tableau_unified"], index=False)
    else:
        raw = _load_raw(input_path)
        train = _apply_date_filters(raw["train"], min_date, max_date)

        LOGGER.info("Building unified Tableau extract")
        unified, family_list = _build_unified_extract(
            train,
            raw["stores"],
            raw["transactions"],
            raw["oil"],
            raw["holidays"],
            top_families,
        )

        outputs = {
            "tableau_unified": output_path / "tableau_unified.csv",
        }
        unified.to_csv(outputs["tableau_unified"], index=False)

    metadata = {
        "generated_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "input_dir": str(input_path),
        "output_dir": str(output_path),
        "top_families": family_list,
        "dataset": dataset,
        "row_counts": {
            "tableau_unified": len(unified),
        },
    }

    metadata_path = output_path / "metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2))

    outputs["metadata"] = metadata_path
    return outputs


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a unified Tableau-ready extract from Kaggle store sales data."
    )
    parser.add_argument("--input-dir", help="Directory containing raw CSV files.")
    parser.add_argument("--output-dir", help="Directory to write Tableau extracts.")
    parser.add_argument(
        "--dataset",
        choices=["store-sales", "walmart"],
        default="store-sales",
        help="Dataset to process (store-sales or walmart).",
    )
    parser.add_argument("--top-families", type=int, default=10)
    parser.add_argument("--min-date", help="Filter start date (YYYY-MM-DD).")
    parser.add_argument("--max-date", help="Filter end date (YYYY-MM-DD).")
    return parser.parse_args()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    args = _parse_args()
    run_pipeline(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        dataset=args.dataset,
        top_families=args.top_families,
        min_date=args.min_date,
        max_date=args.max_date,
    )


if __name__ == "__main__":
    main()
