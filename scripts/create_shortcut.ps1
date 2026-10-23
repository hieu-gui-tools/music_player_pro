# PowerShell script to create Desktop Shortcut for Music Player Pro
$ScriptDir = $PSScriptRoot
if (-not $ScriptDir) {
    $ScriptDir = (Get-Location).Path
}
$ProjectDir = (Get-Item $ScriptDir).Parent.FullName
if (-not (Test-Path (Join-Path $ProjectDir "run.vbs"))) {
    $ProjectDir = (Get-Location).Path
}

$WshShell = New-Object -ComObject WScript.Shell
$Desktop = [System.Environment]::GetFolderPath('Desktop')
$ShortcutPath = Join-Path $Desktop "Music Player Pro.lnk"

$VbsPath = Join-Path $ProjectDir "run.vbs"
$IconPath = Join-Path $ProjectDir "assets\icon.ico"

$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = "wscript.exe"
$Shortcut.Arguments = "`"$VbsPath`""
$Shortcut.WorkingDirectory = $ProjectDir
$Shortcut.IconLocation = "$IconPath, 0"
$Shortcut.Description = "Music Player Pro - Trình phát nhạc chuyên nghiệp"
$Shortcut.Save()

Write-Host "Desktop shortcut created successfully at: $ShortcutPath"
Write-Host "Target: wscript.exe `"$VbsPath`""
Write-Host "WorkingDirectory: $ProjectDir"
Write-Host "Icon: $IconPath"
