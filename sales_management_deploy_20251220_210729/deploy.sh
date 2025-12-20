#!/bin/bash
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
