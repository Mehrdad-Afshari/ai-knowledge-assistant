import os
from pathlib import Path

from dotenv import load_dotenv


BACKEND_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BACKEND_DIR / ".env")


class Settings:
    """Central application settings loaded from environment variables."""

    def __init__(self):
        self.ollama_host = os.getenv(
            "OLLAMA_HOST",
            "http://localhost:11434",
        )
        self.ollama_embedding_model = os.getenv(
            "OLLAMA_EMBEDDING_MODEL",
            "nomic-embed-text",
        )
        self.ollama_llm_model = os.getenv(
            "OLLAMA_LLM_MODEL",
            "llama3.2",
        )
        self.cors_origins = [
            origin.strip()
            for origin in os.getenv(
                "CORS_ORIGINS",
                "http://localhost:3000,http://127.0.0.1:3000",
            ).split(",")
            if origin.strip()
        ]
        self.max_upload_mb = self._positive_int(
            os.getenv("MAX_UPLOAD_MB", "20"),
            "MAX_UPLOAD_MB",
        )

    @staticmethod
    def _positive_int(value: str, name: str) -> int:
        try:
            parsed = int(value)
        except ValueError as exc:
            raise RuntimeError(
                f"{name} must be an integer."
            ) from exc

        if parsed <= 0:
            raise RuntimeError(
                f"{name} must be greater than zero."
            )

        return parsed


settings = Settings()
