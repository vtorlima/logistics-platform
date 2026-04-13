Attribute VB_Name = "modConfig"
Option Explicit

' ============================================================================
' Sheet names — change here if sheets are renamed
' ============================================================================
Public Const SH_CONTROLE    As String = "Controle"
Public Const SH_PASSAGEIRO  As String = "Passageiro"
Public Const SH_EMPRESA     As String = "Empresa"
Public Const SH_COLABORADORES As String = "Colaboradores"
Public Const SH_FROTA       As String = "Frota"
Public Const SH_REGIAO      As String = "Região"
Public Const SH_CONFIG      As String = "Config"
Public Const SH_FOLHA       As String = "Folha"
Public Const SH_FINANCEIRO  As String = "Financeiro"
Public Const SH_FROTA_STATS As String = "Frota Stats"
Public Const SH_FOLGA       As String = "Folga"
Public Const SH_METAS       As String = "Metas"

' ============================================================================
' Controle sheet column indices (1-based)
' ============================================================================
Public Const COL_MES        As Integer = 1   ' A
Public Const COL_OS         As Integer = 2   ' B
Public Const COL_TIPO_NF    As Integer = 3   ' C
Public Const COL_DATA       As Integer = 4   ' D
Public Const COL_EMPRESA    As Integer = 5   ' E
Public Const COL_SOLICITANTE As Integer = 6  ' F
Public Const COL_CANAL      As Integer = 7   ' G
Public Const COL_AGENDADOR  As Integer = 8   ' H
Public Const COL_PLACA      As Integer = 9   ' I
Public Const COL_MOTORISTA  As Integer = 10  ' J
Public Const COL_KM_VAZIO   As Integer = 11  ' K
Public Const COL_KM_CHEIO   As Integer = 12  ' L
Public Const COL_KM_TOTAL   As Integer = 13  ' M
Public Const COL_KM_INICIAL As Integer = 14  ' N
Public Const COL_KM_FINAL   As Integer = 15  ' O
Public Const COL_H_SOL      As Integer = 16  ' P
Public Const COL_H_SAIDA    As Integer = 17  ' Q
Public Const COL_H_FINAL    As Integer = 18  ' R
Public Const COL_T_EMPRESA  As Integer = 19  ' S
Public Const COL_T_MOT      As Integer = 20  ' T
Public Const COL_ORIGEM     As Integer = 21  ' U
Public Const COL_DESTINO    As Integer = 22  ' V
Public Const COL_PASSAGEIRO As Integer = 23  ' W
Public Const COL_QTD_PASS   As Integer = 24  ' X
Public Const COL_TIPO_SERV  As Integer = 25  ' Y
Public Const COL_TIPO_VIAGEM As Integer = 26 ' Z
Public Const COL_PEDAGIO    As Integer = 27  ' AA
Public Const COL_ESTAC      As Integer = 28  ' AB
Public Const COL_HP         As Integer = 29  ' AC
Public Const COL_PASSAGEM   As Integer = 30  ' AD
Public Const COL_RETORNO    As Integer = 31  ' AE
Public Const COL_PRECO_CORR As Integer = 32  ' AF
Public Const COL_ADICIONAL  As Integer = 33  ' AG
Public Const COL_TOTAL      As Integer = 34  ' AH
Public Const COL_KM_NOT     As Integer = 35  ' AI
Public Const COL_KM_FER     As Integer = 36  ' AJ
Public Const COL_KM_DOM     As Integer = 37  ' AK
Public Const COL_PRECO_KM   As Integer = 38  ' AL
Public Const COL_CUSTO_PASS As Integer = 39  ' AM
Public Const COL_STATUS     As Integer = 40  ' AN

' ============================================================================
' Config sheet row indices for key-value pairs (column A = key, B = value)
' ============================================================================
Public Const CFG_FERIADO_1      As Integer = 2
Public Const CFG_FERIADO_2      As Integer = 3
Public Const CFG_FERIADO_3      As Integer = 4
Public Const CFG_FERIADO_4      As Integer = 5
Public Const CFG_HORA_NOT_INI   As Integer = 6
Public Const CFG_HORA_NOT_FIM   As Integer = 7
Public Const CFG_OS_INICIAL     As Integer = 8

' ============================================================================
' Empresa sheet column indices
' ============================================================================
Public Const EMP_NOME           As Integer = 1
Public Const EMP_KM_RATE        As Integer = 2
Public Const EMP_HP_RATE        As Integer = 3
Public Const EMP_HP_CORTESIA    As Integer = 4
Public Const EMP_TAX            As Integer = 5
Public Const EMP_NOTURNO        As Integer = 6
Public Const EMP_FERIADO        As Integer = 7
Public Const EMP_DOMINGO        As Integer = 8
Public Const EMP_PEDAGIO_TAX    As Integer = 9
Public Const EMP_RETORNO_RATE   As Integer = 10
Public Const EMP_TRANSIT_RATE   As Integer = 11

' ============================================================================
' Frota sheet column indices
' ============================================================================
Public Const FRO_PLACA          As Integer = 1
Public Const FRO_MODELO         As Integer = 2
Public Const FRO_ANO            As Integer = 3
Public Const FRO_COR            As Integer = 4
Public Const FRO_MOTORISTA      As Integer = 5

' ============================================================================
' Shared helpers
' ============================================================================

Public Function GetConfig(rowIndex As Integer) As Variant
    ' Read a value from the Config sheet by row index (column B)
    GetConfig = ThisWorkbook.Sheets(SH_CONFIG).Cells(rowIndex, 2).Value
End Function

Public Function GetLastRow(sheetName As String, col As Integer) As Long
    ' Return the last used row in a column on the given sheet
    Dim ws As Worksheet
    Set ws = ThisWorkbook.Sheets(sheetName)
    GetLastRow = ws.Cells(ws.Rows.Count, col).End(xlUp).Row
End Function

Public Function IsHoliday(d As Date) As Boolean
    ' Check if a date matches any of the 4 configured holidays
    Dim ws As Worksheet
    Set ws = ThisWorkbook.Sheets(SH_CONFIG)
    Dim i As Integer
    For i = CFG_FERIADO_1 To CFG_FERIADO_4
        If CDate(ws.Cells(i, 2).Value) = d Then
            IsHoliday = True
            Exit Function
        End If
    Next i
    IsHoliday = False
End Function

Public Function IsNightRide(departureTime As Date) As Boolean
    ' Night ride: departs at or after 22:00 or before 05:00
    Dim h As Integer
    h = Hour(departureTime)
    IsNightRide = (h >= 22 Or h < 5)
End Function

Public Function IsSunday(d As Date) As Boolean
    IsSunday = (Weekday(d, vbSunday) = 1)
End Function
