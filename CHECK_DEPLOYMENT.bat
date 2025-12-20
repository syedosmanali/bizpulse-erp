@echo off
echo ========================================
echo   DEPLOYMENT STATUS CHECK
echo ========================================
echo.

echo Checking current Git status...
git status
echo.

echo Checking recent commits...
git log --oneline -5
echo.

echo Checking if files are ready for deployment...
if exist "app.py" (
    echo ✅ app.py - Ready
) else (
    echo ❌ app.py - Missing
)

if exist "templates\sales_management_wine.html" (
    echo ✅ sales_management_wine.html - Ready
) else (
    echo ❌ sales_management_wine.html - Missing
)

echo.
echo ========================================
echo   DEPLOYMENT COMMANDS
echo ========================================
echo.
echo To deploy to production, run:
echo   QUICK_DEPLOY.bat
echo.
echo Or manually:
echo   git add .
echo   git commit -m "Deploy sales management fix"
echo   git push origin main
echo.
pause