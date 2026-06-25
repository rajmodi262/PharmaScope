@echo off
title EconoScope - Stop
echo Stopping EconoScope servers (ports 8900 and 5180)...
for %%P in (8900 5180) do (
  for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":%%P " ^| findstr LISTENING') do (
    echo   - killing PID %%a on port %%P
    taskkill /F /PID %%a >nul 2>&1
  )
)
echo Done.
timeout /t 2 /nobreak >nul
