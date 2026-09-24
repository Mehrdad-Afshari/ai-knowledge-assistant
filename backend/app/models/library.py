from pydantic import BaseModel


class IndexedDocument(BaseModel):
    document_id: str
    filename: str
    file_type: str
    chunk_count: int
    page_count: int


class DocumentListResponse(BaseModel):
    documents: list[IndexedDocument]
    document_count: int
    indexed_vectors: int


class DeleteDocumentResponse(BaseModel):
    document_id: str
    removed_chunks: int
    indexed_vectors: int
    status: str


class KnowledgeBaseStats(BaseModel):
    document_count: int
    indexed_vectors: int
    embedding_dimension: int
    persisted: bool
