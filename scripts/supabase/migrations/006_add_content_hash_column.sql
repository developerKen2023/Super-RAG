-- Add content_hash column to documents table for deduplication
ALTER TABLE public.documents
ADD COLUMN IF NOT EXISTS content_hash TEXT;

-- Index for fast duplicate lookup (user_id + content_hash)
CREATE INDEX IF NOT EXISTS idx_documents_user_content_hash
ON public.documents(user_id, content_hash);

-- Index for hash existence queries
CREATE INDEX IF NOT EXISTS idx_documents_content_hash_exists
ON public.documents(content_hash) WHERE content_hash IS NOT NULL;
