-- Add missing business_owner_id column to bills and sales tables
-- This is the CRITICAL FIX for the 500 error on Sales API

-- Add to bills table
ALTER TABLE bills 
ADD COLUMN IF NOT EXISTS business_owner_id VARCHAR(255);

-- Add to sales table
ALTER TABLE sales 
ADD COLUMN IF NOT EXISTS business_owner_id VARCHAR(255);

-- Update existing bills to set business_owner_id = 'admin-bizpulse' (default user)
UPDATE bills 
SET business_owner_id = 'admin-bizpulse' 
WHERE business_owner_id IS NULL;

-- Update existing sales to set business_owner_id = 'admin-bizpulse' (default user)
UPDATE sales 
SET business_owner_id = 'admin-bizpulse' 
WHERE business_owner_id IS NULL;

-- Verify
SELECT 'Bills with business_owner_id:' as info, COUNT(*) as count FROM bills WHERE business_owner_id IS NOT NULL
UNION ALL
SELECT 'Sales with business_owner_id:' as info, COUNT(*) as count FROM sales WHERE business_owner_id IS NOT NULL;
