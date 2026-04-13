# Power BI Dashboard

Interactive analytics for the VCTrans logistics platform.

## Prerequisites

- Power BI Desktop (free download from Microsoft)
- PostgreSQL ODBC driver installed (64-bit)
- `vctrans` database populated via the ETL pipeline (Phase 2)

## Setup

1. Open Power BI Desktop
2. Get Data → PostgreSQL database
3. Server: localhost, Database: vctrans, Mode: Import
4. For each file in `powerbi/queries/`, load as a separate query (name matches filename)
5. Set up relationships and Date table as described in `powerbi/README.md`
6. Save as `VCTrans_Dashboard.pbix` (gitignored)

## Refresh

After running the ETL pipeline with new data:
Home → Refresh (in Power BI Desktop)

## Pages

| Page | Description |
|------|-------------|
| Visão Geral | Executive summary — KPIs and monthly trends |
| Receita | Revenue breakdown by company |
| Motoristas | Driver performance and payroll |
| Frota | Vehicle utilization and ranking |
