@echo off
echo ================================================
echo BILLING MODULE TEST - बिलिंग मॉड्यूल टेस्ट
echo ================================================
echo.

echo Step 1: Database Check...
python test_billing_fix.py
echo.

echo ================================================
echo अब server start करो और test करो:
echo.
echo 1. START_SERVER_CLEAN.bat चलाओ
echo 2. Browser में खोलो: http://localhost:5000/retail/billing
echo 3. Products load हो रहे हैं check करो
echo 4. Bill create करके test करो
echo.
echo ================================================
pause
