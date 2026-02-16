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
    cursor.execute("SELECT id, bill_number, total_amount, created_at FROM bills WHERE created_at::date = '2026-02-10'")
    bills = cursor.fetchall()
    
    if bills:
        print(f"Found {len(bills)} bills from today:")
        bill_ids = []
        for bill in bills:
            bill_id, bill_number, total_amount, created_at = bill
            bill_ids.append(bill_id)
            print(f"  {bill_number}: ₹{total_amount} - {created_at}")
        
        # Delete payments first (due to foreign key constraint)
        print("\nDeleting related payments...")
        bill_ids_tuple = tuple(bill_ids)
        cursor.execute("DELETE FROM payments WHERE bill_id IN %s", (bill_ids_tuple,))
        deleted_payments = cursor.rowcount
        print(f"Deleted {deleted_payments} payments")
        
        # Delete bill items next
        print("Deleting related bill items...")
        cursor.execute("DELETE FROM bill_items WHERE bill_id IN %s", (bill_ids_tuple,))
        deleted_items = cursor.rowcount
        print(f"Deleted {deleted_items} bill items")
        
        # Now delete the bills
        print("Deleting bills...")
        cursor.execute("DELETE FROM bills WHERE created_at::date = '2026-02-10'")
        deleted_bills = cursor.rowcount
        conn.commit()
        
        print(f"Deleted {deleted_bills} bills from today")
        print(f"Total records deleted: {deleted_payments + deleted_items + deleted_bills}")
    else:
        print("No bills found from today")
    
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")
    if 'conn' in locals():
        conn.rollback()
        conn.close()