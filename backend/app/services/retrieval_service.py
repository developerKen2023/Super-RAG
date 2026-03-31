from supabase import Client
from app.services.embedding_service import embed_query
from typing import List

class RetrievalService:
    def __init__(self, supabase: Client):
        self.supabase = supabase

    def retrieve_relevant_chunks(
        self,
        query: str,
        user_id: str,
        top_k: int = 5,
        similarity_threshold: float = 0.5,
        tag_filter: str | None = None,
        category_filter: str | None = None
    ) -> List[dict]:
        """
        Retrieve relevant document chunks for a query.

        Args:
            query: User's question/query
            user_id: Current user's ID (for RLS)
            top_k: Number of chunks to retrieve
            similarity_threshold: Minimum similarity score (0-1)
            tag_filter: Optional tag to filter documents by
            category_filter: Optional category to filter documents by

        Returns:
            List of relevant chunks with content and metadata
        """
        # Generate embedding for the query
        query_embedding = embed_query(query)
        print(f"Query embedding generated, dimension: {len(query_embedding)}")

        # Search for similar chunks using vector similarity
        # Using match_documents RPC or direct SQL for vector search
        response = self.supabase.rpc(
            "match_document_chunks",
            {
                "query_embedding": query_embedding,
                "match_threshold": similarity_threshold,
                "match_count": top_k,
                "p_user_id": user_id,
                "p_tag": tag_filter,
                "p_category": category_filter
            }
        ).execute()

        print(f"Vector search returned {len(response.data) if response.data else 0} chunks")
        return response.data if response.data else []

    def get_context_for_query(
        self,
        query: str,
        user_id: str,
        top_k: int = 5,
        tag_filter: str | None = None,
        category_filter: str | None = None
    ) -> str:
        """
        Get formatted context string from relevant chunks for LLM context.

        Args:
            query: User's question/query
            user_id: Current user's ID (for RLS)
            top_k: Number of chunks to retrieve
            tag_filter: Optional tag to filter documents by
            category_filter: Optional category to filter documents by

        Returns:
            Formatted string with relevant document excerpts
        """
        chunks = self.retrieve_relevant_chunks(
            query, user_id, top_k, tag_filter=tag_filter, category_filter=category_filter
        )

        if not chunks:
            return ""

        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            context_parts.append(
                f"[Document {i}] {chunk.get('filename', 'Unknown')}:\n{chunk.get('content', '')}"
            )

        return "\n\n".join(context_parts)
