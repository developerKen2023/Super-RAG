-- Migration 010: BM25 Full-Text Search Index
-- Adds tsvector column for PostgreSQL full-text search (BM25-like)

-- Add tsvector column for full-text search on document_chunks
ALTER TABLE public.document_chunks
ADD COLUMN IF NOT EXISTS search_vector tsvector;

-- Create GIN index for full-text search
CREATE INDEX IF NOT EXISTS idx_chunks_search_vector
ON public.document_chunks USING gin(search_vector);

-- Create function to update search_vector
CREATE OR REPLACE FUNCTION update_chunk_search_vector()
RETURNS TRIGGER AS $$
BEGIN
    NEW.search_vector := to_tsvector('english', COALESCE(NEW.content, ''));
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to automatically update search_vector on insert/update
DROP TRIGGER IF EXISTS trg_update_chunk_search_vector ON public.document_chunks;
CREATE TRIGGER trg_update_chunk_search_vector
    BEFORE INSERT OR UPDATE OF content ON public.document_chunks
    FOR EACH ROW
    EXECUTE FUNCTION update_chunk_search_vector();

-- BM25 search function using ts_rank_cd (BM25-like ranking)
CREATE OR REPLACE FUNCTION search_chunks_bm25(
    p_query TEXT,
    p_user_id UUID,
    p_limit INT DEFAULT 20
)
RETURNS TABLE (
    id UUID,
    document_id UUID,
    chunk_index INTEGER,
    content TEXT,
    filename TEXT,
    metadata JSONB,
    bm25_score REAL
)
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    RETURN QUERY
    SELECT
        dc.id,
        dc.document_id,
        dc.chunk_index,
        dc.content,
        d.filename,
        dc.metadata,
        ts_rank_cd(dc.search_vector, plainto_tsquery('english', p_query)) AS bm25_score
    FROM public.document_chunks dc
    JOIN public.documents d ON dc.document_id = d.id
    WHERE
        d.user_id = p_user_id
        AND d.status = 'completed'
        AND dc.search_vector @@ plainto_tsquery('english', p_query)
    ORDER BY ts_rank_cd(dc.search_vector, plainto_tsquery('english', p_query)) DESC
    LIMIT p_limit;
END;
$$;

-- Grant execute permission
GRANT EXECUTE ON FUNCTION search_chunks_bm25 TO authenticated;
GRANT EXECUTE ON FUNCTION search_chunks_bm25 TO anon;
