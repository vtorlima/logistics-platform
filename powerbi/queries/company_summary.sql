SELECT
    id,
    month,
    company,
    total_rides,
    km_loaded,
    km_total,
    revenue_toll,
    revenue_parking,
    revenue_surcharges,
    revenue_idle_time,
    revenue_transit,
    revenue_return,
    revenue_rides,
    revenue_subtotal,
    revenue_final,
    revenue_share,
    avg_ride_value,
    avg_km_loaded
FROM monthly_company_summary
ORDER BY month, revenue_final DESC
