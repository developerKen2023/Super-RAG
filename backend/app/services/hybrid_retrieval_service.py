from supabase import Client
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class HybridRetrievalService:
    """
    Hybrid search combining BM25 keyword search with vector similarity.
    Uses Reciprocal Rank Fusion (RRF) to combine results.
    """

    RRF_K = 60  # RRF constant

    def __init__(self, supabase: Client):
        self.supabase = supabase

    def search_chunks_bm25(
        self,
        query: str,
        user_id: str,
        limit: int = 20
    ) -> List[dict]:
        """Execute BM25 keyword search."""
        try:
            response = self.supabase.rpc(
                "search_chunks_bm25",
                {
                    "p_query": query,
                    "p_user_id": user_id,
                    "p_limit": limit
                }
            ).execute()

            logger.info(f"BM25 search returned {len(response.data) if response.data else 0} chunks")
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"BM25 search failed: {e}")
            return []

    def retrieve_relevant_chunks(
        self,
        query: str,
        user_id: str,
        top_k: int = 10,
        vector_weight: float = 0.5,
        tag_filter: str | None = None,
        category_filter: str | None = None
    ) -> List[dict]:
        """
        Hybrid search combining BM25 + vector search with RRF.

        Args:
            query: User's question/query
            user_id: Current user's ID
            top_k: Number of final chunks to return
            vector_weight: Weight for vector scores (1 - vector_weight for BM25)
            tag_filter: Optional tag filter
            category_filter: Optional category filter

        Returns:
            List of chunks ranked by RRF scores
        """
        # Get BM25 results (keyword search)
        bm25_results = self.search_chunks_bm25(query, user_id, limit=top_k * 2)

        # Get vector results via existing retrieval
        from app.services.retrieval_service import RetrievalService
        vector_service = RetrievalService(self.supabase)
        vector_results = vector_service.retrieve_relevant_chunks(
            query=query,
            user_id=user_id,
            top_k=top_k * 2,
            similarity_threshold=0.0,  # No threshold for hybrid
            tag_filter=tag_filter,
            category_filter=category_filter
        )

        # Apply RRF fusion
        fused_results = self._rrf_fusion(bm25_results, vector_results, top_k)

        logger.info(f"Hybrid search: BM25={len(bm25_results)}, Vector={len(vector_results)}, Fused={len(fused_results)}")
        return fused_results

    def _rrf_fusion(
        self,
        bm25_results: List[dict],
        vector_results: List[dict],
        top_k: int
    ) -> List[dict]:
        """
        Apply Reciprocal Rank Fusion to combine BM25 and vector rankings.

        RRF formula: score(d) = SUM(1 / (k + rank(d)))
        """
        # Create rank maps
        bm25_ranks = {r["id"]: rank for rank, r in enumerate(bm25_results)}
        vector_ranks = {r["id"]: rank for rank, r in enumerate(vector_results)}

        # Calculate RRF scores
        rrf_scores: Dict[str, float] = {}

        # Add BM25 scores
        for chunk_id, rank in bm25_ranks.items():
            rrf_scores[chunk_id] = rrf_scores.get(chunk_id, 0) + (1 / (self.RRF_K + rank))

        # Add vector scores
        for chunk_id, rank in vector_ranks.items():
            rrf_scores[chunk_id] = rrf_scores.get(chunk_id, 0) + (1 / (self.RRF_K + rank))

        # Sort by RRF score
        sorted_ids = sorted(rrf_scores.keys(), key=lambda x: rrf_scores[x], reverse=True)

        # Build result list with all metadata
        all_chunks = {r["id"]: r for r in bm25_results + vector_results}

        fused = []
        for chunk_id in sorted_ids[:top_k]:
            chunk = all_chunks[chunk_id].copy()
            chunk["rrf_score"] = rrf_scores[chunk_id]
            # Add source indicators
            chunk["bm25_rank"] = bm25_ranks.get(chunk_id)
            chunk["vector_rank"] = vector_ranks.get(chunk_id)
            fused.append(chunk)

        return fused

    def get_context_for_query(
        self,
        query: str,
        user_id: str,
        top_k: int = 5,
        vector_weight: float = 0.5,
        tag_filter: str | None = None,
        category_filter: str | None = None
    ) -> str:
        """
        Get formatted context string from hybrid search results.
        """
        chunks = self.retrieve_relevant_chunks(
            query=query,
            user_id=user_id,
            top_k=top_k,
            vector_weight=vector_weight,
            tag_filter=tag_filter,
            category_filter=category_filter
        )

        if not chunks:
            return ""

        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            # Include source attribution info
            sources = []
            if chunk.get("bm25_rank") is not None:
                sources.append(f"BM25 rank: {chunk['bm25_rank'] + 1}")
            if chunk.get("vector_rank") is not None:
                sources.append(f"Vector rank: {chunk['vector_rank'] + 1}")

            source_str = f" ({', '.join(sources)})" if sources else ""

            context_parts.append(
                f"[Document {i}] {chunk.get('filename', 'Unknown')}{source_str}:\n{chunk.get('content', '')}"
            )

        return "\n\n".join(context_parts)
