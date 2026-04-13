Attribute VB_Name = "modBilling"
Option Explicit

' ============================================================================
' CalcRidePrice
' Base ride price = km_loaded * km_rate
' ============================================================================
Public Function CalcRidePrice(kmLoaded As Double, kmRate As Double) As Double
    CalcRidePrice = Round(kmLoaded * kmRate, 2)
End Function

' ============================================================================
' CalcSurcharges
' Returns total surcharge amount based on which type of ride it is.
' Priority: Holiday > Sunday > Night (mutually exclusive buckets).
' ============================================================================
Public Function CalcSurcharges( _
    kmLoaded As Double, _
    kmRate As Double, _
    rideDate As Date, _
    departureTime As Date, _
    nightRate As Double, _
    holidayRate As Double, _
    sundayRate As Double _
) As Double
    Dim surcharge As Double
    surcharge = 0

    If IsHoliday(rideDate) Then
        surcharge = Round(kmLoaded * kmRate * holidayRate, 2)
    ElseIf IsSunday(rideDate) Then
        surcharge = Round(kmLoaded * kmRate * sundayRate, 2)
    ElseIf IsNightRide(departureTime) Then
        surcharge = Round(kmLoaded * kmRate * nightRate, 2)
    End If

    CalcSurcharges = surcharge
End Function

' ============================================================================
' CalcIdleTime (Hora Parada)
' Only billed after the courtesy threshold. Returns R$ amount.
' idleHours: actual idle time in hours (decimal)
' courtesyHours: free window in hours (e.g. 0.5 = 30 min free)
' hpRate: company R$/hour idle rate
' ============================================================================
Public Function CalcIdleTime( _
    idleHours As Double, _
    courtesyHours As Double, _
    hpRate As Double _
) As Double
    Dim billable As Double
    billable = idleHours - courtesyHours
    If billable <= 0 Then
        CalcIdleTime = 0
    Else
        CalcIdleTime = Round(billable * hpRate, 2)
    End If
End Function

' ============================================================================
' CalcReturn
' Return trip billing = ride_price * return_rate
' ============================================================================
Public Function CalcReturn(ridePrice As Double, returnRate As Double) As Double
    CalcReturn = Round(ridePrice * returnRate, 2)
End Function

' ============================================================================
' CalcTotal
' Sum of all billing components.
' ============================================================================
Public Function CalcTotal( _
    toll As Double, _
    parking As Double, _
    idleTime As Double, _
    transitFare As Double, _
    returnBilling As Double, _
    ridePrice As Double, _
    surcharges As Double _
) As Double
    CalcTotal = Round(toll + parking + idleTime + transitFare + returnBilling + ridePrice + surcharges, 2)
End Function

' ============================================================================
' FillBillingForRow
' Master function: reads KM and company from a Controle row and fills all
' billing columns (AC, AE, AF, AG, AI, AJ, AK).
' Call this after KM columns and date/time are filled.
' ============================================================================
Public Sub FillBillingForRow(ws As Worksheet, rowNum As Long)
    Dim company As String
    company = ws.Cells(rowNum, COL_EMPRESA).Value
    If company = "" Then Exit Sub

    Dim kmLoaded As Double
    Dim kmVazio As Double
    kmLoaded = Val(ws.Cells(rowNum, COL_KM_CHEIO).Value)
    kmVazio = Val(ws.Cells(rowNum, COL_KM_VAZIO).Value)
    If kmLoaded = 0 Then Exit Sub

    ' Read rates from Empresa sheet
    Dim kmRate As Double:       kmRate = GetCompanyRate(company, EMP_KM_RATE)
    Dim hpRate As Double:       hpRate = GetCompanyRate(company, EMP_HP_RATE)
    Dim hpCortesia As Double:   hpCortesia = GetCompanyRate(company, EMP_HP_CORTESIA)
    Dim nightRate As Double:    nightRate = GetCompanyRate(company, EMP_NOTURNO)
    Dim holidayRate As Double:  holidayRate = GetCompanyRate(company, EMP_FERIADO)
    Dim sundayRate As Double:   sundayRate = GetCompanyRate(company, EMP_DOMINGO)
    Dim returnRate As Double:   returnRate = GetCompanyRate(company, EMP_RETORNO_RATE)

    ' Date and time
    Dim rideDate As Date
    Dim departTime As Date
    On Error Resume Next
    rideDate = CDate(ws.Cells(rowNum, COL_DATA).Value)
    departTime = CDate(ws.Cells(rowNum, COL_H_SAIDA).Value)
    On Error GoTo 0

    ' Ride price
    Dim ridePrice As Double
    ridePrice = CalcRidePrice(kmLoaded, kmRate)
    ws.Cells(rowNum, COL_PRECO_CORR).Value = ridePrice

    ' Surcharges
    Dim surcharges As Double
    surcharges = CalcSurcharges(kmLoaded, kmRate, rideDate, departTime, nightRate, holidayRate, sundayRate)
    ws.Cells(rowNum, COL_ADICIONAL).Value = surcharges

    ' Set KM surcharge buckets (AI, AJ, AK)
    If IsHoliday(rideDate) Then
        ws.Cells(rowNum, COL_KM_NOT).Value = 0
        ws.Cells(rowNum, COL_KM_FER).Value = kmLoaded
        ws.Cells(rowNum, COL_KM_DOM).Value = 0
    ElseIf IsSunday(rideDate) Then
        ws.Cells(rowNum, COL_KM_NOT).Value = 0
        ws.Cells(rowNum, COL_KM_FER).Value = 0
        ws.Cells(rowNum, COL_KM_DOM).Value = kmLoaded
    ElseIf IsNightRide(departTime) Then
        ws.Cells(rowNum, COL_KM_NOT).Value = kmLoaded
        ws.Cells(rowNum, COL_KM_FER).Value = 0
        ws.Cells(rowNum, COL_KM_DOM).Value = 0
    Else
        ws.Cells(rowNum, COL_KM_NOT).Value = 0
        ws.Cells(rowNum, COL_KM_FER).Value = 0
        ws.Cells(rowNum, COL_KM_DOM).Value = 0
    End If

    ' Return trip (AE) — only if Tipo Viagem is "Volta" or "Ida e Volta"
    Dim tripType As String
    tripType = ws.Cells(rowNum, COL_TIPO_VIAGEM).Value
    Dim returnBilling As Double
    If tripType = "Volta" Or tripType = "Ida e Volta" Then
        returnBilling = CalcReturn(ridePrice, returnRate)
    Else
        returnBilling = 0
    End If
    ws.Cells(rowNum, COL_RETORNO).Value = returnBilling

    ' NF type based on route (C column auto-fill)
    Dim origin As String:      origin = ws.Cells(rowNum, COL_ORIGEM).Value
    Dim destination As String: destination = ws.Cells(rowNum, COL_DESTINO).Value
    If origin <> "" And destination <> "" Then
        ws.Cells(rowNum, COL_TIPO_NF).Value = GetRouteType(origin, destination)
    End If

    ' Month (A column auto-fill)
    ws.Cells(rowNum, COL_MES).Value = Format(rideDate, "YYYY-MM")
End Sub
