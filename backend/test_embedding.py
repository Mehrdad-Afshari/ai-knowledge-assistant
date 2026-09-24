from app.services.embedding_service import EmbeddingService


def main():
    service = EmbeddingService()

    text = """
    Retrieval-Augmented Generation combines semantic retrieval
    with large language models to provide answers based on
    external knowledge.
    """

    vector = service.embed_text(text)

    print(f"Embedding model: {service.MODEL_NAME}")
    print(f"Vector dimensions: {len(vector)}")
    print(f"First 5 values: {vector[:5]}")


if __name__ == "__main__":
    main()