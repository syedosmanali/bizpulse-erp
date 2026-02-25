-- Verification Script for Inventory Module Schema
-- Run this script after migrations to verify everything is set up correctly

-- ============================================================================
-- CHECK TABLES EXIST
-- ============================================================================

SELECT 
    'Tables Check' as check_type,
    COUNT(*) as count,
    CASE 
        WHEN COUNT(*) = 7 THEN '✅ PASS'
        ELSE '❌ FAIL'
    END as status
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('categories', 'brands', 'products', 'locations', 'stock', 'stock_ledger', 'stock_alerts');

-- List all Inventory tables
SELECT 
    table_name,
    (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name AND table_schema = 'public') as column_count
FROM information_schema.tables t
WHERE table_schema = 'public' 
AND table_name IN ('categories', 'brands', 'products', 'locations', 'stock', 'stock_ledger', 'stock_alerts')
ORDER BY table_name;

-- ============================================================================
-- CHECK INDEXES
-- ============================================================================

SELECT 
    'Indexes Check' as check_type,
    COUNT(*) as count,
    CASE 
        WHEN COUNT(*) >= 30 THEN '✅ PASS'
        ELSE '⚠️  WARNING'
    END as status
FROM pg_indexes 
WHERE schemaname = 'public' 
AND tablename IN ('categories', 'brands', 'products', 'locations', 'stock', 'stock_ledger', 'stock_alerts');

-- List all indexes
SELECT 
    tablename,
    indexname,
    indexdef
FROM pg_indexes 
WHERE schemaname = 'public' 
AND tablename IN ('categories', 'brands', 'products', 'locations', 'stock', 'stock_ledger', 'stock_alerts')
ORDER BY tablename, indexname;

-- ============================================================================
-- CHECK FOREIGN KEY CONSTRAINTS
-- ============================================================================

SELECT 
    'Foreign Keys Check' as check_type,
    COUNT(*) as count,
    CASE 
        WHEN COUNT(*) >= 10 THEN '✅ PASS'
        ELSE '❌ FAIL'
    END as status
FROM information_schema.table_constraints 
WHERE constraint_schema = 'public' 
AND constraint_type = 'FOREIGN KEY'
AND table_name IN ('categories', 'brands', 'products', 'locations', 'stock', 'stock_ledger', 'stock_alerts');

-- List all foreign keys
SELECT 
    tc.table_name,
    tc.constraint_name,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name
FROM information_schema.table_constraints AS tc 
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
    AND tc.table_schema = kcu.table_schema
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
    AND ccu.table_schema = tc.table_schema
WHERE tc.constraint_type = 'FOREIGN KEY' 
AND tc.table_schema = 'public'
AND tc.table_name IN ('categories', 'brands', 'products', 'locations', 'stock', 'stock_ledger', 'stock_alerts')
ORDER BY tc.table_name, tc.constraint_name;

-- ============================================================================
-- CHECK UNIQUE CONSTRAINTS
-- ============================================================================

SELECT 
    'Unique Constraints Check' as check_type,
    COUNT(*) as count,
    CASE 
        WHEN COUNT(*) >= 3 THEN '✅ PASS'
        ELSE '❌ FAIL'
    END as status
FROM information_schema.table_constraints 
WHERE constraint_schema = 'public' 
AND constraint_type = 'UNIQUE'
AND table_name IN ('products', 'stock');

-- List unique constraints
SELECT 
    tc.table_name,
    tc.constraint_name,
    STRING_AGG(kcu.column_name, ', ') as columns
FROM information_schema.table_constraints AS tc 
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
    AND tc.table_schema = kcu.table_schema
WHERE tc.constraint_type = 'UNIQUE' 
AND tc.table_schema = 'public'
AND tc.table_name IN ('products', 'stock')
GROUP BY tc.table_name, tc.constraint_name
ORDER BY tc.table_name;

-- ============================================================================
-- CHECK CHECK CONSTRAINTS
-- ============================================================================

SELECT 
    'Check Constraints' as check_type,
    COUNT(*) as count,
    CASE 
        WHEN COUNT(*) >= 3 THEN '✅ PASS'
        ELSE '❌ FAIL'
    END as status
FROM information_schema.check_constraints 
WHERE constraint_schema = 'public'
AND constraint_name LIKE '%gst_rate%' 
   OR constraint_name LIKE '%movement_type%'
   OR constraint_name LIKE '%alert_type%';

-- List check constraints
SELECT 
    tc.table_name,
    tc.constraint_name,
    cc.check_clause
FROM information_schema.table_constraints AS tc
JOIN information_schema.check_constraints AS cc
    ON tc.constraint_name = cc.constraint_name
    AND tc.constraint_schema = cc.constraint_schema
WHERE tc.constraint_schema = 'public'
AND tc.table_name IN ('products', 'stock_ledger', 'stock_alerts')
ORDER BY tc.table_name;

-- ============================================================================
-- CHECK RLS ENABLED
-- ============================================================================

SELECT 
    'RLS Enabled Check' as check_type,
    COUNT(*) as count,
    CASE 
        WHEN COUNT(*) = 7 THEN '✅ PASS'
        ELSE '❌ FAIL'
    END as status
FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename IN ('categories', 'brands', 'products', 'locations', 'stock', 'stock_ledger', 'stock_alerts')
AND rowsecurity = true;

-- List RLS status
SELECT 
    tablename,
    rowsecurity as rls_enabled
FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename IN ('categories', 'brands', 'products', 'locations', 'stock', 'stock_ledger', 'stock_alerts')
ORDER BY tablename;

-- ============================================================================
-- CHECK RLS POLICIES
-- ============================================================================

SELECT 
    'RLS Policies Check' as check_type,
    COUNT(*) as count,
    CASE 
        WHEN COUNT(*) >= 25 THEN '✅ PASS'
        ELSE '❌ FAIL'
    END as status
FROM pg_policies 
WHERE schemaname = 'public' 
AND tablename IN ('categories', 'brands', 'products', 'locations', 'stock', 'stock_ledger', 'stock_alerts');

-- List all policies
SELECT 
    tablename,
    policyname,
    cmd as operation,
    CASE 
        WHEN qual IS NOT NULL THEN 'USING clause present'
        ELSE 'No USING clause'
    END as using_clause,
    CASE 
        WHEN with_check IS NOT NULL THEN 'WITH CHECK clause present'
        ELSE 'No WITH CHECK clause'
    END as with_check_clause
FROM pg_policies 
WHERE schemaname = 'public' 
AND tablename IN ('categories', 'brands', 'products', 'locations', 'stock', 'stock_ledger', 'stock_alerts')
ORDER BY tablename, cmd, policyname;

-- ============================================================================
-- CHECK TRIGGERS
-- ============================================================================

SELECT 
    'Triggers Check' as check_type,
    COUNT(*) as count,
    CASE 
        WHEN COUNT(*) >= 5 THEN '✅ PASS'
        ELSE '❌ FAIL'
    END as status
FROM information_schema.triggers 
WHERE event_object_schema = 'public' 
AND event_object_table IN ('categories', 'brands', 'products', 'locations', 'stock')
AND trigger_name LIKE '%updated_at%';

-- List all triggers
SELECT 
    event_object_table as table_name,
    trigger_name,
    event_manipulation as event,
    action_timing as timing
FROM information_schema.triggers 
WHERE event_object_schema = 'public' 
AND event_object_table IN ('categories', 'brands', 'products', 'locations', 'stock', 'stock_ledger', 'stock_alerts')
ORDER BY event_object_table, trigger_name;

-- ============================================================================
-- CHECK AUDIT FIELDS
-- ============================================================================

SELECT 
    'Audit Fields Check' as check_type,
    table_name,
    CASE 
        WHEN COUNT(*) >= 4 THEN '✅ PASS'
        ELSE '❌ FAIL'
    END as status
FROM information_schema.columns
WHERE table_schema = 'public'
AND table_name IN ('categories', 'brands', 'products', 'locations')
AND column_name IN ('created_at', 'updated_at', 'created_by', 'updated_by')
GROUP BY table_name
ORDER BY table_name;

-- ============================================================================
-- SUMMARY REPORT
-- ============================================================================

SELECT 
    '=== INVENTORY MODULE SCHEMA VERIFICATION SUMMARY ===' as summary;

SELECT 
    'Total Tables' as metric,
    COUNT(*) as value
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('categories', 'brands', 'products', 'locations', 'stock', 'stock_ledger', 'stock_alerts');

SELECT 
    'Total Indexes' as metric,
    COUNT(*) as value
FROM pg_indexes 
WHERE schemaname = 'public' 
AND tablename IN ('categories', 'brands', 'products', 'locations', 'stock', 'stock_ledger', 'stock_alerts');

SELECT 
    'Total Foreign Keys' as metric,
    COUNT(*) as value
FROM information_schema.table_constraints 
WHERE constraint_schema = 'public' 
AND constraint_type = 'FOREIGN KEY'
AND table_name IN ('categories', 'brands', 'products', 'locations', 'stock', 'stock_ledger', 'stock_alerts');

SELECT 
    'Total RLS Policies' as metric,
    COUNT(*) as value
FROM pg_policies 
WHERE schemaname = 'public' 
AND tablename IN ('categories', 'brands', 'products', 'locations', 'stock', 'stock_ledger', 'stock_alerts');

SELECT 
    'Total Triggers' as metric,
    COUNT(*) as value
FROM information_schema.triggers 
WHERE event_object_schema = 'public' 
AND event_object_table IN ('categories', 'brands', 'products', 'locations', 'stock', 'stock_ledger', 'stock_alerts');
