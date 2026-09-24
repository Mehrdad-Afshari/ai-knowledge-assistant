from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    query: str = Field(
        min_length=1,
        description="User question.",
    )
    top_k: int = Field(
        default=5,
        ge=1,
        le=10,
    )


class Source(BaseModel):
    chunk_id: str
    document_id: str
    filename: str
    page_number: int | None = None
    relevance_score: float


class ChatResponse(BaseModel):
    query: str
    answer: str
    sources: list[Source]