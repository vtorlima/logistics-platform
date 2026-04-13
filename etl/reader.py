"""
ETL reader — extracts data from XLSX workbooks into pandas DataFrames.
Handles column mapping, type conversion, and validation.
"""

import pandas as pd
from pathlib import Path

# ---------------------------------------------------------------------------
# Column mappings (Portuguese sheet headers → English DB field names)
# ---------------------------------------------------------------------------

CONTROLE_COLUMNS = {
    "Mês": "month",
    "OS": "os_number",
    "Tipo NF": "nf_type",
    "Data": "ride_date",
    "Empresa": "company",
    "Solicitante": "requester",
    "Canal": "channel",
    "Agendador": "scheduler",
    "Placa": "vehicle_plate",
    "Motorista": "driver",
    "Km Vazio": "km_empty",
    "Km Cheio": "km_loaded",
    "Km Total": "km_total",
    "Km Inicial": "km_initial",
    "Km Final": "km_final",
    "H. Solicitada": "time_requested",
    "H. Saída": "time_start",
    "H. Final": "time_end",
    "T. Empresa": "company_time",
    "T. Motorista": "driver_time",
    "Origem": "origin",
    "Destino": "destination",
    "Passageiro Principal": "main_passenger",
    "Qtd Passageiros": "passenger_count",
    "Tipo Serviço": "service_type",
    "Tipo Viagem": "trip_type",
    "Pedágio": "toll",
    "Estacionamento": "parking",
    "Hora Parada": "idle_time_billing",
    "Passagem": "transit_fare",
    "Retorno": "return_billing",
    "Preço Corrida": "ride_price",
    "Adicional": "surcharges",
    "Total": "total",
    "Km Noturno": "night_km",
    "Km Feriado": "holiday_km",
    "Km Domingo": "sunday_km",
    "Preço/Km": "price_per_km",
    "Custo/Passageiro": "cost_per_passenger",
    "Status": "status",
}

FOLHA_COLUMNS = {
    "Mês": "month",
    "Motorista": "driver",
    "Dias Trabalhados": "days_worked",
    "Corridas": "total_rides",
    "Km Total": "km_total",
    "Km Cheio": "km_loaded",
    "Km Noturno": "km_night",
    "Km Feriado": "km_holiday",
    "Km Domingo": "km_sunday",
    "Pag. Km": "pay_km",
    "Pag. HP": "pay_idle_time",
    "Adic. Noturno": "surcharge_night",
    "Adic. Feriado": "surcharge_holiday",
    "Adic. Domingo": "surcharge_sunday",
    "Total Adicional": "surcharge_total",
    "Total Pagar": "pay_total",
    "Meta Km": "km_goal",
    "Meta Atingida": "goal_met",
    "Eficiência": "efficiency",
}

FINANCEIRO_COLUMNS = {
    "Mês": "month",
    "Empresa": "company",
    "Corridas": "total_rides",
    "Km Cheio": "km_loaded",
    "Km Total": "km_total",
    "Pedágio": "revenue_toll",
    "Estacionamento": "revenue_parking",
    "Adicional": "revenue_surcharges",
    "Hora Parada": "revenue_idle_time",
    "Passagem": "revenue_transit",
    "Retorno": "revenue_return",
    "Corridas (R$)": "revenue_rides",
    "Subtotal": "revenue_subtotal",
    "Total Final": "revenue_final",
    "Part. (%)": "revenue_share",
    "Ticket Médio": "avg_ride_value",
    "Km Médio": "avg_km_loaded",
}

FROTA_STATS_COLUMNS = {
    "Mês": "month",
    "Placa": "plate",
    "Modelo": "model",
    "Motorista": "assigned_driver",
    "Dias Trabalhados": "working_days",
    "Km/Dia": "km_per_day",
    "Corridas": "total_rides",
    "Corridas/Dia": "rides_per_day",
    "Km Cheio": "km_loaded",
    "Km Vazio": "km_empty",
    "Km Total": "km_total",
    "Km Não Contab.": "km_unaccounted",
    "Km Inicial": "odometer_start",
    "Km Final": "odometer_end",
    "Ranking": "fleet_rank",
}

FOLGA_COLUMNS = {
    "Mês": "month",
    "Motorista": "driver",
    "Folgas": "days_off",
    "Folgas Solicitadas": "days_off_requested",
    "Compensatórias": "days_compensatory",
    "Feriados": "days_holiday",
    "Férias": "days_vacation",
    "Atestado": "days_medical",
    "Faltas": "days_absence",
    "Dispensado": "days_dispensed",
    "Dias Trabalhados": "days_worked",
    "Dias Disponíveis": "days_available",
    "Dias p/ Salário": "days_salary",
}

EMPRESA_COLUMNS = {
    "Empresa": "company",
    "Km Rate (R$)": "km_rate",
    "HP Rate (R$/h)": "idle_rate",
    "HP Cortesia (h)": "idle_courtesy_hours",
    "Taxa NF (%)": "invoice_tax_rate",
    "Adicional Noturno (%)": "night_surcharge_rate",
    "Adicional Feriado (%)": "holiday_surcharge_rate",
    "Adicional Domingo (%)": "sunday_surcharge_rate",
    "Taxa Pedágio": "toll_tax_rate",
    "Retorno Rate": "return_rate",
    "Taxa Passagem": "transit_rate",
    "Status": "status",
}


# ---------------------------------------------------------------------------
# Required fields per sheet (validation rejects rows missing these)
# ---------------------------------------------------------------------------

REQUIRED_FIELDS = {
    "Controle": ["os_number", "ride_date", "company", "vehicle_plate", "driver"],
    "Folha": ["month", "driver"],
    "Financeiro": ["month", "company"],
    "Frota Stats": ["month", "plate"],
    "Folga": ["month", "driver"],
    "Empresa": ["company"],
}


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _read_sheet(path: str, sheet_name: str, column_map: dict) -> pd.DataFrame:
    """
    Read a single sheet from an XLSX file, rename columns, drop unmapped columns.
    Returns an empty DataFrame if the sheet doesn't exist or is empty.
    """
    try:
        df = pd.read_excel(path, sheet_name=sheet_name, engine="openpyxl")
    except (ValueError, KeyError):
        # Sheet doesn't exist in this workbook
        print(f"  WARNING: sheet '{sheet_name}' not found in {path}")
        return pd.DataFrame()

    if df.empty:
        return df

    # Only keep columns that exist in both the sheet and the mapping
    found = {col: column_map[col] for col in df.columns if col in column_map}
    df = df[list(found.keys())]
    df = df.rename(columns=found)
    return df


def _validate(df: pd.DataFrame, sheet_name: str) -> tuple[pd.DataFrame, list[str]]:
    """
    Check required fields. Returns (clean_df, warnings).
    Rows missing required fields are dropped with a warning.
    """
    warnings = []
    required = REQUIRED_FIELDS.get(sheet_name, [])
    if not required or df.empty:
        return df, warnings

    mask = pd.Series(True, index=df.index)
    for field in required:
        if field in df.columns:
            mask &= df[field].notna()

    bad_count = (~mask).sum()
    if bad_count > 0:
        warnings.append(f"{sheet_name}: dropped {bad_count} rows missing required fields")
        df = df[mask].reset_index(drop=True)

    return df, warnings


def _convert_types_controle(df: pd.DataFrame) -> pd.DataFrame:
    """Type conversions specific to the Controle (rides) sheet."""
    if df.empty:
        return df

    # Dates
    if "ride_date" in df.columns:
        df["ride_date"] = pd.to_datetime(df["ride_date"], errors="coerce").dt.date

    # Integer KM columns
    int_cols = ["os_number", "km_empty", "km_loaded", "km_total",
                "passenger_count", "night_km", "holiday_km", "sunday_km"]
    for col in int_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")

    # Decimal money columns
    decimal_cols = ["toll", "parking", "idle_time_billing", "transit_fare",
                    "return_billing", "ride_price", "surcharges", "total",
                    "price_per_km", "cost_per_passenger"]
    for col in decimal_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Time columns — keep as strings (HH:MM), loader converts to TIME
    # company_time and driver_time are integers (minutes), loader converts to INTERVAL

    return df


def _convert_types_folha(df: pd.DataFrame) -> pd.DataFrame:
    """Type conversions for the Folha (driver summary) sheet."""
    if df.empty:
        return df

    int_cols = ["days_worked", "total_rides", "km_total", "km_loaded",
                "km_night", "km_holiday", "km_sunday"]
    for col in int_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")

    decimal_cols = ["pay_km", "pay_idle_time", "surcharge_night", "surcharge_holiday",
                    "surcharge_sunday", "surcharge_total", "pay_total", "km_goal", "efficiency"]
    for col in decimal_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    if "goal_met" in df.columns:
        df["goal_met"] = df["goal_met"].map({"Sim": True, "Não": False})

    return df


def _convert_types_financeiro(df: pd.DataFrame) -> pd.DataFrame:
    """Type conversions for the Financeiro (company summary) sheet."""
    if df.empty:
        return df

    int_cols = ["total_rides", "km_loaded", "km_total"]
    for col in int_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")

    decimal_cols = ["revenue_toll", "revenue_parking", "revenue_surcharges",
                    "revenue_idle_time", "revenue_transit", "revenue_return",
                    "revenue_rides", "revenue_subtotal", "revenue_final",
                    "revenue_share", "avg_ride_value", "avg_km_loaded"]
    for col in decimal_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def _convert_types_frota_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Type conversions for the Frota Stats (vehicle summary) sheet."""
    if df.empty:
        return df

    int_cols = ["fleet_rank", "working_days", "total_rides",
                "km_loaded", "km_total", "km_unaccounted",
                "odometer_start", "odometer_end"]
    for col in int_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")

    decimal_cols = ["km_per_day", "rides_per_day"]
    for col in decimal_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def _convert_types_folga(df: pd.DataFrame) -> pd.DataFrame:
    """Type conversions for the Folga (driver schedule) sheet."""
    if df.empty:
        return df

    int_cols = ["days_off", "days_off_requested", "days_compensatory", "days_holiday",
                "days_vacation", "days_medical", "days_absence", "days_dispensed",
                "days_worked", "days_available", "days_salary"]
    for col in int_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")

    return df


def _convert_types_empresa(df: pd.DataFrame) -> pd.DataFrame:
    """Type conversions for the Empresa (rate snapshot) sheet."""
    if df.empty:
        return df

    decimal_cols = ["km_rate", "idle_rate", "idle_courtesy_hours", "invoice_tax_rate",
                    "night_surcharge_rate", "holiday_surcharge_rate", "sunday_surcharge_rate",
                    "toll_tax_rate", "return_rate", "transit_rate"]
    for col in decimal_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def read_workbook(path: str) -> dict[str, pd.DataFrame]:
    """
    Read all relevant sheets from a VCTrans XLSX workbook.

    Returns a dict keyed by target table name:
        {
            "rides": DataFrame,
            "monthly_driver_summary": DataFrame,
            "monthly_company_summary": DataFrame,
            "monthly_vehicle_summary": DataFrame,
            "driver_schedule": DataFrame,
            "rate_history": DataFrame,
        }

    Each DataFrame has English column names matching the DB schema,
    correct types, and invalid rows removed.
    """
    print(f"  Reading: {path}")
    all_warnings: list[str] = []
    result = {}

    # --- Controle → rides ---
    df = _read_sheet(path, "Controle", CONTROLE_COLUMNS)
    df = _convert_types_controle(df)
    df, w = _validate(df, "Controle")
    all_warnings.extend(w)
    result["rides"] = df

    # --- Folha → monthly_driver_summary ---
    df = _read_sheet(path, "Folha", FOLHA_COLUMNS)
    df = _convert_types_folha(df)
    df, w = _validate(df, "Folha")
    all_warnings.extend(w)
    result["monthly_driver_summary"] = df

    # --- Financeiro → monthly_company_summary ---
    df = _read_sheet(path, "Financeiro", FINANCEIRO_COLUMNS)
    df = _convert_types_financeiro(df)
    df, w = _validate(df, "Financeiro")
    all_warnings.extend(w)
    result["monthly_company_summary"] = df

    # --- Frota Stats → monthly_vehicle_summary ---
    df = _read_sheet(path, "Frota Stats", FROTA_STATS_COLUMNS)
    df = _convert_types_frota_stats(df)
    df, w = _validate(df, "Frota Stats")
    all_warnings.extend(w)
    result["monthly_vehicle_summary"] = df

    # --- Folga → driver_schedule ---
    df = _read_sheet(path, "Folga", FOLGA_COLUMNS)
    df = _convert_types_folga(df)
    df, w = _validate(df, "Folga")
    all_warnings.extend(w)
    result["driver_schedule"] = df

    # --- Empresa → rate_history ---
    df = _read_sheet(path, "Empresa", EMPRESA_COLUMNS)
    df = _convert_types_empresa(df)
    df, w = _validate(df, "Empresa")
    all_warnings.extend(w)
    result["rate_history"] = df

    # Print warnings
    for warning in all_warnings:
        print(f"  WARNING: {warning}")

    return result
