@echo off
echo ========================================
echo Testing BizPulse Mobile Route
echo ========================================
echo.

echo Step 1: Starting Flask Server...
start cmd /k "python app.py"

echo.
echo Waiting 5 seconds for server to start...
timeout /t 5 /nobreak > nul

echo.
echo Step 2: Testing local mobile route...
echo Opening: http://localhost:5000/mobile
start http://localhost:5000/mobile

echo.
echo Step 3: Testing production mobile route...
echo Opening: https://bizpulse24.com/mobile
start https://bizpulse24.com/mobile

echo.
echo ========================================
echo Check if both URLs work!
echo ========================================
echo.
echo If LOCAL works but PRODUCTION doesn't:
echo - You need to deploy latest code to production
echo - Or use ngrok for testing
echo.
pause
