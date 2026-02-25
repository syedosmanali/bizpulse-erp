# Database Schema Documentation

## Overview

The BizPulse24 ERP backend uses PostgreSQL (via Supabase) with a normalized schema design following third normal form (3NF). All tables use UUID primary keys and include comprehensive audit fields.

## Core Tables

### 1. Companies Table

Stores company profile information including GST and PAN details for tax compliance.

**Table Name:** `companies`

**Columns:**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique identifier |
| name | VARCHAR(255) | NOT NULL | Company name |
| gstin | VARCHAR(15) | UNIQUE | GST Identification Number (15 chars) |
| pan | VARCHAR(10) | | Permanent Account Number |
| address | TEXT | | Company address |
| city | VARCHAR(100) | | City name |
| state | VARCHAR(100) | | State for GST classification |
| pincode | VARCHAR(10) | | Postal code |
| phone | VARCHAR(20) | | Contact phone number |
| email | VARCHAR(255) | | Contact email |
| logo_url | TEXT | | URL to company logo |
| created_at | TIMESTAMP | DEFAULT NOW() | Record creation timestamp |
| updated_at | TIMESTAMP | DEFAULT NOW() | Last update timestamp (auto-updated) |
| created_by | UUID | FK to auth.users | User who created the record |
| updated_by | UUID | FK to auth.users | User who last updated the record |

**Indexes:**
- `idx_companies_gstin` on `gstin` - Fast GSTIN lookups
- `idx_companies_name` on `name` - Company name searches

**Requirements Mapping:**
- Requirement 1.1: Company profile storage
- Requirement 1.2: Single active company per tenant
- Requirement 1.3: GSTIN validation and storage

**Business Rules:**
- GSTIN must be unique across all companies
- GSTIN format: 15 alphanumeric characters
- State field is used for GST classification (intra-state vs inter-state)

---

### 2. Financial Years Table

Manages accounting periods with locking capability to prevent modifications to closed periods.

**Table Name:** `financial_years`

**Columns:**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique identifier |
| company_id | UUID | NOT NULL, FK to companies | Company reference |
| name | VARCHAR(100) | NOT NULL | Financial year name (e.g., "FY 2024-25") |
| start_date | DATE | NOT NULL | Period start date |
| end_date | DATE | NOT NULL | Period end date |
| is_locked | BOOLEAN | DEFAULT FALSE | Lock status |
| created_at | TIMESTAMP | DEFAULT NOW() | Record creation timestamp |
| updated_at | TIMESTAMP | DEFAULT NOW() | Last update timestamp (auto-updated) |
| created_by | UUID | FK to auth.users | User who created the record |
| updated_by | UUID | FK to auth.users | User who last updated the record |

**Constraints:**
- `check_date_range`: Ensures `end_date > start_date`
- `unique_fy_dates`: Prevents overlapping periods for same company (company_id, start_date, end_date)

**Indexes:**
- `idx_fy_company` on `company_id` - Company financial years lookup
- `idx_fy_dates` on `(start_date, end_date)` - Date range queries
- `idx_fy_locked` on `is_locked` - Filter locked periods

**Requirements Mapping:**
- Requirement 2.1: Financial year creation with date ranges
- Requirement 2.2: Non-overlapping date ranges enforcement
- Requirement 2.3: Lock status to prevent modifications
- Requirement 2.5: Database-level lock enforcement

**Business Rules:**
- When `is_locked = TRUE`, all create/update/delete operations for transactions in this period are rejected
- Date ranges cannot overlap for the same company
- End date must be after start date
- Typically represents a 12-month accounting period

---

### 3. User Roles Table

Manages role-based access control (RBAC) mapping users to companies with specific permission levels.

**Table Name:** `user_roles`

**Columns:**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique identifier |
| user_id | UUID | NOT NULL, FK to auth.users | User reference |
| company_id | UUID | NOT NULL, FK to companies | Company reference |
| role | VARCHAR(20) | NOT NULL, CHECK | User role (OWNER/ADMIN/STAFF) |
| created_at | TIMESTAMP | DEFAULT NOW() | Record creation timestamp |
| updated_at | TIMESTAMP | DEFAULT NOW() | Last update timestamp (auto-updated) |

**Constraints:**
- `unique_user_company`: Ensures one role per user per company (user_id, company_id)
- CHECK constraint: `role IN ('OWNER', 'ADMIN', 'STAFF')`

**Indexes:**
- `idx_user_roles_user` on `user_id` - User's roles lookup
- `idx_user_roles_company` on `company_id` - Company users lookup
- `idx_user_roles_role` on `role` - Filter by role type

**Requirements Mapping:**
- Requirement 3.1: Three role types (OWNER, ADMIN, STAFF)
- Requirement 3.2: RLS policy enforcement based on roles
- Requirement 3.3: OWNER - full access
- Requirement 3.4: ADMIN - all modules except company setup
- Requirement 3.5: STAFF - limited access

**Role Permissions:**

| Role | Permissions |
|------|-------------|
| OWNER | Full access to all modules and operations including company setup and user management |
| ADMIN | Access to all modules except company setup and user management |
| STAFF | Read-only access to reports, limited write access to Sales and Inventory modules |

---

## Database Features

### UUID Primary Keys

All tables use UUID (Universally Unique Identifier) as primary keys instead of auto-incrementing integers.

**Benefits:**
- Better distribution across sharded databases
- No sequential ID guessing attacks
- Can generate IDs client-side
- Easier data merging from multiple sources

**Implementation:**
```sql
id UUID PRIMARY KEY DEFAULT gen_random_uuid()
```

### Audit Fields

All tables include four audit fields for tracking record lifecycle:

| Field | Type | Purpose |
|-------|------|---------|
| created_at | TIMESTAMP | When the record was created |
| updated_at | TIMESTAMP | When the record was last modified (auto-updated via trigger) |
| created_by | UUID | User who created the record |
| updated_by | UUID | User who last modified the record |

**Auto-Update Trigger:**
```sql
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';
```

### Foreign Key Constraints

All relationships are enforced with foreign key constraints:

- `companies.created_by` → `auth.users.id`
- `companies.updated_by` → `auth.users.id`
- `financial_years.company_id` → `companies.id` (CASCADE DELETE)
- `financial_years.created_by` → `auth.users.id`
- `financial_years.updated_by` → `auth.users.id`
- `user_roles.user_id` → `auth.users.id` (CASCADE DELETE)
- `user_roles.company_id` → `companies.id` (CASCADE DELETE)

**CASCADE DELETE:** When a company is deleted, all related financial years and user roles are automatically deleted.

### Indexes

Indexes are strategically placed on:
- Primary keys (automatic)
- Foreign keys for join performance
- Frequently queried fields (GSTIN, dates)
- Fields used in WHERE clauses

### Check Constraints

Data validation at database level:
- Financial year date ranges: `end_date > start_date`
- User roles: `role IN ('OWNER', 'ADMIN', 'STAFF')`

### Unique Constraints

Prevent duplicate data:
- `companies.gstin` - One GSTIN per company
- `financial_years(company_id, start_date, end_date)` - No overlapping periods
- `user_roles(user_id, company_id)` - One role per user per company

---

## Migration Files

### 000_init_core_schema.sql
Complete initialization script with all core tables, indexes, triggers, and constraints.

### 001_core_tables.sql
Original migration file (kept for compatibility).

### 002_rls_policies.sql
Row Level Security policies for multi-tenancy (separate file).

---

## Running Migrations

### Option 1: Using npm scripts
```bash
npm run migrate
```

### Option 2: Using shell script (Linux/Mac)
```bash
npm run migrate:sh
```

### Option 3: Using batch script (Windows)
```bash
npm run migrate:bat
```

### Option 4: Manual execution
```bash
psql $DATABASE_URL -f prisma/migrations/000_init_core_schema.sql
```

---

## Verification Queries

After running migrations, verify the setup:

```sql
-- Check if all tables exist
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('companies', 'financial_years', 'user_roles');

-- Check if all indexes exist
SELECT indexname, tablename 
FROM pg_indexes 
WHERE schemaname = 'public' 
AND tablename IN ('companies', 'financial_years', 'user_roles');

-- Check if all triggers exist
SELECT trigger_name, event_object_table 
FROM information_schema.triggers 
WHERE trigger_schema = 'public' 
AND event_object_table IN ('companies', 'financial_years', 'user_roles');

-- Check if all constraints exist
SELECT constraint_name, table_name, constraint_type 
FROM information_schema.table_constraints 
WHERE table_schema = 'public' 
AND table_name IN ('companies', 'financial_years', 'user_roles');
```

---

## Next Steps

After core tables are set up:

1. Run RLS policies migration (`002_rls_policies.sql`)
2. Create Inventory module tables
3. Create Party module tables
4. Create Sales module tables
5. Create Purchase module tables
6. Create Finance module tables

---

## Requirements Traceability

| Requirement | Table | Implementation |
|-------------|-------|----------------|
| 1.1 | companies | Company profile storage |
| 1.2 | companies | Single active company per tenant |
| 1.3 | companies | GSTIN validation and storage |
| 2.1 | financial_years | Financial year with date ranges |
| 2.2 | financial_years | Non-overlapping constraint |
| 2.3 | financial_years | is_locked field |
| 2.5 | financial_years | Database triggers for lock enforcement |
| 3.1 | user_roles | Three role types |
| 3.2 | user_roles | RLS policy base |
| 19.1 | All tables | UUID primary keys |
| 19.4 | All tables | Audit fields (created_at, updated_at, created_by, updated_by) |

---

## Support

For issues or questions about the database schema:
1. Check the migration README: `prisma/migrations/README.md`
2. Review the design document: `.kiro/specs/bizpulse24-erp-backend/design.md`
3. Check requirements: `.kiro/specs/bizpulse24-erp-backend/requirements.md`
