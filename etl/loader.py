"""
ETL loader — upserts DataFrames into PostgreSQL tables.
All tables loaded in a single transaction; rolls back on any error.
"""

import pandas as pd
import psycopg2

BATCH_SIZE = 500

RIDES_COLS = [
    "month", "os_number", "nf_type", "ride_date", "company", "requester",
    "channel", "scheduler", "vehicle_plate", "driver",
    "km_empty", "km_loaded", "km_total",
    "time_requested", "time_start", "time_end", "company_time", "driver_time",
    "origin", "destination", "main_passenger", "passenger_count",
    "service_type", "trip_type",
    "toll", "parking", "idle_time_billing", "transit_fare",
    "return_billing", "ride_price", "surcharges", "total",
    "night_km", "holiday_km", "sunday_km",
    "price_per_km", "cost_per_passenger", "status",
]

DRIVER_SUMMARY_COLS = [
    "month", "driver", "days_worked", "total_rides",
    "km_total", "km_loaded", "km_night", "km_holiday", "km_sunday",
    "pay_km", "pay_idle_time",
    "surcharge_night", "surcharge_holiday", "surcharge_sunday", "surcharge_total",
    "pay_total", "km_goal", "goal_met", "efficiency",
]

VEHICLE_SUMMARY_COLS = [
    "month", "plate", "model", "assigned_driver", "fleet_rank",
    "working_days", "km_per_day", "rides_per_day",
    "total_rides", "km_loaded", "km_total", "km_unaccounted",
    "odometer_start", "odometer_end",
]

COMPANY_SUMMARY_COLS = [
    "month", "company", "total_rides", "km_loaded", "km_total",
    "revenue_toll", "revenue_parking", "revenue_surcharges",
    "revenue_idle_time", "revenue_transit", "revenue_return",
    "revenue_rides", "revenue_subtotal", "revenue_final",
    "revenue_share", "avg_ride_value", "avg_km_loaded",
]

DRIVER_SCHEDULE_COLS = [
    "month", "driver",
    "days_off", "days_off_requested", "days_compensatory", "days_holiday",
    "days_vacation", "days_medical", "days_absence", "days_dispensed",
    "days_worked", "days_available", "days_salary",
]

RATE_HISTORY_COLS = [
    "month", "company",
    "km_rate", "idle_rate", "idle_courtesy_hours",
    "transit_rate", "return_rate", "toll_tax_rate", "invoice_tax_rate",
    "night_surcharge_rate", "holiday_surcharge_rate", "sunday_surcharge_rate",
    "status",
]


def _df_to_tuples(df: pd.DataFrame, cols: list[str]) -> list[tuple]:
    """
    Extract rows from a DataFrame as a list of tuples, ordered by cols.
    Missing columns are filled with None. pandas NA values become None.
    """
    out = []
    for _, row in df.iterrows():
        out.append(tuple(
            None if pd.isna(row.get(col)) else row.get(col)
            for col in cols
        ))
    return out


def _upsert(
    cursor,
    table: str,
    cols: list[str],
    conflict_cols: list[str],
    rows: list[tuple],
):
    """
    Batch upsert rows into table. On conflict (unique key), update all non-key columns.
    """
    if not rows:
        return 0

    update_cols = [c for c in cols if c not in conflict_cols]
    placeholders = ", ".join(["%s"] * len(cols))
    col_list = ", ".join(cols)
    conflict_target = ", ".join(conflict_cols)
    update_set = ", ".join(f"{c} = EXCLUDED.{c}" for c in update_cols)

    sql = (
        f"INSERT INTO {table} ({col_list}) VALUES ({placeholders}) "
        f"ON CONFLICT ({conflict_target}) DO UPDATE SET {update_set}"
    )

    inserted = 0
    for i in range(0, len(rows), BATCH_SIZE):
        batch = rows[i : i + BATCH_SIZE]
        cursor.executemany(sql, batch)
        inserted += len(batch)

    return inserted


def load(data: dict[str, pd.DataFrame], conn) -> dict[str, int]:
    """
    Load all 6 DataFrames into PostgreSQL inside a single transaction.

    Args:
        data: Output of transformer.transform() — keyed by target table name.
        conn: psycopg2 connection (open, not yet in a transaction).

    Returns:
        Dict of {table_name: rows_upserted}.

    Raises:
        Exception: rolls back the transaction and re-raises on any error.
    """
    counts = {}

    try:
        with conn:  # psycopg2 context manager: commits on exit, rolls back on exception
            with conn.cursor() as cur:

                rows = _df_to_tuples(data.get("rides", pd.DataFrame()), RIDES_COLS)
                counts["rides"] = _upsert(cur, "rides", RIDES_COLS, ["month", "os_number"], rows)
                print(f"  rides: {counts['rides']} rows upserted")

                rows = _df_to_tuples(data.get("monthly_driver_summary", pd.DataFrame()), DRIVER_SUMMARY_COLS)
                counts["monthly_driver_summary"] = _upsert(
                    cur, "monthly_driver_summary", DRIVER_SUMMARY_COLS, ["month", "driver"], rows
                )
                print(f"  monthly_driver_summary: {counts['monthly_driver_summary']} rows upserted")

                rows = _df_to_tuples(data.get("monthly_company_summary", pd.DataFrame()), COMPANY_SUMMARY_COLS)
                counts["monthly_company_summary"] = _upsert(
                    cur, "monthly_company_summary", COMPANY_SUMMARY_COLS, ["month", "company"], rows
                )
                print(f"  monthly_company_summary: {counts['monthly_company_summary']} rows upserted")

                rows = _df_to_tuples(data.get("monthly_vehicle_summary", pd.DataFrame()), VEHICLE_SUMMARY_COLS)
                counts["monthly_vehicle_summary"] = _upsert(
                    cur, "monthly_vehicle_summary", VEHICLE_SUMMARY_COLS, ["month", "plate"], rows
                )
                print(f"  monthly_vehicle_summary: {counts['monthly_vehicle_summary']} rows upserted")

                rows = _df_to_tuples(data.get("driver_schedule", pd.DataFrame()), DRIVER_SCHEDULE_COLS)
                counts["driver_schedule"] = _upsert(
                    cur, "driver_schedule", DRIVER_SCHEDULE_COLS, ["month", "driver"], rows
                )
                print(f"  driver_schedule: {counts['driver_schedule']} rows upserted")

                rows = _df_to_tuples(data.get("rate_history", pd.DataFrame()), RATE_HISTORY_COLS)
                counts["rate_history"] = _upsert(
                    cur, "rate_history", RATE_HISTORY_COLS, ["month", "company"], rows
                )
                print(f"  rate_history: {counts['rate_history']} rows upserted")

    except Exception as e:
        print(f"  ERROR: transaction rolled back — {e}")
        raise

    return counts
