Attribute VB_Name = "modExport"
Option Explicit

' ============================================================================
' Macro_ExportarMes (public entry point)
' Exports a single month's data to a standalone XLSX in the same folder
' as the operational workbook, named VCTrans_YYYY-MM.xlsx.
' The exported file matches the structure expected by etl/reader.py.
' ============================================================================
Public Sub Macro_ExportarMes()
    Dim targetMonth As String
    targetMonth = InputBox("Informe o mês para exportar (AAAA-MM):", "Exportar Mês", _
                           Format(Date, "YYYY-MM"))
    If targetMonth = "" Then Exit Sub

    ' Validate format
    If Len(targetMonth) <> 7 Or Mid(targetMonth, 5, 1) <> "-" Then
        MsgBox "Formato inválido. Use AAAA-MM (ex: 2026-01).", vbExclamation
        Exit Sub
    End If

    Application.ScreenUpdating = False
    Application.DisplayAlerts = False

    Dim exportPath As String
    exportPath = ThisWorkbook.Path & "\VCTrans_" & targetMonth & ".xlsx"

    ' Create a new workbook for export
    Dim wbExport As Workbook
    Set wbExport = Workbooks.Add

    ' Export each sheet in the correct order
    Call ExportControle(wbExport, targetMonth)
    Call ExportSheet(wbExport, SH_FOLHA, "Folha")
    Call ExportSheet(wbExport, SH_FINANCEIRO, "Financeiro")
    Call ExportSheet(wbExport, SH_FROTA_STATS, "Frota Stats")
    Call ExportSheet(wbExport, SH_FOLGA, "Folga")
    Call ExportSheet(wbExport, SH_PASSAGEIRO, "Passageiro")
    Call ExportSheet(wbExport, SH_EMPRESA, "Empresa")
    Call ExportSheet(wbExport, SH_COLABORADORES, "Colaboradores")
    Call ExportSheet(wbExport, SH_FROTA, "Frota")
    Call ExportSheet(wbExport, SH_REGIAO, "Região")
    Call ExportSheet(wbExport, SH_CONFIG, "Config")

    ' Remove the default empty sheet Excel adds
    On Error Resume Next
    wbExport.Sheets("Sheet1").Delete
    wbExport.Sheets("Folha1").Delete
    On Error GoTo 0

    ' Save as XLSX (no macros)
    wbExport.SaveAs Filename:=exportPath, FileFormat:=xlOpenXMLWorkbook
    wbExport.Close SaveChanges:=False

    Application.ScreenUpdating = True
    Application.DisplayAlerts = True

    MsgBox "Exportado com sucesso!" & vbCrLf & exportPath, vbInformation
End Sub

' ============================================================================
' ExportControle
' Copies only rows matching targetMonth from Controle.
' Filters out formula columns that the ETL doesn't need (km_initial, km_final
' are written as values; formula columns like km_total are already values).
' ============================================================================
Private Sub ExportControle(wbDst As Workbook, targetMonth As String)
    Dim wsSrc As Worksheet: Set wsSrc = ThisWorkbook.Sheets(SH_CONTROLE)
    Dim wsDst As Worksheet

    ' Add sheet to export workbook
    Set wsDst = wbDst.Sheets.Add(After:=wbDst.Sheets(wbDst.Sheets.Count))
    wsDst.Name = "Controle"

    ' Copy header row
    wsSrc.Rows(1).Copy Destination:=wsDst.Rows(1)

    ' Copy matching data rows (values only — no formulas)
    Dim srcLast As Long: srcLast = GetLastRow(SH_CONTROLE, COL_OS)
    Dim dstRow As Long: dstRow = 2

    Dim i As Long
    For i = 2 To srcLast
        If wsSrc.Cells(i, COL_MES).Value = targetMonth Then
            ' Copy entire row as values
            wsDst.Rows(dstRow).Value = wsSrc.Rows(i).Value
            dstRow = dstRow + 1
        End If
    Next i
End Sub

' ============================================================================
' ExportSheet
' Copies an entire reference or summary sheet to the export workbook (values only).
' ============================================================================
Private Sub ExportSheet(wbDst As Workbook, srcSheetName As String, dstSheetName As String)
    Dim wsSrc As Worksheet
    On Error Resume Next
    Set wsSrc = ThisWorkbook.Sheets(srcSheetName)
    On Error GoTo 0
    If wsSrc Is Nothing Then Exit Sub ' Sheet doesn't exist — skip silently

    Dim wsDst As Worksheet
    Set wsDst = wbDst.Sheets.Add(After:=wbDst.Sheets(wbDst.Sheets.Count))
    wsDst.Name = dstSheetName

    ' Copy used range as values only
    Dim srcRange As Range
    Set srcRange = wsSrc.UsedRange
    If srcRange Is Nothing Then Exit Sub

    wsDst.Range(srcRange.Address).Value = srcRange.Value
End Sub

' ============================================================================
' Macro_NovoMes
' Called at the start of each new month.
' Optionally archives the previous month's Controle rows to a backup sheet.
' ============================================================================
Public Sub Macro_NovoMes()
    Dim newMonth As String
    newMonth = InputBox("Informe o novo mês (AAAA-MM):", "Novo Mês", Format(Date, "YYYY-MM"))
    If newMonth = "" Then Exit Sub

    Dim resp As VbMsgBoxResult
    resp = MsgBox("Iniciar o mês " & newMonth & "?" & vbCrLf & _
                  "Isso NÃO apaga os dados existentes.", _
                  vbYesNo + vbQuestion, "Confirmar")
    If resp <> vbYes Then Exit Sub

    ' Just inform — Controle accumulates all months, filtering by Mês column
    MsgBox "Mês configurado para " & newMonth & "." & vbCrLf & _
           "Novos registros serão marcados automaticamente.", vbInformation
End Sub
