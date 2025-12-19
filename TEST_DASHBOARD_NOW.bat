@echo off
echo ================================================
echo DASHBOARD REAL-TIME DATA TEST
echo ================================================
echo.

echo Step 1: Checking current data...
python check_data_now.py
echo.

echo Step 2: Testing dashboard stats API...
python test_dashboard_stats.py
echo.

echo ================================================
echo INSTRUCTIONS:
echo.
echo 1. Server restart karo (naya code load hoga):
echo    - Current server ko Ctrl+C se stop karo
echo    - START_SERVER_CLEAN.bat run karo
echo.
echo 2. Dashboard kholo:
echo    http://localhost:5000/retail/dashboard
echo.
echo 3. Billing module se bill banao:
echo    http://localhost:5000/retail/billing
echo.
echo 4. Dashboard refresh karo - Stats update honge!
echo.
echo ================================================
pause
