@echo off
echo ========================================
echo   SALES MANAGEMENT - CMD DEPLOYMENT
echo ========================================
echo.

echo [STEP 1] Adding all changes to Git...
git add .
if errorlevel 1 (
    echo ERROR: Git add failed
    pause
    exit /b 1
)

echo.
echo [STEP 2] Committing changes...
git commit -m "Fix: Sales management date filters - Production deployment"
if errorlevel 1 (
    echo WARNING: Nothing to commit or commit failed
)

echo.
echo [STEP 3] Pushing to production repository...
git push origin main
if errorlevel 1 (
    echo ERROR: Git push failed
    echo Check your Git credentials and connection
    pause
    exit /b 1
)

echo.
echo ========================================
echo   LOCAL DEPLOYMENT COMPLETE!
echo ========================================
echo.
echo Now run these commands on your PRODUCTION SERVER:
echo.
echo   git pull origin main
echo   sudo systemctl restart your-app-name
echo   # OR: pkill -f python ^&^& python app.py ^&
echo.
echo After server restart, test at:
echo   https://yourdomain.com/sales-management
echo.
echo IMPORTANT: Clear browser cache after deployment!
echo.
pause