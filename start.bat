@echo off
setlocal enabledelayedexpansion
title EconoScope - Pharma Intelligence Launcher
cd /d "%~dp0"

echo ===============================================
echo    EconoScope . Pharma Intelligence
echo    one-click launcher
echo ===============================================
echo.

REM ---------------------------------------------------------------
REM  1. Free the ports we use (8900 backend, 5180 frontend)
REM ---------------------------------------------------------------
echo [1/4] Freeing ports 8900 and 5180...
for %%P in (8900 5180) do (
  for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":%%P " ^| findstr LISTENING') do (
    echo       - killing PID %%a holding port %%P
    taskkill /F /PID %%a >nul 2>&1
  )
)
echo       ports clear.
echo.

REM ---------------------------------------------------------------
REM  2. Backend dependencies (FastAPI etc.)
REM ---------------------------------------------------------------
echo [2/4] Installing backend dependencies...
pushd backend
python -m pip install -q -r requirements.txt
if errorlevel 1 (
  echo       ! pip install failed - is Python on PATH?
  popd & goto :fail
)
popd
echo       backend ready.
echo.

REM ---------------------------------------------------------------
REM  3. Frontend dependencies (React / Vite)
REM ---------------------------------------------------------------
echo [3/4] Installing frontend dependencies...
pushd frontend
call npm install --silent
if errorlevel 1 (
  echo       ! npm install failed - is Node.js on PATH?
  popd & goto :fail
)
popd
echo       frontend ready.
echo.

REM ---------------------------------------------------------------
REM  4. Launch both servers in their own windows + open browser
REM ---------------------------------------------------------------
echo [4/4] Starting servers...
start "EconoScope Backend"  cmd /k "cd /d %~dp0backend  && python -m uvicorn app.main:app --port 8900"
start "EconoScope Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

echo       waiting for the dev server to boot...
REM poll the frontend port for up to ~20s, then open the browser
set /a tries=0
:waitloop
timeout /t 2 /nobreak >nul
set /a tries+=1
netstat -aon | findstr ":5180 " | findstr LISTENING >nul 2>&1
if errorlevel 1 (
  if !tries! lss 10 goto :waitloop
)
start "" http://localhost:5180

echo.
echo ===============================================
echo    EconoScope is starting in your browser:
echo    http://localhost:5180
echo.
echo    Two server windows opened (Backend + Frontend).
echo    Close them - or run stop.bat - to shut down.
echo ===============================================
echo.
echo Press any key to close this launcher (servers keep running)...
pause >nul
exit /b 0

:fail
echo.
echo Launch aborted. See the error above.
pause >nul
exit /b 1
