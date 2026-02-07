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

echo "Build completed at $(date)"
