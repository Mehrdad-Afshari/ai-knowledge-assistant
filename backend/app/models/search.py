from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    query: str = Field(
        min_length=1,
        description="Question or search query.",
    )
    top_k: int = Field(
        default=5,
        ge=1,
        le=20,
    )


class SearchResult(BaseModel):
    chunk_id: str
    document_id: str
    filename: str
    text: str
    page_number: int | None = None
    chunk_index: int
    relevance_score: float