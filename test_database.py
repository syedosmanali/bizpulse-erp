from modules.shared.database import get_db_connection, get_db_type

def test_database_connection():
    """Test database connection and simple queries"""
    print("=== TESTING DATABASE CONNECTION ===")
    
    try:
        # Check database type
        db_type = get_db_type()
        print(f"Database type: {db_type}")
        
        # Get connection
        conn = get_db_connection()
        print(f"Connection object: {conn}")
        
        # Get cursor
        cursor = conn.cursor()
        print(f"Cursor object: {cursor}")
        
        # Test simple query
        print("\nTesting simple query...")
        if db_type == 'postgresql':
            result = cursor.execute("SELECT 1 as test").fetchone()
        else:
            result = cursor.execute("SELECT 1 as test").fetchone()
        print(f"Simple query result: {result}")
        
        # Test bills table query
        print("\nTesting bills table query...")
        if db_type == 'postgresql':
            result = cursor.execute("SELECT COUNT(*) as count FROM bills").fetchone()
        else:
            result = cursor.execute("SELECT COUNT(*) as count FROM bills").fetchone()
        print(f"Bills table count: {result}")
        
        # Test payments table query
        print("\nTesting payments table query...")
        try:
            if db_type == 'postgresql':
                result = cursor.execute("SELECT COUNT(*) as count FROM payments").fetchone()
            else:
                result = cursor.execute("SELECT COUNT(*) as count FROM payments").fetchone()
            print(f"Payments table count: {result}")
        except Exception as e:
            print(f"Payments table error: {e}")
            
        # Test the specific failing query
        print("\nTesting the failing query...")
        today = '2026-02-09'  # Use a fixed date for testing
        user_filter = ""
        user_params = []
        
        try:
            if db_type == 'postgresql':
                query = f'''
                    SELECT 
                        COALESCE(SUM(total_amount), 0) as total_sales,
                        COUNT(*) as transactions
                    FROM bills 
                    WHERE CAST(created_at AS DATE) = %s {user_filter}
                '''
                print(f"PostgreSQL Query: {query}")
                print(f"Parameters: {[today] + user_params}")
                result = cursor.execute(query, [today] + user_params).fetchone()
                print(f"Failing query result: {result}")
            else:
                query = f'''
                    SELECT 
                        COALESCE(SUM(total_amount), 0) as total_sales,
                        COUNT(*) as transactions
                    FROM bills 
                    WHERE DATE(created_at) = ? {user_filter}
                '''
                print(f"SQLite Query: {query}")
                print(f"Parameters: {[today] + user_params}")
                result = cursor.execute(query, [today] + user_params).fetchone()
                print(f"Failing query result: {result}")
        except Exception as e:
            print(f"Specific query error: {e}")
            import traceback
            traceback.print_exc()
            
    except Exception as e:
        print(f"Database connection error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_database_connection()