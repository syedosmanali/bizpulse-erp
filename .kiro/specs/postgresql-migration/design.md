# Design Document: PostgreSQL Migration for Render Deployment

## Overview

This design document outlines the technical approach for migrating the BizPulse ERP application from SQLite to PostgreSQL to ensure data persistence on Render's cloud platform. The migration involves updating database connection logic, converting schema definitions, migrating existing data, and ensuring query compatibility across both database systems.

The solution maintains backward compatibility with SQLite for local development while using PostgreSQL in production on Render.

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Flask Application                        │
├─────────────────────────────────────────────────────────────┤
│                  Database Abstraction Layer                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Database Manager (modules/shared/database.py)       │  │
│  │  - Connection Factory                                 │  │
│  │  - Environment Detection                              │  │
│  │  - Query Adapter                                      │  │
│  └──────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│                    Database Drivers                          │
│  ┌──────────────┐              ┌──────────────────────┐    │
│  │   sqlite3    │              │   psycopg2-binary    │    │
│  │ (Local Dev)  │              │   (Production)       │    │
│  └──────────────┘              └──────────────────────┘    │
├─────────────────────────────────────────────────────────────┤
│                      Databases                               │
│  ┌──────────────┐              ┌──────────────────────┐    │
│  │ billing.db   │              │ Render PostgreSQL    │    │
│  │  (SQLite)    │              │    (Cloud)           │    │
│  └──────────────┘              └──────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### Migration Flow

```
┌──────────────┐
│  SQLite DB   │
│ (billing.db) │
└──────┬───────┘
       │
       │ 1. Read Schema
       │ 2. Read Data
       ▼
┌──────────────────┐
│ Migration Script │
│  - Schema Conv.  │
│  - Data Transfer │
│  - Validation    │
└──────┬───────────┘
       │
       │ 3. Create Tables
       │ 4. Insert Data
       ▼
┌──────────────────┐
│  PostgreSQL DB   │
│  (Render Cloud)  │
└──────────────────┘
```

## Components and Interfaces

### 1. Database Connection Manager

**File:** `modules/shared/database.py`

**Responsibilities:**
- Detect environment (local vs production)
- Create appropriate database connections
- Provide unified interface for both SQLite and PostgreSQL
- Handle connection pooling for PostgreSQL

**Key Functions:**

```python
def get_db_connection():
    """
    Returns database connection based on environment.
    - Production (DATABASE_URL set): PostgreSQL connection
    - Local (no DATABASE_URL): SQLite connection
    """
    
def get_database_url():
    """
    Retrieves DATABASE_URL from environment variables.
    Returns None if not set (local development).
    """
    
def init_db():
    """
    Initializes database schema.
    Creates all tables with appropriate SQL for current database type.
    """
```

### 2. Schema Converter

**File:** `scripts/schema_converter.py` (new file)

**Responsibilities:**
- Convert SQLite CREATE TABLE statements to PostgreSQL syntax
- Map SQLite data types to PostgreSQL equivalents
- Handle AUTOINCREMENT → SERIAL conversion
- Preserve foreign keys and indexes

**Type Mappings:**

| SQLite Type | PostgreSQL Type |
|-------------|-----------------|
| TEXT | VARCHAR(255) or TEXT |
| INTEGER | INTEGER |
| REAL | NUMERIC(10,2) or DOUBLE PRECISION |
| BOOLEAN | BOOLEAN |
| TIMESTAMP | TIMESTAMP |
| DATE | DATE |
| TIME | TIME |

**Key Functions:**

```python
def convert_create_table_statement(sqlite_sql: str) -> str:
    """
    Converts SQLite CREATE TABLE to PostgreSQL syntax.
    Handles type conversions and AUTOINCREMENT.
    """
    
def extract_table_schema(conn) -> dict:
    """
    Extracts all table schemas from SQLite database.
    Returns dict mapping table names to CREATE statements.
    """
```

### 3. Data Migration Tool

**File:** `scripts/migrate_to_postgres.py` (new file)

**Responsibilities:**
- Read all data from SQLite tables
- Insert data into PostgreSQL tables
- Handle errors gracefully
- Provide migration progress and summary

**Key Functions:**

```python
def migrate_table_data(sqlite_conn, postgres_conn, table_name: str):
    """
    Migrates all records from SQLite table to PostgreSQL table.
    Preserves primary keys and handles foreign key dependencies.
    """
    
def get_table_names(conn) -> list:
    """
    Returns list of all table names in database.
    """
    
def verify_migration(sqlite_conn, postgres_conn) -> dict:
    """
    Compares record counts between SQLite and PostgreSQL.
    Returns dict with table names and count differences.
    """
```

### 4. Query Adapter

**File:** `modules/shared/query_adapter.py` (new file)

**Responsibilities:**
- Adapt SQL queries for different database systems
- Convert placeholder syntax (? → %s)
- Handle database-specific functions

**Key Functions:**

```python
def adapt_query(query: str, db_type: str) -> str:
    """
    Adapts SQL query for target database type.
    Converts placeholders and database-specific syntax.
    """
    
def get_db_type() -> str:
    """
    Returns current database type ('sqlite' or 'postgresql').
    """
```

### 5. Environment Configuration

**File:** `.env` and `render.yaml`

**Environment Variables:**

```bash
# Production (Render)
DATABASE_URL=postgresql://user:password@host:port/database

# Local Development (optional, defaults to SQLite)
# DATABASE_URL not set → uses billing.db
```

**Render Configuration:**

```yaml
databases:
  - name: bizpulse-db
    databaseName: bizpulse_erp
    user: bizpulse_user
    plan: free

services:
  - type: web
    name: bizpulse-erp
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn app:app
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: bizpulse-db
          property: connectionString
```

## Data Models

### Connection Configuration

```python
class DatabaseConfig:
    """Configuration for database connection"""
    db_type: str  # 'sqlite' or 'postgresql'
    connection_string: str
    pool_size: int = 5  # For PostgreSQL only
    max_overflow: int = 10  # For PostgreSQL only
```

### Migration Status

```python
class MigrationStatus:
    """Tracks migration progress"""
    table_name: str
    total_records: int
    migrated_records: int
    failed_records: int
    status: str  # 'pending', 'in_progress', 'completed', 'failed'
    error_message: str = None
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Connection Type Consistency

*For any* application startup, if DATABASE_URL environment variable is set, then the database connection type should be PostgreSQL, otherwise it should be SQLite.

**Validates: Requirements 1.2, 1.3**

### Property 2: Schema Equivalence

*For any* table in SQLite, after schema conversion, the PostgreSQL table should have the same number of columns with equivalent data types.

**Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5, 2.6**

### Property 3: Data Preservation

*For any* table migration, the number of records in PostgreSQL should equal the number of records in SQLite after successful migration.

**Validates: Requirements 3.1, 3.2, 3.4**

### Property 4: Foreign Key Integrity

*For any* foreign key relationship in SQLite, the same relationship should exist in PostgreSQL after migration, and all foreign key references should remain valid.

**Validates: Requirements 2.7, 3.5**

### Property 5: Primary Key Preservation

*For any* record with a primary key in SQLite, the same primary key value should exist in PostgreSQL after migration.

**Validates: Requirements 3.4**

### Property 6: Query Placeholder Conversion

*For any* SQL query using SQLite placeholders (?), after adaptation, the query should use PostgreSQL placeholders (%s) in the correct positions.

**Validates: Requirements 7.5**

### Property 7: Environment Variable Fallback

*For any* application startup without DATABASE_URL set, the system should successfully connect to SQLite without errors.

**Validates: Requirements 4.2**

### Property 8: Connection String Parsing

*For any* valid PostgreSQL connection string in DATABASE_URL, the system should successfully extract host, port, username, password, and database name.

**Validates: Requirements 4.3, 4.4**

### Property 9: Data Persistence After Restart

*For any* data written to PostgreSQL before a Render service restart, the same data should be retrievable after the restart.

**Validates: Requirements 5.4**

### Property 10: CRUD Operations Equivalence

*For any* CRUD operation (Create, Read, Update, Delete) that works on SQLite, the same operation should work on PostgreSQL with equivalent results.

**Validates: Requirements 8.2**

## Error Handling

### Connection Errors

**Scenario:** PostgreSQL connection fails
- **Action:** Log detailed error with connection parameters (excluding password)
- **Fallback:** Raise exception with clear message for debugging
- **User Impact:** Application fails to start with informative error

### Migration Errors

**Scenario:** Data migration fails for specific records
- **Action:** Log failed record details and continue with remaining records
- **Fallback:** Complete migration of successful records
- **User Impact:** Migration summary shows failed records count

### Query Errors

**Scenario:** SQL query fails due to syntax incompatibility
- **Action:** Log query and error details
- **Fallback:** Raise exception to prevent data corruption
- **User Impact:** Operation fails with error message

### Environment Configuration Errors

**Scenario:** DATABASE_URL is malformed
- **Action:** Validate connection string format
- **Fallback:** Raise clear error message with expected format
- **User Impact:** Application fails to start with helpful error

## Testing Strategy

### Unit Tests

**Test Coverage:**
1. Database connection factory (SQLite vs PostgreSQL selection)
2. Schema conversion functions (type mapping)
3. Query adapter (placeholder conversion)
4. Environment variable parsing
5. Connection string validation

**Example Unit Tests:**
- Test SQLite connection when DATABASE_URL is not set
- Test PostgreSQL connection when DATABASE_URL is valid
- Test schema converter with various SQLite CREATE TABLE statements
- Test query adapter with different placeholder patterns
- Test connection string parser with valid and invalid URLs

### Property-Based Tests

**Test Coverage:**
1. Schema conversion preserves column count and types
2. Data migration preserves record count
3. Primary key values remain unchanged after migration
4. Foreign key relationships remain valid after migration
5. Query placeholder conversion maintains parameter order

**Property Test Configuration:**
- Minimum 100 iterations per test
- Use random table schemas and data
- Test with various connection string formats

**Example Property Tests:**

```python
# Property 3: Data Preservation
@given(table_data=lists(dictionaries(keys=text(), values=integers())))
def test_data_preservation(table_data):
    """
    Feature: postgresql-migration, Property 3: Data Preservation
    For any table migration, record count should be preserved.
    """
    # Create temp SQLite table with random data
    # Migrate to temp PostgreSQL table
    # Assert: len(sqlite_records) == len(postgres_records)
```

### Integration Tests

**Test Coverage:**
1. End-to-end migration from SQLite to PostgreSQL
2. Application startup with PostgreSQL connection
3. CRUD operations on PostgreSQL
4. Data persistence after simulated restart

**Test Environment:**
- Use Docker containers for PostgreSQL
- Create temporary test databases
- Clean up after each test

### Manual Testing on Render

**Test Steps:**
1. Provision PostgreSQL database on Render
2. Deploy application with DATABASE_URL configured
3. Run migration script
4. Verify data in PostgreSQL
5. Create new billing records
6. Restart Render service
7. Verify data persists after restart

## Implementation Notes

### Backward Compatibility

The solution maintains backward compatibility with SQLite for local development:
- No DATABASE_URL → SQLite connection
- DATABASE_URL set → PostgreSQL connection
- All existing code continues to work without changes

### Performance Considerations

**PostgreSQL Connection Pooling:**
- Use connection pool to handle concurrent requests
- Configure pool size based on Render plan limits
- Implement connection timeout and retry logic

**Migration Performance:**
- Batch insert operations for large tables
- Use transactions for data consistency
- Provide progress indicators for long migrations

### Security Considerations

**Credential Management:**
- Never hardcode database credentials
- Use environment variables for all sensitive data
- Render automatically provides secure DATABASE_URL

**SQL Injection Prevention:**
- Continue using parameterized queries
- Validate and sanitize all user inputs
- Use ORM or query builder where appropriate

## Deployment Steps

### Step 1: Provision PostgreSQL on Render

1. Log in to Render dashboard
2. Create new PostgreSQL database
3. Select free tier plan
4. Note the DATABASE_URL provided

### Step 2: Update Application Code

1. Add psycopg2-binary to requirements.txt
2. Update database.py with PostgreSQL support
3. Create migration scripts
4. Test locally with PostgreSQL (optional)

### Step 3: Deploy to Render

1. Push code changes to Git repository
2. Render automatically deploys new version
3. DATABASE_URL is automatically injected

### Step 4: Run Migration

1. Connect to Render shell or run migration script
2. Execute migration from SQLite to PostgreSQL
3. Verify migration success
4. Test application functionality

### Step 5: Verify Data Persistence

1. Create test billing records
2. Restart Render service
3. Verify records still exist
4. Monitor application logs

## Rollback Plan

If migration fails or issues arise:

1. **Immediate Rollback:** Revert to previous Git commit
2. **Data Recovery:** SQLite backup file remains unchanged
3. **Re-migration:** Fix issues and re-run migration script
4. **Gradual Migration:** Migrate tables incrementally if needed

## Future Enhancements

1. **Database Migrations Framework:** Use Alembic or Flask-Migrate for schema versioning
2. **Read Replicas:** Add read replicas for improved performance
3. **Backup Automation:** Implement automated PostgreSQL backups
4. **Monitoring:** Add database performance monitoring and alerts
5. **Connection Pooling:** Optimize connection pool configuration based on usage patterns
