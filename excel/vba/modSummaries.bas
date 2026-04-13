Attribute VB_Name = "modSummaries"
Option Explicit

' ============================================================================
' Macro_GerarResumos (public entry point)
' Rebuilds Folha, Financeiro, and Frota Stats from Controle data.
' Assign this to a button on the Folha or Financeiro sheet.
' ============================================================================
Public Sub Macro_GerarResumos()
    Dim currentMonth As String
    currentMonth = InputBox("Informe o mês (AAAA-MM):", "Gerar Resumos", Format(Date, "YYYY-MM"))
    If currentMonth = "" Then Exit Sub

    Application.ScreenUpdating = False
    Application.Calculation = xlCalculationManual

    On Error GoTo Cleanup
    Call BuildFolha(currentMonth)
    Call BuildFinanceiro(currentMonth)
    Call BuildFrotaStats(currentMonth)

    MsgBox "Resumos gerados para " & currentMonth & " com sucesso!", vbInformation

Cleanup:
    Application.ScreenUpdating = True
    Application.Calculation = xlCalculationAutomatic
    If Err.Number <> 0 Then
        MsgBox "Erro ao gerar resumos: " & Err.Description, vbCritical
    End If
End Sub

' ============================================================================
' BuildFolha
' Aggregates driver payroll from Controle into the Folha sheet.
' ============================================================================
Private Sub BuildFolha(targetMonth As String)
    Dim wsSrc As Worksheet: Set wsSrc = ThisWorkbook.Sheets(SH_CONTROLE)
    Dim wsDst As Worksheet: Set wsDst = ThisWorkbook.Sheets(SH_FOLHA)

    ' Clear existing data (keep header row)
    Dim lastDst As Long
    lastDst = GetLastRow(SH_FOLHA, 1)
    If lastDst > 1 Then wsDst.Rows("2:" & lastDst).Delete

    ' Write headers
    Dim headers As Variant
    headers = Array("Mês", "Motorista", "Dias Trabalhados", "Corridas", _
                    "Km Total", "Km Cheio", "Km Noturno", "Km Feriado", "Km Domingo", _
                    "Pag. Km", "Pag. HP", "Adic. Noturno", "Adic. Feriado", "Adic. Domingo", _
                    "Total Adicional", "Total Pagar", "Meta Km", "Meta Atingida", "Eficiência")
    Dim h As Integer
    For h = 0 To UBound(headers)
        wsDst.Cells(1, h + 1).Value = headers(h)
    Next h

    ' --- Aggregate from Controle ---
    ' Use a Collection of driver names to track unique drivers
    Dim srcLast As Long: srcLast = GetLastRow(SH_CONTROLE, COL_OS)

    ' Collect unique drivers for this month
    Dim driverList As New Collection
    Dim driverSet As Object: Set driverSet = CreateObject("Scripting.Dictionary")

    Dim i As Long
    For i = 2 To srcLast
        If wsSrc.Cells(i, COL_MES).Value = targetMonth Then
            Dim drv As String: drv = wsSrc.Cells(i, COL_MOTORISTA).Value
            If drv <> "" And Not driverSet.Exists(drv) Then
                driverSet.Add drv, drv
            End If
        End If
    Next i

    ' For each driver, sum their data
    Dim dstRow As Long: dstRow = 2
    Dim drvKey As Variant
    For Each drvKey In driverSet.Keys
        Dim driverName As String: driverName = CStr(drvKey)

        Dim rides As Long: rides = 0
        Dim kmTotal As Long: kmTotal = 0
        Dim kmCheio As Long: kmCheio = 0
        Dim kmNot As Long: kmNot = 0
        Dim kmFer As Long: kmFer = 0
        Dim kmDom As Long: kmDom = 0
        Dim sumHP As Double: sumHP = 0
        Dim uniqueDates As Object: Set uniqueDates = CreateObject("Scripting.Dictionary")

        For i = 2 To srcLast
            If wsSrc.Cells(i, COL_MES).Value = targetMonth And _
               wsSrc.Cells(i, COL_MOTORISTA).Value = driverName Then
                rides = rides + 1
                kmTotal = kmTotal + Val(wsSrc.Cells(i, COL_KM_TOTAL).Value)
                kmCheio = kmCheio + Val(wsSrc.Cells(i, COL_KM_CHEIO).Value)
                kmNot = kmNot + Val(wsSrc.Cells(i, COL_KM_NOT).Value)
                kmFer = kmFer + Val(wsSrc.Cells(i, COL_KM_FER).Value)
                kmDom = kmDom + Val(wsSrc.Cells(i, COL_KM_DOM).Value)
                sumHP = sumHP + Val(wsSrc.Cells(i, COL_HP).Value)
                Dim rDate As String: rDate = CStr(wsSrc.Cells(i, COL_DATA).Value)
                If Not uniqueDates.Exists(rDate) Then uniqueDates.Add rDate, 1
            End If
        Next i

        Dim daysWorked As Long: daysWorked = uniqueDates.Count
        Const KM_RATE_DRV As Double = 1.8   ' R$/km for driver
        Const HP_RATE_DRV As Double = 40#   ' R$/h for driver
        Const NOITE_DRV As Double = 0.15
        Const FER_DRV As Double = 0.4
        Const DOM_DRV As Double = 0.4
        Const KM_GOAL As Long = 4000

        Dim payKm As Double:    payKm = Round(kmCheio * KM_RATE_DRV, 2)
        Dim payHP As Double:    payHP = Round(sumHP * (HP_RATE_DRV / 85#), 2)
        Dim adicNot As Double:  adicNot = Round(kmNot * KM_RATE_DRV * NOITE_DRV, 2)
        Dim adicFer As Double:  adicFer = Round(kmFer * KM_RATE_DRV * FER_DRV, 2)
        Dim adicDom As Double:  adicDom = Round(kmDom * KM_RATE_DRV * DOM_DRV, 2)
        Dim adicTotal As Double: adicTotal = Round(adicNot + adicFer + adicDom, 2)
        Dim payTotal As Double: payTotal = Round(payKm + payHP + adicTotal, 2)
        Dim efficiency As Double
        If kmTotal > 0 Then efficiency = Round(kmCheio / kmTotal, 4) Else efficiency = 0

        Dim row As Variant
        row = Array(targetMonth, driverName, daysWorked, rides, _
                    kmTotal, kmCheio, kmNot, kmFer, kmDom, _
                    payKm, payHP, adicNot, adicFer, adicDom, _
                    adicTotal, payTotal, KM_GOAL, _
                    IIf(kmTotal >= KM_GOAL, "Sim", "Não"), efficiency)

        Dim c As Integer
        For c = 0 To UBound(row)
            wsDst.Cells(dstRow, c + 1).Value = row(c)
        Next c
        dstRow = dstRow + 1
    Next drvKey
End Sub

' ============================================================================
' BuildFinanceiro
' Aggregates company revenue from Controle into the Financeiro sheet.
' ============================================================================
Private Sub BuildFinanceiro(targetMonth As String)
    Dim wsSrc As Worksheet: Set wsSrc = ThisWorkbook.Sheets(SH_CONTROLE)
    Dim wsDst As Worksheet: Set wsDst = ThisWorkbook.Sheets(SH_FINANCEIRO)

    Dim lastDst As Long: lastDst = GetLastRow(SH_FINANCEIRO, 1)
    If lastDst > 1 Then wsDst.Rows("2:" & lastDst).Delete

    Dim headers As Variant
    headers = Array("Mês", "Empresa", "Corridas", "Km Cheio", "Km Total", _
                    "Pedágio", "Estacionamento", "Adicional", "Hora Parada", "Passagem", _
                    "Retorno", "Corridas (R$)", "Subtotal", "Total Final", "Part. (%)", _
                    "Ticket Médio", "Km Médio")
    Dim h As Integer
    For h = 0 To UBound(headers)
        wsDst.Cells(1, h + 1).Value = headers(h)
    Next h

    Dim srcLast As Long: srcLast = GetLastRow(SH_CONTROLE, COL_OS)

    Dim compSet As Object: Set compSet = CreateObject("Scripting.Dictionary")
    Dim i As Long
    For i = 2 To srcLast
        If wsSrc.Cells(i, COL_MES).Value = targetMonth Then
            Dim comp As String: comp = wsSrc.Cells(i, COL_EMPRESA).Value
            If comp <> "" And Not compSet.Exists(comp) Then compSet.Add comp, comp
        End If
    Next i

    ' First pass: compute subtotals
    Dim totalAll As Double: totalAll = 0

    ' Use arrays for each company (index matches compSet order)
    Dim compKeys As Variant: compKeys = compSet.Keys
    Dim numComp As Integer: numComp = compSet.Count
    ReDim ridesArr(numComp - 1) As Long
    ReDim revArr(numComp - 1, 10) As Double  ' indices: toll,park,surch,hp,trans,ret,ride,sub,fin
    ReDim kmCArr(numComp - 1) As Long
    ReDim kmTArr(numComp - 1) As Long

    For i = 2 To srcLast
        If wsSrc.Cells(i, COL_MES).Value = targetMonth Then
            Dim cname As String: cname = wsSrc.Cells(i, COL_EMPRESA).Value
            Dim idx As Integer
            Dim k As Integer
            For k = 0 To numComp - 1
                If compKeys(k) = cname Then idx = k: Exit For
            Next k

            ridesArr(idx) = ridesArr(idx) + 1
            kmCArr(idx) = kmCArr(idx) + Val(wsSrc.Cells(i, COL_KM_CHEIO).Value)
            kmTArr(idx) = kmTArr(idx) + Val(wsSrc.Cells(i, COL_KM_TOTAL).Value)
            revArr(idx, 0) = revArr(idx, 0) + Val(wsSrc.Cells(i, COL_PEDAGIO).Value)
            revArr(idx, 1) = revArr(idx, 1) + Val(wsSrc.Cells(i, COL_ESTAC).Value)
            revArr(idx, 2) = revArr(idx, 2) + Val(wsSrc.Cells(i, COL_ADICIONAL).Value)
            revArr(idx, 3) = revArr(idx, 3) + Val(wsSrc.Cells(i, COL_HP).Value)
            revArr(idx, 4) = revArr(idx, 4) + Val(wsSrc.Cells(i, COL_PASSAGEM).Value)
            revArr(idx, 5) = revArr(idx, 5) + Val(wsSrc.Cells(i, COL_RETORNO).Value)
            revArr(idx, 6) = revArr(idx, 6) + Val(wsSrc.Cells(i, COL_PRECO_CORR).Value)
            Dim rowTotal As Double: rowTotal = Val(wsSrc.Cells(i, COL_TOTAL).Value)
            totalAll = totalAll + rowTotal
        End If
    Next i

    ' Write rows
    Dim dstRow As Long: dstRow = 2
    For k = 0 To numComp - 1
        Dim cKey As String: cKey = CStr(compKeys(k))
        Dim taxRate As Double: taxRate = GetCompanyRate(cKey, EMP_TAX)
        Dim subtotal As Double
        subtotal = Round(revArr(k,0)+revArr(k,1)+revArr(k,2)+revArr(k,3)+_
                         revArr(k,4)+revArr(k,5)+revArr(k,6), 2)
        Dim finalRev As Double: finalRev = Round(subtotal * (1 + taxRate), 2)
        Dim share As Double
        If totalAll > 0 Then share = Round(finalRev / totalAll, 4) Else share = 0
        Dim avgTicket As Double
        If ridesArr(k) > 0 Then avgTicket = Round(finalRev / ridesArr(k), 2)
        Dim avgKm As Double
        If ridesArr(k) > 0 Then avgKm = Round(kmCArr(k) / ridesArr(k), 2)

        Dim outRow As Variant
        outRow = Array(targetMonth, cKey, ridesArr(k), kmCArr(k), kmTArr(k), _
                       Round(revArr(k,0),2), Round(revArr(k,1),2), Round(revArr(k,2),2), _
                       Round(revArr(k,3),2), Round(revArr(k,4),2), Round(revArr(k,5),2), _
                       Round(revArr(k,6),2), subtotal, finalRev, share, avgTicket, avgKm)

        Dim c As Integer
        For c = 0 To UBound(outRow)
            wsDst.Cells(dstRow, c + 1).Value = outRow(c)
        Next c
        dstRow = dstRow + 1
    Next k
End Sub

' ============================================================================
' BuildFrotaStats
' Aggregates vehicle performance from Controle into the Frota Stats sheet.
' ============================================================================
Private Sub BuildFrotaStats(targetMonth As String)
    Dim wsSrc As Worksheet: Set wsSrc = ThisWorkbook.Sheets(SH_CONTROLE)
    Dim wsDst As Worksheet: Set wsDst = ThisWorkbook.Sheets(SH_FROTA_STATS)

    Dim lastDst As Long: lastDst = GetLastRow(SH_FROTA_STATS, 1)
    If lastDst > 1 Then wsDst.Rows("2:" & lastDst).Delete

    Dim headers As Variant
    headers = Array("Mês", "Placa", "Motorista", "Dias Trab.", "Corridas", _
                    "Km Total", "Km Cheio", "Km/Dia", "Corridas/Dia", "Ranking")
    Dim h As Integer
    For h = 0 To UBound(headers)
        wsDst.Cells(1, h + 1).Value = headers(h)
    Next h

    Dim srcLast As Long: srcLast = GetLastRow(SH_CONTROLE, COL_OS)
    Dim vehSet As Object: Set vehSet = CreateObject("Scripting.Dictionary")
    Dim i As Long
    For i = 2 To srcLast
        If wsSrc.Cells(i, COL_MES).Value = targetMonth Then
            Dim pl As String: pl = wsSrc.Cells(i, COL_PLACA).Value
            If pl <> "" And Not vehSet.Exists(pl) Then vehSet.Add pl, pl
        End If
    Next i

    Dim vKeys As Variant: vKeys = vehSet.Keys
    Dim numV As Integer: numV = vehSet.Count
    ReDim vRides(numV - 1) As Long
    ReDim vKmT(numV - 1) As Long
    ReDim vKmC(numV - 1) As Long
    ReDim vDrv(numV - 1) As String
    Dim vDates() As Object
    ReDim vDates(numV - 1)
    Dim j As Integer
    For j = 0 To numV - 1
        Set vDates(j) = CreateObject("Scripting.Dictionary")
    Next j

    For i = 2 To srcLast
        If wsSrc.Cells(i, COL_MES).Value = targetMonth Then
            Dim vpl As String: vpl = wsSrc.Cells(i, COL_PLACA).Value
            Dim vidx As Integer
            For j = 0 To numV - 1
                If vKeys(j) = vpl Then vidx = j: Exit For
            Next j
            vRides(vidx) = vRides(vidx) + 1
            vKmT(vidx) = vKmT(vidx) + Val(wsSrc.Cells(i, COL_KM_TOTAL).Value)
            vKmC(vidx) = vKmC(vidx) + Val(wsSrc.Cells(i, COL_KM_CHEIO).Value)
            vDrv(vidx) = wsSrc.Cells(i, COL_MOTORISTA).Value
            Dim vd As String: vd = CStr(wsSrc.Cells(i, COL_DATA).Value)
            If Not vDates(vidx).Exists(vd) Then vDates(vidx).Add vd, 1
        End If
    Next i

    ' Sort by km total descending (bubble sort — small dataset)
    Dim swapped As Boolean
    Do
        swapped = False
        For j = 0 To numV - 2
            If vKmT(j) < vKmT(j + 1) Then
                Dim tmpL As Long: tmpL = vKmT(j): vKmT(j) = vKmT(j+1): vKmT(j+1) = tmpL
                tmpL = vKmC(j): vKmC(j) = vKmC(j+1): vKmC(j+1) = tmpL
                tmpL = vRides(j): vRides(j) = vRides(j+1): vRides(j+1) = tmpL
                Dim tmpS As String: tmpS = vKeys(j): vKeys(j) = vKeys(j+1): vKeys(j+1) = tmpS
                tmpS = vDrv(j): vDrv(j) = vDrv(j+1): vDrv(j+1) = tmpS
                Dim tmpD As Object: Set tmpD = vDates(j): Set vDates(j) = vDates(j+1): Set vDates(j+1) = tmpD
                swapped = True
            End If
        Next j
    Loop While swapped

    For j = 0 To numV - 1
        Dim days As Long: days = vDates(j).Count
        Dim kmDay As Double: If days > 0 Then kmDay = Round(vKmT(j) / days, 2)
        Dim ridesDay As Double: If days > 0 Then ridesDay = Round(vRides(j) / days, 2)

        Dim outRow As Variant
        outRow = Array(targetMonth, vKeys(j), vDrv(j), days, vRides(j), _
                       vKmT(j), vKmC(j), kmDay, ridesDay, j + 1)
        Dim c As Integer
        For c = 0 To UBound(outRow)
            wsDst.Cells(j + 2, c + 1).Value = outRow(c)
        Next c
    Next j
End Sub
