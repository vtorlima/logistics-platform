VERSION 1.0 CLASS
BEGIN
  MultiUse = -1
END
Attribute VB_Name = "Sheet_Controle"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = True
Attribute VB_Exposed = True
Option Explicit

' ============================================================================
' Worksheet_Change
' Fires whenever a cell in Controle is edited.
' Handles: auto-fill driver from plate, auto-fill OS, trigger billing.
' ============================================================================
Private Sub Worksheet_Change(ByVal Target As Range)
    ' Ignore changes outside the data rows
    If Target.Row < 2 Then Exit Sub
    ' Ignore multi-cell pastes (too expensive to process cell by cell)
    If Target.Cells.Count > 10 Then Exit Sub

    Application.EnableEvents = False
    On Error GoTo Cleanup

    Dim col As Integer
    col = Target.Column
    Dim rowNum As Long
    rowNum = Target.Row

    ' --- Plate entered → auto-fill driver ---
    If col = COL_PLACA Then
        Dim plate As String
        plate = Me.Cells(rowNum, COL_PLACA).Value
        If plate <> "" Then
            Me.Cells(rowNum, COL_MOTORISTA).Value = GetDriverByPlate(plate)
        End If
    End If

    ' --- Company changed → update passenger dropdown ---
    If col = COL_EMPRESA Then
        Dim company As String
        company = Me.Cells(rowNum, COL_EMPRESA).Value
        ' Update Solicitante dropdown (col F)
        Call PopulatePassengerDropdown(Me.Cells(rowNum, COL_SOLICITANTE), company)
        ' Update Passageiro Principal dropdown (col W)
        Call PopulatePassengerDropdown(Me.Cells(rowNum, COL_PASSAGEIRO), company)
        ' Clear billing when company changes (rates may differ)
        Call ClearBillingCols(rowNum)
    End If

    ' --- Data row started (OS auto-fill when Date is entered) ---
    If col = COL_DATA Then
        Dim currentOS As Variant
        currentOS = Me.Cells(rowNum, COL_OS).Value
        If IsEmpty(currentOS) Or currentOS = "" Then
            Me.Cells(rowNum, COL_OS).Value = GetNextOS()
        End If
    End If

    ' --- Trigger billing recalc when any billing-relevant column changes ---
    Dim billingTriggerCols As Variant
    billingTriggerCols = Array(COL_KM_CHEIO, COL_KM_VAZIO, COL_DATA, COL_H_SAIDA, _
                               COL_TIPO_VIAGEM, COL_ORIGEM, COL_DESTINO)
    Dim trigger As Variant
    For Each trigger In billingTriggerCols
        If col = trigger Then
            Call FillBillingForRow(Me, rowNum)
            Exit For
        End If
    Next trigger

Cleanup:
    Application.EnableEvents = True
    If Err.Number <> 0 Then
        MsgBox "Erro ao processar linha " & rowNum & ": " & Err.Description, vbExclamation
    End If
End Sub

' ============================================================================
' ClearBillingCols
' Clears all auto-calculated billing values for a row.
' Called when company changes (rates may be different).
' ============================================================================
Private Sub ClearBillingCols(rowNum As Long)
    Dim billingCols As Variant
    billingCols = Array(COL_HP, COL_RETORNO, COL_PRECO_CORR, COL_ADICIONAL, _
                        COL_KM_NOT, COL_KM_FER, COL_KM_DOM, COL_TIPO_NF, COL_MES)
    Dim c As Variant
    For Each c In billingCols
        Me.Cells(rowNum, c).Value = ""
    Next c
End Sub
