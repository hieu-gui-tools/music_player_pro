Option Explicit

Dim objShell, objFSO, scriptDir, cmd

On Error Resume Next

Set objShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")

' 1. Thiet lap thu muc lam viec la thu muc chua du an
scriptDir = objFSO.GetParentFolderName(WScript.ScriptFullName)
objShell.CurrentDirectory = scriptDir

' 2. Khoi chay thong qua run.cmd o che do an (0 = vbHide, True = giu session chay em ai)
cmd = "cmd.exe /c """ & scriptDir & "\run.cmd"""

objShell.Run cmd, 0, True

If Err.Number <> 0 Then
    MsgBox "Không thể khởi động Music Player Pro!" & vbCrLf & vbCrLf & _
           "Chi tiết lỗi: " & Err.Description & vbCrLf & _
           "Lệnh chạy: " & cmd, 16, "Music Player Pro - Lỗi Khởi Động"
    Err.Clear
End If
