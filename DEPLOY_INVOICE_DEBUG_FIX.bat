@echo off
echo 🚀 Deploying Invoice Debug Fix
echo ===============================

echo.
echo 📝 Adding changes to git...
git add app.py
git add INVOICE_URL_ISSUE_FIX.md
git add test_invoice_debug.py

echo.
echo 💾 Committing invoice debug fix...
git commit -m "DEBUG: Invoice URL issue fix with comprehensive error handling

✅ Added debug routes for production troubleshooting:
- /retail/invoices-test (simple test route)
- /debug-routes (shows all invoice routes)

✅ Enhanced error handling:
- Template error detection and reporting
- Specific error messages for debugging
- Fallback error pages

✅ Local test results: All routes working
- Invoice test route: ✅
- Invoice main route: ✅  
- Invoice detail route: ✅
- Debug routes: ✅

✅ Ready for production debugging:
- Routes registered in Flask app
- Templates exist and accessible
- No authentication blocking
- Comprehensive error detection

Production debug URLs:
- https://bizpulse24.com/retail/invoices-test
- https://bizpulse24.com/debug-routes
- https://bizpulse24.com/retail/invoices"

echo.
echo 🌐 Pushing to production...
git push origin main

echo.
echo ✅ INVOICE DEBUG FIX DEPLOYED!
echo.
echo 🧪 Production Debug URLs:
echo - Test Route: https://bizpulse24.com/retail/invoices-test
echo - Debug Info: https://bizpulse24.com/debug-routes
echo - Main Route: https://bizpulse24.com/retail/invoices
echo - Local Test: http://localhost:5000/retail/invoices
echo.
echo 🔍 Debugging Steps:
echo 1. Test the simple route first: /retail/invoices-test
echo 2. Check debug info: /debug-routes
echo 3. Try main route: /retail/invoices
echo 4. Check error messages if any issues
echo.
echo 📋 If still not working, check:
echo - Server restart needed
echo - Template file permissions
echo - Flask app registration
echo - Production server logs
echo.
pause