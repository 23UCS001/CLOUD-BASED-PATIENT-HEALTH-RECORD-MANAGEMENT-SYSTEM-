@echo off
title CareNest Health Records
cd /d "%~dp0"
echo ==========================================
echo        CareNest Health Records
echo ==========================================
echo.
where py >nul 2>nul
if %errorlevel%==0 (
  set PYTHON=py
) else (
  set PYTHON=python
)
echo Checking Python...
%PYTHON% --version
if errorlevel 1 (
  echo.
  echo Python was not found. Install Python 3.10 or newer from https://www.python.org/downloads/
  echo During installation, tick "Add Python to PATH".
  pause
  exit /b 1
)
echo.
echo Installing required package (internet is needed the first time)...
%PYTHON% -m pip install -r requirements.txt
if errorlevel 1 (
  echo.
  echo Package installation failed. Check your internet connection and try again.
  pause
  exit /b 1
)
echo.
echo Starting CareNest...
echo When the server starts, open http://127.0.0.1:5000 in your browser.
echo Keep this black window open while using the website.
echo Press Ctrl+C in this window to stop.
echo.
start "" cmd /c "timeout /t 3 >nul & start http://127.0.0.1:5000"
%PYTHON% app.py
pause
