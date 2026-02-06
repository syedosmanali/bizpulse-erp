# 🚀 Supabase Setup Guide for BizPulse ERP

## 📋 What I Need From You:

To migrate your ERP to Supabase, I need these 3 credentials:

### 1. **Supabase Project URL**
- Format: `https://xxxxx.supabase.co`
- Where to find: Supabase Dashboard → Project Settings → API → Project URL

### 2. **Database Password**
- The password you set when creating the Supabase project
- If you forgot it, you can reset it in: Project Settings → Database → Reset Database Password

### 3. **Supabase API Key (anon/public)**
- Format: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`
- Where to find: Supabase Dashboard → Project Settings → API → anon/public key

---

## 🆕 Don't Have Supabase Yet?

### Create Free Supabase Account:

1. **Go to:** https://app.supabase.com
2. **Sign up** with GitHub/Google/Email
3. **Create New Project:**
   - Project Name: `bizpulse-erp`
   - Database Password: (choose a strong password - SAVE IT!)
   - Region: Choose closest to you
   - Click "Create new project"
4. **Wait 2-3 minutes** for project to be ready

### Get Your Credentials:

Once project is ready:

1. Click **"Project Settings"** (gear icon)
2. Go to **"API"** section
3. Copy these 3 things:
   - **Project URL** (under "Project URL")
   - **anon/public key** (under "Project API keys")
   - **Database Password** (the one you set during creation)

---

## 📝 Provide Credentials:

**Reply with this format:**

```
Project URL: https://xxxxx.supabase.co
Database Password: your_password_here
API Key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## ✅ What Will Happen Next:

Once you provide credentials, I will:

1. ✅ Update `modules/shared/database.py` to connect to Supabase
2. ✅ Create all tables in Supabase (bills, products, customers, etc.)
3. ✅ Migrate existing data from `billing.db` to Supabase
4. ✅ Update environment variables for Render deployment
5. ✅ Test the connection
6. ✅ Deploy to Render with persistent storage

**Your data will be:**
- ✅ Stored in Supabase cloud (not local file)
- ✅ Persistent (survives restarts)
- ✅ Accessible from anywhere
- ✅ Backed up automatically by Supabase

---

## 🔒 Security:

- Credentials will be stored in environment variables (`.env` file)
- Never committed to Git
- Secure connection to Supabase
- Your data is encrypted at rest

---

**Ready? Provide your Supabase credentials and I'll start the migration!** 🚀
