@echo off
echo 🔥 Adding Windows Firewall Rule for Mobile Access...
echo.

REM Add firewall rule for Python Flask server
netsh advfirewall firewall add rule name="BizPulse Mobile ERP" dir=in action=allow protocol=TCP localport=5000 profile=any

echo.
echo ✅ Firewall rule added successfully!
echo 📱 Mobile devices can now access: http://192.168.0.3:5000
echo.
echo 🔧 If still not working, try:
echo    1. Restart WiFi on mobile
echo    2. Check if mobile and laptop are on same WiFi network
echo    3. Try: http://192.168.0.3:5000/mobile-simple
echo.
pause