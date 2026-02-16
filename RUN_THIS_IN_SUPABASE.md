# 🔧 FIX SUPABASE DATABASE - RUN THIS NOW!

## ⚠️ CRITICAL: Your billing is broken because columns are missing!

### Missing Columns Found:
- ❌ `bills.customer_phone`
- ❌ `bills.business_owner_id`
- ❌ `bills.user_id`
- ❌ `bills.paid_amount`
- ❌ `bills.partial_payment_amount`
- ❌ `bills.partial_payment_method`
- ❌ `products.business_owner_id`
- ❌ `customers.business_owner_id`
- ❌ `sales.business_owner_id`
- ❌ `sales.user_id`
- ❌ `bill_items.user_id`
- ❌ `payments.user_id`

---

## 📋 STEP-BY-STEP INSTRUCTIONS:

### Step 1: Open Supabase SQL Editor
1. Go to: https://supabase.com/dashboard
2. Select your project: **bizpulse-erp**
3. Click on **SQL Editor** in the left sidebar
4. Click **New Query**

### Step 2: Copy and Run This SQL
Copy the entire SQL script from `fix_supabase_bills_table.sql` and paste it into the SQL editor.

Or copy this:

```sql
-- Fix Supabase bills table - Add missing columns
-- Run this in Supabase SQL Editor

-- Add customer_phone column
ALTER TABLE bills ADD COLUMN IF NOT EXISTS customer_phone VARCHAR(20);

-- Add business_owner_id column
ALTER TABLE bills ADD COLUMN IF NOT EXISTS business_owner_id VARCHAR(255);

-- Add user_id column
ALTER TABLE bills ADD COLUMN IF NOT EXISTS user_id VARCHAR(255);

-- Add paid_amount column
ALTER TABLE bills ADD COLUMN IF NOT EXISTS paid_amount NUMERIC(10,2) DEFAULT 0;

-- Add partial_payment_amount column
ALTER TABLE bills ADD COLUMN IF NOT EXISTS partial_payment_amount NUMERIC(10,2);

-- Add partial_payment_method column
ALTER TABLE bills ADD COLUMN IF NOT EXISTS partial_payment_method VARCHAR(50);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_bills_business_owner_id ON bills(business_owner_id);
CREATE INDEX IF NOT EXISTS idx_bills_user_id ON bills(user_id);

-- Also add missing columns to other tables
ALTER TABLE products ADD COLUMN IF NOT EXISTS business_owner_id VARCHAR(255);

ALTER TABLE customers ADD COLUMN IF NOT EXISTS business_owner_id VARCHAR(255);

ALTER TABLE sales ADD COLUMN IF NOT EXISTS business_owner_id VARCHAR(255);
ALTER TABLE sales ADD COLUMN IF NOT EXISTS user_id VARCHAR(255);

ALTER TABLE bill_items ADD COLUMN IF NOT EXISTS user_id VARCHAR(255);
ALTER TABLE payments ADD COLUMN IF NOT EXISTS user_id VARCHAR(255);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_products_business_owner_id ON products(business_owner_id);
CREATE INDEX IF NOT EXISTS idx_customers_business_owner_id ON customers(business_owner_id);
CREATE INDEX IF NOT EXISTS idx_sales_business_owner_id ON sales(business_owner_id);

-- Success message
SELECT 'All missing columns added successfully!' AS status;
```

### Step 3: Click "Run" Button
- Click the **Run** button (or press Ctrl+Enter)
- Wait for the query to complete
- You should see: "All missing columns added successfully!"

### Step 4: Verify the Fix
Run this query to verify all columns exist:

```sql
SELECT column_name 
FROM information_schema.columns 
WHERE table_name = 'bills' 
ORDER BY column_name;
```

You should see all these columns:
- business_owner_id ✅
- customer_id ✅
- customer_name ✅
- customer_phone ✅
- user_id ✅
- paid_amount ✅
- partial_payment_amount ✅
- partial_payment_method ✅
- (and all other existing columns)

---

## ✅ AFTER RUNNING THE SQL:

1. **Wait 1-2 minutes** for Render to auto-deploy the latest code
2. **Go to your billing page**: https://bizpulse-erp.onrender.com/retail/billing
3. **Try creating a bill** - it should work now!

---

## 🔍 TROUBLESHOOTING:

### If you still get errors:
1. Check Render logs: https://dashboard.render.com
2. Look for the auto-fix message: "✅ Added customer_phone column to bills table"
3. If auto-fix didn't run, manually restart the service in Render

### If columns already exist:
- The SQL uses `IF NOT EXISTS` so it's safe to run multiple times
- You'll see: "column already exists" - that's OK!

---

## 📝 WHAT THIS FIXES:

✅ Billing system will work again
✅ Customer phone numbers will be saved
✅ Multi-tenant data isolation will work
✅ User tracking will work
✅ Partial payments will work

---

## ⚡ QUICK FIX (Alternative):

If you don't want to run SQL manually, just:
1. Wait for the auto-deploy to complete (2-3 minutes)
2. The auto-fix will run automatically on startup
3. Check Render logs to confirm it ran

But running the SQL manually is FASTER and GUARANTEED to work!

---

**Run this NOW to fix your billing system!** 🚀
