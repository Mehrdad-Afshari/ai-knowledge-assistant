from pydantic import BaseModel


class EmbeddedChunk(BaseModel):
    chunk_id: str
    vector: list[float]