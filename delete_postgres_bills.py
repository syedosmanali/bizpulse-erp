import psycopg2
import os
from urllib.parse import urlparse

# Get database URL from environment
database_url = os.environ.get('DATABASE_URL')
if not database_url:
    print("DATABASE_URL not found in environment variables")
    exit(1)

# Parse the database URL
parsed = urlparse(database_url)

# Connect to PostgreSQL
try:
    conn = psycopg2.connect(
        host=parsed.hostname,
        port=parsed.port or 5432,
        user=parsed.username,
        password=parsed.password,
        database=parsed.path[1:]  # Remove leading '/'
    )
    cursor = conn.cursor()
    
    print("Connected to PostgreSQL database")
    
    # Check for bills from today
    print("Checking for bills from today...")
    cursor.execute("SELECT bill_number, total_amount, created_at FROM bills WHERE created_at::date = '2026-02-10'")
    bills = cursor.fetchall()
    
    if bills:
        print(f"Found {len(bills)} bills from today:")
        for bill in bills:
            print(f"  {bill[0]}: ₹{bill[1]} - {bill[2]}")
        
        # Delete today's bills
        cursor.execute("DELETE FROM bills WHERE created_at::date = '2026-02-10'")
        deleted_count = cursor.rowcount
        conn.commit()
        
        print(f"\nDeleted {deleted_count} bills from today")
    else:
        print("No bills found from today")
    
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")