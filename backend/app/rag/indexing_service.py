from app.models.chunk import DocumentChunk
from app.models.document import LoadedDocument
from app.rag.vector_store import FAISSVectorStore
from app.services.chunker import DocumentChunker
from app.services.document_loader import DocumentLoader
from app.services.embedding_service import EmbeddingService


class IndexingService:
    """Coordinate document loading, chunking, embedding, and indexing."""

    def __init__(
        self,
        loader: DocumentLoader,
        chunker: DocumentChunker,
        embedding_service: EmbeddingService,
        vector_store: FAISSVectorStore,
    ):
        self.loader = loader
        self.chunker = chunker
        self.embedding_service = embedding_service
        self.vector_store = vector_store

    def index_document(
        self,
        document_path,
        document_id: str,
    ) -> tuple[LoadedDocument, list[DocumentChunk]]:
        document = self.loader.load(
            document_path,
            document_id=document_id,
        )

        chunks = self.chunker.chunk_document(document)

        if not chunks:
            raise ValueError(
                "The document does not contain any usable text."
            )

        embeddings = self.embedding_service.embed_chunks(
            chunks
        )

        self.vector_store.add_chunks(
            chunks,
            embeddings,
        )

        return document, chunks