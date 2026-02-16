from modules.shared.database import get_db_connection

conn = get_db_connection()
cursor = conn.cursor()

cursor.execute("SELECT bill_number, payment_method, payment_status, credit_paid_amount, is_credit FROM bills WHERE CAST(created_at AS DATE) = '2026-02-10'")
rows = cursor.fetchall()

print("Today's bills:")
for r in rows:
    print(f"  - {r['bill_number']}: {r['payment_method']} - {r['payment_status']} - paid: {r['credit_paid_amount']} - credit: {r['is_credit']}")

conn.close()