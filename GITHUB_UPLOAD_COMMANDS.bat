@echo off
echo ========================================
echo  BizPulse ERP - GitHub Upload Commands
echo ========================================
echo.
echo STEP 1: Create repository on GitHub.com
echo - Go to github.com and login
echo - Click "New repository"
echo - Name: bizpulse-erp
echo - Description: BizPulse ERP - Complete Business Management System
echo - Public (required for free Render)
echo - DON'T initialize with README
echo.
echo STEP 2: Copy these commands (replace YOUR_USERNAME):
echo.
echo cd BizPulse_ERP_Clean_001933
echo git remote add origin https://github.com/YOUR_USERNAME/bizpulse-erp.git
echo git branch -M main
echo git push -u origin main
echo.
echo STEP 3: Deploy to Render.com
echo - Go to render.com and signup
echo - Click "New Web Service"
echo - Connect your GitHub repo: bizpulse-erp
echo - Build Command: pip install -r requirements.txt
echo - Start Command: gunicorn app:app --bind 0.0.0.0:$PORT
echo - Click Deploy!
echo.
echo ========================================
echo Your ERP will be live in 2-3 minutes!
echo ========================================
pause