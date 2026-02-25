# Quick Start Guide - Database Setup

## Prerequisites

- PostgreSQL 14+ or Supabase account
- Node.js 18+
- psql command-line tool (optional)

## Setup Steps

### 1. Configure Environment

Create a `.env` file in the project root:

```env
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# Database Connection
DATABASE_URL=postgresql://postgres:[password]@db.[project].supabase.co:5432/postgres
```

### 2. Run Migrations

Choose one of the following methods:

#### Method A: Using npm (Recommended)
```bash
npm run migrate
```

#### Method B: Using shell script (Linux/Mac)
```bash
chmod +x scripts/migrate.sh
npm run migrate:sh
```

#### Method C: Using batch script (Windows)
```bash
npm run migrate:bat
```

#### Method D: Manual execution via Supabase SQL Editor
1. Open your Supabase project dashboard
2. Go to SQL Editor
3. Copy the contents of `prisma/migrations/000_init_core_schema.sql`
4. Paste and execute

### 3. Verify Setup

Run verification queries in Supabase SQL Editor:

```sql
-- Check tables
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('companies', 'financial_years', 'user_roles');

-- Expected output: 3 rows
```

### 4. Test Connection

Create a test script `test-db.ts`:

```typescript
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(
  process.env.SUPABASE_URL!,
  process.env.SUPABASE_ANON_KEY!
);

async function testConnection() {
  const { data, error } = await supabase
    .from('companies')
    .select('count');
  
  if (error) {
    console.error('Connection failed:', error);
  } else {
    console.log('✅ Database connection successful!');
  }
}

testConnection();
```

## Core Tables Created

After running migrations, you'll have:

1. **companies** - Company profile and GST information
2. **financial_years** - Accounting periods with locking
3. **user_roles** - Role-based access control

## Common Issues

### Issue: "relation already exists"
**Solution:** Tables already exist. This is safe to ignore if using `CREATE TABLE IF NOT EXISTS`.

### Issue: "permission denied"
**Solution:** Ensure you're using the service role key, not the anon key.

### Issue: "auth.users does not exist"
**Solution:** Supabase Auth is not enabled. Enable it in Supabase dashboard under Authentication.

### Issue: psql command not found
**Solution:** 
- **Windows:** Install PostgreSQL from postgresql.org
- **Mac:** `brew install postgresql`
- **Linux:** `sudo apt-get install postgresql-client`

## Next Steps

1. ✅ Core tables created
2. ⏭️ Run RLS policies: `002_rls_policies.sql`
3. ⏭️ Create Inventory module tables
4. ⏭️ Implement API endpoints
5. ⏭️ Write tests

## Useful Commands

```bash
# Generate Prisma client
npm run prisma:generate

# Open Prisma Studio (GUI for database)
npm run prisma:studio

# Check migration status
psql $DATABASE_URL -c "\dt"

# View table structure
psql $DATABASE_URL -c "\d companies"
```

## Documentation

- Full schema documentation: `SCHEMA_DOCUMENTATION.md`
- Migration details: `migrations/README.md`
- Design document: `.kiro/specs/bizpulse24-erp-backend/design.md`

## Support

If you encounter issues:
1. Check the error message carefully
2. Verify environment variables are set correctly
3. Ensure Supabase project is active
4. Check database connection string format
