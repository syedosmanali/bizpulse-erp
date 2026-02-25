#!/bin/bash

# Database Migration Script for BizPulse24 ERP Backend
# This script runs all SQL migrations in order

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 BizPulse24 ERP Database Migration${NC}\n"

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${RED}❌ Error: .env file not found${NC}"
    echo "Please create a .env file with your database connection details"
    exit 1
fi

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# Check required environment variables
if [ -z "$DATABASE_URL" ]; then
    echo -e "${RED}❌ Error: DATABASE_URL not set in .env file${NC}"
    exit 1
fi

echo -e "${YELLOW}Database URL: ${DATABASE_URL}${NC}\n"

# Get migration files directory
MIGRATIONS_DIR="$(dirname "$0")/../prisma/migrations"

# Check if migrations directory exists
if [ ! -d "$MIGRATIONS_DIR" ]; then
    echo -e "${RED}❌ Error: Migrations directory not found: $MIGRATIONS_DIR${NC}"
    exit 1
fi

# Get all SQL migration files sorted by name
MIGRATION_FILES=$(ls -1 "$MIGRATIONS_DIR"/*.sql 2>/dev/null | sort)

if [ -z "$MIGRATION_FILES" ]; then
    echo -e "${YELLOW}⚠️  No migration files found${NC}"
    exit 0
fi

echo -e "${GREEN}Found migration files:${NC}"
echo "$MIGRATION_FILES" | while read file; do
    echo "  - $(basename "$file")"
done
echo ""

# Run each migration
echo -e "${GREEN}Running migrations...${NC}\n"

for migration_file in $MIGRATION_FILES; do
    filename=$(basename "$migration_file")
    echo -e "${YELLOW}📄 Running: $filename${NC}"
    
    # Execute the migration using psql
    if psql "$DATABASE_URL" -f "$migration_file" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ $filename completed successfully${NC}\n"
    else
        echo -e "${RED}❌ Error running $filename${NC}"
        echo "Please check the error message above and fix the issue"
        exit 1
    fi
done

echo -e "${GREEN}✅ All migrations completed successfully!${NC}"
