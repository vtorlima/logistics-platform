-- VCTrans Logistics Data Platform — Database Schema
-- Run: psql -U <user> -d vctrans -f database/schema.sql

BEGIN;

-- =========================================================================
-- rides — core transaction table, one row per ride
-- =========================================================================

CREATE TABLE rides (
    id SERIAL PRIMARY KEY,
    month VARCHAR(7) NOT NULL,
    os_number INTEGER NOT NULL,
    nf_type VARCHAR(10),
    ride_date DATE NOT NULL,
    company VARCHAR(100) NOT NULL,
    requester VARCHAR(200),
    channel VARCHAR(50),
    scheduler VARCHAR(100),
    vehicle_plate VARCHAR(10) NOT NULL,
    driver VARCHAR(100) NOT NULL,
    km_empty INTEGER,
    km_loaded INTEGER,
    km_total INTEGER,
    time_requested TIME,
    time_start TIME,
    time_end TIME,
    company_time INTERVAL,
    driver_time INTERVAL,
    origin VARCHAR(200),
    destination VARCHAR(200),
    main_passenger VARCHAR(200),
    passenger_count INTEGER,
    service_type VARCHAR(200),
    trip_type VARCHAR(200),
    toll DECIMAL(10,2),
    parking DECIMAL(10,2),
    idle_time_billing DECIMAL(10,2),
    transit_fare DECIMAL(10,2),
    return_billing DECIMAL(10,2),
    ride_price DECIMAL(10,2),
    surcharges DECIMAL(10,2),
    total DECIMAL(10,2),
    night_km INTEGER DEFAULT 0,
    holiday_km INTEGER DEFAULT 0,
    sunday_km INTEGER DEFAULT 0,
    price_per_km DECIMAL(10,4),
    cost_per_passenger DECIMAL(10,2),
    status VARCHAR(50),
    UNIQUE(month, os_number)
);

CREATE INDEX idx_rides_month ON rides(month);
CREATE INDEX idx_rides_company ON rides(company);
CREATE INDEX idx_rides_driver ON rides(driver);
CREATE INDEX idx_rides_vehicle ON rides(vehicle_plate);
CREATE INDEX idx_rides_date ON rides(ride_date);

-- =========================================================================
-- monthly_driver_summary — one row per driver per month (Folha)
-- =========================================================================

CREATE TABLE monthly_driver_summary (
    id SERIAL PRIMARY KEY,
    month VARCHAR(7) NOT NULL,
    driver VARCHAR(100) NOT NULL,
    days_worked INTEGER,
    total_rides INTEGER,
    km_total INTEGER,
    km_loaded INTEGER,
    km_night INTEGER,
    km_holiday INTEGER,
    km_sunday INTEGER,
    pay_km DECIMAL(10,2),
    pay_idle_time DECIMAL(10,2),
    surcharge_night DECIMAL(10,2),
    surcharge_holiday DECIMAL(10,2),
    surcharge_sunday DECIMAL(10,2),
    surcharge_total DECIMAL(10,2),
    pay_total DECIMAL(10,2),
    km_goal DECIMAL(10,2),
    goal_met BOOLEAN,
    efficiency DECIMAL(5,4),
    UNIQUE(month, driver)
);

-- =========================================================================
-- monthly_vehicle_summary — one row per vehicle per month (Frota Stats)
-- =========================================================================

CREATE TABLE monthly_vehicle_summary (
    id SERIAL PRIMARY KEY,
    month VARCHAR(7) NOT NULL,
    plate VARCHAR(10) NOT NULL,
    model VARCHAR(50),
    assigned_driver VARCHAR(100),
    fleet_rank INTEGER,
    working_days INTEGER,
    km_per_day DECIMAL(10,2),
    rides_per_day DECIMAL(10,2),
    total_rides INTEGER,
    km_loaded INTEGER,
    km_total INTEGER,
    km_unaccounted INTEGER,
    odometer_start INTEGER,
    odometer_end INTEGER,
    UNIQUE(month, plate)
);

-- =========================================================================
-- monthly_company_summary — one row per company per month (Financeiro)
-- =========================================================================

CREATE TABLE monthly_company_summary (
    id SERIAL PRIMARY KEY,
    month VARCHAR(7) NOT NULL,
    company VARCHAR(100) NOT NULL,
    total_rides INTEGER,
    km_loaded INTEGER,
    km_total INTEGER,
    revenue_toll DECIMAL(10,2),
    revenue_parking DECIMAL(10,2),
    revenue_surcharges DECIMAL(10,2),
    revenue_idle_time DECIMAL(10,2),
    revenue_transit DECIMAL(10,2),
    revenue_return DECIMAL(10,2),
    revenue_rides DECIMAL(10,2),
    revenue_subtotal DECIMAL(10,2),
    revenue_final DECIMAL(10,2),
    revenue_share DECIMAL(5,4),
    avg_ride_value DECIMAL(10,2),
    avg_km_loaded DECIMAL(10,2),
    UNIQUE(month, company)
);

-- =========================================================================
-- driver_schedule — one row per driver per month (Folga)
-- =========================================================================

CREATE TABLE driver_schedule (
    id SERIAL PRIMARY KEY,
    month VARCHAR(7) NOT NULL,
    driver VARCHAR(100) NOT NULL,
    days_off INTEGER DEFAULT 0,
    days_off_requested INTEGER DEFAULT 0,
    days_compensatory INTEGER DEFAULT 0,
    days_holiday INTEGER DEFAULT 0,
    days_vacation INTEGER DEFAULT 0,
    days_medical INTEGER DEFAULT 0,
    days_absence INTEGER DEFAULT 0,
    days_dispensed INTEGER DEFAULT 0,
    days_worked INTEGER,
    days_available INTEGER,
    days_salary INTEGER,
    UNIQUE(month, driver)
);

-- =========================================================================
-- rate_history — one row per company per month (rate snapshot)
-- =========================================================================

CREATE TABLE rate_history (
    id SERIAL PRIMARY KEY,
    month VARCHAR(7) NOT NULL,
    company VARCHAR(100) NOT NULL,
    km_rate DECIMAL(10,2),
    idle_rate DECIMAL(10,2),
    idle_courtesy_hours DECIMAL(5,2),
    transit_rate DECIMAL(10,2),
    return_rate DECIMAL(10,2),
    toll_tax_rate DECIMAL(5,4),
    invoice_tax_rate DECIMAL(5,4),
    night_surcharge_rate DECIMAL(5,4),
    holiday_surcharge_rate DECIMAL(5,4),
    sunday_surcharge_rate DECIMAL(5,4),
    status VARCHAR(20),
    UNIQUE(month, company)
);

COMMIT;
