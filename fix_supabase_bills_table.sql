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
ALTER TABLE products ADD COLUMN IF NOT EXISTS user_id VARCHAR(255);

ALTER TABLE customers ADD COLUMN IF NOT EXISTS business_owner_id VARCHAR(255);
ALTER TABLE customers ADD COLUMN IF NOT EXISTS user_id VARCHAR(255);

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
