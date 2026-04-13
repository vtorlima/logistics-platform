VERSION 1.0 CLASS
BEGIN
  MultiUse = -1
END
Attribute VB_Name = "ThisWorkbook"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = True
Attribute VB_Exposed = True
Option Explicit

' ============================================================================
' Workbook_Open
' Protects reference sheets (green tabs) against accidental edits.
' Leaves Controle and summary sheets unprotected for normal use.
' ============================================================================
Private Sub Workbook_Open()
    Dim protectedSheets As Variant
    protectedSheets = Array(SH_PASSAGEIRO, SH_EMPRESA, SH_COLABORADORES, _
                            SH_FROTA, SH_REGIAO, SH_CONFIG)

    Dim shName As Variant
    For Each shName In protectedSheets
        On Error Resume Next
        ThisWorkbook.Sheets(CStr(shName)).Protect Password:="vctrans2026", _
            UserInterfaceOnly:=True   ' Allows VBA to write, blocks manual edits
        On Error GoTo 0
    Next shName
End Sub

' ============================================================================
' Workbook_BeforeClose
' Warns if there are unsaved rides (Controle has rows without Status = "Concluído")
' and offers to run summaries before closing.
' ============================================================================
Private Sub Workbook_BeforeClose(Cancel As Boolean)
    Dim ws As Worksheet
    Set ws = ThisWorkbook.Sheets(SH_CONTROLE)
    Dim lastRow As Long: lastRow = GetLastRow(SH_CONTROLE, COL_OS)

    Dim pendingCount As Long: pendingCount = 0
    Dim i As Long
    For i = 2 To lastRow
        Dim st As String: st = ws.Cells(i, COL_STATUS).Value
        If st = "Pendente" Or st = "" Then
            pendingCount = pendingCount + 1
        End If
    Next i

    If pendingCount > 0 Then
        Dim resp As VbMsgBoxResult
        resp = MsgBox(pendingCount & " corrida(s) com status pendente." & vbCrLf & _
                      "Deseja revisar antes de fechar?", _
                      vbYesNo + vbExclamation, "Corridas Pendentes")
        If resp = vbYes Then
            Cancel = True  ' Abort close so user can review
        End If
    End If
End Sub
