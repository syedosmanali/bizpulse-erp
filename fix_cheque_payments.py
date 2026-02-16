from modules.shared.database import get_db_connection

conn = get_db_connection()
cursor = conn.cursor()

# Get the bill IDs for today's cheque bills
cursor.execute("SELECT id, total_amount FROM bills WHERE CAST(created_at AS DATE) = '2026-02-10' AND payment_method = 'cheque'")
bills = cursor.fetchall()

print("Updating payment records for cheque bills...")

for bill in bills:
    bill_id = bill['id']
    total_amount = bill['total_amount']
    
    # Update the payment record to have amount = 0 for cheque bills (since money not received yet)
    cursor.execute("""
        UPDATE payments 
        SET amount = 0 
        WHERE bill_id = %s AND method = 'cheque'
    """, (bill_id,))
    
    print(f"Updated payment for bill {bill_id} - amount set to 0 (was {total_amount})")

conn.commit()
conn.close()

print("All payment records updated successfully")