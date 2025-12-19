@echo off
echo 🧪 Testing Profile Persistence Fix
echo ================================
echo.
echo Starting Flask server...
start /B python app.py
echo.
echo Waiting for server to start...
timeout /t 3 /nobreak > nul
echo.
echo Running profile persistence test...
python test_profile_persistence_fix.py
echo.
echo ✅ Profile persistence fix test completed!
echo.
echo 📋 Manual Test Steps:
echo 1. Go to: http://localhost:5000/login
echo 2. Login with your credentials  
echo 3. Go to Profile page
echo 4. Edit and save profile details
echo 5. Refresh the page - details should remain!
echo.
pause