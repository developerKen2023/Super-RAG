-- Migration 011: Backfill search_vector for existing chunks
-- Populates the tsvector column for all existing document chunks

UPDATE public.document_chunks
SET search_vector = to_tsvector('english', COALESCE(content, ''))
WHERE search_vector IS NULL;
