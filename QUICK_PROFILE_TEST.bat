@echo off
echo 🧪 Quick Profile API Test
echo ========================
echo.
echo Starting Flask server with debug logs...
echo.
echo 📋 What to do:
echo 1. Server will start with debug logging
echo 2. Go to: http://localhost:5000/login
echo 3. Login with your credentials
echo 4. Go to Profile page
echo 5. Edit and save profile details
echo 6. Check console for DEBUG messages
echo 7. Refresh page to see if data persists
echo.
echo 🔍 Watch the console for DEBUG messages that will show:
echo    - Client ID from session
echo    - Profile data being saved
echo    - Profile data being loaded
echo    - Any errors
echo.
echo Starting server now...
python app.py
pause