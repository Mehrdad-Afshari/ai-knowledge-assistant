import faiss
import numpy as np

from app.models.chunk import DocumentChunk
from app.models.embedding import EmbeddedChunk


class FAISSVectorStore:
    """In-memory FAISS vector store for semantic similarity search."""

    def __init__(self, dimension: int = 768):
        self.dimension = dimension
        self.index = faiss.IndexFlatIP(dimension)

        self.chunks: list[DocumentChunk] = []
        self.chunk_id_to_position: dict[str, int] = {}

    def add_chunks(
        self,
        chunks: list[DocumentChunk],
        embeddings: list[EmbeddedChunk],
    ) -> None:
        if not chunks:
            return

        if len(chunks) != len(embeddings):
            raise ValueError(
                "The number of chunks and embeddings must match."
            )

        vectors = np.array(
            [embedding.vector for embedding in embeddings],
            dtype=np.float32,
        )

        if vectors.ndim != 2:
            raise ValueError(
                "Embeddings must form a 2-dimensional matrix."
            )

        if vectors.shape[1] != self.dimension:
            raise ValueError(
                f"Expected embedding dimension {self.dimension}, "
                f"but received {vectors.shape[1]}."
            )

        faiss.normalize_L2(vectors)

        start_position = len(self.chunks)

        self.index.add(vectors)

        for offset, chunk in enumerate(chunks):
            position = start_position + offset

            self.chunks.append(chunk)
            self.chunk_id_to_position[chunk.chunk_id] = position

    def search(
        self,
        query_vector: list[float],
        top_k: int = 5,
    ) -> list[tuple[DocumentChunk, float]]:
        if not query_vector:
            raise ValueError(
                "Query vector cannot be empty."
            )

        if top_k <= 0:
            raise ValueError(
                "top_k must be greater than zero."
            )

        if self.index.ntotal == 0:
            return []

        vector = np.array(
            [query_vector],
            dtype=np.float32,
        )

        if vector.shape[1] != self.dimension:
            raise ValueError(
                f"Expected query vector dimension {self.dimension}, "
                f"but received {vector.shape[1]}."
            )

        faiss.normalize_L2(vector)

        actual_k = min(top_k, self.index.ntotal)

        scores, positions = self.index.search(
            vector,
            actual_k,
        )

        results: list[tuple[DocumentChunk, float]] = []

        for score, position in zip(
            scores[0],
            positions[0],
        ):
            if position < 0:
                continue

            chunk = self.chunks[int(position)]

            results.append(
                (
                    chunk,
                    float(score),
                )
            )

        return results

    def remove_document(self, document_id: str) -> int:
        positions = [
            index
            for index, chunk in enumerate(self.chunks)
            if chunk.document_id == document_id
        ]

        if not positions:
            return 0

        keep_chunks = [
            chunk
            for index, chunk in enumerate(self.chunks)
            if index not in positions
        ]

        keep_embeddings = []

        for index in range(self.index.ntotal):
            if index not in positions:
                vector = self.index.reconstruct(index)
                keep_embeddings.append(vector)

        self.index = faiss.IndexFlatIP(self.dimension)

        if keep_embeddings:
            vectors = np.array(
                keep_embeddings,
                dtype=np.float32,
            )
            self.index.add(vectors)

        self.chunks = keep_chunks

        self.chunk_id_to_position = {
            chunk.chunk_id: index
            for index, chunk in enumerate(self.chunks)
        }

        return len(positions)

    def clear(self) -> None:
        self.index.reset()
        self.chunks.clear()
        self.chunk_id_to_position.clear()

    @property
    def size(self) -> int:
        return self.index.ntotal