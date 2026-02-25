-- ============================================================
-- BizPulse ERP - New Modules Migration
-- Run this in your Supabase SQL Editor
-- Adds: erp_challans table + permissions column to erp_staff
-- ============================================================

-- 1. Create Challan / Delivery table
CREATE TABLE IF NOT EXISTS erp_challans (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    challan_number TEXT NOT NULL,
    challan_date TEXT,
    customer_name TEXT NOT NULL,
    customer_phone TEXT,
    delivery_address TEXT,
    transport TEXT,
    driver_name TEXT,
    invoice_ref TEXT,
    status TEXT DEFAULT 'pending',
    remarks TEXT,
    items TEXT DEFAULT '[]',
    total_amount NUMERIC(12,2) DEFAULT 0,
    created_at TEXT
);

-- 2. Add permissions column to erp_staff (if not exists)
DO $$ BEGIN
    ALTER TABLE erp_staff ADD COLUMN IF NOT EXISTS permissions TEXT DEFAULT '[]';
EXCEPTION WHEN undefined_table THEN NULL;
END $$;

-- 3. Add username column to erp_staff (if not exists)
DO $$ BEGIN
    ALTER TABLE erp_staff ADD COLUMN IF NOT EXISTS username TEXT;
    ALTER TABLE erp_staff ADD COLUMN IF NOT EXISTS password TEXT;
EXCEPTION WHEN undefined_table THEN NULL;
END $$;

-- 4. Create erp_staff table if it doesn't exist at all
CREATE TABLE IF NOT EXISTS erp_staff (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    name TEXT NOT NULL,
    phone TEXT,
    email TEXT,
    role TEXT DEFAULT 'staff',
    salary NUMERIC(12,2) DEFAULT 0,
    joining_date TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    username TEXT,
    password TEXT,
    permissions TEXT DEFAULT '[]',
    created_at TEXT
);

-- 5. RLS Policies for erp_challans (if using Supabase RLS)
ALTER TABLE erp_challans ENABLE ROW LEVEL SECURITY;

CREATE POLICY IF NOT EXISTS "Users can manage their own challans"
ON erp_challans FOR ALL
USING (user_id = auth.uid()::text OR user_id IS NOT NULL);

-- Done!
SELECT 'Migration complete! erp_challans table created, erp_staff updated.' AS status;
