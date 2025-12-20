@echo off
echo 🚀 Deploying Billing Fix to Production...
echo ==========================================

echo.
echo 📝 Adding changes to git...
git add app.py
git add BILL_CREATION_FIXED.md
git add test_billing_fix_final.py
git add test_billing_simple.py

echo.
echo 💾 Committing changes...
git commit -m "Fix: Billing creation backend - handle frontend data format properly

- Map frontend 'total' to backend 'total_amount'
- Map frontend 'cgst'+'sgst' to backend 'tax_amount'  
- Map item fields: id->product_id, name->product_name, price->unit_price
- Add auto customer creation with phone lookup
- Handle walk-in customers properly
- Fix data format mismatch between retail_billing.html and /api/sales POST

Resolves: Bill creation failing with 'cannot access local variable' error"

echo.
echo 🌐 Pushing to GitHub...
git push origin main

echo.
echo ✅ Billing fix deployed successfully!
echo.
echo 🧪 Test URLs:
echo - Local: http://localhost:5000/retail/billing
echo - Production: https://bizpulse24.com/retail/billing
echo.
echo 📋 The fix handles the exact data format from frontend:
echo - Frontend sends: total, cgst, sgst, items[id, name, price]
echo - Backend now maps: total->total_amount, cgst+sgst->tax_amount, id->product_id
echo.
pause