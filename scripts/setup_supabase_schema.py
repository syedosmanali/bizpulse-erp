"""
Setup Supabase PostgreSQL schema
Creates all tables in Supabase before migration
"""
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load .env file manually
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

# Import database initialization
from modules.shared.database import init_db, get_db_connection, get_db_type

def setup_schema():
    """Initialize Supabase PostgreSQL schema"""
    print("🚀 Setting up Supabase PostgreSQL schema...")
    
    db_type = get_db_type()
    print(f"📊 Database Type: {db_type}")
    
    if db_type != 'postgresql':
        print("❌ DATABASE_URL not set or not PostgreSQL")
        print("   Please set DATABASE_URL environment variable")
        return False
    
    try:
        # Test connection
        conn = get_db_connection()
        print("✅ Connected to Supabase PostgreSQL")
        conn.close()
        
        # Initialize schema
        print("\n📋 Creating tables...")
        init_db()
        
        print("\n✅ Schema setup complete!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error setting up schema: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = setup_schema()
    sys.exit(0 if success else 1)
