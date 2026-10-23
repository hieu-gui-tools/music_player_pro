@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"
title Music Player Pro

:: 1. Check if uv is available in PATH
where uv >nul 2>&1
if %errorlevel% equ 0 (
    uv run music-player-pro
    goto :end
)

:: 2. Check uv in default user directory
if exist "%USERPROFILE%\.local\bin\uv.exe" (
    "%USERPROFILE%\.local\bin\uv.exe" run music-player-pro
    goto :end
)

if exist "%USERPROFILE%\.cargo\bin\uv.exe" (
    "%USERPROFILE%\.cargo\bin\uv.exe" run music-player-pro
    goto :end
)

:: 3. Direct execution via virtual environment
if exist ".venv\Scripts\python.exe" (
    set PYTHONPATH=%~dp0src
    ".venv\Scripts\python.exe" -m music_player_pro.main
    goto :end
)

echo.
echo ==============================================================
echo [ERROR] Khong tim thay 'uv' hoac moi truong '.venv'!
echo Vui long kiem tra lai hoac chay 'uv sync' truoc khi su dung.
echo ==============================================================
echo.
pause

:end
endlocal
