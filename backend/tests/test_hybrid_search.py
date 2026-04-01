import pytest
from unittest.mock import MagicMock
from app.services.hybrid_retrieval_service import HybridRetrievalService


class TestHybridRetrieval:
    """Tests for hybrid search combining BM25 + vector."""

    def test_rrf_fusion_combines_rankings(self):
        """RRF properly combines BM25 and vector rankings."""
        service = HybridRetrievalService(MagicMock())

        bm25_results = [
            {"id": "a", "content": "doc a", "filename": "a.txt"},
            {"id": "b", "content": "doc b", "filename": "b.txt"},
            {"id": "c", "content": "doc c", "filename": "c.txt"},
        ]
        vector_results = [
            {"id": "b", "content": "doc b", "filename": "b.txt"},
            {"id": "c", "content": "doc c", "filename": "c.txt"},
            {"id": "d", "content": "doc d", "filename": "d.txt"},
        ]

        fused = service._rrf_fusion(bm25_results, vector_results, top_k=4)

        # 'b' and 'c' should be first since they appear in both
        ids = [r["id"] for r in fused]
        assert ids.index("b") < ids.index("a")  # b before a
        assert ids.index("b") < ids.index("c")  # b before c
        assert ids.index("c") < ids.index("a")  # c before a
        assert "d" in ids  # d should be included
        assert ids.index("d") > ids.index("b")  # d after b (only in vector)

    def test_rrf_fusion_empty_bm25(self):
        """RRF works with empty BM25 results."""
        service = HybridRetrievalService(MagicMock())

        bm25_results = []
        vector_results = [
            {"id": "a", "content": "doc a", "filename": "a.txt"},
        ]

        fused = service._rrf_fusion(bm25_results, vector_results, top_k=3)
        assert len(fused) == 1
        assert fused[0]["id"] == "a"

    def test_rrf_fusion_empty_vector(self):
        """RRF works with empty vector results."""
        service = HybridRetrievalService(MagicMock())

        bm25_results = [
            {"id": "a", "content": "doc a", "filename": "a.txt"},
        ]
        vector_results = []

        fused = service._rrf_fusion(bm25_results, vector_results, top_k=3)
        assert len(fused) == 1
        assert fused[0]["id"] == "a"

    def test_rrf_fusion_preserves_metadata(self):
        """RRF fusion preserves chunk metadata."""
        service = HybridRetrievalService(MagicMock())

        bm25_results = [
            {"id": "a", "content": "doc a", "filename": "a.txt", "bm25_rank": 0},
        ]
        vector_results = [
            {"id": "a", "content": "doc a", "filename": "a.txt", "vector_rank": 0},
        ]

        fused = service._rrf_fusion(bm25_results, vector_results, top_k=3)
        assert len(fused) == 1
        assert fused[0]["filename"] == "a.txt"
        assert fused[0]["bm25_rank"] == 0
        assert fused[0]["vector_rank"] == 0
        assert "rrf_score" in fused[0]

    def test_rrf_fusion_respects_top_k(self):
        """RRF fusion respects top_k limit."""
        service = HybridRetrievalService(MagicMock())

        bm25_results = [
            {"id": str(i), "content": f"doc {i}", "filename": f"{i}.txt"}
            for i in range(10)
        ]
        vector_results = [
            {"id": str(i), "content": f"doc {i}", "filename": f"{i}.txt"}
            for i in range(5, 15)
        ]

        fused = service._rrf_fusion(bm25_results, vector_results, top_k=5)
        assert len(fused) == 5


class TestRerankerService:
    """Tests for reranker service."""

    @pytest.mark.asyncio
    async def test_rerank_chunks_few_results(self):
        """Reranking returns early when too few chunks."""
        from app.services.reranker_service import RerankerService

        service = RerankerService()
        chunks = [
            {"id": "a", "content": "doc a", "filename": "a.txt"},
        ]

        # With only 1 chunk, should return as-is (no LLM call)
        result = await service.rerank_chunks("query", chunks, top_n=5)
        assert len(result) == 1
        assert result[0]["id"] == "a"

    def test_build_rerank_prompt(self):
        """Rerank prompt is built correctly."""
        from app.services.reranker_service import RerankerService

        service = RerankerService()
        chunks = [
            {"id": "a", "content": "This is test content", "filename": "a.txt"},
            {"id": "b", "content": "Another piece of content", "filename": "b.txt"},
        ]

        prompt = service._build_rerank_prompt("test query", chunks)

        assert "test query" in prompt
        assert "Chunk 1" in prompt
        assert "Chunk 2" in prompt
        assert "ID: a" in prompt
        assert "This is test content" in prompt

    def test_parse_rerank_response_valid_json(self):
        """Parse valid JSON rerank response."""
        from app.services.reranker_service import RerankerService

        service = RerankerService()
        chunks = [
            {"id": "a", "content": "doc a", "filename": "a.txt"},
            {"id": "b", "content": "doc b", "filename": "b.txt"},
        ]

        response = '[{"id": "a", "score": 8.5, "reasoning": "good"}, {"id": "b", "score": 3.0}]'
        scores = service._parse_rerank_response(response, chunks)

        assert scores["a"]["score"] == 8.5
        assert scores["a"]["reasoning"] == "good"
        assert scores["b"]["score"] == 3.0

    def test_parse_rerank_response_invalid_json(self):
        """Fallback to equal scores on invalid JSON."""
        from app.services.reranker_service import RerankerService

        service = RerankerService()
        chunks = [
            {"id": "a", "content": "doc a", "filename": "a.txt"},
            {"id": "b", "content": "doc b", "filename": "b.txt"},
        ]

        response = "invalid json response"
        scores = service._parse_rerank_response(response, chunks)

        assert scores["a"]["score"] == 5.0
        assert scores["b"]["score"] == 5.0
