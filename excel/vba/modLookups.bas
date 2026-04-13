Attribute VB_Name = "modLookups"
Option Explicit

' ============================================================================
' GetCompanyRate
' Returns a rate value from the Empresa sheet for a given company name and column index.
' ============================================================================
Public Function GetCompanyRate(companyName As String, rateCol As Integer) As Double
    Dim ws As Worksheet
    Set ws = ThisWorkbook.Sheets(SH_EMPRESA)
    Dim lastRow As Long
    lastRow = GetLastRow(SH_EMPRESA, EMP_NOME)

    Dim i As Long
    For i = 2 To lastRow
        If ws.Cells(i, EMP_NOME).Value = companyName Then
            GetCompanyRate = CDbl(ws.Cells(i, rateCol).Value)
            Exit Function
        End If
    Next i
    GetCompanyRate = 0
End Function

' ============================================================================
' GetDriverByPlate
' Looks up the assigned driver for a given vehicle plate from the Frota sheet.
' ============================================================================
Public Function GetDriverByPlate(plate As String) As String
    Dim ws As Worksheet
    Set ws = ThisWorkbook.Sheets(SH_FROTA)
    Dim lastRow As Long
    lastRow = GetLastRow(SH_FROTA, FRO_PLACA)

    Dim i As Long
    For i = 2 To lastRow
        If ws.Cells(i, FRO_PLACA).Value = plate Then
            GetDriverByPlate = ws.Cells(i, FRO_MOTORISTA).Value
            Exit Function
        End If
    Next i
    GetDriverByPlate = ""
End Function

' ============================================================================
' GetNextOS
' Returns the next available OS number by scanning the Controle sheet.
' ============================================================================
Public Function GetNextOS() As Long
    Dim ws As Worksheet
    Set ws = ThisWorkbook.Sheets(SH_CONTROLE)
    Dim lastRow As Long
    lastRow = GetLastRow(SH_CONTROLE, COL_OS)

    If lastRow < 2 Then
        ' No rides yet — use the starting OS from Config
        GetNextOS = CLng(GetConfig(CFG_OS_INICIAL))
        Exit Function
    End If

    Dim maxOS As Long
    maxOS = 0
    Dim i As Long
    For i = 2 To lastRow
        Dim v As Variant
        v = ws.Cells(i, COL_OS).Value
        If IsNumeric(v) And CLng(v) > maxOS Then
            maxOS = CLng(v)
        End If
    Next i
    GetNextOS = maxOS + 1
End Function

' ============================================================================
' PopulatePassengerDropdown
' Fills a validation dropdown in the Solicitante and Passageiro cells
' with passengers filtered to the selected company.
' Called from Sheet_Controle.cls on company cell change.
' ============================================================================
Public Sub PopulatePassengerDropdown(targetCell As Range, companyName As String)
    Dim ws As Worksheet
    Set ws = ThisWorkbook.Sheets(SH_PASSAGEIRO)
    Dim lastRow As Long
    lastRow = GetLastRow(SH_PASSAGEIRO, 1)

    ' Collect matching passenger names
    Dim names() As String
    ReDim names(0)
    Dim count As Integer
    count = 0

    Dim i As Long
    For i = 2 To lastRow
        If ws.Cells(i, 2).Value = companyName And ws.Cells(i, 3).Value = "Ativo" Then
            ReDim Preserve names(count)
            names(count) = ws.Cells(i, 1).Value
            count = count + 1
        End If
    Next i

    If count = 0 Then
        ' No passengers for this company — clear validation
        targetCell.Validation.Delete
        Exit Sub
    End If

    ' Apply as dropdown validation
    Dim listStr As String
    listStr = Join(names, ",")

    With targetCell.Validation
        .Delete
        .Add Type:=xlValidateList, AlertStyle:=xlValidAlertStop, _
             Operator:=xlBetween, Formula1:=listStr
        .ShowInput = False
        .ShowError = False
    End With
End Sub

' ============================================================================
' GetRouteType
' Returns 'MUNIC' or 'INTER' for a given origin-destination pair from Região sheet.
' ============================================================================
Public Function GetRouteType(origin As String, destination As String) As String
    Dim ws As Worksheet
    Set ws = ThisWorkbook.Sheets(SH_REGIAO)
    Dim lastRow As Long
    lastRow = GetLastRow(SH_REGIAO, 1)

    Dim i As Long
    For i = 2 To lastRow
        If ws.Cells(i, 1).Value = origin And ws.Cells(i, 2).Value = destination Then
            GetRouteType = ws.Cells(i, 4).Value
            Exit Function
        End If
    Next i
    GetRouteType = "MUNIC" ' Default fallback
End Function

' ============================================================================
' IsNumeric
' Helper to check if a value is numeric
' ============================================================================
Private Function IsNumeric(v As Variant) As Boolean
    On Error Resume Next
    IsNumeric = IsNumeric(CDbl(v))
    On Error GoTo 0
End Function
