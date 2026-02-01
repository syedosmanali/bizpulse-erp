# PostgreSQL Migration - Quick Start Guide

## 🎯 Problem Solved

**Before:** Billing data disappeared every time Render service restarted (15 min inactivity)  
**After:** Data persists permanently in PostgreSQL database ✅

## 🚀 Quick Deployment Steps

### 1. Push Code to Git
```bash
git add .
git commit -m "Add PostgreSQL support"
git push origin main
```

### 2. Deploy on Render
1. Go to [render.com](https://render.com)
2. Click "New +" → "Blueprint"
3. Connect your repository
4. Render automatically creates:
   - PostgreSQL database (free tier)
   - Web service (free tier)
   - Links them together

### 3. Migrate Your Data
```bash
# Get DATABASE_URL from Render dashboard
export DATABASE_URL='postgresql://user:pass@host:port/db'

# Run migration
python scripts/migrate_to_postgres.py
```

### 4. Done! 🎉
Your app now uses PostgreSQL. Data persists across restarts!

## 📁 Files Created/Modified

### Core Files
- ✅ `requirements.txt` - Added psycopg2-binary
- ✅ `modules/shared/database.py` - PostgreSQL support
- ✅ `render.yaml` - Render configuration
- ✅ `.env.example` - DATABASE_URL documentation

### Migration Scripts
- ✅ `scripts/schema_converter.py` - Convert SQLite schema to PostgreSQL
- ✅ `scripts/migrate_to_postgres.py` - Migrate data from SQLite to PostgreSQL

### Documentation
- ✅ `docs/postgresql_migration_guide.md` - Complete migration guide
- ✅ `POSTGRESQL_MIGRATION_README.md` - This file

## 🔄 How It Works

### Local Development (SQLite)
```
No DATABASE_URL → Uses billing.db file
```

### Production (PostgreSQL)
```
DATABASE_URL set by Render → Uses PostgreSQL
```

The app automatically detects which database to use!

## 📊 Migration Script Features

- ✅ Migrates all tables in correct order (respects foreign keys)
- ✅ Shows progress for each table
- ✅ Handles errors gracefully
- ✅ Verifies data integrity
- ✅ Provides detailed summary

## 🧪 Testing

### Test Data Persistence
1. Create a bill in your app
2. Restart Render service
3. Check if bill still exists ✅

## 📚 Full Documentation

See `docs/postgresql_migration_guide.md` for:
- Detailed step-by-step instructions
- Troubleshooting guide
- Performance optimization tips
- Backup and restore procedures

## 🆘 Quick Troubleshooting

### Data still disappearing?
- Check DATABASE_URL is set in Render
- Verify app is using PostgreSQL (check logs)

### Migration fails?
- Ensure psycopg2-binary is installed
- Check DATABASE_URL format
- Verify network connectivity

### Slow performance?
- Free tier has limited resources
- Consider upgrading to paid plan
- Add database indexes

## 💡 Key Benefits

✅ **Data Persistence** - No more data loss on restart  
✅ **Production Ready** - PostgreSQL is industry standard  
✅ **Scalable** - Easy to upgrade as you grow  
✅ **Backward Compatible** - Still works with SQLite locally  
✅ **Zero Downtime** - Migrate without stopping service  

## 🎓 Next Steps

1. ✅ Deploy to Render
2. ✅ Migrate your data
3. ✅ Test data persistence
4. 📈 Monitor performance
5. 💾 Set up regular backups
6. 🚀 Consider paid plan for better performance

---

**Need Help?** Check `docs/postgresql_migration_guide.md` for detailed instructions!
