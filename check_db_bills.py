from modules.shared.database import get_db_connection

conn = get_db_connection()
cursor = conn.cursor()

try:
    # Check if bills table exists and has data
    result = cursor.execute('SELECT COUNT(*) as count FROM bills')
    row = result.fetchone()
    print('Bills count:', row['count'])
    
    if row['count'] > 0:
        # Get a sample bill
        result = cursor.execute('SELECT id, bill_number FROM bills LIMIT 1')
        sample = result.fetchone()
        print('Sample bill:', sample)
    else:
        print('No bills found in database')
        
except Exception as e:
    print('Error:', e)
    # Try to see what tables exist
    try:
        result = cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        tables = result.fetchall()
        print('Available tables:')
        for table in tables:
            print('  -', table['table_name'])
    except Exception as e2:
        print('Cannot list tables:', e2)

conn.close()