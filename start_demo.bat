@echo off
echo.
echo ========================================
echo   BizPulse ERP - Live Demo Server
echo ========================================
echo.
echo 🎯 Creating shareable link for your client...
echo ✅ Includes automatic stock alerts system
echo 🌐 Accessible from anywhere in the world
echo.

REM Start the Flask app in background
echo 🚀 Starting BizPulse ERP server...
start /B python app.py

REM Wait for server to start
echo ⏳ Waiting for server to start...
timeout /t 8 /nobreak >nul

REM Start ngrok tunnel
echo.
echo 🌐 Creating secure tunnel with ngrok...
echo.
echo ========================================
echo   SHARE THESE LINKS WITH YOUR CLIENT:
echo ========================================
echo.

.\ngrok.exe http 5000