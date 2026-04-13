# Excel Operational Tool

The working spreadsheet used by VCTrans dispatchers to log rides in real time.

## Setup

1. Open Excel and create a new macro-enabled workbook (`.xlsm`)
2. Create sheets in this order with these exact names:
   Controle, Passageiro, Empresa, Colaboradores, Frota, Região, Config,
   Folha, Financeiro, Frota Stats, Folga, Metas
3. Apply the column headers from `docs/controle-columns.md` to the Controle sheet
4. Open the VBA editor (Alt+F11)
5. Import all `.bas` and `.cls` files from `excel/vba/`
6. Populate the reference sheets (Empresa, Passageiro, Frota, Região, Config)
   by copying from a seed-generated XLSX or entering manually
7. Save as `VCTrans_Operacional.xlsm`

## VBA modules

See `excel/vba/` for all macro source files.

## Monthly workflow

1. At month start: run `Macro_NovoMes` to set the month header and reset counters
2. During the month: dispatchers log each ride in the Controle sheet
3. At month end: run `Macro_GerarResumos` to populate Folha, Financeiro, Frota Stats
4. Export: run `Macro_ExportarMes` to save a clean XLSX for the ETL pipeline
