from fastapi import FastAPI

from app.api.documents import router as documents_router


app = FastAPI(
    title="AI Knowledge Assistant API",
    description=(
        "Backend API for a Retrieval-Augmented Generation "
        "knowledge assistant."
    ),
    version="0.3.0",
)


app.include_router(documents_router)


@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": "ai-knowledge-assistant",
    }