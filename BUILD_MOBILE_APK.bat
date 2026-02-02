@echo off
echo ========================================
echo BizPulse Mobile APK Builder
echo ========================================
echo.

echo Step 1: Syncing Capacitor...
call npx cap sync android

echo.
echo Step 2: Opening Android Studio...
echo.
echo MANUAL STEPS IN ANDROID STUDIO:
echo 1. Wait for Gradle sync to complete
echo 2. Click Build > Build Bundle(s) / APK(s) > Build APK(s)
echo 3. Wait for build to complete
echo 4. APK will be in: android\app\build\outputs\apk\debug\app-debug.apk
echo.

cd android
start "" "C:\Program Files\Android\Android Studio\bin\studio64.exe" .

echo.
echo ========================================
echo Android Studio opened!
echo Follow the manual steps above to build APK
echo ========================================
pause
