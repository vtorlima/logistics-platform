SELECT
    id,
    month,
    plate,
    model,
    assigned_driver,
    fleet_rank,
    working_days,
    km_per_day,
    rides_per_day,
    total_rides,
    km_loaded,
    km_total,
    km_unaccounted,
    odometer_start,
    odometer_end
FROM monthly_vehicle_summary
ORDER BY month, fleet_rank
