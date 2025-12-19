@echo off
echo ========================================
echo    BizPulse Mobile Access Setup
echo ========================================
echo.
echo Your IP Address: 192.168.0.3
echo.
echo Mobile URLs:
echo ✅ Main Website: http://192.168.0.3:5000
echo ✅ Mobile App: http://192.168.0.3:5000/mobile
echo ✅ Premium Mobile: http://192.168.0.3:5000/mobile-clean
echo.
echo Login Credentials:
echo Email: bizpulse.erp@gmail.com
echo Password: demo123
echo.
echo ========================================
echo Starting Server...
echo ========================================
echo.
python app.py
pause