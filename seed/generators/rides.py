"""
Ride generator — produces ~2,400 internally consistent ride records per month.
"""

import random
from datetime import date, datetime, timedelta
from faker import Faker
from seed.config import (
    COMPANIES,
    DRIVERS,
    VEHICLES,
    ROUTES,
    CHANNELS,
    SERVICE_TYPES,
    TRIP_TYPES,
    RIDES_PER_MONTH,
    IDLE_TIME_PERCENTAGE,
    NIGHT_RIDE_PERCENTAGE,
    HOLIDAY_RIDE_PERCENTAGE,
    SUNDAY_RIDE_PERCENTAGE,
    RETURN_TRIP_PERCENTAGE,
    KM_EMPTY_RATIO_MIN,
    KM_EMPTY_RATIO_MAX,
    PASSENGERS_MIN,
    PASSENGERS_MAX,
    MORNING_PEAK_START,
    MORNING_PEAK_END,
    EVENING_PEAK_START,
    EVENING_PEAK_END,
    OS_NUMBER_START,
)

fake = Faker("pt_BR")

# ---------------------------------------------------------------------------
# Holiday dates for the generated months (2026-01 through 2026-03)
# ---------------------------------------------------------------------------

HOLIDAYS = {
    date(2026, 1, 1),   # New Year's Day
    date(2026, 2, 16),  # Carnival Monday
    date(2026, 2, 17),  # Carnival Tuesday
    date(2026, 3, 6),   # Ash Wednesday (half day / observed)
}

# ---------------------------------------------------------------------------
# Vehicle state — tracks current odometer per plate across the entire
# generation run so KM values are sequential and realistic.
# ---------------------------------------------------------------------------

def _build_vehicle_state() -> dict:
    """Initialize one odometer per vehicle, starting between 30,000–90,000 km."""
    return {plate: random.randint(30_000, 90_000) for plate in VEHICLES}


# ---------------------------------------------------------------------------
# Driver–vehicle assignment — fixed mapping (one driver per vehicle).
# The last vehicle has no assigned driver (None).
# ---------------------------------------------------------------------------

VEHICLE_DRIVER = {
    plate: (DRIVERS[i] if i < len(DRIVERS) else None)
    for i, plate in enumerate(VEHICLES)
}

# ---------------------------------------------------------------------------
# Date helpers
# ---------------------------------------------------------------------------

def _dates_for_month(month: str) -> list[date]:
    """
    Return all calendar dates in the month, weighted so weekdays appear
    ~5x more than weekends, and holidays are excluded entirely.
    """
    year, mon = map(int, month.split("-"))
    # Build month date range
    start = date(year, mon, 1)
    if mon == 12:
        end = date(year + 1, 1, 1)
    else:
        end = date(year, mon + 1, 1)

    all_dates = []
    d = start
    while d < end:
        if d not in HOLIDAYS:
            # weekday() 0=Mon … 6=Sun
            weight = 1 if d.weekday() >= 5 else 5
            all_dates.extend([d] * weight)
        d += timedelta(days=1)
    return all_dates


# ---------------------------------------------------------------------------
# Time helpers
# ---------------------------------------------------------------------------

def _random_peak_time() -> datetime:
    """Return a random time biased toward morning or evening peak."""
    if random.random() < 0.55:
        # morning peak
        hour = random.randint(MORNING_PEAK_START, MORNING_PEAK_END - 1)
    else:
        # evening peak
        hour = random.randint(EVENING_PEAK_START, EVENING_PEAK_END - 1)
    minute = random.randint(0, 59)
    return datetime(2000, 1, 1, hour, minute)  # date part is a placeholder


def _is_night(dt: datetime) -> bool:
    """Night ride: departs between 22:00–05:00."""
    return dt.hour >= 22 or dt.hour < 5


# ---------------------------------------------------------------------------
# Billing calculation
# ---------------------------------------------------------------------------

def _calculate_billing(
    company: str,
    route: dict,
    km_loaded: int,
    km_empty: int,
    ride_dt: datetime,
    ride_date: date,
    has_idle: bool,
    idle_hours: float,
    has_return: bool,
) -> dict:
    """
    Apply all billing rules for a single ride. Returns a dict with:
    toll, parking, idle_time_billing, transit_fare, return_billing,
    ride_price, surcharges, total, night_km, holiday_km, sunday_km,
    price_per_km, is_night, is_holiday, is_sunday.
    """
    cfg = COMPANIES[company]
    km_rate = cfg["km_rate"]

    # Base ride price
    ride_price = round(km_loaded * km_rate, 2)

    # Surcharge flags
    is_night = _is_night(ride_dt)
    is_holiday = ride_date in HOLIDAYS
    is_sunday = ride_date.weekday() == 6

    # KM buckets (only one surcharge applies at a time, priority: holiday > sunday > night)
    night_km = km_loaded if (is_night and not is_holiday and not is_sunday) else 0
    holiday_km = km_loaded if is_holiday else 0
    sunday_km = km_loaded if (is_sunday and not is_holiday) else 0

    # Surcharge amounts
    surcharge_night = round(night_km * km_rate * cfg["night_surcharge"], 2)
    surcharge_holiday = round(holiday_km * km_rate * cfg["holiday_surcharge"], 2)
    surcharge_sunday = round(sunday_km * km_rate * cfg["sunday_surcharge"], 2)
    surcharges = round(surcharge_night + surcharge_holiday + surcharge_sunday, 2)

    # Idle time billing (HP)
    idle_time_billing = 0.0
    if has_idle:
        billable_idle = max(0.0, idle_hours - cfg["idle_courtesy_hours"])
        idle_time_billing = round(billable_idle * cfg["idle_rate"], 2)

    # Return trip
    return_billing = round(ride_price * cfg["return_rate"], 2) if has_return else 0.0

    # Toll and parking — small fixed random values for realism
    toll = round(random.choice([0.0, 0.0, 5.60, 7.20, 11.40]), 2)
    parking = round(random.choice([0.0, 0.0, 0.0, 8.00, 15.00]), 2)

    # Transit fare (passagem) — only for INTER routes, occasionally
    transit_fare = 0.0
    if route["type"] == "INTER" and random.random() < 0.1:
        transit_fare = round(random.choice([4.50, 5.00, 9.00]), 2)

    total = round(
        toll + parking + idle_time_billing + transit_fare
        + return_billing + ride_price + surcharges,
        2,
    )

    price_per_km = round(ride_price / (km_loaded + km_empty), 4) if (km_loaded + km_empty) > 0 else 0.0

    return {
        "toll": toll,
        "parking": parking,
        "idle_time_billing": idle_time_billing,
        "transit_fare": transit_fare,
        "return_billing": return_billing,
        "ride_price": ride_price,
        "surcharges": surcharges,
        "total": total,
        "night_km": night_km,
        "holiday_km": holiday_km,
        "sunday_km": sunday_km,
        "price_per_km": price_per_km,
    }


# ---------------------------------------------------------------------------
# Passenger pool — grouped by company for fast lookup
# ---------------------------------------------------------------------------

def _build_passenger_pool(passengers: list[dict]) -> dict:
    """Return {company_name: [passenger_dict, ...]} for O(1) per-company lookup."""
    pool = {company: [] for company in COMPANIES}
    for p in passengers:
        company = p["Empresa"]
        if company in pool:
            pool[company].append(p)
    return pool


# ---------------------------------------------------------------------------
# Main generator
# ---------------------------------------------------------------------------

def generate_rides(month: str, passengers: list[dict], os_start: int) -> list[dict]:
    """
    Generate RIDES_PER_MONTH ride records for the given month.

    Args:
        month:    e.g. "2026-01"
        passengers: output of generate_passageiro() — used for passenger assignment
        os_start: first OS number to use (sequential)

    Returns:
        List of ride dicts matching the rides table schema.
    """
    random.seed(int(month.replace("-", "")))  # deterministic per month

    vehicle_odometer = _build_vehicle_state()
    passenger_pool = _build_passenger_pool(passengers)
    available_dates = _dates_for_month(month)

    # Build weighted company list based on ride_share
    company_names = list(COMPANIES.keys())
    company_weights = [COMPANIES[c]["ride_share"] for c in company_names]

    rides = []
    os_number = os_start

    for _ in range(RIDES_PER_MONTH):
        # --- Company & vehicle ---
        company = random.choices(company_names, weights=company_weights, k=1)[0]
        vehicle_plate = random.choice(VEHICLES)
        driver = VEHICLE_DRIVER[vehicle_plate]

        # --- Route ---
        route = random.choice(ROUTES)

        # --- KM ---
        # km_loaded: use route base KM ± 20% variation
        km_loaded = max(5, int(route["km"] * random.uniform(0.8, 1.2)))
        km_empty = max(1, int(km_loaded * random.uniform(KM_EMPTY_RATIO_MIN, KM_EMPTY_RATIO_MAX)))
        km_total = km_loaded + km_empty

        # Odometer (sequential per vehicle)
        km_initial = vehicle_odometer[vehicle_plate]
        vehicle_odometer[vehicle_plate] += km_total
        km_final = vehicle_odometer[vehicle_plate]

        # --- Date & time ---
        ride_date = random.choice(available_dates)
        ride_dt = _random_peak_time()

        # Timestamps (all as time strings — date is stored separately)
        time_requested = ride_dt
        time_start = ride_dt + timedelta(minutes=random.randint(10, 30))
        travel_minutes = max(10, int(km_loaded * random.uniform(1.5, 3.0)))
        time_end = time_start + timedelta(minutes=travel_minutes)
        time_final = time_end + timedelta(minutes=random.randint(5, 20))

        company_time_minutes = int((time_end - time_requested).total_seconds() / 60)
        driver_time_minutes = int((time_final - time_start).total_seconds() / 60)

        # --- Flags ---
        has_idle = random.random() < IDLE_TIME_PERCENTAGE
        idle_hours = round(random.uniform(0.3, 2.0), 2) if has_idle else 0.0
        has_return = random.random() < RETURN_TRIP_PERCENTAGE

        # --- Passengers ---
        company_passengers = passenger_pool.get(company, [])
        pax_count = random.randint(PASSENGERS_MIN, min(PASSENGERS_MAX, max(1, len(company_passengers))))
        selected = random.sample(company_passengers, pax_count) if len(company_passengers) >= pax_count else company_passengers
        main_passenger = selected[0]["Nome"] if selected else fake.name()
        requester = random.choice(selected)["Nome"] if selected else fake.name()

        # --- Billing ---
        billing = _calculate_billing(
            company=company,
            route=route,
            km_loaded=km_loaded,
            km_empty=km_empty,
            ride_dt=ride_dt,
            ride_date=ride_date,
            has_idle=has_idle,
            idle_hours=idle_hours,
            has_return=has_return,
        )

        cost_per_passenger = round(billing["total"] / pax_count, 2) if pax_count > 0 else billing["total"]

        rides.append({
            "month": month,
            "os_number": os_number,
            "nf_type": route["type"],
            "ride_date": ride_date.isoformat(),
            "company": company,
            "requester": requester,
            "channel": random.choice(CHANNELS),
            "scheduler": fake.name(),
            "vehicle_plate": vehicle_plate,
            "driver": driver,
            "km_empty": km_empty,
            "km_loaded": km_loaded,
            "km_total": km_total,
            "km_initial": km_initial,
            "km_final": km_final,
            "time_requested": time_requested.strftime("%H:%M"),
            "time_start": time_start.strftime("%H:%M"),
            "time_end": time_end.strftime("%H:%M"),
            "company_time": company_time_minutes,   # stored as minutes
            "driver_time": driver_time_minutes,     # stored as minutes
            "origin": route["origin"],
            "destination": route["destination"],
            "main_passenger": main_passenger,
            "passenger_count": pax_count,
            "service_type": random.choice(SERVICE_TYPES),
            "trip_type": random.choice(TRIP_TYPES),
            "toll": billing["toll"],
            "parking": billing["parking"],
            "idle_time_billing": billing["idle_time_billing"],
            "transit_fare": billing["transit_fare"],
            "return_billing": billing["return_billing"],
            "ride_price": billing["ride_price"],
            "surcharges": billing["surcharges"],
            "total": billing["total"],
            "night_km": billing["night_km"],
            "holiday_km": billing["holiday_km"],
            "sunday_km": billing["sunday_km"],
            "price_per_km": billing["price_per_km"],
            "cost_per_passenger": cost_per_passenger,
            "status": "Concluído",
        })

        os_number += 1

    return rides
