#!/usr/bin/env python3
"""
Deploy sales management fixes to production server
"""
import os
import shutil
from datetime import datetime

def create_deployment_package():
    """Create deployment package with all fixes"""
    
    print("📦 Creating deployment package...")
    
    # Create deployment folder
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    deploy_folder = f"sales_management_deploy_{timestamp}"
    
    if os.path.exists(deploy_folder):
        shutil.rmtree(deploy_folder)
    
    os.makedirs(deploy_folder)
    os.makedirs(f"{deploy_folder}/templates")
    
    # Copy fixed files
    files_to_deploy = [
        ('app.py', 'app.py'),
        ('templates/sales_management_wine.html', 'templates/sales_management_wine.html'),
        ('templates/debug_sales_management.html', 'templates/debug_sales_management.html')
    ]
    
    for src, dst in files_to_deploy:
        if os.path.exists(src):
            dst_path = os.path.join(deploy_folder, dst)
            os.makedirs(os.path.dirname(dst_path), exist_ok=True)
            shutil.copy2(src, dst_path)
            print(f"✅ Copied: {src} → {dst}")
        else:
            print(f"⚠️  File not found: {src}")
    
    # Create deployment instructions
    instructions = f"""# SALES MANAGEMENT DEPLOYMENT INSTRUCTIONS

## 📋 DEPLOYMENT CHECKLIST

### 1. BACKUP CURRENT FILES
```bash
# Backup current files before deployment
cp app.py app_backup_{timestamp}.py
cp templates/sales_management_wine.html templates/sales_management_wine_backup_{timestamp}.html
```

### 2. UPLOAD NEW FILES
- Upload `app.py` to your server root
- Upload `templates/sales_management_wine.html` to templates folder
- Upload `templates/debug_sales_management.html` to templates folder

### 3. RESTART SERVER
```bash
# Restart your Flask/Python server
sudo systemctl restart your-app-name
# OR
pkill -f python
python app.py &
```

### 4. TEST DEPLOYMENT
1. Open: https://yourdomain.com/sales-management
2. Clear browser cache (Ctrl+Shift+Delete)
3. Hard refresh (Ctrl+F5)
4. Test filters:
   - Today: Should show today's sales
   - Yesterday: Should show yesterday's sales
   - Week: Should show this week's sales
   - Month: Should show this month's sales

### 5. VERIFY API
- Test API directly: https://yourdomain.com/api/sales/all?filter=today
- Should return JSON with sales data

## 🔧 FIXES INCLUDED

### Backend (app.py)
- ✅ Working `/api/sales/all` endpoint
- ✅ Proper date filtering with ISO 8601
- ✅ Debug routes added
- ✅ Error handling improved

### Frontend (sales_management_wine.html)
- ✅ Complete template rewrite
- ✅ Working API integration
- ✅ Proper date filtering
- ✅ Beautiful UI design
- ✅ Real-time data loading
- ✅ Custom date range support

### Debug Tools
- ✅ Debug page: /debug-sales
- ✅ API testing capabilities
- ✅ Error diagnostics

## 📊 EXPECTED RESULTS

After deployment, the sales management page should show:
- TODAY: Real-time today's sales data
- YESTERDAY: Yesterday's sales data
- WEEK: This week's sales data
- MONTH: This month's sales data

## 🚨 TROUBLESHOOTING

### If page still shows old data:
1. Clear server cache/restart server
2. Clear browser cache completely
3. Check server logs for errors
4. Verify file upload was successful

### If API returns errors:
1. Check database connection
2. Verify table structure
3. Check server logs
4. Test API endpoint directly

## 🎯 DEPLOYMENT TIMESTAMP
{timestamp}

## ✅ DEPLOYMENT STATUS
Ready for production deployment!
"""
    
    with open(f"{deploy_folder}/DEPLOYMENT_INSTRUCTIONS.md", 'w', encoding='utf-8') as f:
        f.write(instructions)
    
    # Create quick deployment script
    deploy_script = """#!/bin/bash
# Quick deployment script

echo "🚀 Deploying Sales Management Fixes..."

# Backup current files
echo "📦 Creating backups..."
cp app.py app_backup_$(date +%Y%m%d_%H%M%S).py
cp templates/sales_management_wine.html templates/sales_management_wine_backup_$(date +%Y%m%d_%H%M%S).html

# Copy new files
echo "📁 Copying new files..."
cp sales_management_deploy_*/app.py .
cp sales_management_deploy_*/templates/sales_management_wine.html templates/
cp sales_management_deploy_*/templates/debug_sales_management.html templates/

# Restart server (adjust command as needed)
echo "🔄 Restarting server..."
# sudo systemctl restart your-app-name
# OR
# pkill -f python && python app.py &

echo "✅ Deployment complete!"
echo "🌐 Test at: https://yourdomain.com/sales-management"
"""
    
    with open(f"{deploy_folder}/deploy.sh", 'w', encoding='utf-8') as f:
        f.write(deploy_script)
    
    # Make script executable
    os.chmod(f"{deploy_folder}/deploy.sh", 0o755)
    
    print(f"✅ Deployment package created: {deploy_folder}")
    return deploy_folder

def create_git_commands():
    """Create Git commands for deployment"""
    
    git_commands = """# GIT DEPLOYMENT COMMANDS

## If using Git for deployment:

```bash
# Add all changes
git add .

# Commit changes
git commit -m "Fix: Sales management date filters - Complete rewrite"

# Push to production branch
git push origin main

# On production server, pull changes
git pull origin main

# Restart server
sudo systemctl restart your-app-name
```

## Alternative: Direct file upload
- Use FTP/SFTP to upload files
- Use cPanel file manager
- Use hosting provider's deployment tools
"""
    
    with open("GIT_DEPLOYMENT_COMMANDS.md", 'w', encoding='utf-8') as f:
        f.write(git_commands)
    
    print("✅ Git deployment commands created")

def main():
    print("🚀 PRODUCTION DEPLOYMENT PREPARATION")
    print("=" * 50)
    
    # Create deployment package
    deploy_folder = create_deployment_package()
    
    # Create Git commands
    create_git_commands()
    
    print("\n📋 DEPLOYMENT OPTIONS:")
    print("=" * 30)
    
    print("\n1️⃣ MANUAL DEPLOYMENT:")
    print(f"   - Use files in: {deploy_folder}/")
    print("   - Follow: DEPLOYMENT_INSTRUCTIONS.md")
    print("   - Upload to your .com server")
    
    print("\n2️⃣ GIT DEPLOYMENT:")
    print("   - Use: GIT_DEPLOYMENT_COMMANDS.md")
    print("   - Commit and push changes")
    print("   - Pull on production server")
    
    print("\n3️⃣ QUICK SCRIPT:")
    print(f"   - Run: {deploy_folder}/deploy.sh")
    print("   - On your production server")
    
    print("\n🎯 AFTER DEPLOYMENT:")
    print("   1. Clear browser cache")
    print("   2. Test: https://yourdomain.com/sales-management")
    print("   3. Verify all filters work")
    print("   4. Check API: https://yourdomain.com/api/sales/all?filter=today")
    
    print("\n✅ DEPLOYMENT PACKAGE READY!")
    print("Upload karo aur server restart karo - production me fix ho jayega!")

if __name__ == "__main__":
    main()