@echo off
echo 🔥 BizPulse Mobile Firewall Fix
echo ================================
echo.
echo This script will add firewall rules to allow mobile access
echo.
pause

echo 📝 Adding firewall rule for Python.exe...
netsh advfirewall firewall add rule name="BizPulse Python Server" dir=in action=allow program="%~dp0.venv\Scripts\python.exe" enable=yes
if %errorlevel% equ 0 (
    echo ✅ Python.exe firewall rule added successfully
) else (
    echo ⚠️ Could not add Python.exe rule, trying alternative...
    netsh advfirewall firewall add rule name="BizPulse Python Server" dir=in action=allow program="python.exe" enable=yes
)

echo.
echo 📝 Adding firewall rule for Port 5000...
netsh advfirewall firewall add rule name="BizPulse Port 5000" dir=in action=allow protocol=TCP localport=5000
if %errorlevel% equ 0 (
    echo ✅ Port 5000 firewall rule added successfully
) else (
    echo ❌ Failed to add port rule
)

echo.
echo 🔍 Testing connection...
echo Try this URL on your mobile: http://192.168.0.3:5000/mobile-test-connection
echo.
echo 📱 If it still doesn't work:
echo 1. Make sure both devices are on same WiFi
echo 2. Try temporarily disabling Windows Firewall
echo 3. Check your router settings
echo.
pause