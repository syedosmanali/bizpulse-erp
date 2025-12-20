@echo off
echo ========================================
echo   SALES MODULE DATE FILTER FIX
echo ========================================
echo.

echo [1/4] Stopping any running servers...
taskkill /F /IM python.exe 2>nul
timeout /t 2 >nul

echo.
echo [2/4] Testing database queries...
python debug_date_filters.py
if errorlevel 1 (
    echo ERROR: Database test failed!
    pause
    exit /b 1
)

echo.
echo [3/4] Starting Flask server...
start "BizPulse Server" python app.py
timeout /t 5 >nul

echo.
echo [4/4] Testing API endpoints...
python test_api_direct.py
if errorlevel 1 (
    echo ERROR: API test failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo   DEPLOYMENT SUCCESSFUL!
echo ========================================
echo.
echo Server is running at:
echo   - Desktop: http://localhost:5000
echo   - Sales Module: http://localhost:5000/retail/sales
echo.
echo Press any key to open Sales Module in browser...
pause >nul
start http://localhost:5000/retail/sales

echo.
echo Server is running in background.
echo Close this window when done testing.
pause