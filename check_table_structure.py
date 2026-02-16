import sqlite3

# Connect to database
conn = sqlite3.connect('billing.db')
cursor = conn.cursor()

print("=== TABLE STRUCTURE ===")

# Check bills table columns
cursor.execute("PRAGMA table_info(bills)")
columns = cursor.fetchall()
print("\nbills table columns:")
for col in columns:
    print(f"  {col[1]} ({col[2]})")

# Check payments table columns
cursor.execute("PRAGMA table_info(payments)")
columns = cursor.fetchall()
print("\npayments table columns:")
for col in columns:
    print(f"  {col[1]} ({col[2]})")

conn.close()