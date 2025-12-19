@echo off
echo 🚀 Deploying Reports Module to BizPulse24.com
echo.

echo ✅ Checking files...
if exist "templates\reports_professional.html" (
    echo - reports_professional.html ✓
) else (
    echo - reports_professional.html ✗ MISSING
    pause
    exit
)

if exist "templates\reports_mobile.html" (
    echo - reports_mobile.html ✓
) else (
    echo - reports_mobile.html ✗ MISSING
    pause
    exit
)

if exist "app.py" (
    echo - app.py ✓
) else (
    echo - app.py ✗ MISSING
    pause
    exit
)

echo.
echo 📦 Creating deployment package...
mkdir reports_deployment_temp 2>nul

echo Copying files...
copy "templates\reports_professional.html" "reports_deployment_temp\"
copy "templates\reports_mobile.html" "reports_deployment_temp\"
copy "app.py" "reports_deployment_temp\"
copy "REPORTS_MODULE_COMPLETE.md" "reports_deployment_temp\"

echo.
echo 📋 Deployment Instructions:
echo.
echo 1. Upload these files to your server:
echo    - templates/reports_professional.html
echo    - templates/reports_mobile.html
echo    - app.py (updated version)
echo.
echo 2. Restart your server:
echo    sudo systemctl restart bizpulse
echo.
echo 3. Test URLs:
echo    https://bizpulse24.com/retail/reports
echo    https://bizpulse24.com/mobile/reports
echo.
echo 📁 Files ready in: reports_deployment_temp folder
echo.
pause