@echo off
REM BizPulse24 ERP Backend Setup Script for Windows

echo Setting up BizPulse24 ERP Backend...

REM Check Node.js version
echo Checking Node.js version...
node --version

REM Check npm version
echo Checking npm version...
npm --version

REM Install dependencies
echo Installing dependencies...
call npm install

REM Generate Prisma client
echo Generating Prisma client...
call npm run prisma:generate

REM Create logs directory
echo Creating logs directory...
if not exist logs mkdir logs

REM Copy environment file if not exists
if not exist .env (
  echo Creating .env file from .env.example...
  copy .env.example .env
  echo Please configure your .env file with Supabase credentials
)

echo Setup complete!
echo.
echo Next steps:
echo 1. Configure your .env file with Supabase credentials
echo 2. Run 'npm run prisma:migrate' to set up the database
echo 3. Run 'npm run dev' to start the development server

pause
