-- Migration 009: Verify cascade delete is properly configured
-- The document_chunks table already has ON DELETE CASCADE via foreign key
-- This migration verifies the existing configuration

-- Check if document_chunks has proper CASCADE delete
SELECT
    tc.constraint_name,
    tc.table_name,
    kcu.column_name,
    rc.delete_rule
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
    AND tc.table_schema = kcu.table_schema
JOIN information_schema.referential_constraints AS rc
    ON tc.constraint_name = rc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
    AND tc.table_name = 'document_chunks'
    AND rc.delete_rule = 'CASCADE';
