from modules.shared.database import get_db_connection

conn = get_db_connection()
cursor = conn.cursor()

# Update all today's bills to be proper cheque bills
today_bills = ['BILL-20260210-f1597447', 'BILL-20260210-2e9f4ae6', 'BILL-20260210-82e19303']

print("Updating today's bills to proper cheque bills...")

for bill_number in today_bills:
    cursor.execute("""
        UPDATE bills 
        SET payment_method = 'cheque', 
            payment_status = 'cheque_deposited', 
            is_credit = TRUE,
            credit_paid_amount = 0,
            credit_balance = total_amount
        WHERE bill_number = ?
    """, (bill_number,))
    
    print(f"Updated {bill_number}")

conn.commit()
conn.close()

print("All bills updated successfully")