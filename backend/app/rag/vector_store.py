import json
from pathlib import Path

import faiss
import numpy as np

from app.models.chunk import DocumentChunk
from app.models.embedding import EmbeddedChunk
from app.models.library import IndexedDocument


class FAISSVectorStore:
    """Persistent FAISS vector store for semantic similarity search."""

    STORAGE_VERSION = 1

    def __init__(
        self,
        dimension: int = 768,
        storage_dir: Path | None = None,
    ):
        self.dimension = dimension

        backend_dir = Path(__file__).resolve().parents[2]
        self.storage_dir = storage_dir or backend_dir / "data" / "index"
        self.index_path = self.storage_dir / "index.faiss"
        self.metadata_path = self.storage_dir / "chunks.json"

        self.index = faiss.IndexFlatIP(dimension)
        self.chunks: list[DocumentChunk] = []
        self.chunk_id_to_position: dict[str, int] = {}

        self.load()

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

        for chunk, embedding in zip(chunks, embeddings):
            if chunk.chunk_id != embedding.chunk_id:
                raise ValueError(
                    "Chunk and embedding IDs must match."
                )

            if chunk.chunk_id in self.chunk_id_to_position:
                raise ValueError(
                    f"Chunk already exists: {chunk.chunk_id}"
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

        self.save()

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

    def list_documents(self) -> list[IndexedDocument]:
        grouped: dict[str, list[DocumentChunk]] = {}

        for chunk in self.chunks:
            grouped.setdefault(
                chunk.document_id,
                [],
            ).append(chunk)

        documents: list[IndexedDocument] = []

        for document_id, chunks in grouped.items():
            first_chunk = chunks[0]
            page_numbers = {
                chunk.page_number
                for chunk in chunks
                if chunk.page_number is not None
            }

            documents.append(
                IndexedDocument(
                    document_id=document_id,
                    filename=first_chunk.filename,
                    file_type=first_chunk.file_type,
                    chunk_count=len(chunks),
                    page_count=(
                        max(page_numbers)
                        if page_numbers
                        else 0
                    ),
                )
            )

        documents.sort(
            key=lambda document: document.filename.lower()
        )

        return documents

    def remove_document(self, document_id: str) -> int:
        positions_to_remove = {
            index
            for index, chunk in enumerate(self.chunks)
            if chunk.document_id == document_id
        }

        if not positions_to_remove:
            return 0

        keep_chunks = [
            chunk
            for index, chunk in enumerate(self.chunks)
            if index not in positions_to_remove
        ]

        keep_embeddings = [
            self.index.reconstruct(index)
            for index in range(self.index.ntotal)
            if index not in positions_to_remove
        ]

        self.index = faiss.IndexFlatIP(self.dimension)

        if keep_embeddings:
            vectors = np.array(
                keep_embeddings,
                dtype=np.float32,
            )
            self.index.add(vectors)

        self.chunks = keep_chunks
        self._rebuild_chunk_positions()
        self.save()

        return len(positions_to_remove)

    def save(self) -> None:
        self.storage_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        temporary_index_path = self.index_path.with_suffix(
            ".faiss.tmp"
        )
        temporary_metadata_path = self.metadata_path.with_suffix(
            ".json.tmp"
        )

        faiss.write_index(
            self.index,
            str(temporary_index_path),
        )

        metadata = {
            "version": self.STORAGE_VERSION,
            "dimension": self.dimension,
            "chunks": [
                chunk.model_dump()
                for chunk in self.chunks
            ],
        }

        temporary_metadata_path.write_text(
            json.dumps(
                metadata,
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

        temporary_index_path.replace(
            self.index_path
        )
        temporary_metadata_path.replace(
            self.metadata_path
        )

    def load(self) -> None:
        index_exists = self.index_path.exists()
        metadata_exists = self.metadata_path.exists()

        if not index_exists and not metadata_exists:
            return

        if index_exists != metadata_exists:
            raise RuntimeError(
                "FAISS persistence is incomplete. "
                "Both index.faiss and chunks.json are required."
            )

        loaded_index = faiss.read_index(
            str(self.index_path)
        )

        metadata = json.loads(
            self.metadata_path.read_text(
                encoding="utf-8"
            )
        )

        stored_version = metadata.get("version")

        if stored_version != self.STORAGE_VERSION:
            raise RuntimeError(
                "Unsupported vector store persistence version: "
                f"{stored_version}."
            )

        stored_dimension = metadata.get("dimension")

        if stored_dimension != self.dimension:
            raise RuntimeError(
                f"Stored embedding dimension is {stored_dimension}, "
                f"but the application expects {self.dimension}."
            )

        if loaded_index.d != self.dimension:
            raise RuntimeError(
                f"Stored FAISS index dimension is {loaded_index.d}, "
                f"but the application expects {self.dimension}."
            )

        chunks = [
            DocumentChunk.model_validate(chunk_data)
            for chunk_data in metadata.get("chunks", [])
        ]

        if loaded_index.ntotal != len(chunks):
            raise RuntimeError(
                "FAISS index and chunk metadata are inconsistent."
            )

        self.index = loaded_index
        self.chunks = chunks
        self._rebuild_chunk_positions()

    def clear(self) -> None:
        self.index = faiss.IndexFlatIP(self.dimension)
        self.chunks.clear()
        self.chunk_id_to_position.clear()

        self.index_path.unlink(
            missing_ok=True
        )
        self.metadata_path.unlink(
            missing_ok=True
        )

    def _rebuild_chunk_positions(self) -> None:
        self.chunk_id_to_position = {
            chunk.chunk_id: index
            for index, chunk in enumerate(self.chunks)
        }

    @property
    def size(self) -> int:
        return self.index.ntotal

    @property
    def document_count(self) -> int:
        return len(
            {
                chunk.document_id
                for chunk in self.chunks
            }
        )

    @property
    def is_persisted(self) -> bool:
        return (
            self.index_path.exists()
            and self.metadata_path.exists()
        )
