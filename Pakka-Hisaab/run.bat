@echo off
setlocal EnableExtensions
cd /d "%~dp0"
set "LOG_DIR=%CD%\logs"
set "VENV_PY=%CD%\.venv\Scripts\python.exe"
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"
echo [%DATE% %TIME%] Pakka Hisaab launcher started > "%LOG_DIR%\setup.log"
echo [%DATE% %TIME%] Frontend is served by the FastAPI backend. > "%LOG_DIR%\frontend.log"

echo ==========================================
echo PAKKA HISAAB - ONE CLICK SETUP
echo ==========================================
echo Installing or verifying the local runtime. Please wait...
call build.bat >> "%LOG_DIR%\setup.log" 2>&1
if errorlevel 1 goto :failed
if not exist "%VENV_PY%" goto :failed

set "PORT="
for /f %%P in ('powershell -NoProfile -Command "$ports=8000..8010; foreach($port in $ports){if(-not (Get-NetTCPConnection -State Listen -LocalPort $port -ErrorAction SilentlyContinue)){Write-Output $port; break}}"') do set "PORT=%%P"
if not defined PORT goto :failed

echo [%DATE% %TIME%] Starting backend on port %PORT% >> "%LOG_DIR%\setup.log"
start "Pakka Hisaab Backend" /b "%VENV_PY%" -m uvicorn backend.app:app --host 127.0.0.1 --port %PORT% 1>> "%LOG_DIR%\backend.log" 2>> "%LOG_DIR%\error.log"
timeout /t 3 /nobreak >nul
powershell -NoProfile -Command "try { $r=Invoke-WebRequest 'http://127.0.0.1:%PORT%/api/health' -UseBasicParsing -TimeoutSec 5; if($r.StatusCode -eq 200){exit 0}; exit 1 } catch { exit 1 }"
if errorlevel 1 goto :failed

start "Pakka Hisaab" "http://127.0.0.1:%PORT%"
echo.
echo ==========================================
echo PAKKA HISAAB
echo ==========================================
echo Setup completed.
echo Application: http://127.0.0.1:%PORT%
echo Logs: .\logs\
echo.
echo Keep this window open while you use the app.
pause
exit /b 0

:failed
echo [%DATE% %TIME%] Startup failed. >> "%LOG_DIR%\error.log"
echo.
echo ==========================================
echo PAKKA HISAAB STARTUP FAILED
echo ==========================================
echo Check logs\setup.log, logs\backend.log, logs\frontend.log, and logs\error.log.
pause
exit /b 1
