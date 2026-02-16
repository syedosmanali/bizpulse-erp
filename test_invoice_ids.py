from modules.shared.database import get_db_connection

conn = get_db_connection()
cursor = conn.cursor()

# Test with the ID we know exists in PostgreSQL
result = cursor.execute("SELECT id, bill_number FROM bills WHERE id = '032ff899-eefc-4c46-aae6-f7ae6c23583c'")
row = result.fetchone()
print('Known invoice in PostgreSQL:', row)

# Test with the problematic ID
result = cursor.execute("SELECT id, bill_number FROM bills WHERE id = '61f6f126-21f3-4dea-b2e1-ac1d3c259ba3'")
row = result.fetchone()
print('Problematic invoice in PostgreSQL:', row)

conn.close()