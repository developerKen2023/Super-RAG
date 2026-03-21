from app.services.embeddings.minimax_embedding import MiniMaxEmbedding
from typing import List

_embedding_service = None

def get_embedding_service() -> MiniMaxEmbedding:
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = MiniMaxEmbedding()
    return _embedding_service

def embed_texts(texts: List[str]) -> List[List[float]]:
    """Batch embed texts."""
    service = get_embedding_service()
    return service.embed(texts)

def embed_query(query: str) -> List[float]:
    """Embed a single query."""
    service = get_embedding_service()
    return service.embed_query(query)