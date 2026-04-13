SELECT
    id,
    month,
    company,
    km_rate,
    idle_rate,
    idle_courtesy_hours,
    transit_rate,
    return_rate,
    invoice_tax_rate,
    night_surcharge_rate,
    holiday_surcharge_rate,
    sunday_surcharge_rate,
    status
FROM rate_history
ORDER BY month, company
