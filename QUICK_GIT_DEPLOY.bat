@echo off
echo ========================================
echo   QUICK GIT DEPLOYMENT
echo ========================================
echo.

echo [1/4] Adding all changes to Git...
git add .

echo.
echo [2/4] Committing changes...
git commit -m "Fix: Sales management date filters - Complete working solution"

echo.
echo [3/4] Pushing to production...
git push origin main

echo.
echo [4/4] Deployment commands for production server:
echo.
echo Run these commands on your production server:
echo   git pull origin main
echo   sudo systemctl restart your-app-name
echo   # OR: pkill -f python && python app.py &
echo.

echo ========================================
echo   DEPLOYMENT COMPLETE!
echo ========================================
echo.
echo After server restart, test at:
echo   https://yourdomain.com/sales-management
echo.
echo Clear browser cache and test all filters!
pause