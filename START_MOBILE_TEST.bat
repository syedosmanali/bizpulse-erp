@echo off
title BizPulse Mobile Connection Test
color 0A

echo.
echo  ██████╗ ██╗███████╗██████╗ ██╗   ██╗██╗     ███████╗███████╗
echo  ██╔══██╗██║╚══███╔╝██╔══██╗██║   ██║██║     ██╔════╝██╔════╝
echo  ██████╔╝██║  ███╔╝ ██████╔╝██║   ██║██║     ███████╗█████╗  
echo  ██╔══██╗██║ ███╔╝  ██╔═══╝ ██║   ██║██║     ╚════██║██╔══╝  
echo  ██████╔╝██║███████╗██║     ╚██████╔╝███████╗███████║███████╗
echo  ╚═════╝ ╚═╝╚══════╝╚═╝      ╚═════╝ ╚══════╝╚══════╝╚══════╝
echo.
echo                    📱 MOBILE CONNECTION TEST 📱
echo.

echo 🔍 Step 1: Checking server status...
python test_mobile_connection.py

echo.
echo 🔥 Step 2: Fixing Windows Firewall...
echo Adding firewall rules for mobile access...

netsh advfirewall firewall delete rule name="BizPulse Python Server" >nul 2>&1
netsh advfirewall firewall delete rule name="BizPulse Port 5000" >nul 2>&1

netsh advfirewall firewall add rule name="BizPulse Python Server" dir=in action=allow program="python.exe" enable=yes >nul 2>&1
netsh advfirewall firewall add rule name="BizPulse Port 5000" dir=in action=allow protocol=TCP localport=5000 >nul 2>&1

echo ✅ Firewall rules added!

echo.
echo 📱 Step 3: Test URLs for your mobile:
echo.
echo    🎯 SIMPLE TEST:  http://192.168.0.3:5000/mobile-test-connection
echo    🚀 FULL APP:     http://192.168.0.3:5000/mobile-simple
echo.

echo 🔧 Troubleshooting:
echo    1. Make sure mobile and PC are on same WiFi
echo    2. If still not working, try disabling Windows Firewall temporarily
echo    3. Check if antivirus is blocking the connection
echo.

echo 📞 Need help? Check MOBILE_CONNECTION_FIX.md for detailed guide
echo.
pause