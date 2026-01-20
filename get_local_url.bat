@echo off
echo.
echo ========================================
echo   BizPulse ERP - Local Access
echo ========================================
echo.
echo Your BizPulse ERP is running locally at:
echo.
echo 🌐 LOCAL URL: http://localhost:5000
echo.
echo ========================================
echo   TO SHARE WITH OTHERS:
echo ========================================
echo.
echo Option 1: Use your local IP address
echo   - Find your IP: ipconfig
echo   - Share: http://YOUR_IP:5000
echo.
echo Option 2: Update ngrok (recommended)
echo   - Download latest from: https://ngrok.com/download
echo   - Replace old ngrok.exe with new version
echo   - Run: ngrok http 5000
echo.
echo Option 3: Use other tunneling services
echo   - LocalTunnel: npx localtunnel --port 5000
echo   - Serveo: ssh -R 80:localhost:5000 serveo.net
echo.
echo ========================================
echo   CURRENT STATUS:
echo ========================================
echo.
echo ✅ Flask Server: RUNNING on port 5000
echo ❌ Ngrok: VERSION TOO OLD (needs update)
echo.
echo Press any key to continue...
pause >nul