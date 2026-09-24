from app.models.search import SearchResult
from app.rag.vector_store import FAISSVectorStore
from app.services.embedding_service import EmbeddingService


class RetrievalService:
    """Retrieve relevant document chunks for a user query."""

    def __init__(
        self,
        embedding_service: EmbeddingService,
        vector_store: FAISSVectorStore,
    ):
        self.embedding_service = embedding_service
        self.vector_store = vector_store

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[SearchResult]:
        if not query.strip():
            raise ValueError(
                "Query cannot be empty."
            )

        if self.vector_store.size == 0:
            return []

        query_vector = (
            self.embedding_service.embed_text(query)
        )

        matches = self.vector_store.search(
            query_vector=query_vector,
            top_k=top_k,
        )

        return [
            SearchResult(
                chunk_id=chunk.chunk_id,
                document_id=chunk.document_id,
                filename=chunk.filename,
                text=chunk.text,
                page_number=chunk.page_number,
                chunk_index=chunk.chunk_index,
                relevance_score=round(score, 4),
            )
            for chunk, score in matches
        ]