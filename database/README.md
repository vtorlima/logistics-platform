# Database Setup

## Prerequisites

- PostgreSQL 14+ installed and running

## Create the database

```bash
createdb vctrans
```

Or via psql:

```sql
CREATE DATABASE vctrans;
```

## Run the schema

```bash
psql -U <your_user> -d vctrans -f database/schema.sql
```

This creates 6 tables:

| Table | Description |
|-------|-------------|
| `rides` | Core ride transactions (~2,400 rows/month) |
| `monthly_driver_summary` | Driver payroll per month |
| `monthly_vehicle_summary` | Vehicle stats per month |
| `monthly_company_summary` | Company revenue per month |
| `driver_schedule` | Driver day-off patterns per month |
| `rate_history` | Company billing rate snapshots |

## Connection string

The ETL pipeline reads the connection from a `.env` file in the project root:

```
DATABASE_URL=postgresql://user:password@localhost:5432/vctrans
```

See `.env.example` (created in commit 2.4).

## Reset

To drop and recreate all tables:

```bash
psql -U <your_user> -d vctrans -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
psql -U <your_user> -d vctrans -f database/schema.sql
```

## Table relationship overview

```
rate_history ──────┐
                   │ month + company
                   ▼
rides ◄──── monthly_company_summary
  │                ▲
  │ month + driver │ month + company
  ▼                │
monthly_driver_summary     (all joined via string columns, no FKs)
driver_schedule
                   │
  │ month + plate  │
  ▼
monthly_vehicle_summary
```

All tables share `month VARCHAR(7)` as the partitioning dimension. Queries across months
use `WHERE month = '2026-01'` or `WHERE month IN (...)`.
