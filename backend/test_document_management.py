from pathlib import Path
from tempfile import TemporaryDirectory

from app.models.chunk import DocumentChunk
from app.models.embedding import EmbeddedChunk
from app.rag.vector_store import FAISSVectorStore


def build_chunk(
    chunk_id: str,
    document_id: str,
    filename: str,
    chunk_index: int,
) -> DocumentChunk:
    return DocumentChunk(
        chunk_id=chunk_id,
        document_id=document_id,
        filename=filename,
        file_type="txt",
        text=f"Content for {chunk_id}",
        page_number=None,
        chunk_index=chunk_index,
        metadata={
            "filename": filename,
            "file_type": "txt",
        },
    )


def main():
    with TemporaryDirectory() as directory:
        storage_dir = Path(directory)

        store = FAISSVectorStore(
            dimension=3,
            storage_dir=storage_dir,
        )

        chunks = [
            build_chunk("chunk-a1", "doc-a", "alpha.txt", 0),
            build_chunk("chunk-a2", "doc-a", "alpha.txt", 1),
            build_chunk("chunk-b1", "doc-b", "beta.txt", 0),
        ]

        embeddings = [
            EmbeddedChunk(chunk_id="chunk-a1", vector=[1.0, 0.0, 0.0]),
            EmbeddedChunk(chunk_id="chunk-a2", vector=[0.9, 0.1, 0.0]),
            EmbeddedChunk(chunk_id="chunk-b1", vector=[0.0, 1.0, 0.0]),
        ]

        store.add_chunks(chunks, embeddings)

        documents = store.list_documents()

        assert store.document_count == 2
        assert store.size == 3
        assert len(documents) == 2
        assert documents[0].filename == "alpha.txt"
        assert documents[0].chunk_count == 2

        removed = store.remove_document("doc-a")

        assert removed == 2
        assert store.document_count == 1
        assert store.size == 1
        assert store.list_documents()[0].filename == "beta.txt"

        reloaded_store = FAISSVectorStore(
            dimension=3,
            storage_dir=storage_dir,
        )

        assert reloaded_store.document_count == 1
        assert reloaded_store.size == 1
        assert reloaded_store.list_documents()[0].document_id == "doc-b"

        print("Document management test passed.")


if __name__ == "__main__":
    main()
