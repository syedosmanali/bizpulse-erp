@echo off
REM Database Migration Script for BizPulse24 ERP Backend (Windows)
REM This script runs all SQL migrations in order

echo.
echo ========================================
echo BizPulse24 ERP Database Migration
echo ========================================
echo.

REM Check if .env file exists
if not exist .env (
    echo ERROR: .env file not found
    echo Please create a .env file with your database connection details
    exit /b 1
)

REM Load DATABASE_URL from .env file
for /f "tokens=1,2 delims==" %%a in (.env) do (
    if "%%a"=="DATABASE_URL" set DATABASE_URL=%%b
)

REM Check if DATABASE_URL is set
if "%DATABASE_URL%"=="" (
    echo ERROR: DATABASE_URL not set in .env file
    exit /b 1
)

echo Database URL: %DATABASE_URL%
echo.

REM Set migrations directory
set MIGRATIONS_DIR=%~dp0..\prisma\migrations

REM Check if migrations directory exists
if not exist "%MIGRATIONS_DIR%" (
    echo ERROR: Migrations directory not found: %MIGRATIONS_DIR%
    exit /b 1
)

echo Found migration files:
dir /b /o:n "%MIGRATIONS_DIR%\*.sql"
echo.

echo Running migrations...
echo.

REM Run each migration file in order
for /f "delims=" %%f in ('dir /b /o:n "%MIGRATIONS_DIR%\*.sql"') do (
    echo Running: %%f
    psql "%DATABASE_URL%" -f "%MIGRATIONS_DIR%\%%f"
    if errorlevel 1 (
        echo ERROR: Failed to run %%f
        exit /b 1
    )
    echo SUCCESS: %%f completed
    echo.
)

echo.
echo ========================================
echo All migrations completed successfully!
echo ========================================
