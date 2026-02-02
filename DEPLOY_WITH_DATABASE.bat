@echo off
echo ========================================
echo BizPulse - Deploy to Render with PostgreSQL
echo ========================================
echo.

echo Step 1: Checking files...
if exist "render.yaml" (
    echo [OK] render.yaml found
) else (
    echo [ERROR] render.yaml not found!
    pause
    exit /b 1
)

if exist "requirements.txt" (
    echo [OK] requirements.txt found
) else (
    echo [ERROR] requirements.txt not found!
    pause
    exit /b 1
)

echo.
echo Step 2: Committing changes...
git add .
git commit -m "Deploy with PostgreSQL database for data persistence"

echo.
echo Step 3: Pushing to GitHub...
git push origin main

echo.
echo ========================================
echo DEPLOYMENT PUSHED!
echo ========================================
echo.
echo NEXT STEPS ON RENDER DASHBOARD:
echo.
echo Option A - New Blueprint Deployment (RECOMMENDED):
echo   1. Go to: https://dashboard.render.com
echo   2. Click "New" -^> "Blueprint"
echo   3. Connect your GitHub repo
echo   4. Select render.yaml
echo   5. Click "Apply"
echo   6. Wait for deployment (5-10 minutes)
echo.
echo Option B - Manual Database Setup:
echo   1. Go to: https://dashboard.render.com
echo   2. Click "New" -^> "PostgreSQL"
echo   3. Name: bizpulse-db
echo   4. Create database
echo   5. Go to your web service
echo   6. Environment -^> Add DATABASE_URL
echo   7. Copy connection string from PostgreSQL
echo   8. Manual Deploy -^> Deploy latest commit
echo.
echo ========================================
echo After deployment, test:
echo   1. Create a bill
echo   2. Restart service on Render
echo   3. Check if bill still exists
echo   4. If yes, FIXED!
echo ========================================
echo.
pause
