import sqlite3

# Connect to database
conn = sqlite3.connect('billing.db')
cursor = conn.cursor()

# Delete today's sales
cursor.execute("DELETE FROM bills WHERE DATE(created_at) = '2026-02-10'")
deleted_count = cursor.rowcount

conn.commit()
conn.close()

print(f"Deleted {deleted_count} sales from today")