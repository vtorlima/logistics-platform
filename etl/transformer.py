"""
ETL transformer — cleans and normalizes reader DataFrames into
database-ready form for all 6 target tables.
"""

import pandas as pd
from pathlib import Path


# ---------------------------------------------------------------------------
# Time / interval helpers
# ---------------------------------------------------------------------------

def _minutes_to_interval(minutes) -> str | None:
    """
    Convert an integer minute count to a PostgreSQL INTERVAL string.
    e.g. 75 → '75 minutes'
    Returns None if the value is null or non-numeric.
    """
    try:
        m = int(minutes)
        return f"{m} minutes"
    except (TypeError, ValueError):
        return None


def _time_str_to_pg(value) -> str | None:
    """
    Ensure a time value is in HH:MM format for PostgreSQL TIME.
    Accepts strings like '07:30', '7:30', or pandas Timestamp objects.
    Returns None if unparseable.
    """
    if pd.isna(value) or value is None:
        return None
    s = str(value).strip()
    # pandas may read times as '07:30:00' — truncate seconds
    if len(s) >= 5:
        return s[:5]
    return None


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _inject_month(df: pd.DataFrame, month: str) -> pd.DataFrame:
    """
    Ensure the 'month' column exists and is filled with the given value.
    Used for the Empresa sheet which doesn't include a month column natively —
    the ETL injects it so rate_history has one snapshot per month.
    """
    df = df.copy()
    df["month"] = month
    return df


def _deduplicate(df: pd.DataFrame, subset: list[str]) -> pd.DataFrame:
    """Drop exact duplicate rows based on the unique key columns."""
    before = len(df)
    df = df.drop_duplicates(subset=subset, keep="first").reset_index(drop=True)
    dropped = before - len(df)
    if dropped > 0:
        print(f"  Deduplication: dropped {dropped} duplicate rows on {subset}")
    return df


# ---------------------------------------------------------------------------
# Per-table transformers
# ---------------------------------------------------------------------------

def transform_rides(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transform the Controle sheet DataFrame into the rides table format.

    Changes made:
    - Convert time strings to HH:MM format
    - Convert integer minutes to PostgreSQL INTERVAL strings
    - Ensure numeric precision on money columns
    - Deduplicate on (month, os_number)
    - Drop rows where ride_date is null
    """
    if df.empty:
        return df

    df = df.copy()

    # Drop rows with no ride date (unfilled template rows)
    df = df.dropna(subset=["ride_date"]).reset_index(drop=True)

    # Time columns → HH:MM strings
    for col in ["time_requested", "time_start", "time_end"]:
        if col in df.columns:
            df[col] = df[col].apply(_time_str_to_pg)

    # Minute integers → INTERVAL strings
    for col in ["company_time", "driver_time"]:
        if col in df.columns:
            df[col] = df[col].apply(_minutes_to_interval)

    # Round money columns to 2 decimal places
    money_cols = ["toll", "parking", "idle_time_billing", "transit_fare",
                  "return_billing", "ride_price", "surcharges", "total", "cost_per_passenger"]
    for col in money_cols:
        if col in df.columns:
            df[col] = df[col].round(2)

    # Round price_per_km to 4 places
    if "price_per_km" in df.columns:
        df["price_per_km"] = df["price_per_km"].round(4)

    # Drop columns not in the rides schema (km_initial, km_final are XLSX-only)
    for col in ["km_initial", "km_final"]:
        if col in df.columns:
            df = df.drop(columns=[col])

    df = _deduplicate(df, ["month", "os_number"])

    return df


def transform_monthly_driver_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transform the Folha sheet DataFrame into the monthly_driver_summary table format.

    Changes made:
    - Convert 'goal_met' string to boolean if not already converted by reader
    - Round decimal columns
    - Deduplicate on (month, driver)
    """
    if df.empty:
        return df

    df = df.copy()

    # goal_met may still be string if reader didn't catch it
    if "goal_met" in df.columns and df["goal_met"].dtype == object:
        df["goal_met"] = df["goal_met"].map({"Sim": True, "Não": False, True: True, False: False})

    decimal_cols = ["pay_km", "pay_idle_time", "surcharge_night", "surcharge_holiday",
                    "surcharge_sunday", "surcharge_total", "pay_total", "km_goal", "efficiency"]
    for col in decimal_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").round(4)

    df = _deduplicate(df, ["month", "driver"])
    return df


def transform_monthly_company_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transform the Financeiro sheet DataFrame into the monthly_company_summary table format.

    Changes made:
    - Round all revenue columns to 2 decimal places
    - Round revenue_share to 4 decimal places
    - Deduplicate on (month, company)
    """
    if df.empty:
        return df

    df = df.copy()

    revenue_cols = ["revenue_toll", "revenue_parking", "revenue_surcharges",
                    "revenue_idle_time", "revenue_transit", "revenue_return",
                    "revenue_rides", "revenue_subtotal", "revenue_final",
                    "avg_ride_value", "avg_km_loaded"]
    for col in revenue_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").round(2)

    if "revenue_share" in df.columns:
        df["revenue_share"] = pd.to_numeric(df["revenue_share"], errors="coerce").round(4)

    df = _deduplicate(df, ["month", "company"])
    return df


def transform_monthly_vehicle_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transform the Frota Stats sheet DataFrame into the monthly_vehicle_summary table format.

    Changes made:
    - Round decimal columns
    - Deduplicate on (month, plate)
    """
    if df.empty:
        return df

    df = df.copy()

    decimal_cols = ["km_per_day", "rides_per_day"]
    for col in decimal_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").round(2)

    df = _deduplicate(df, ["month", "plate"])
    return df


def transform_driver_schedule(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transform the Folga sheet DataFrame into the driver_schedule table format.
    Minimal transformation — all columns are integers, already handled by reader.
    """
    if df.empty:
        return df

    df = df.copy()
    df = _deduplicate(df, ["month", "driver"])
    return df


def transform_rate_history(df: pd.DataFrame, month: str) -> pd.DataFrame:
    """
    Transform the Empresa sheet DataFrame into the rate_history table format.

    Changes made:
    - Inject the month column (Empresa sheet has no month — ETL adds it)
    - Round all rate columns to 4 decimal places
    - Deduplicate on (month, company)
    """
    if df.empty:
        return df

    df = _inject_month(df, month)

    rate_cols = ["km_rate", "idle_rate", "idle_courtesy_hours", "invoice_tax_rate",
                 "night_surcharge_rate", "holiday_surcharge_rate", "sunday_surcharge_rate",
                 "toll_tax_rate", "return_rate", "transit_rate"]
    for col in rate_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").round(4)

    df = _deduplicate(df, ["month", "company"])
    return df


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def transform(data: dict[str, pd.DataFrame], month: str) -> dict[str, pd.DataFrame]:
    """
    Transform all DataFrames from the reader into database-ready form.

    Args:
        data:  Output of reader.read_workbook() — keyed by target table name.
        month: The month string (e.g. '2026-01') extracted from the filename.

    Returns:
        Dict with the same keys, each value a cleaned DataFrame.
    """
    return {
        "rides": transform_rides(
            data.get("rides", pd.DataFrame())
        ),
        "monthly_driver_summary": transform_monthly_driver_summary(
            data.get("monthly_driver_summary", pd.DataFrame())
        ),
        "monthly_company_summary": transform_monthly_company_summary(
            data.get("monthly_company_summary", pd.DataFrame())
        ),
        "monthly_vehicle_summary": transform_monthly_vehicle_summary(
            data.get("monthly_vehicle_summary", pd.DataFrame())
        ),
        "driver_schedule": transform_driver_schedule(
            data.get("driver_schedule", pd.DataFrame())
        ),
        "rate_history": transform_rate_history(
            data.get("rate_history", pd.DataFrame()), month
        ),
    }
