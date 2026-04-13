"""
Monthly summary generators — aggregate ride data into Folha, Financeiro,
Frota stats, Folga, and Metas sheets.
"""

import random
from collections import defaultdict
from datetime import date, timedelta
from seed.config import COMPANIES, DRIVERS, MONTHS

DRIVER_KM_RATE = 1.80
DRIVER_IDLE_RATE = 40.00
DRIVER_NIGHT_SURCHARGE = 0.15
DRIVER_HOLIDAY_SURCHARGE = 0.40
DRIVER_SUNDAY_SURCHARGE = 0.40
DRIVER_MONTHLY_KM_GOAL = 4000


# ---------------------------------------------------------------------------
# Folha — driver payroll summary
# ---------------------------------------------------------------------------

def generate_folha(month: str, rides: list[dict]) -> list[dict]:
    """
    One row per driver. Aggregates ride data to compute pay totals.
    Only drivers who actually worked in the month appear.
    """
    # Group rides by driver
    driver_rides: dict[str, list] = defaultdict(list)
    for ride in rides:
        if ride["driver"]:
            driver_rides[ride["driver"]].append(ride)

    rows = []
    for driver, dr in driver_rides.items():
        km_total = sum(r["km_total"] for r in dr)
        km_loaded = sum(r["km_loaded"] for r in dr)
        km_night = sum(r["night_km"] for r in dr)
        km_holiday = sum(r["holiday_km"] for r in dr)
        km_sunday = sum(r["sunday_km"] for r in dr)
        days_worked = len({r["ride_date"] for r in dr})
        total_rides = len(dr)

        pay_km = round(km_loaded * DRIVER_KM_RATE, 2)
        pay_idle = round(
            sum(r["idle_time_billing"] for r in dr) * (DRIVER_IDLE_RATE / 85.0), 2
        )  # scale company idle billing back to driver rate

        surcharge_night = round(km_night * DRIVER_KM_RATE * DRIVER_NIGHT_SURCHARGE, 2)
        surcharge_holiday = round(km_holiday * DRIVER_KM_RATE * DRIVER_HOLIDAY_SURCHARGE, 2)
        surcharge_sunday = round(km_sunday * DRIVER_KM_RATE * DRIVER_SUNDAY_SURCHARGE, 2)
        surcharge_total = round(surcharge_night + surcharge_holiday + surcharge_sunday, 2)

        pay_total = round(pay_km + pay_idle + surcharge_total, 2)
        efficiency = round(km_loaded / km_total, 4) if km_total > 0 else 0.0
        goal_met = km_total >= DRIVER_MONTHLY_KM_GOAL

        rows.append({
            "Mês": month,
            "Motorista": driver,
            "Dias Trabalhados": days_worked,
            "Corridas": total_rides,
            "Km Total": km_total,
            "Km Cheio": km_loaded,
            "Km Noturno": km_night,
            "Km Feriado": km_holiday,
            "Km Domingo": km_sunday,
            "Pag. Km": pay_km,
            "Pag. HP": pay_idle,
            "Adic. Noturno": surcharge_night,
            "Adic. Feriado": surcharge_holiday,
            "Adic. Domingo": surcharge_sunday,
            "Total Adicional": surcharge_total,
            "Total Pagar": pay_total,
            "Meta Km": DRIVER_MONTHLY_KM_GOAL,
            "Meta Atingida": "Sim" if goal_met else "Não",
            "Eficiência": efficiency,
        })

    return sorted(rows, key=lambda r: r["Total Pagar"], reverse=True)


# ---------------------------------------------------------------------------
# Financeiro — company revenue summary
# ---------------------------------------------------------------------------

def generate_financeiro(month: str, rides: list[dict]) -> list[dict]:
    """
    One row per company. Aggregates revenue components and applies invoice tax.
    """
    company_rides: dict[str, list] = defaultdict(list)
    for ride in rides:
        company_rides[ride["company"]].append(ride)

    total_revenue_all = sum(r["total"] for r in rides)
    rows = []

    for company, cr in company_rides.items():
        cfg = COMPANIES[company]
        total_rides = len(cr)
        km_loaded = sum(r["km_loaded"] for r in cr)
        km_total = sum(r["km_total"] for r in cr)

        rev_toll = round(sum(r["toll"] for r in cr), 2)
        rev_parking = round(sum(r["parking"] for r in cr), 2)
        rev_surcharges = round(sum(r["surcharges"] for r in cr), 2)
        rev_idle = round(sum(r["idle_time_billing"] for r in cr), 2)
        rev_transit = round(sum(r["transit_fare"] for r in cr), 2)
        rev_return = round(sum(r["return_billing"] for r in cr), 2)
        rev_rides = round(sum(r["ride_price"] for r in cr), 2)

        rev_subtotal = round(
            rev_toll + rev_parking + rev_surcharges + rev_idle
            + rev_transit + rev_return + rev_rides, 2
        )
        rev_final = round(rev_subtotal * (1 + cfg["tax_rate"]), 2)
        revenue_share = round(rev_final / total_revenue_all, 4) if total_revenue_all > 0 else 0.0
        avg_ride_value = round(rev_final / total_rides, 2) if total_rides > 0 else 0.0
        avg_km_loaded = round(km_loaded / total_rides, 2) if total_rides > 0 else 0.0

        rows.append({
            "Mês": month,
            "Empresa": company,
            "Corridas": total_rides,
            "Km Cheio": km_loaded,
            "Km Total": km_total,
            "Pedágio": rev_toll,
            "Estacionamento": rev_parking,
            "Adicional": rev_surcharges,
            "Hora Parada": rev_idle,
            "Passagem": rev_transit,
            "Retorno": rev_return,
            "Corridas (R$)": rev_rides,
            "Subtotal": rev_subtotal,
            "Total Final": rev_final,
            "Part. (%)": revenue_share,
            "Ticket Médio": avg_ride_value,
            "Km Médio": avg_km_loaded,
        })

    return sorted(rows, key=lambda r: r["Total Final"], reverse=True)


# ---------------------------------------------------------------------------
# Frota stats — vehicle performance summary
# ---------------------------------------------------------------------------

def generate_frota_stats(month: str, rides: list[dict], frota: list[dict]) -> list[dict]:
    """
    One row per vehicle. Aggregates KM and ride counts, computes fleet rank.
    """
    vehicle_rides: dict[str, list] = defaultdict(list)
    for ride in rides:
        vehicle_rides[ride["vehicle_plate"]].append(ride)

    # Build lookup for vehicle metadata
    vehicle_meta = {v["Placa"]: v for v in frota}

    rows = []
    for plate, vr in vehicle_rides.items():
        meta = vehicle_meta.get(plate, {})
        working_days = len({r["ride_date"] for r in vr})
        total_rides = len(vr)
        km_loaded = sum(r["km_loaded"] for r in vr)
        km_total = sum(r["km_total"] for r in vr)
        km_empty = sum(r["km_empty"] for r in vr)

        odometer_start = min(r["km_initial"] for r in vr)
        odometer_end = max(r["km_final"] for r in vr)
        # km_unaccounted: difference between odometer delta and recorded km_total
        km_unaccounted = max(0, (odometer_end - odometer_start) - km_total)

        rows.append({
            "Mês": month,
            "Placa": plate,
            "Modelo": meta.get("Modelo", ""),
            "Motorista": meta.get("Motorista", ""),
            "Dias Trabalhados": working_days,
            "Km/Dia": round(km_total / working_days, 2) if working_days > 0 else 0.0,
            "Corridas": total_rides,
            "Corridas/Dia": round(total_rides / working_days, 2) if working_days > 0 else 0.0,
            "Km Cheio": km_loaded,
            "Km Vazio": km_empty,
            "Km Total": km_total,
            "Km Não Contab.": km_unaccounted,
            "Km Inicial": odometer_start,
            "Km Final": odometer_end,
            "Ranking": 0,  # filled after sorting below
        })

    # Rank by total km descending
    rows.sort(key=lambda r: r["Km Total"], reverse=True)
    for i, row in enumerate(rows, start=1):
        row["Ranking"] = i

    return rows


# ---------------------------------------------------------------------------
# Folga — driver monthly schedule
# ---------------------------------------------------------------------------

def generate_folga(month: str) -> list[dict]:
    """
    One row per driver. Generates realistic day-off patterns for the month.
    Working days in a month ≈ 26 (Mon–Sat schedule for taxi drivers).
    """
    year, mon = map(int, month.split("-"))
    # Count calendar days in month
    if mon == 12:
        days_in_month = (date(year + 1, 1, 1) - date(year, mon, 1)).days
    else:
        days_in_month = (date(year, mon + 1, 1) - date(year, mon, 1)).days

    rows = []
    random.seed(int(month.replace("-", "")) + 99)  # separate seed from rides

    for driver in DRIVERS:
        days_off = random.randint(4, 6)           # regular weekly rest days
        days_off_requested = random.randint(0, 2)
        days_medical = 1 if random.random() < 0.08 else 0
        days_vacation = random.randint(0, 5) if random.random() < 0.05 else 0
        days_absence = 1 if random.random() < 0.03 else 0
        days_compensatory = random.randint(0, 1)
        days_dispensed = 0
        days_holiday = 1 if mon == 1 else (2 if mon == 2 else 0)  # New Year / Carnival

        days_off_total = (days_off + days_off_requested + days_medical
                          + days_vacation + days_absence + days_holiday)
        days_worked = max(0, days_in_month - days_off_total)
        days_available = days_in_month - days_off - days_vacation
        days_salary = days_in_month - days_absence

        rows.append({
            "Mês": month,
            "Motorista": driver,
            "Folgas": days_off,
            "Folgas Solicitadas": days_off_requested,
            "Compensatórias": days_compensatory,
            "Feriados": days_holiday,
            "Férias": days_vacation,
            "Atestado": days_medical,
            "Faltas": days_absence,
            "Dispensado": days_dispensed,
            "Dias Trabalhados": days_worked,
            "Dias Disponíveis": days_available,
            "Dias p/ Salário": days_salary,
        })

    return rows


# ---------------------------------------------------------------------------
# Metas — driver KM goals
# ---------------------------------------------------------------------------

def generate_metas(month: str, folha: list[dict]) -> list[dict]:
    """
    One row per driver. Compares actual KM against the monthly goal.
    Derived from Folha — must be called after generate_folha().
    """
    rows = []
    for row in folha:
        rows.append({
            "Mês": month,
            "Motorista": row["Motorista"],
            "Meta Km": DRIVER_MONTHLY_KM_GOAL,
            "Km Realizado": row["Km Total"],
            "Diferença": row["Km Total"] - DRIVER_MONTHLY_KM_GOAL,
            "Meta Atingida": row["Meta Atingida"],
            "Eficiência": row["Eficiência"],
        })
    return rows
