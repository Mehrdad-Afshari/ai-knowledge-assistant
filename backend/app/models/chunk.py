from pydantic import BaseModel, Field


class DocumentChunk(BaseModel):
    chunk_id: str
    document_id: str
    filename: str
    file_type: str
    text: str
    page_number: int | None = None
    chunk_index: int
    metadata: dict = Field(default_factory=dict)