@echo off
title Sales Management Deployment
color 0A

echo.
echo  ███████╗ █████╗ ██╗     ███████╗███████╗    ███████╗██╗██╗  ██╗
echo  ██╔════╝██╔══██╗██║     ██╔════╝██╔════╝    ██╔════╝██║╚██╗██╔╝
echo  ███████╗███████║██║     █████╗  ███████╗    █████╗  ██║ ╚███╔╝ 
echo  ╚════██║██╔══██║██║     ██╔══╝  ╚════██║    ██╔══╝  ██║ ██╔██╗ 
echo  ███████║██║  ██║███████╗███████╗███████║    ██║     ██║██╔╝ ██╗
echo  ╚══════╝╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝    ╚═╝     ╚═╝╚═╝  ╚═╝
echo.
echo                    PRODUCTION DEPLOYMENT
echo ========================================================================
echo.

echo [1/5] Checking Git status...
git status --porcelain
if errorlevel 1 (
    echo ERROR: Not a Git repository or Git not installed
    echo Please ensure you're in the correct directory
    pause
    exit /b 1
)

echo.
echo [2/5] Adding all changes...
git add .
git add templates/sales_management_wine.html
git add app.py
echo ✅ Files added to Git

echo.
echo [3/5] Committing changes...
git commit -m "🚀 Deploy: Sales management date filters fixed - Production ready"
echo ✅ Changes committed

echo.
echo [4/5] Pushing to production...
git push origin main
if errorlevel 1 (
    echo ❌ Push failed - checking alternative branches...
    git push origin master
    if errorlevel 1 (
        echo ❌ Push failed on both main and master branches
        echo Please check your Git configuration
        pause
        exit /b 1
    )
)
echo ✅ Code pushed to production repository

echo.
echo [5/5] Deployment commands for PRODUCTION SERVER:
echo ========================================================================
echo.
echo Copy and run these commands on your production server:
echo.
echo   cd /path/to/your/app
echo   git pull origin main
echo   sudo systemctl restart your-app-name
echo.
echo Alternative restart commands:
echo   pkill -f python ^&^& python app.py ^&
echo   pm2 restart app
echo   sudo service apache2 restart
echo.
echo ========================================================================
echo                        DEPLOYMENT COMPLETE!
echo ========================================================================
echo.
echo 🎯 NEXT STEPS:
echo   1. Run the above commands on your production server
echo   2. Clear browser cache (Ctrl+Shift+Delete)
echo   3. Test: https://yourdomain.com/sales-management
echo   4. Verify all date filters work correctly
echo.
echo 📊 EXPECTED RESULTS:
echo   ✅ Today filter shows current sales data
echo   ✅ Yesterday filter shows previous day data
echo   ✅ Week/Month filters work correctly
echo   ✅ No "No sales found" errors
echo.
echo 🔧 IF ISSUES PERSIST:
echo   - Check server error logs
echo   - Verify database connection
echo   - Test API: https://yourdomain.com/api/sales/all?filter=today
echo.
pause