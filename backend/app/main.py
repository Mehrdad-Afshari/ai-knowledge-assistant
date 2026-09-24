import ollama
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.documents import router as documents_router
from app.core.config import settings


app = FastAPI(
    title="AI Knowledge Assistant API",
    description=(
        "Backend API for a Retrieval-Augmented Generation "
        "knowledge assistant."
    ),
    version="0.9.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(documents_router)


@app.get("/health")
async def health_check():
    ollama_status = "unavailable"

    try:
        client = ollama.Client(host=settings.ollama_host)
        client.list()
        ollama_status = "ok"
    except Exception:
        pass

    return {
        "status": "ok" if ollama_status == "ok" else "degraded",
        "service": "ai-knowledge-assistant",
        "version": app.version,
        "ollama": ollama_status,
        "embedding_model": settings.ollama_embedding_model,
        "llm_model": settings.ollama_llm_model,
        "max_upload_mb": settings.max_upload_mb,
    }
