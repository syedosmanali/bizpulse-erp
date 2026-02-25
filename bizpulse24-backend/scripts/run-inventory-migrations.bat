@echo off
REM Script to run Inventory module database migrations on Windows
REM This script executes the SQL migration files using psql

echo 🚀 Starting Inventory Module Migrations...
echo.

REM Check if .env file exists
if not exist .env (
    echo ❌ Error: .env file not found
    echo Please create a .env file with your Supabase connection details
    exit /b 1
)

REM Load DATABASE_URL from .env file
for /f "tokens=1,2 delims==" %%a in (.env) do (
    if "%%a"=="DATABASE_URL" set DATABASE_URL=%%b
)

REM Check if DATABASE_URL is set
if "%DATABASE_URL%"=="" (
    echo ❌ Error: DATABASE_URL not set in .env file
    echo Example: DATABASE_URL=postgresql://user:password@host:port/database
    exit /b 1
)

set MIGRATIONS_DIR=prisma\migrations

REM Run migrations in order
echo 📄 Executing migration: 004_inventory_module.sql
psql "%DATABASE_URL%" -f "%MIGRATIONS_DIR%\004_inventory_module.sql"
if errorlevel 1 (
    echo ❌ Error executing: 004_inventory_module.sql
    exit /b 1
)
echo ✅ Successfully executed: 004_inventory_module.sql
echo.

echo 📄 Executing migration: 005_inventory_rls_policies.sql
psql "%DATABASE_URL%" -f "%MIGRATIONS_DIR%\005_inventory_rls_policies.sql"
if errorlevel 1 (
    echo ❌ Error executing: 005_inventory_rls_policies.sql
    exit /b 1
)
echo ✅ Successfully executed: 005_inventory_rls_policies.sql
echo.

echo ✅ All Inventory module migrations completed successfully!
echo.
echo 📊 Created tables:
echo    - categories
echo    - brands
echo    - products
echo    - locations
echo    - stock
echo    - stock_ledger
echo    - stock_alerts
echo.
echo 🔒 RLS policies applied to all Inventory tables
echo ✨ Indexes created for optimal query performance
