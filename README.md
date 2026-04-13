## Overview

This repository is an adapted version of a real data platform built for a transportation logistics operation.

The original system supports a taxi/logistics service handling corporate transportation (~2,400 rides/month), covering everything from operational data collection to analytics and reporting.

Because the real environment contains sensitive data (passengers, companies, financials, etc.), it cannot be shared publicly. This project was recreated to preserve the architecture, logic, and workflows, while using fully synthetic data.

## What this project is

A complete end-to-end data platform, including:

- A seed data generator that simulates realistic operational data
- A Python ETL pipeline that processes monthly Excel files
- A PostgreSQL data warehouse with normalized tables
- An Excel/VBA operational tool (data entry + automation)
- A Power BI dashboard layer for analytics

All components reflect how the real system works, but with fictional data that mimics the structure and behavior of the original spreadsheets.

## Why this exists

The goal of this repository is to:

- Demonstrate ETL + warehouse + BI integration
- Reproduce business logic and data modeling decisions
- Provide a portfolio-ready version of a deployed system

Instead of sharing real data, this project focuses on how the system works, not the data itself.

## Data note

- No real company data is included
- All datasets are generated using a custom seed generator
- Data follows realistic distributions (rides, pricing, time patterns, etc.)
- Referential integrity and business rules are preserved

This allows the system to behave like the real one without exposing sensitive information.

## Seed Data

Generates 3 months of realistic fake ride data (Jan–Mar 2026) as `.xlsx` workbooks,
matching the structure of the real operational spreadsheet. No real data is included.

### Setup

```bash
pip install openpyxl faker python-dotenv
```

### Run

```bash
python -m seed.main
```

Output files are written to `seed/output/` (gitignored):
- `VCTrans_2026-01.xlsx`
- `VCTrans_2026-02.xlsx`
- `VCTrans_2026-03.xlsx`

Each workbook contains: Controle, Passageiro, Empresa, Colaboradores, Frota, Região, Config.

## ETL Pipeline

Reads monthly XLSX workbooks and loads the data into PostgreSQL.

### Prerequisites

1. PostgreSQL running with the `vctrans` database created
2. Schema applied: `psql -U <user> -d vctrans -f database/schema.sql`
3. Dependencies installed: `pip install pandas psycopg2-binary python-dotenv openpyxl faker`
4. `.env` file configured (copy `.env.example` and fill in credentials)

### Run — single file

```bash
python -m etl.main seed/output/VCTrans_2026-01.xlsx
```

### Run — all files in a directory

```bash
python -m etl.main seed/output/
```

The pipeline is idempotent — re-running the same file overwrites existing rows,
it does not create duplicates.

### Output

```
Files to process: 3
  VCTrans_2026-01.xlsx
  VCTrans_2026-02.xlsx
  VCTrans_2026-03.xlsx

Connected to database.

=== 2026-01 (VCTrans_2026-01.xlsx) ===
  Reading: seed/output/VCTrans_2026-01.xlsx
  rides: 2400 rows upserted
  monthly_driver_summary: 25 rows upserted
  monthly_company_summary: 8 rows upserted
  monthly_vehicle_summary: 26 rows upserted
  driver_schedule: 25 rows upserted
  rate_history: 8 rows upserted
...

=== Summary ===
  rides: 7200 rows total
  monthly_driver_summary: 75 rows total
  monthly_company_summary: 24 rows total
  monthly_vehicle_summary: 78 rows total
  driver_schedule: 75 rows total
  rate_history: 24 rows total

ETL complete.
```
