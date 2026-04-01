-- GIN index for efficient JSONB filtering on documents.metadata
CREATE INDEX idx_documents_metadata ON public.documents USING gin(metadata);
