from app.rag.vector_store import FAISSVectorStore
from app.services.embedding_service import EmbeddingService


def main():
    embedding_service = EmbeddingService()

    vector_store = FAISSVectorStore(
        dimension=768,
    )

    texts = [
        (
            "Retrieval-Augmented Generation combines "
            "semantic search with large language models."
        ),
        (
            "FAISS is a library for efficient similarity "
            "search over dense vectors."
        ),
        (
            "Python is widely used for artificial intelligence "
            "and machine learning applications."
        ),
    ]

    print("Generating embeddings...")

    vectors = [
        embedding_service.embed_text(text)
        for text in texts
    ]

    print("Creating test chunks...")

    from app.models.chunk import DocumentChunk

    chunks = [
        DocumentChunk(
            chunk_id=f"test-{index}",
            document_id="test-document",
            filename="test.txt",
            file_type="txt",
            text=text,
            page_number=None,
            chunk_index=index,
            metadata={
                "filename": "test.txt",
                "file_type": "txt",
            },
        )
        for index, text in enumerate(texts)
    ]

    from app.models.embedding import EmbeddedChunk

    embedded_chunks = [
        EmbeddedChunk(
            chunk_id=chunk.chunk_id,
            vector=vector,
        )
        for chunk, vector in zip(
            chunks,
            vectors,
        )
    ]

    vector_store.add_chunks(
        chunks,
        embedded_chunks,
    )

    print(f"Vectors stored: {vector_store.size}")

    query = (
        "How does semantic search work with "
        "large language models?"
    )

    print("\nQuery:")
    print(query)

    query_vector = embedding_service.embed_text(
        query
    )

    results = vector_store.search(
        query_vector,
        top_k=3,
    )

    print("\nSearch results:")

    for rank, (chunk, score) in enumerate(
        results,
        start=1,
    ):
        print(f"\n#{rank}")
        print(f"Score: {score:.4f}")
        print(f"Chunk ID: {chunk.chunk_id}")
        print(f"Text: {chunk.text}")


if __name__ == "__main__":
    main()
    