import os

import ollama

from app.models.chunk import DocumentChunk
from app.models.embedding import EmbeddedChunk


class EmbeddingService:
    """Generate local vector embeddings using Ollama."""

    MODEL_NAME = os.getenv(
        "OLLAMA_EMBEDDING_MODEL",
        "nomic-embed-text",
    )

    def __init__(self):
        self.client = ollama.Client(
            host=os.getenv(
                "OLLAMA_HOST",
                "http://localhost:11434",
            )
        )

    def embed_text(self, text: str) -> list[float]:
        if not text.strip():
            raise ValueError(
                "Cannot generate an embedding for empty text."
            )

        response = self.client.embed(
            model=self.MODEL_NAME,
            input=text,
        )

        return response["embeddings"][0]

    def embed_chunks(
        self,
        chunks: list[DocumentChunk],
    ) -> list[EmbeddedChunk]:
        if not chunks:
            return []

        texts = [chunk.text for chunk in chunks]

        response = self.client.embed(
            model=self.MODEL_NAME,
            input=texts,
        )

        embeddings = response["embeddings"]

        return [
            EmbeddedChunk(
                chunk_id=chunk.chunk_id,
                vector=vector,
            )
            for chunk, vector in zip(chunks, embeddings)
        ]