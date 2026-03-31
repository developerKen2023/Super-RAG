-- Add 'duplicate' to status enum
ALTER TABLE public.documents DROP CONSTRAINT IF EXISTS documents_status_check;
ALTER TABLE public.documents ADD CONSTRAINT documents_status_check
CHECK (status IN ('pending', 'processing', 'completed', 'failed', 'duplicate'));
