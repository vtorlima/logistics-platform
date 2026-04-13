SELECT
    id,
    month,
    driver,
    days_off,
    days_off_requested,
    days_compensatory,
    days_holiday,
    days_vacation,
    days_medical,
    days_absence,
    days_dispensed,
    days_worked,
    days_available,
    days_salary
FROM driver_schedule
ORDER BY month, driver
