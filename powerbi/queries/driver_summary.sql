SELECT
    id,
    month,
    driver,
    days_worked,
    total_rides,
    km_total,
    km_loaded,
    km_night,
    km_holiday,
    km_sunday,
    pay_km,
    pay_idle_time,
    surcharge_night,
    surcharge_holiday,
    surcharge_sunday,
    surcharge_total,
    pay_total,
    km_goal,
    goal_met,
    efficiency
FROM monthly_driver_summary
ORDER BY month, pay_total DESC
