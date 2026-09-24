from pydantic import BaseModel, Field


class DocumentPage(BaseModel):
    page_number: int
    content: str


class LoadedDocument(BaseModel):
    document_id: str
    filename: str
    file_type: str
    content: str
    pages: list[DocumentPage] = Field(default_factory=list)