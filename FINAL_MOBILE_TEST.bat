@echo off
title Final Mobile ERP Test
color 0A

echo.
echo ===============================================
echo           FINAL MOBILE ERP TEST
echo ===============================================
echo.

echo 🔍 Step 1: Testing Server Response
curl -s -I http://192.168.0.3:5000/mobile-simple | findstr "200 OK"
if %errorlevel% equ 0 (
    echo ✅ Server responding correctly
) else (
    echo ❌ Server not responding
    pause
    exit
)

echo.
echo 🔍 Step 2: Testing Content Size
for /f %%i in ('curl -s http://192.168.0.3:5000/mobile-simple ^| find /c /v ""') do set lines=%%i
echo Content lines: %lines%
if %lines% gtr 100 (
    echo ✅ Content loading properly
) else (
    echo ❌ Content too small
)

echo.
echo 🔍 Step 3: Testing Mobile Detection
curl -s -H "User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)" http://192.168.0.3:5000/ | findstr "mobile-simple" >nul
if %errorlevel% equ 0 (
    echo ✅ Mobile detection working
) else (
    echo ⚠️ Mobile detection may have issues
)

echo.
echo 📱 MOBILE URLS TO TEST:
echo.
echo 🎯 MAIN ERP:     http://192.168.0.3:5000/mobile-simple
echo 🧪 SIMPLE TEST:  http://192.168.0.3:5000/mobile-ultra-test  
echo 🚀 INSTANT:      http://192.168.0.3:5000/mobile-instant
echo.

echo 🔐 LOGIN CREDENTIALS:
echo Email: bizpulse.erp@gmail.com
echo Password: demo123
echo.

echo 💡 TROUBLESHOOTING TIPS:
echo 1. If loading screen stuck - wait 3 seconds or click "Skip Loading"
echo 2. Clear browser cache completely
echo 3. Try incognito/private mode
echo 4. Try different browser (Chrome, Safari, Firefox)
echo 5. Make sure same WiFi network
echo.

echo 🎯 START WITH: http://192.168.0.3:5000/mobile-ultra-test
echo    This is the simplest test - if this works, connection is fine
echo.

pause