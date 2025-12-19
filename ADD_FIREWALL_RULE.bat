@echo off
echo 🔥 Adding Windows Firewall Rules for Mobile Access...
echo.

echo Adding rule for port 5000...
netsh advfirewall firewall add rule name="BizPulse Port 5000" dir=in action=allow protocol=TCP localport=5000 profile=any

echo Adding rule for port 8080...
netsh advfirewall firewall add rule name="BizPulse Port 8080" dir=in action=allow protocol=TCP localport=8080 profile=any

echo Adding rule for Python...
netsh advfirewall firewall add rule name="Python Flask Server" dir=in action=allow program="python.exe" profile=any

echo.
echo ✅ Firewall rules added!
echo.
echo 📱 Now try these URLs on mobile:
echo    http://192.168.0.3:8080/mobile-simple
echo    http://192.168.0.3:5000/mobile-simple
echo.
pause