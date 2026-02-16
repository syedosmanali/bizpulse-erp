from modules.shared.database import get_db_connection

conn = get_db_connection()
cursor = conn.cursor()

# Update the bill to be a cheque bill
cursor.execute("UPDATE bills SET payment_method = 'cheque', payment_status = 'cheque_deposited', is_credit = TRUE WHERE bill_number = 'BILL-20260210-f1597447'")
conn.commit()
conn.close()

print("Bill updated successfully")