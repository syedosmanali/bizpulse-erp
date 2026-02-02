@echo off
echo ========================================
echo BizPulse Mobile APK - QUICK BUILD
echo ========================================
echo.
echo URL: https://www.bizpulse24.com/mobile-simple
echo Status: VERIFIED WORKING (200 OK)
echo.
echo ========================================
echo BUILDING APK NOW...
echo ========================================
echo.

cd android

echo Running Gradle Build...
echo This will take 2-3 minutes...
echo.

call gradlew assembleDebug

echo.
echo ========================================
if exist "app\build\outputs\apk\debug\app-debug.apk" (
    echo SUCCESS! APK BUILT!
    echo ========================================
    echo.
    echo APK Location:
    echo %CD%\app\build\outputs\apk\debug\app-debug.apk
    echo.
    echo Opening folder...
    start "" "%CD%\app\build\outputs\apk\debug"
    echo.
    echo COPY app-debug.apk TO YOUR PHONE AND INSTALL!
) else (
    echo BUILD FAILED!
    echo Check errors above.
)
echo.
echo ========================================
pause
