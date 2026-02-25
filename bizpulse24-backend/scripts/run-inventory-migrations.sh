#!/bin/bash

# Script to run Inventory module database migrations
# This script executes the SQL migration files using psql

set -e  # Exit on error

echo "🚀 Starting Inventory Module Migrations..."
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found"
    echo "Please create a .env file with your Supabase connection details"
    exit 1
fi

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# Check required environment variables
if [ -z "$DATABASE_URL" ]; then
    echo "❌ Error: DATABASE_URL not set in .env file"
    echo "Example: DATABASE_URL=postgresql://user:password@host:port/database"
    exit 1
fi

MIGRATIONS_DIR="prisma/migrations"

# Migration files to run in order
MIGRATIONS=(
    "004_inventory_module.sql"
    "005_inventory_rls_policies.sql"
)

# Run each migration
for migration in "${MIGRATIONS[@]}"; do
    migration_file="$MIGRATIONS_DIR/$migration"
    
    if [ ! -f "$migration_file" ]; then
        echo "❌ Error: Migration file not found: $migration_file"
        exit 1
    fi
    
    echo "📄 Executing migration: $migration"
    
    # Execute the migration using psql
    psql "$DATABASE_URL" -f "$migration_file"
    
    if [ $? -eq 0 ]; then
        echo "✅ Successfully executed: $migration"
        echo ""
    else
        echo "❌ Error executing: $migration"
        exit 1
    fi
done

echo "✅ All Inventory module migrations completed successfully!"
echo ""
echo "📊 Created tables:"
echo "   - categories"
echo "   - brands"
echo "   - products"
echo "   - locations"
echo "   - stock"
echo "   - stock_ledger"
echo "   - stock_alerts"
echo ""
echo "🔒 RLS policies applied to all Inventory tables"
echo "✨ Indexes created for optimal query performance"
