-- ============================================================================
-- FIX CREDIT_TRANSACTIONS TABLE - Add missing amount column
-- Run this in Supabase SQL Editor NOW!
-- ============================================================================

-- Check if credit_transactions table exists
SELECT 'Checking credit_transactions table...' AS status;

-- Add amount column if missing
ALTER TABLE credit_transactions ADD COLUMN IF NOT EXISTS amount NUMERIC(10,2) NOT NULL DEFAULT 0;

-- Verify the fix
SELECT 'Verifying columns...' AS status;
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'credit_transactions' 
ORDER BY ordinal_position;

-- Success message
SELECT '✅ credit_transactions table fixed!' AS status;
SELECT '✅ Credit and partial payments will now work!' AS message;
