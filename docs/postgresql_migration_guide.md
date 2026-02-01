# PostgreSQL Migration Guide for Render Deployment

## Overview

This guide walks you through migrating your BizPulse ERP application from SQLite to PostgreSQL for deployment on Render. This migration ensures data persistence across service restarts.

## Problem Statement

**Issue:** Render's free tier uses ephemeral filesystem, meaning:
- Files (including `billing.db`) are reset on every service restart
- Service restarts happen after 15 minutes of inactivity
- All billing data disappears after restart

**Solution:** Migrate to PostgreSQL database which provides persistent storage on Render.

## Prerequisites

- Git repository with your BizPulse ERP code
- Render account (free tier works)
- Existing SQLite database (`billing.db`) with data to migrate

## Step-by-Step Migration

### Step 1: Update Code for PostgreSQL Support

✅ **Already Done!** The following files have been updated:

1. **requirements.txt** - Added `psycopg2-binary==2.9.9`
2. **modules/shared/database.py** - Updated to support both SQLite and PostgreSQL
3. **render.yaml** - Render deployment configuration
4. **.env.example** - Updated with DATABASE_URL documentation

### Step 2: Commit and Push Changes

```bash
# Add all changes
git add .

# Commit changes
git commit -m "Add PostgreSQL support for Render deployment"

# Push to your repository
git push origin main
```

### Step 3: Create Render Account and Connect Repository

1. Go to [https://render.com](https://render.com)
2. Sign up or log in
3. Click "New +" → "Blueprint"
4. Connect your Git repository
5. Select the repository containing your BizPulse ERP code

### Step 4: Deploy Using Blueprint

Render will automatically detect `render.yaml` and:

1. **Create PostgreSQL Database**
   - Name: `bizpulse-db`
   - Plan: Free tier
   - Database: `bizpulse_erp`
   - User: `bizpulse_user`

2. **Create Web Service**
   - Name: `bizpulse-erp`
   - Plan: Free tier
   - Automatically links to PostgreSQL database
   - Sets `DATABASE_URL` environment variable

3. **Deploy Application**
   - Installs dependencies from `requirements.txt`
   - Starts application with gunicorn
   - Initializes PostgreSQL database schema

### Step 5: Verify Deployment

1. Wait for deployment to complete (5-10 minutes)
2. Click on your web service URL
3. Application should load successfully
4. PostgreSQL database is now active but empty

### Step 6: Migrate Data from SQLite to PostgreSQL

Now you need to transfer your existing data from `billing.db` to PostgreSQL.

#### Option A: Migrate from Local Machine (Recommended)

1. **Get PostgreSQL Connection String**
   - Go to Render Dashboard
   - Click on `bizpulse-db` database
   - Copy "External Database URL"
   - Format: `postgresql://user:password@host:port/database`

2. **Set Environment Variable**
   ```bash
   # Windows (CMD)
   set DATABASE_URL=postgresql://user:password@host:port/database
   
   # Windows (PowerShell)
   $env:DATABASE_URL="postgresql://user:password@host:port/database"
   
   # Linux/Mac
   export DATABASE_URL='postgresql://user:password@host:port/database'
   ```

3. **Run Migration Script**
   ```bash
   python scripts/migrate_to_postgres.py
   ```

4. **Verify Migration**
   - Script will show progress for each table
   - Check summary at the end
   - Verify record counts match

#### Option B: Migrate from Render Shell

1. **Open Render Shell**
   - Go to your web service in Render Dashboard
   - Click "Shell" tab
   - Wait for shell to connect

2. **Upload SQLite Database**
   ```bash
   # You'll need to upload billing.db to Render
   # This can be done via:
   # - SCP/SFTP (if available)
   # - Or recreate sample data directly in PostgreSQL
   ```

3. **Run Migration**
   ```bash
   python scripts/migrate_to_postgres.py billing.db
   ```

### Step 7: Test Data Persistence

1. **Create Test Data**
   - Log in to your application
   - Create a new bill or product
   - Note the details

2. **Restart Service**
   - Go to Render Dashboard
   - Click "Manual Deploy" → "Clear build cache & deploy"
   - Or wait for automatic restart (15 min inactivity)

3. **Verify Data Persists**
   - Log in again
   - Check if your test data still exists
   - ✅ Data should persist across restarts!

## Database Connection Logic

The application automatically detects which database to use:

### Local Development (SQLite)
```python
# No DATABASE_URL set
# Uses: billing.db file
# Location: Project root directory
```

### Production (PostgreSQL)
```python
# DATABASE_URL environment variable set by Render
# Uses: PostgreSQL on Render
# Connection: Automatic via DATABASE_URL
```

## Troubleshooting

### Issue: "Failed to connect to PostgreSQL"

**Solution:**
1. Check DATABASE_URL is set correctly
2. Verify PostgreSQL database is running on Render
3. Check database credentials in Render dashboard

### Issue: "Migration script fails"

**Solution:**
1. Ensure `psycopg2-binary` is installed: `pip install psycopg2-binary`
2. Check DATABASE_URL format is correct
3. Verify network connectivity to Render database
4. Check database has enough storage space

### Issue: "Tables not found in PostgreSQL"

**Solution:**
1. Ensure application has been deployed and started at least once
2. Check Render logs for database initialization errors
3. Manually run `init_db()` if needed

### Issue: "Data disappears after restart"

**Solution:**
1. Verify DATABASE_URL is set in Render environment variables
2. Check application is actually using PostgreSQL (check logs)
3. Ensure you're not accidentally using SQLite in production

### Issue: "Slow database queries"

**Solution:**
1. PostgreSQL free tier has limited resources
2. Consider upgrading to paid plan for better performance
3. Add indexes to frequently queried columns
4. Optimize queries to reduce database load

## Monitoring and Maintenance

### Check Database Size
```sql
-- Connect to PostgreSQL
SELECT pg_size_pretty(pg_database_size('bizpulse_erp'));
```

### View Active Connections
```sql
SELECT count(*) FROM pg_stat_activity;
```

### Backup Database

Render provides automatic backups for paid plans. For free tier:

```bash
# Export database
pg_dump $DATABASE_URL > backup.sql

# Restore database
psql $DATABASE_URL < backup.sql
```

## Rollback Plan

If you need to rollback to SQLite:

1. **Remove DATABASE_URL**
   - Go to Render Dashboard
   - Environment Variables
   - Delete DATABASE_URL

2. **Redeploy**
   - Application will automatically use SQLite
   - Note: Data in PostgreSQL will remain but won't be used

3. **Restore SQLite Data**
   - Upload your backup `billing.db` file
   - Or recreate data manually

## Performance Optimization

### Connection Pooling

For better performance, consider implementing connection pooling:

```python
from psycopg2 import pool

# Create connection pool
connection_pool = pool.SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    dsn=DATABASE_URL
)
```

### Indexes

Add indexes to frequently queried columns:

```sql
CREATE INDEX idx_bills_customer_id ON bills(customer_id);
CREATE INDEX idx_bills_created_at ON bills(created_at);
CREATE INDEX idx_products_category ON products(category);
```

### Query Optimization

- Use `EXPLAIN ANALYZE` to identify slow queries
- Avoid `SELECT *` - specify only needed columns
- Use pagination for large result sets
- Cache frequently accessed data

## Upgrading to Paid Plan

Benefits of upgrading from free tier:

1. **No Sleep Mode** - Service stays active 24/7
2. **More Resources** - Better CPU and memory
3. **Persistent Disk** - For file uploads
4. **Automatic Backups** - Daily database backups
5. **Better Performance** - Faster response times

## Additional Resources

- [Render Documentation](https://render.com/docs)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [psycopg2 Documentation](https://www.psycopg.org/docs/)

## Support

If you encounter issues:

1. Check Render logs for error messages
2. Review this guide's troubleshooting section
3. Check Render community forum
4. Contact Render support (for paid plans)

## Summary

✅ **What We Achieved:**
- Migrated from SQLite to PostgreSQL
- Data now persists across Render restarts
- Application works on both local (SQLite) and production (PostgreSQL)
- Automatic database selection based on environment

✅ **Next Steps:**
- Monitor application performance
- Set up regular backups
- Consider upgrading to paid plan for better reliability
- Optimize database queries as needed

---

**Congratulations!** Your BizPulse ERP is now running on Render with persistent PostgreSQL storage. Your billing data will no longer disappear after service restarts! 🎉
