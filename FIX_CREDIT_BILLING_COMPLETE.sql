-- ============================================================================
-- COMPLETE FIX FOR CREDIT & PARTIAL PAYMENT BILLING
-- Run this entire script in Supabase SQL Editor
-- ============================================================================

-- ============================================================================
-- STEP 1: Create credit_transactions table if it doesn't exist
-- ============================================================================

CREATE TABLE IF NOT EXISTS credit_transactions (
    id VARCHAR(255) PRIMARY KEY,
    bill_id VARCHAR(255) NOT NULL,
    customer_id VARCHAR(255) NOT NULL,
    transaction_type VARCHAR(50) NOT NULL,
    amount NUMERIC(10,2) NOT NULL DEFAULT 0,
    payment_method VARCHAR(50) DEFAULT 'cash',
    reference_number VARCHAR(255),
    notes TEXT,
    created_by VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tenant_id VARCHAR(255),
    FOREIGN KEY (bill_id) REFERENCES bills (id),
    FOREIGN KEY (customer_id) REFERENCES customers (id)
);

-- ============================================================================
-- STEP 2: Add missing columns if table already exists
-- ============================================================================

-- Add amount column if missing (this is the critical one causing the error)
ALTER TABLE credit_transactions ADD COLUMN IF NOT EXISTS amount NUMERIC(10,2) NOT NULL DEFAULT 0;

-- Add other columns if missing
ALTER TABLE credit_transactions ADD COLUMN IF NOT EXISTS payment_method VARCHAR(50) DEFAULT 'cash';
ALTER TABLE credit_transactions ADD COLUMN IF NOT EXISTS reference_number VARCHAR(255);
ALTER TABLE credit_transactions ADD COLUMN IF NOT EXISTS notes TEXT;
ALTER TABLE credit_transactions ADD COLUMN IF NOT EXISTS created_by VARCHAR(255);
ALTER TABLE credit_transactions ADD COLUMN IF NOT EXISTS tenant_id VARCHAR(255);

-- ============================================================================
-- STEP 3: Ensure bills table has all required columns for credit/partial
-- ============================================================================

-- These should already exist from previous fix, but adding IF NOT EXISTS for safety
ALTER TABLE bills ADD COLUMN IF NOT EXISTS is_credit BOOLEAN DEFAULT FALSE;
ALTER TABLE bills ADD COLUMN IF NOT EXISTS credit_amount NUMERIC(10,2) DEFAULT 0;
ALTER TABLE bills ADD COLUMN IF NOT EXISTS credit_paid_amount NUMERIC(10,2) DEFAULT 0;
ALTER TABLE bills ADD COLUMN IF NOT EXISTS credit_balance NUMERIC(10,2) DEFAULT 0;
ALTER TABLE bills ADD COLUMN IF NOT EXISTS credit_due_date DATE;
ALTER TABLE bills ADD COLUMN IF NOT EXISTS partial_payment_amount NUMERIC(10,2);
ALTER TABLE bills ADD COLUMN IF NOT EXISTS partial_payment_method VARCHAR(50);

-- ============================================================================
-- STEP 4: Create indexes for performance
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_credit_transactions_bill_id ON credit_transactions(bill_id);
CREATE INDEX IF NOT EXISTS idx_credit_transactions_customer_id ON credit_transactions(customer_id);
CREATE INDEX IF NOT EXISTS idx_credit_transactions_created_at ON credit_transactions(created_at);

-- ============================================================================
-- STEP 5: Verify the fix
-- ============================================================================

-- Check credit_transactions table structure
SELECT 'credit_transactions table columns:' AS info;
SELECT column_name, data_type, is_nullable
FROM information_schema.columns 
WHERE table_name = 'credit_transactions' 
ORDER BY ordinal_position;

-- Check bills table has credit columns
SELECT 'bills table credit columns:' AS info;
SELECT column_name, data_type
FROM information_schema.columns 
WHERE table_name = 'bills' 
AND column_name IN ('is_credit', 'credit_amount', 'credit_paid_amount', 'credit_balance', 'partial_payment_amount', 'partial_payment_method')
ORDER BY column_name;

-- Success message
SELECT '✅ ALL CREDIT & PARTIAL PAYMENT FIXES APPLIED!' AS status;
SELECT '✅ You can now create credit bills' AS message;
SELECT '✅ You can now create partial payment bills' AS message;
SELECT '✅ credit_transactions table is ready' AS message;
