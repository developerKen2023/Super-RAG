import httpx
from app.config import get_settings
from typing import List
import logging

logger = logging.getLogger(__name__)

settings = get_settings()

class MiniMaxEmbedding:
    def __init__(self):
        self.base_url = settings.minimax_base_url
        self.api_key = settings.minimax_api_key
        self.model = "embo-01"  # MiniMax embedding model

    def embed(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts using httpx directly."""
        # Filter out empty or whitespace-only texts
        texts = [t.strip() for t in texts if t and t.strip()]
        if not texts:
            raise ValueError("No valid texts to embed after filtering empty strings")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "texts": texts,
            "type": "db"  # MiniMax requires type: "query" or "db"
        }

        logger.info(f"[Embedding] Sending {len(texts)} chunks to MiniMax API")

        with httpx.Client() as client:
            response = client.post(
                f"{self.base_url}/embeddings",
                json=payload,
                headers=headers,
                timeout=60.0
            )

            logger.info(f"[Embedding] Response status: {response.status_code}")

            if response.status_code != 200:
                raise Exception(f"Embedding API error: {response.status_code} - {response.text}")

            data = response.json()
            logger.info(f"[Embedding] Response data keys: {data.keys()}")

            # MiniMax returns "vectors" not "data"
            if "vectors" in data and data["vectors"]:
                logger.info(f"[Embedding] Received {len(data['vectors'])} vectors")
                return data["vectors"]
            raise Exception(f"No vectors in response: {data}")

    def embed_query(self, query: str) -> List[float]:
        """Embed a single query."""
        embeddings = self.embed([query])
        return embeddings[0]
