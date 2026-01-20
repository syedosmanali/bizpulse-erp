@echo off
echo.
echo ========================================
echo   BizPulse ERP - Live Demo Server
echo ========================================
echo.

REM Start the Flask app in background
echo Starting BizPulse ERP server...
start /B python app.py

REM Wait a moment for server to start
timeout /t 5 /nobreak >nul

REM Start ngrok tunnel
echo.
echo Creating secure tunnel with ngrok...
echo.
echo ========================================
echo   SHARE THIS LINK WITH YOUR CLIENT:
echo ========================================
echo.

ngrok http 5000

echo.
echo Server stopped.
pause