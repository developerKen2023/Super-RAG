import httpx
from app.config import get_settings
from typing import List

settings = get_settings()

class MiniMaxEmbedding:
    def __init__(self):
        self.base_url = settings.minimax_base_url
        self.api_key = settings.minimax_api_key
        self.model = "embo-01"  # MiniMax embedding model

    def embed(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts using httpx directly."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "texts": texts,
            "type": "db"  # MiniMax requires type: "query" or "db"
        }

        with httpx.Client() as client:
            response = client.post(
                f"{self.base_url}/embeddings",
                json=payload,
                headers=headers,
                timeout=60.0
            )

            if response.status_code != 200:
                raise Exception(f"Embedding API error: {response.status_code} - {response.text}")

            data = response.json()
            # MiniMax returns "vectors" not "data"
            if "vectors" in data and data["vectors"]:
                return data["vectors"]
            raise Exception(f"No vectors in response: {data}")

    def embed_query(self, query: str) -> List[float]:
        """Embed a single query."""
        embeddings = self.embed([query])
        return embeddings[0]
