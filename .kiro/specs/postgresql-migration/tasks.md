# Implementation Plan: PostgreSQL Migration for Render Deployment

## Overview

This implementation plan outlines the step-by-step tasks to migrate the BizPulse ERP application from SQLite to PostgreSQL for deployment on Render. The migration ensures data persistence by moving from ephemeral filesystem storage to a cloud-hosted PostgreSQL database.

## Tasks

- [x] 1. Add PostgreSQL dependencies and update requirements
  - Add `psycopg2-binary` to requirements.txt for PostgreSQL support
  - Ensure all existing dependencies remain compatible
  - _Requirements: 6.1, 6.2_

- [x] 2. Create database connection abstraction layer
  - [x] 2.1 Update `modules/shared/database.py` to support both SQLite and PostgreSQL
    - Add environment detection logic (check for DATABASE_URL)
    - Create connection factory that returns appropriate connection type
    - Implement PostgreSQL connection with connection pooling
    - Maintain backward compatibility with SQLite for local development
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 4.1, 4.2, 4.3, 4.4_

  - [x] 2.2 Write property test for connection type selection
    - **Property 1: Connection Type Consistency**
    - **Validates: Requirements 1.2, 1.3**

  - [x] 2.3 Write unit tests for connection factory
    - Test SQLite connection when DATABASE_URL is not set
    - Test PostgreSQL connection when DATABASE_URL is valid
    - Test connection string parsing
    - _Requirements: 1.1, 1.2, 1.3, 4.3, 4.4_

- [x] 3. Create schema conversion utility
  - [x] 3.1 Create `scripts/schema_converter.py`
    - Implement function to extract SQLite table schemas
    - Implement SQLite to PostgreSQL type mapping
    - Convert AUTOINCREMENT to SERIAL
    - Handle TEXT PRIMARY KEY to VARCHAR(255) PRIMARY KEY conversion
    - Preserve foreign key constraints
    - Preserve indexes
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 7.1_

  - [x] 3.2 Write property test for schema equivalence
    - **Property 2: Schema Equivalence**
    - **Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5, 2.6**

  - [x] 3.3 Write unit tests for type conversion
    - Test each SQLite type maps to correct PostgreSQL type
    - Test AUTOINCREMENT conversion
    - Test foreign key preservation
    - _Requirements: 2.2, 2.3, 2.4, 2.5, 2.6, 2.7_

- [x] 4. Update database initialization for PostgreSQL compatibility
  - [x] 4.1 Modify `init_db()` function in `modules/shared/database.py`
    - Detect database type (SQLite vs PostgreSQL)
    - Use appropriate SQL syntax for each database type
    - Replace SQLite-specific syntax with PostgreSQL equivalents
    - Handle AUTOINCREMENT vs SERIAL differences
    - Ensure all CREATE TABLE statements work on both databases
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 7.1, 7.2, 7.3_

  - [x] 4.2 Write unit tests for init_db with PostgreSQL
    - Test table creation on PostgreSQL
    - Verify all tables are created successfully
    - _Requirements: 2.1_

- [x] 5. Create data migration script
  - [x] 5.1 Create `scripts/migrate_to_postgres.py`
    - Implement function to get all table names from SQLite
    - Implement function to read all records from SQLite table
    - Implement function to insert records into PostgreSQL table
    - Handle migration errors gracefully (log and continue)
    - Preserve primary key values during migration
    - Respect foreign key dependencies (migrate parent tables first)
    - Display migration progress and summary
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6_

  - [x] 5.2 Write property test for data preservation
    - **Property 3: Data Preservation**
    - **Validates: Requirements 3.1, 3.2, 3.4**

  - [x] 5.3 Write property test for primary key preservation
    - **Property 5: Primary Key Preservation**
    - **Validates: Requirements 3.4**

  - [x] 5.4 Write property test for foreign key integrity
    - **Property 4: Foreign Key Integrity**
    - **Validates: Requirements 2.7, 3.5**

  - [x] 5.5 Write unit tests for migration script
    - Test table data migration with sample data
    - Test error handling for failed records
    - Test migration summary generation
    - _Requirements: 3.1, 3.2, 3.3, 3.6_

- [x] 6. Checkpoint - Test migration locally with PostgreSQL
  - Set up local PostgreSQL instance (Docker or native)
  - Run migration script from SQLite to local PostgreSQL
  - Verify all tables and data migrated successfully
  - Test application with local PostgreSQL connection
  - Ensure all tests pass, ask the user if questions arise.

- [x] 7. Create query adapter for placeholder conversion
  - [x] 7.1 Create `modules/shared/query_adapter.py`
    - Implement function to detect database type
    - Implement function to convert ? placeholders to %s for PostgreSQL
    - Handle queries with multiple placeholders
    - Preserve placeholder order
    - _Requirements: 7.5_

  - [x] 7.2 Write property test for query placeholder conversion
    - **Property 6: Query Placeholder Conversion**
    - **Validates: Requirements 7.5**

  - [x] 7.3 Write unit tests for query adapter
    - Test placeholder conversion with various query patterns
    - Test queries with no placeholders
    - Test queries with multiple placeholders
    - _Requirements: 7.5_

- [x] 8. Update all database queries for PostgreSQL compatibility
  - [x] 8.1 Scan codebase for SQLite-specific queries
    - Search for queries using ? placeholders
    - Search for SQLite-specific datetime functions
    - Search for AUTOINCREMENT usage
    - _Requirements: 7.1, 7.2, 7.3, 7.5_

  - [x] 8.2 Update queries to be database-agnostic
    - Replace ? with %s for PostgreSQL or use query adapter
    - Replace SQLite datetime functions with compatible alternatives
    - Test each updated query on both SQLite and PostgreSQL
    - _Requirements: 7.2, 7.3, 7.4, 7.5_

  - [x] 8.3 Write integration tests for CRUD operations
    - Test Create, Read, Update, Delete on PostgreSQL
    - Verify operations produce same results as SQLite
    - _Requirements: 8.2_

- [x] 9. Create Render configuration files
  - [x] 9.1 Create or update `render.yaml`
    - Define PostgreSQL database resource
    - Configure database name, user, and plan (free tier)
    - Define web service configuration
    - Link DATABASE_URL environment variable to PostgreSQL connection string
    - _Requirements: 5.1, 5.2, 5.3_

  - [x] 9.2 Update `.env.example` with DATABASE_URL
    - Add DATABASE_URL example for PostgreSQL
    - Document connection string format
    - Add comments for local vs production usage
    - _Requirements: 4.1, 4.3_

- [x] 10. Create migration documentation
  - [x] 10.1 Create `docs/postgresql_migration_guide.md`
    - Document step-by-step migration process
    - Include Render PostgreSQL provisioning steps
    - Include migration script usage instructions
    - Include troubleshooting tips
    - Include rollback procedures
    - _Requirements: 5.1, 5.2, 5.3, 5.4_

- [x] 11. Checkpoint - Deploy to Render and run migration
  - Provision PostgreSQL database on Render
  - Deploy application to Render
  - Verify DATABASE_URL is set correctly
  - Run migration script on Render
  - Verify all data migrated successfully
  - Ensure all tests pass, ask the user if questions arise.

- [x] 12. Validate data persistence after deployment
  - [x] 12.1 Test data persistence on Render
    - Create new billing records through the application
    - Restart Render service manually
    - Verify billing records still exist after restart
    - Test all CRUD operations work correctly
    - _Requirements: 5.4, 8.3, 8.4_

  - [x] 12.2 Write property test for data persistence
    - **Property 9: Data Persistence After Restart**
    - **Validates: Requirements 5.4**

  - [x] 12.3 Write integration test for CRUD equivalence
    - **Property 10: CRUD Operations Equivalence**
    - **Validates: Requirements 8.2**

- [x] 13. Add error handling and logging
  - [x] 13.1 Add comprehensive error handling
    - Add try-catch blocks for database connections
    - Add error logging for failed queries
    - Add clear error messages for configuration issues
    - Handle connection timeouts and retries
    - _Requirements: 1.5, 3.3, 4.5_

  - [x] 13.2 Write unit tests for error handling
    - Test connection failure scenarios
    - Test malformed DATABASE_URL handling
    - Test query error handling
    - _Requirements: 1.5, 4.5_

- [x] 14. Final checkpoint - Verify complete migration
  - Run all unit tests and property tests
  - Verify application works on both SQLite (local) and PostgreSQL (Render)
  - Test all major features (billing, products, customers, reports)
  - Verify no data loss after multiple Render restarts
  - Document any issues or limitations
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties
- Unit tests validate specific examples and edge cases
- The migration maintains backward compatibility with SQLite for local development
- All sensitive credentials are managed via environment variables
- Render automatically provides DATABASE_URL when PostgreSQL is provisioned
