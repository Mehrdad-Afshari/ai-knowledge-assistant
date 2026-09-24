from collections.abc import Iterator

from app.models.chat import ChatResponse, Source
from app.rag.retrieval_service import RetrievalService
from app.services.llm_service import LLMService


class RAGService:
    """Retrieve relevant context and generate an answer."""

    def __init__(
        self,
        retrieval_service: RetrievalService,
        llm_service: LLMService,
    ):
        self.retrieval_service = retrieval_service
        self.llm_service = llm_service

    def _build_context(
        self,
        results,
    ) -> str:
        context_parts = []

        for index, result in enumerate(
            results,
            start=1,
        ):
            context_parts.append(
                f"""
[Source {index}]
Document: {result.filename}
Page: {result.page_number}
Relevance: {result.relevance_score}

Content:
{result.text}
"""
            )

        return "\n".join(context_parts)

    def _build_sources(
        self,
        results,
    ) -> list[Source]:
        return [
            Source(
                chunk_id=result.chunk_id,
                document_id=result.document_id,
                filename=result.filename,
                page_number=result.page_number,
                relevance_score=result.relevance_score,
            )
            for result in results
        ]

    def answer(
        self,
        query: str,
        top_k: int = 5,
    ) -> ChatResponse:
        results = self.retrieval_service.retrieve(
            query=query,
            top_k=top_k,
        )

        if not results:
            return ChatResponse(
                query=query,
                answer=(
                    "I could not find relevant information "
                    "in the indexed documents."
                ),
                sources=[],
            )

        context = self._build_context(results)

        answer = self.llm_service.generate(
            question=query,
            context=context,
        )

        return ChatResponse(
            query=query,
            answer=answer,
            sources=self._build_sources(results),
        )

    def stream_answer(
        self,
        query: str,
        top_k: int = 5,
    ) -> tuple[Iterator[str], list[Source]]:
        results = self.retrieval_service.retrieve(
            query=query,
            top_k=top_k,
        )

        if not results:
            def empty_result():
                yield (
                    "I could not find relevant information "
                    "in the indexed documents."
                )

            return empty_result(), []

        context = self._build_context(results)

        stream = self.llm_service.stream(
            question=query,
            context=context,
        )

        return stream, self._build_sources(results)