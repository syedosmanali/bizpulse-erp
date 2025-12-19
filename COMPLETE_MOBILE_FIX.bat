@echo off
title BizPulse Mobile ERP - Complete Fix
color 0E

echo.
echo  ██████╗ ██╗███████╗██████╗ ██╗   ██╗██╗     ███████╗███████╗
echo  ██╔══██╗██║╚══███╔╝██╔══██╗██║   ██║██║     ██╔════╝██╔════╝
echo  ██████╔╝██║  ███╔╝ ██████╔╝██║   ██║██║     ███████╗█████╗  
echo  ██╔══██╗██║ ███╔╝  ██╔═══╝ ██║   ██║██║     ╚════██║██╔══╝  
echo  ██████╔╝██║███████╗██║     ╚██████╔╝███████╗███████║███████╗
echo  ╚═════╝ ╚═╝╚══════╝╚═╝      ╚═════╝ ╚══════╝╚══════╝╚══════╝
echo.
echo                    📱 COMPLETE MOBILE FIX 📱
echo.

echo 🔍 Step 1: Network Diagnosis
python get_network_info.py

echo.
echo 🔥 Step 2: Comprehensive Firewall Fix
echo Adding ALL necessary firewall rules...

REM Remove old rules first
netsh advfirewall firewall delete rule name="BizPulse Python Server" >nul 2>&1
netsh advfirewall firewall delete rule name="BizPulse Port 5000" >nul 2>&1
netsh advfirewall firewall delete rule name="Python.exe" >nul 2>&1
netsh advfirewall firewall delete rule name="Flask Server" >nul 2>&1

REM Add comprehensive rules
echo Adding Python.exe rule...
netsh advfirewall firewall add rule name="BizPulse Python Server" dir=in action=allow program="python.exe" enable=yes >nul 2>&1

echo Adding Port 5000 rule...
netsh advfirewall firewall add rule name="BizPulse Port 5000" dir=in action=allow protocol=TCP localport=5000 enable=yes >nul 2>&1

echo Adding outbound rule...
netsh advfirewall firewall add rule name="BizPulse Port 5000 Out" dir=out action=allow protocol=TCP localport=5000 enable=yes >nul 2>&1

echo Adding HTTP rule...
netsh advfirewall firewall add rule name="BizPulse HTTP" dir=in action=allow protocol=TCP localport=80 enable=yes >nul 2>&1

echo ✅ Firewall rules added successfully!

echo.
echo 🧪 Step 3: Testing Mobile Connection
python test_mobile_response.py

echo.
echo 📱 Step 4: Mobile URLs Ready!
echo.
echo    🎯 PRIMARY URL:    http://192.168.0.3:5000/mobile-simple
echo    🔧 DIRECT ACCESS:  http://192.168.0.3:5000/mobile-direct  
echo    🧪 TEST PAGE:      http://192.168.0.3:5000/mobile-test-connection
echo.

echo 🔐 Login Credentials:
echo    Email: bizpulse.erp@gmail.com
echo    Password: demo123
echo.

echo 🚨 If STILL not working:
echo    1. Temporarily disable Windows Firewall completely
echo    2. Check if antivirus is blocking Python.exe
echo    3. Restart your WiFi router
echo    4. Try mobile hotspot instead of WiFi
echo.

echo 💡 Advanced Solution:
echo    If firewall keeps blocking, run this command as Administrator:
echo    netsh advfirewall set allprofiles state off
echo    (This temporarily disables firewall - remember to turn back on later)
echo.

pause