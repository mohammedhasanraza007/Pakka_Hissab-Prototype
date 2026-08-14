@echo off
setlocal EnableExtensions
cd /d "%~dp0"
set "PYTHON_VERSION=3.11.9"
set "PYTHON_ROOT=%LOCALAPPDATA%\PakkaHisaab\python311"
set "PYTHON_EXE=%PYTHON_ROOT%\python.exe"
set "PYTHON_COMMAND="
set "PYTHON_INSTALLER=%TEMP%\python-%PYTHON_VERSION%-amd64.exe"

echo [1/4] Checking fixed Python %PYTHON_VERSION%...
if not exist "%PYTHON_EXE%" (
  where py >nul 2>nul
  if not errorlevel 1 (
    py -3.11 -c "import sys; assert sys.version_info[:3] == (3,11,9)" >nul 2>nul
    if not errorlevel 1 set "PYTHON_COMMAND=py -3.11"
  )
)
if exist "%PYTHON_EXE%" set "PYTHON_COMMAND=%PYTHON_EXE%"
if not defined PYTHON_COMMAND (
  echo Downloading the official Python %PYTHON_VERSION% installer...
  powershell -NoProfile -ExecutionPolicy Bypass -Command "$ErrorActionPreference='Stop'; try { Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/%PYTHON_VERSION%/python-%PYTHON_VERSION%-amd64.exe' -OutFile '%PYTHON_INSTALLER%' } catch { exit 1 }"
  if errorlevel 1 set "PYTHON_DOWNLOAD_FAILED=1"
  if not exist "%PYTHON_INSTALLER%" set "PYTHON_DOWNLOAD_FAILED=1"
  if defined PYTHON_DOWNLOAD_FAILED echo Setup failed: Python installer download did not complete.
  if defined PYTHON_DOWNLOAD_FAILED exit /b 1
  "%PYTHON_INSTALLER%" /quiet InstallAllUsers=0 PrependPath=0 Include_test=0 TargetDir="%PYTHON_ROOT%"
  if exist "%PYTHON_EXE%" set "PYTHON_COMMAND=%PYTHON_EXE%"
)
if not defined PYTHON_COMMAND echo Setup failed: Python %PYTHON_VERSION% is unavailable.
if not defined PYTHON_COMMAND exit /b 1

echo [2/4] Creating isolated environment...
if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" -c "import sys; assert sys.version_info[:3] == (3,11,9)" >nul 2>nul
  if errorlevel 1 (
    echo Existing environment is not Python %PYTHON_VERSION%; rebuilding it...
    rmdir /s /q ".venv"
  )
)
if not exist ".venv\Scripts\python.exe" (
  %PYTHON_COMMAND% -m venv .venv
  if errorlevel 1 exit /b 1
)
set "VENV_PY=.venv\Scripts\python.exe"
echo [3/4] Installing pinned app and multilingual TTS dependencies...
"%VENV_PY%" -m pip install --upgrade pip
"%VENV_PY%" -m pip install -r requirements.txt
if errorlevel 1 exit /b 1
echo [4/4] Verifying the database and app import...
"%VENV_PY%" -c "from backend.db import ensure_database; c=ensure_database(); print('SQLite ready:', c.execute('select count(*) from products').fetchone()[0], 'products'); c.close()"
if errorlevel 1 exit /b 1
echo.
echo Build complete. Run run.bat to open Pakka Hisaab.
exit /b 0
