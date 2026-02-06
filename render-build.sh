#!/usr/bin/env bash
# Render build script

set -o errexit

# Install system dependencies for psycopg2
apt-get update
apt-get install -y libpq-dev

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt
