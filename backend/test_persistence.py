from pathlib import Path
from tempfile import TemporaryDirectory

from app.models.chunk import DocumentChunk
from app.models.embedding import EmbeddedChunk
from app.rag.vector_store import FAISSVectorStore


def main():
    with TemporaryDirectory() as temporary_directory:
        storage_dir = Path(temporary_directory)

        store = FAISSVectorStore(
            dimension=3,
            storage_dir=storage_dir,
        )

        chunks = [
            DocumentChunk(
                chunk_id="chunk-1",
                document_id="document-1",
                filename="example.txt",
                file_type="txt",
                text="Artificial intelligence knowledge base.",
                page_number=None,
                chunk_index=0,
                metadata={
                    "filename": "example.txt",
                    "file_type": "txt",
                },
            ),
            DocumentChunk(
                chunk_id="chunk-2",
                document_id="document-1",
                filename="example.txt",
                file_type="txt",
                text="Vector search with FAISS.",
                page_number=None,
                chunk_index=1,
                metadata={
                    "filename": "example.txt",
                    "file_type": "txt",
                },
            ),
        ]

        embeddings = [
            EmbeddedChunk(
                chunk_id="chunk-1",
                vector=[1.0, 0.0, 0.0],
            ),
            EmbeddedChunk(
                chunk_id="chunk-2",
                vector=[0.0, 1.0, 0.0],
            ),
        ]

        store.add_chunks(
            chunks,
            embeddings,
        )

        print(f"Initial store size: {store.size}")
        print(f"Persisted: {store.is_persisted}")

        reloaded_store = FAISSVectorStore(
            dimension=3,
            storage_dir=storage_dir,
        )

        print(f"Reloaded store size: {reloaded_store.size}")

        results = reloaded_store.search(
            query_vector=[1.0, 0.0, 0.0],
            top_k=1,
        )

        if not results:
            raise RuntimeError(
                "Persistence test failed: no search results after reload."
            )

        chunk, score = results[0]

        print(f"Top chunk: {chunk.chunk_id}")
        print(f"Score: {score:.4f}")

        assert store.size == 2
        assert reloaded_store.size == 2
        assert reloaded_store.is_persisted
        assert chunk.chunk_id == "chunk-1"

        print("Persistence test passed.")


if __name__ == "__main__":
    main()
