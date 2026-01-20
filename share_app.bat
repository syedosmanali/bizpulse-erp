@echo off
echo.
echo ========================================
echo   BizPulse ERP - SHARING SOLUTION
echo ========================================
echo.
echo ✅ Your Flask server is RUNNING!
echo.
echo 🌐 LOCAL ACCESS:
echo    http://localhost:5000
echo.
echo 🌍 NETWORK ACCESS (for same WiFi users):
echo    http://192.168.1.50:5000
echo.
echo ========================================
echo   SHARE WITH ANYONE ON INTERNET:
echo ========================================
echo.
echo OPTION 1: Update Ngrok (Recommended)
echo   1. Download latest ngrok from: https://ngrok.com/download
echo   2. Replace your current ngrok.exe
echo   3. Run: ngrok http 5000
echo.
echo OPTION 2: Use LocalTunnel (Quick)
echo   1. Install: npm install -g localtunnel
echo   2. Run: npx localtunnel --port 5000
echo.
echo OPTION 3: Use Serveo (No install needed)
echo   1. Run: ssh -R 80:localhost:5000 serveo.net
echo.
echo ========================================
echo   CURRENT ISSUE:
echo ========================================
echo.
echo ❌ Your ngrok version (3.3.1) is too old
echo ❌ Minimum required: 3.19.0
echo ✅ Fixed ngrok config file (was version 3, now version 2)
echo.
echo 📱 For now, users on same WiFi can access:
echo    http://192.168.1.50:5000
echo.
echo Press any key to continue...
pause >nul