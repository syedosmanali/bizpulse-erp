#!/bin/bash

# BizPulse24 ERP Backend Setup Script

echo "Setting up BizPulse24 ERP Backend..."

# Check Node.js version
echo "Checking Node.js version..."
node --version

# Check npm version
echo "Checking npm version..."
npm --version

# Install dependencies
echo "Installing dependencies..."
npm install

# Generate Prisma client
echo "Generating Prisma client..."
npm run prisma:generate

# Create logs directory
echo "Creating logs directory..."
mkdir -p logs

# Copy environment file if not exists
if [ ! -f .env ]; then
  echo "Creating .env file from .env.example..."
  cp .env.example .env
  echo "Please configure your .env file with Supabase credentials"
fi

echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Configure your .env file with Supabase credentials"
echo "2. Run 'npm run prisma:migrate' to set up the database"
echo "3. Run 'npm run dev' to start the development server"
