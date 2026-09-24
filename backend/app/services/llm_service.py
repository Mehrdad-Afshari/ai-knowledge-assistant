from collections.abc import Iterator

import ollama

from app.core.config import settings


class LLMService:
    """Generate answers using a local Ollama language model."""

    MODEL_NAME = settings.ollama_llm_model

    def __init__(self):
        self.client = ollama.Client(
            host=settings.ollama_host,
        )

    def _build_messages(
        self,
        question: str,
        context: str,
    ) -> list[dict[str, str]]:
        system_prompt = """
You are a knowledge assistant.

Answer the user's question using ONLY the
provided context.

Rules:
- Do not use outside knowledge.
- If the answer is not contained in the context,
  clearly say that the information was not found
  in the provided documents.
- Do not invent facts.
- Be concise and precise.
"""

        user_prompt = f"""
Context:

{context}

Question:

{question}

Answer:
"""

        return [
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ]

    def generate(
        self,
        question: str,
        context: str,
    ) -> str:
        if not question.strip():
            raise ValueError(
                "Question cannot be empty."
            )

        if not context.strip():
            raise ValueError(
                "Context cannot be empty."
            )

        response = self.client.chat(
            model=self.MODEL_NAME,
            messages=self._build_messages(
                question,
                context,
            ),
        )

        return response.message.content.strip()

    def stream(
        self,
        question: str,
        context: str,
    ) -> Iterator[str]:
        if not question.strip():
            raise ValueError(
                "Question cannot be empty."
            )

        if not context.strip():
            raise ValueError(
                "Context cannot be empty."
            )

        response = self.client.chat(
            model=self.MODEL_NAME,
            messages=self._build_messages(
                question,
                context,
            ),
            stream=True,
        )

        for chunk in response:
            content = chunk.message.content

            if content:
                yield content
