-- ⚠️ DELETE OLD TABLES FROM SUPABASE
-- Run this in Supabase SQL Editor

-- Backup reminder
-- IMPORTANT: Make sure you have backup before running this!

-- Drop old tables (from old design)
DROP TABLE IF EXISTS bill_items CASCADE;
DROP TABLE IF EXISTS bills CASCADE;
DROP TABLE IF EXISTS sales CASCADE;

-- Optional: Drop other old tables if they exist
-- DROP TABLE IF EXISTS retail_orders CASCADE;
-- DROP TABLE IF EXISTS hotel_bookings CASCADE;

-- Verify tables are deleted
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('bills', 'bill_items', 'sales', 'retail_orders', 'hotel_bookings');

-- Should return empty result if all deleted successfully
