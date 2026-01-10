import os
import shutil

# List of useless files and directories to delete
useless_files = [
    # Documentation files
    'BILLING_MODULE_ENHANCEMENTS_COMPLETE.md',
    'BILLING_ORDER_FIXED.txt',
    'CLIENT_DETAILS_FIX.md',
    'CLIENT_LOGIN_QUICK_GUIDE.txt',
    'COLLECTED_TODAY_AND_PAYMENT_HISTORY_FIX.md',
    'COMPREHENSIVE_FIXES_PLAN.md',
    'CONSOLE_DEBUG_COMMANDS.txt',
    'CREDIT_FIX_README.md',
    'CREDIT_MODULE_COMPLETE.md',
    'CREDIT_MODULE_FIX_NOW.txt',
    'CREDIT_MODULE_FIX.md',
    'CREDIT_MODULE_FIXES_COMPLETE.md',
    'CREDIT_MODULE_QUICK_REF.txt',
    'CREDIT_MODULE_SUMMARY.md',
    'CREDIT_MODULE_USER_GUIDE.md',
    'CREDIT_PAYMENT_AND_PAGINATION_FIX.md',
    'CREDIT_PAYMENT_HISTORY_EXAMPLE.md',
    'CREDIT_PAYMENT_HISTORY_REPORT.md',
    'CREDIT_SUMMARY_AND_PAYMENT_METHOD_FIX.md',
    'DASHBOARD_RECEIVABLE_FIX.md',
    'DEPLOYMENT_SUMMARY_URDU.md',
    'DESKTOP_MOBILE_SYNC_COMPLETE.md',
    'DESKTOP_MOBILE_SYNC_PLAN.md',
    'DISCOUNT_CALCULATION_FIX.md',
    'DISCOUNT_LOGIC_FIXED.md',
    'EARNINGS_MODULE_COMPLETE.md',
    'EARNINGS_MODULE_FIXED.md',
    'EARNINGS_QUICK_GUIDE.txt',
    'ERROR_FIX_SUMMARY.md',
    'FINAL_DEPLOYMENT_STEPS.md',
    'FINAL_FIXES_SUMMARY.md',
    'FINAL_SUMMARY.md',
    'FIX_APPLIED_RESTART_NOW.txt',
    'FIX_CREDIT_MODULE_CACHE.md',
    'GST_CALCULATION_VERIFIED.txt',
    'MOBILE_ACCESS_GUIDE.md',
    'MOBILE_ACCESS_NOW.txt',
    'MOBILE_ERP_FINAL_UPDATES.md',
    'MOBILE_ERP_FIXES_COMPLETE.txt',
    'MOBILE_MENU_FIXED.txt',
    'MOBILE_NOT_LOADING_CHECKLIST.txt',
    'MOBILE_QUICK_FIX.txt',
    'MOBILE_UI_IMPROVEMENTS_COMPLETE.md',
    'MOBILE_URL_AND_FIX.txt',
    'MODULE_FIX_QUICK_TEST.txt',
    'MODULE_OVERLAP_FIX.md',
    'NOTIFICATION_SETTINGS_COMPLETE.md',
    'PRODUCT_FORM_QUICK_GUIDE.txt',
    'PRODUCT_FORM_REDESIGN_COMPLETE.md',
    'PRODUCT_VARIANTS_IMPLEMENTATION.md',
    'QUICK_CHECKLIST.txt',
    'QUICK_FIX_GUIDE.txt',
    'RBAC_CLIENT_VIEW_QUICK_FIX.txt',
    'RBAC_IMPLEMENTATION_STATUS.md',
    'RBAC_QUICK_START.md',
    'RBAC_SETUP_NOW.md',
    'RBAC_SYSTEM_COMPLETE_SUMMARY.md',
    'RBAC_SYSTEM_README.md',
    'READ_THIS_FIRST.txt',
    'RENDER_DEPLOYMENT_COMPLETE.md',
    'REPORTS_MODULE_COMPLETE.md',
    'SALES_CALCULATION_FIX.md',
    'SALES_FIX_QUICK_TEST.txt',
    'SALES_MODULE_FIXED.md',
    'SALES_SUMMARY_FIXED.md',
    'SALES_TABLE_PAGINATION.md',
    'SALES_VIEW_BUTTON_COMPLETE.md',
    'SALES_VIEW_QUICK_TEST.txt',
    'SETTINGS_COLLAPSIBLE_COMPLETE.md',
    'SETTINGS_REORGANIZED.md',
    'SIMPLE_DEPLOY.md',
    'SMART_LOGO_SYSTEM.md',
    'SQLITE_THREADING_FIX.md',
    'SYNC_IMPLEMENTATION_STATUS.md',
    'TENANT_LOGIN_COMPLETE.md',
    'UI_FIXES_SUMMARY.md',
    'URGENT_FIX_MOBILE_ACCESS.txt',
    'VARIANTS_COMPLETE_SOLUTION.md',
    'VARIANTS_FEATURE_COMPLETE.md',
    'VARIANTS_FIXED_NOW.txt',
    'VARIANTS_VISUAL_GUIDE.txt',
    
    # Test files
    'test_alerts_api.py',
    'test_credit_api.py',
    'test_credit_frontend.html',
    'test_credit_module_simple.html',
    'test_credit_module.html',
    'test_employee_access.py',
    'test_import.py',
    'test_sync_implementation.py',
    'test_tenant_login.py',
    'test_variants_fix.md',
    'check_bill_discount.py',
    'check_credit.py',
    'check_partial.py',
    'check_routes.py',
    'check_today_credit.py',
    'fix_missing_discount.py',
    'verify_credit_module.py',
    
    # Backup files
    'billing.db.backup_20260106_193507',
    'billing.db.backup_before_sync_20260106_193042',
    'billing.db.backup_before_sync_20260106_193410',
    'app_original_backup.py',
    'app_simple.py',
    
    # Deployment files
    'deploy_from_windows.bat',
    'DEPLOY_NOW.bat',
    'DEPLOY_SYNC_TO_SERVER.sh',
    'DEPLOY_TO_PRODUCTION_FINAL.sh',
    'deploy_to_production.bat',
    'deploy_to_production.sh',
    'DEPLOY_TO_SERVER_COMMANDS.txt',
    'deploy_to_server.bat',
    'production_fix.sh',
    'quick_server_deploy.sh',
    'server_deploy_commands.sh',
    'server_update.sh',
    'COMPLETE_MOBILE_FIX.bat',
    'START_SERVER_FOR_MOBILE.bat',
    'start_without_venv.bat',
    'run_server.bat',
    'start_server.sh',
    'add_firewall_rule.bat',
    
    # Migration/setup files (keep some, delete others)
    'add_existing_admin_to_rbac.py',
    'add_expiry_date_column.py',
    'assign_user_data.py',
    'auto_deploy_server.py',
    'create_notification_settings.py',
    'create_product_variants_table.py',
    'fix_partial_bills.py',
    'fix_tenant_passwords.py',
    'initialize_rbac.py',
    'migrate_add_user_id.py',
    'migrate_existing_credit_bills.py',
    'quick_add_clients.py',
    
    # Other useless files
    'credit_module_mobile.html',
    'ngrok.exe',
    'sales_management_deploy_20251220_215417.zip',
    'capacitor.config.ts',
    'nest-cli.json',
    'tsconfig.json',
    'gradle.properties',
    'openapi-paths-v1.yaml',
    'openapi-v1.yaml',
]

# Useless directories
useless_dirs = [
    'Bizpulse',
    'BizPulse_Dynamic_APK',
    'BizPulse_Fresh_Deploy_20251211_015908',
    'BizPulse_Working_APK',
    'sales_management_deploy_20251220_215417',
    'mobile_app_fresh',
    'android',
    'docs',
    'src',
    'services',
    'shared',
    'api',
    'backend',
]

print("🗑️ CLEANING UP USELESS FILES...")
print("=" * 80)

deleted_files = 0
deleted_dirs = 0

# Delete files
for file in useless_files:
    if os.path.exists(file):
        try:
            os.remove(file)
            print(f"✅ Deleted file: {file}")
            deleted_files += 1
        except Exception as e:
            print(f"❌ Failed to delete {file}: {e}")
    else:
        print(f"⚠️ File not found: {file}")

print("\n" + "=" * 80)

# Delete directories
for dir_name in useless_dirs:
    if os.path.exists(dir_name) and os.path.isdir(dir_name):
        try:
            shutil.rmtree(dir_name)
            print(f"✅ Deleted directory: {dir_name}")
            deleted_dirs += 1
        except Exception as e:
            print(f"❌ Failed to delete {dir_name}: {e}")
    else:
        print(f"⚠️ Directory not found: {dir_name}")

print("\n" + "=" * 80)
print(f"🎉 CLEANUP COMPLETE!")
print(f"📁 Deleted {deleted_files} files")
print(f"📂 Deleted {deleted_dirs} directories")
print("=" * 80)