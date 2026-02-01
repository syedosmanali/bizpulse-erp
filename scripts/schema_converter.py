"""
Schema Converter: SQLite to PostgreSQL
Converts SQLite CREATE TABLE statements to PostgreSQL syntax
"""

import re
import sqlite3
from typing import Dict, List, Tuple

# Type mapping from SQLite to PostgreSQL
TYPE_MAPPINGS = {
    'TEXT': 'TEXT',
    'INTEGER': 'INTEGER',
    'REAL': 'NUMERIC(10,2)',
    'BOOLEAN': 'BOOLEAN',
    'TIMESTAMP': 'TIMESTAMP',
    'DATE': 'DATE',
    'TIME': 'TIME',
}

def convert_data_type(sqlite_type: str) -> str:
    """
    Convert SQLite data type to PostgreSQL equivalent
    """
    sqlite_type = sqlite_type.upper().strip()
    
    # Handle TEXT PRIMARY KEY
    if 'TEXT' in sqlite_type and 'PRIMARY KEY' in sqlite_type:
        return 'VARCHAR(255) PRIMARY KEY'
    
    # Handle specific patterns
    if sqlite_type.startswith('TEXT'):
        return 'TEXT'
    elif sqlite_type.startswith('INTEGER'):
        if 'PRIMARY KEY AUTOINCREMENT' in sqlite_type:
            return 'SERIAL PRIMARY KEY'
        elif 'PRIMARY KEY' in sqlite_type:
            return 'INTEGER PRIMARY KEY'
        return 'INTEGER'
    elif sqlite_type.startswith('REAL'):
        return 'NUMERIC(10,2)'
    elif sqlite_type.startswith('BOOLEAN'):
        return 'BOOLEAN'
    elif sqlite_type.startswith('TIMESTAMP'):
        return 'TIMESTAMP'
    elif sqlite_type.startswith('DATE'):
        return 'DATE'
    elif sqlite_type.startswith('TIME'):
        return 'TIME'
    
    # Default to TEXT if unknown
    return 'TEXT'

def convert_default_value(default_val: str, col_type: str) -> str:
    """
    Convert SQLite default values to PostgreSQL format
    """
    if not default_val:
        return default_val
    
    # Handle BOOLEAN defaults
    if 'BOOLEAN' in col_type.upper():
        if default_val in ['0', 'FALSE']:
            return 'FALSE'
        elif default_val in ['1', 'TRUE']:
            return 'TRUE'
    
    # Handle CURRENT_TIMESTAMP
    if 'CURRENT_TIMESTAMP' in default_val.upper():
        return 'CURRENT_TIMESTAMP'
    
    # Handle CURRENT_DATE
    if 'CURRENT_DATE' in default_val.upper():
        return 'CURRENT_DATE'
    
    return default_val

def convert_create_table_statement(sqlite_sql: str) -> str:
    """
    Convert SQLite CREATE TABLE statement to PostgreSQL syntax
    
    Handles:
    - Type conversions (TEXT -> VARCHAR, REAL -> NUMERIC, etc.)
    - AUTOINCREMENT -> SERIAL
    - BOOLEAN defaults (0/1 -> FALSE/TRUE)
    - TEXT PRIMARY KEY -> VARCHAR(255) PRIMARY KEY
    """
    # Replace AUTOINCREMENT with SERIAL
    postgres_sql = re.sub(
        r'INTEGER\s+PRIMARY\s+KEY\s+AUTOINCREMENT',
        'SERIAL PRIMARY KEY',
        sqlite_sql,
        flags=re.IGNORECASE
    )
    
    # Replace TEXT PRIMARY KEY with VARCHAR(255) PRIMARY KEY
    postgres_sql = re.sub(
        r'TEXT\s+PRIMARY\s+KEY',
        'VARCHAR(255) PRIMARY KEY',
        postgres_sql,
        flags=re.IGNORECASE
    )
    
    # Replace REAL with NUMERIC(10,2)
    postgres_sql = re.sub(
        r'\bREAL\b',
        'NUMERIC(10,2)',
        postgres_sql,
        flags=re.IGNORECASE
    )
    
    # Replace BOOLEAN DEFAULT 0 with BOOLEAN DEFAULT FALSE
    postgres_sql = re.sub(
        r'BOOLEAN\s+DEFAULT\s+0',
        'BOOLEAN DEFAULT FALSE',
        postgres_sql,
        flags=re.IGNORECASE
    )
    
    # Replace BOOLEAN DEFAULT 1 with BOOLEAN DEFAULT TRUE
    postgres_sql = re.sub(
        r'BOOLEAN\s+DEFAULT\s+1',
        'BOOLEAN DEFAULT TRUE',
        postgres_sql,
        flags=re.IGNORECASE
    )
    
    # Add VARCHAR length to TEXT columns (except TEXT PRIMARY KEY already handled)
    # This is optional - PostgreSQL supports TEXT type
    
    return postgres_sql

def extract_table_schema(db_path: str) -> Dict[str, str]:
    """
    Extract all table schemas from SQLite database
    
    Returns:
        Dict mapping table names to CREATE TABLE statements
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all table names (excluding sqlite internal tables)
    cursor.execute("""
        SELECT name, sql FROM sqlite_master 
        WHERE type='table' AND name NOT LIKE 'sqlite_%'
        ORDER BY name
    """)
    
    tables = {}
    for row in cursor.fetchall():
        table_name = row[0]
        create_sql = row[1]
        if create_sql:  # Some tables might not have SQL (like views)
            tables[table_name] = create_sql
    
    conn.close()
    return tables

def extract_indexes(db_path: str) -> Dict[str, List[str]]:
    """
    Extract all indexes from SQLite database
    
    Returns:
        Dict mapping table names to list of CREATE INDEX statements
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all indexes
    cursor.execute("""
        SELECT name, tbl_name, sql FROM sqlite_master 
        WHERE type='index' AND name NOT LIKE 'sqlite_%'
        ORDER BY tbl_name, name
    """)
    
    indexes = {}
    for row in cursor.fetchall():
        index_name = row[0]
        table_name = row[1]
        create_sql = row[2]
        
        if create_sql:  # Auto-created indexes don't have SQL
            if table_name not in indexes:
                indexes[table_name] = []
            indexes[table_name].append(create_sql)
    
    conn.close()
    return indexes

def convert_schema(sqlite_db_path: str, output_file: str = None) -> str:
    """
    Convert entire SQLite database schema to PostgreSQL
    
    Args:
        sqlite_db_path: Path to SQLite database file
        output_file: Optional path to write PostgreSQL schema file
    
    Returns:
        PostgreSQL schema as string
    """
    print(f"📊 Extracting schema from {sqlite_db_path}...")
    
    # Extract tables
    tables = extract_table_schema(sqlite_db_path)
    print(f"✅ Found {len(tables)} tables")
    
    # Extract indexes
    indexes = extract_indexes(sqlite_db_path)
    print(f"✅ Found {sum(len(idx_list) for idx_list in indexes.values())} indexes")
    
    # Convert schema
    postgres_schema = []
    postgres_schema.append("-- PostgreSQL Schema")
    postgres_schema.append("-- Converted from SQLite")
    postgres_schema.append("-- Generated by schema_converter.py\n")
    
    # Convert tables
    for table_name, create_sql in tables.items():
        postgres_sql = convert_create_table_statement(create_sql)
        postgres_schema.append(f"-- Table: {table_name}")
        postgres_schema.append(postgres_sql + ";")
        postgres_schema.append("")
    
    # Convert indexes
    if indexes:
        postgres_schema.append("-- Indexes")
        for table_name, index_list in indexes.items():
            for index_sql in index_list:
                postgres_schema.append(index_sql + ";")
        postgres_schema.append("")
    
    schema_text = "\n".join(postgres_schema)
    
    # Write to file if specified
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(schema_text)
        print(f"✅ PostgreSQL schema written to {output_file}")
    
    return schema_text

if __name__ == '__main__':
    import sys
    import os
    
    # Get database path
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    else:
        # Default to billing.db in parent directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(os.path.dirname(script_dir), 'billing.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        sys.exit(1)
    
    # Output file
    output_file = 'postgres_schema.sql'
    
    # Convert schema
    schema = convert_schema(db_path, output_file)
    
    print("\n" + "="*50)
    print("Schema conversion complete!")
    print("="*50)
    print(f"\nTo create PostgreSQL database:")
    print(f"1. Create database: createdb bizpulse_erp")
    print(f"2. Run schema: psql bizpulse_erp < {output_file}")
