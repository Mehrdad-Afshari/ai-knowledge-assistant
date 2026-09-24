import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.documents import router as documents_router


app = FastAPI(
    title="AI Knowledge Assistant API",
    description=(
        "Backend API for a Retrieval-Augmented Generation "
        "knowledge assistant."
    ),
    version="0.8.0",
)


cors_origins = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000",
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(documents_router)


@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": "ai-knowledge-assistant",
    }
