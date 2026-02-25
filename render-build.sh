#!/usr/bin/env bash
# Render build script

set -o errexit

# Install system dependencies for psycopg2
apt-get update
apt-get install -y libpq-dev

# Clean Python cache to force reload
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Run critical migration to add business_owner_id column (if file exists)
if [ -f "migrate_add_business_owner_id.py" ]; then
    echo "Running database migration..."
    python migrate_add_business_owner_id.py || echo "Migration failed or already applied"
else
    echo "Migration file not found, skipping..."
fi

echo "Build completed at $(date)"
