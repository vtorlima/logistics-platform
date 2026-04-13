# VBA Source Files

VBA modules exported from `VCTrans_Operacional.xlsm` for version control.
All files use UTF-8 encoding. Import order matters.

## Import order

1. `modConfig.bas`       — constants and shared helpers
2. `modBilling.bas`      — billing calculation functions
3. `modLookups.bas`      — dropdown population and lookup helpers
4. `modSummaries.bas`    — Folha / Financeiro / Frota Stats generators
5. `modExport.bas`       — monthly export to ETL-compatible XLSX
6. `ThisWorkbook.cls`    — workbook-level event handlers (Workbook_Open, etc.)
7. `Sheet_Controle.cls`  — Controle sheet event handlers (Worksheet_Change)

## Re-exporting after changes

In the VBA editor: File → Export File → save to `excel/vba/`
Do this for every module after making changes before committing.
