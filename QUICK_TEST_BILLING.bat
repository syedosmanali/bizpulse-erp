@echo off
echo ================================================
echo BILLING MODULE QUICK TEST
echo ================================================
echo.
echo Testing database structure...
python -c "import sqlite3; conn = sqlite3.connect('billing.db'); cursor = conn.cursor(); cursor.execute('SELECT COUNT(*) FROM products WHERE stock > 0'); print(f'Products with stock: {cursor.fetchone()[0]}'); conn.close()"
echo.
echo ================================================
echo Database is ready!
echo.
echo Now test billing module:
echo 1. Make sure server is running (START_SERVER_CLEAN.bat)
echo 2. Open: http://localhost:5000/retail/billing
echo 3. Add products to cart
echo 4. Click "Create Bill" button
echo.
echo If error occurs, check server console for details
echo ================================================
pause
