import sqlite3

conn = sqlite3.connect('billing.db')
cursor = conn.cursor()

# Check if client_users table exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='client_users'")
table_exists = cursor.fetchone()

if not table_exists:
    print('Creating client_users table...')
    cursor.execute('''
        CREATE TABLE client_users (
            id TEXT PRIMARY KEY,
            client_id TEXT NOT NULL,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            password_plain TEXT NOT NULL,
            role TEXT NOT NULL,
            department TEXT,
            phone_number TEXT,
            is_active INTEGER DEFAULT 1,
            permissions TEXT,
            created_at TEXT NOT NULL,
            last_login TEXT
        )
    ''')
    conn.commit()
    print('Table created successfully!')
else:
    print('Table already exists')

conn.close()