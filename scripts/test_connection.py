"""
Test Supabase connection with new password
"""
import psycopg2

password = "PEhR2p3tARI915Lz"
project_ref = "dnflpvmertmioebhjzas"
host = "aws-1-ap-south-1.pooler.supabase.com"
port = 5432

print(f"Testing Supabase connection...")
print(f"Host: {host}")
print(f"Port: {port}")
print(f"User: postgres.{project_ref}")
print(f"Password: {password}")
print()

try:
    conn = psycopg2.connect(
        host=host,
        port=port,
        user=f"postgres.{project_ref}",
        password=password,
        database="postgres",
        connect_timeout=10,
        sslmode='require'
    )
    print("✅ CONNECTION SUCCESSFUL!")
    
    # Test query
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    version = cursor.fetchone()[0]
    print(f"✅ PostgreSQL Version: {version[:50]}...")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ CONNECTION FAILED: {e}")

