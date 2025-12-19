@echo off
echo 🔍 BizPulse Mobile Network Diagnostic
echo =====================================
echo.

echo 📡 Current IP Configuration:
ipconfig | findstr "IPv4"
echo.

echo 🔥 Checking Firewall Rules:
netsh advfirewall firewall show rule name="Python" dir=in | findstr "Enabled\|Profiles"
echo.

echo 🌐 Checking if server is listening on port 5000:
netstat -an | findstr :5000
echo.

echo 📱 Testing localhost access:
curl -s -o nul -w "Status: %%{http_code}" http://localhost:5000/mobile-simple
echo.
echo.

echo 🖥️ Testing network IP access:
curl -s -o nul -w "Status: %%{http_code}" http://192.168.0.3:5000/mobile-simple
echo.
echo.

echo 📋 Mobile Access URLs:
echo    Primary: http://192.168.0.3:5000/mobile-simple
echo    Dashboard: http://192.168.0.3:5000/mobile-dashboard
echo    Main: http://192.168.0.3:5000
echo.

echo 💡 Troubleshooting Tips:
echo    1. Ensure mobile and laptop are on SAME WiFi
echo    2. Try different mobile browser
echo    3. Clear mobile browser cache
echo    4. Restart WiFi on mobile device
echo    5. Run MOBILE_FIREWALL_FIX.bat as Administrator
echo.

pause