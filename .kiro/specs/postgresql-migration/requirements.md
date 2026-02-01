# Requirements Document: PostgreSQL Migration for Render Deployment

## Introduction

This document outlines the requirements for migrating the BizPulse ERP billing software from SQLite to PostgreSQL database to ensure data persistence on Render's cloud platform. Currently, the application uses SQLite with a local file (`billing.db`) which gets reset on every service restart due to Render's ephemeral filesystem, causing all billing data to disappear.

## Glossary

- **System**: The BizPulse ERP billing application
- **Database_Manager**: The database connection and initialization module
- **Migration_Tool**: The utility that transfers data from SQLite to PostgreSQL
- **Render_Service**: The cloud hosting platform where the application is deployed
- **Connection_Pool**: PostgreSQL connection management system
- **Environment_Config**: Configuration system for database credentials

## Requirements

### Requirement 1: Database Connection Management

**User Story:** As a developer, I want to switch from SQLite to PostgreSQL connection, so that the application can use a persistent database on Render.

#### Acceptance Criteria

1. WHEN the application starts, THE Database_Manager SHALL establish a connection to PostgreSQL using environment variables
2. WHEN DATABASE_URL environment variable is present, THE Database_Manager SHALL use PostgreSQL connection
3. WHEN DATABASE_URL is not present, THE Database_Manager SHALL fall back to SQLite for local development
4. THE Database_Manager SHALL use connection pooling for PostgreSQL to handle multiple concurrent requests
5. WHEN a database query fails, THE Database_Manager SHALL log the error and raise an appropriate exception

### Requirement 2: Schema Migration

**User Story:** As a developer, I want to recreate all SQLite tables in PostgreSQL, so that the database schema is compatible with the new database system.

#### Acceptance Criteria

1. THE System SHALL create all existing tables in PostgreSQL with equivalent data types
2. WHEN SQLite uses TEXT PRIMARY KEY, THE System SHALL convert it to VARCHAR(255) PRIMARY KEY in PostgreSQL
3. WHEN SQLite uses INTEGER, THE System SHALL convert it to INTEGER in PostgreSQL
4. WHEN SQLite uses REAL, THE System SHALL convert it to NUMERIC or DOUBLE PRECISION in PostgreSQL
5. WHEN SQLite uses BOOLEAN, THE System SHALL convert it to BOOLEAN in PostgreSQL
6. WHEN SQLite uses TIMESTAMP, THE System SHALL convert it to TIMESTAMP in PostgreSQL
7. THE System SHALL preserve all foreign key relationships in PostgreSQL
8. THE System SHALL create all indexes that exist in SQLite schema

### Requirement 3: Data Migration

**User Story:** As a system administrator, I want to migrate existing data from SQLite to PostgreSQL, so that no historical data is lost during the transition.

#### Acceptance Criteria

1. THE Migration_Tool SHALL read all records from each SQLite table
2. THE Migration_Tool SHALL insert all records into corresponding PostgreSQL tables
3. WHEN data migration encounters an error, THE Migration_Tool SHALL log the error and continue with remaining records
4. THE Migration_Tool SHALL preserve all primary key values during migration
5. THE Migration_Tool SHALL preserve all foreign key relationships during migration
6. WHEN migration completes, THE Migration_Tool SHALL display a summary of migrated records per table

### Requirement 4: Environment Configuration

**User Story:** As a developer, I want to configure database credentials via environment variables, so that sensitive information is not hardcoded in the application.

#### Acceptance Criteria

1. THE Environment_Config SHALL read DATABASE_URL from environment variables
2. WHEN DATABASE_URL is not set, THE Environment_Config SHALL use default SQLite path for local development
3. THE System SHALL support PostgreSQL connection string format: `postgresql://user:password@host:port/database`
4. THE System SHALL parse DATABASE_URL to extract host, port, username, password, and database name
5. WHEN environment variables are missing in production, THE System SHALL raise a clear error message

### Requirement 5: Render PostgreSQL Provisioning

**User Story:** As a system administrator, I want to provision a PostgreSQL database on Render, so that the application has a persistent data store.

#### Acceptance Criteria

1. WHEN creating a PostgreSQL instance on Render, THE Render_Service SHALL provide a DATABASE_URL connection string
2. THE Render_Service SHALL provide a free-tier PostgreSQL database with sufficient storage for the application
3. THE System SHALL connect to Render PostgreSQL using the provided DATABASE_URL
4. WHEN the Render service restarts, THE System SHALL reconnect to the same PostgreSQL database without data loss

### Requirement 6: Dependency Management

**User Story:** As a developer, I want to add PostgreSQL driver dependencies, so that the application can communicate with PostgreSQL database.

#### Acceptance Criteria

1. THE System SHALL include `psycopg2-binary` package in requirements.txt
2. WHEN installing dependencies, THE System SHALL install PostgreSQL adapter for Python
3. THE System SHALL maintain backward compatibility with SQLite for local development
4. WHEN deploying to Render, THE System SHALL use only PostgreSQL-compatible code

### Requirement 7: Query Compatibility

**User Story:** As a developer, I want to ensure all SQL queries work with PostgreSQL, so that the application functions correctly after migration.

#### Acceptance Criteria

1. WHEN using AUTOINCREMENT in SQLite, THE System SHALL use SERIAL or GENERATED ALWAYS AS IDENTITY in PostgreSQL
2. WHEN using datetime functions, THE System SHALL use PostgreSQL-compatible syntax
3. WHEN using CURRENT_TIMESTAMP, THE System SHALL ensure it works in both SQLite and PostgreSQL
4. THE System SHALL replace SQLite-specific functions with PostgreSQL equivalents where necessary
5. WHEN executing parameterized queries, THE System SHALL use `%s` placeholders for PostgreSQL instead of `?`

### Requirement 8: Testing and Validation

**User Story:** As a developer, I want to test the PostgreSQL migration, so that I can verify data integrity and application functionality.

#### Acceptance Criteria

1. WHEN migration completes, THE System SHALL verify record counts match between SQLite and PostgreSQL
2. THE System SHALL test all CRUD operations (Create, Read, Update, Delete) on PostgreSQL
3. WHEN running the application with PostgreSQL, THE System SHALL successfully create new bills
4. WHEN the Render service restarts, THE System SHALL retain all previously created data
5. THE System SHALL log all database operations for debugging purposes
