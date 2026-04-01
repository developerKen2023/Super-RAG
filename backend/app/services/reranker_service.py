from app.services.llm_providers import get_llm_provider
from typing import List, Dict
import logging
import json

logger = logging.getLogger(__name__)


class RerankerService:
    """
    Reranks retrieval candidates using LLM-based relevance scoring.
    """

    def __init__(self, provider_type: str = "minimax"):
        self.provider = get_llm_provider(provider_type)

    async def rerank_chunks(
        self,
        query: str,
        chunks: List[dict],
        top_n: int = 5
    ) -> List[dict]:
        """
        Rerank chunks by relevance to query using LLM.

        Args:
            query: The user's question
            chunks: List of chunk dicts with 'id', 'content', 'filename'
            top_n: Number of top results to return

        Returns:
            Chunks reordered by relevance score (descending)
        """
        if not chunks:
            return []

        if len(chunks) <= 2:
            # No need to rerank very few results
            return chunks

        # Build reranking prompt
        rerank_prompt = self._build_rerank_prompt(query, chunks)

        try:
            # Get relevance scores via LLM
            response = await self.provider.chat_complete(
                messages=[
                    {"role": "system", "content": "You are a relevance scoring assistant. Rate each chunk's relevance to the query on a scale of 0-10. Respond with JSON array."},
                    {"role": "user", "content": rerank_prompt}
                ],
                stream=False
            )

            # Parse scores from response
            scores = self._parse_rerank_response(response, chunks)

            # Reorder chunks by score
            chunk_map = {c["id"]: c for c in chunks}
            scored_chunks = []
            for chunk_id, score_data in scores.items():
                chunk = chunk_map[chunk_id].copy()
                chunk["rerank_score"] = score_data["score"]
                chunk["rerank_reasoning"] = score_data.get("reasoning", "")
                scored_chunks.append(chunk)

            scored_chunks.sort(key=lambda x: x["rerank_score"], reverse=True)

            logger.info(f"Reranked {len(chunks)} chunks, top score: {scored_chunks[0]['rerank_score'] if scored_chunks else 0}")
            return scored_chunks[:top_n]

        except Exception as e:
            logger.warning(f"Reranking failed, returning original order: {e}")
            return chunks[:top_n]

    def _build_rerank_prompt(self, query: str, chunks: List[dict]) -> str:
        """Build prompt for reranking."""
        chunks_text = []
        for i, chunk in enumerate(chunks[:10]):  # Limit to 10 for cost
            chunks_text.append(
                f"Chunk {i+1} (ID: {chunk['id']}):\n{chunk.get('content', '')[:500]}"
            )

        return f"""Query: {query}

Rate the relevance of each chunk to the query on a scale of 0-10:
- 0-3: Not relevant, doesn't help answer query
- 4-6: Somewhat relevant, partial answer
- 7-10: Highly relevant, directly answers query

Chunks:
{chr(10).join(chunks_text)}

Respond with JSON array:
[{{"id": "chunk_id", "score": 8.5, "reasoning": "brief reason"}}]"""

    def _parse_rerank_response(self, response: str, chunks: List[dict]) -> dict:
        """Parse LLM response to extract scores."""
        try:
            # Try to extract JSON from response
            json_start = response.find('[')
            json_end = response.rfind(']') + 1
            if json_start >= 0 and json_end > json_start:
                scores_json = response[json_start:json_end]
                scores = json.loads(scores_json)
                return {s["id"]: s for s in scores}
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse rerank response: {e}")

        # Fallback: return equal scores
        return {c["id"]: {"score": 5.0, "reasoning": ""} for c in chunks}
