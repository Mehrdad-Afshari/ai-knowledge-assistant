import json
from pathlib import Path
from tempfile import NamedTemporaryFile
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from app.core.config import settings
from app.models.chat import ChatRequest
from app.models.library import (
    DeleteDocumentResponse,
    DocumentListResponse,
    KnowledgeBaseStats,
)
from app.models.search import SearchRequest
from app.rag.indexing_service import IndexingService
from app.rag.rag_service import RAGService
from app.rag.retrieval_service import RetrievalService
from app.rag.vector_store import FAISSVectorStore
from app.services.chunker import DocumentChunker
from app.services.document_loader import DocumentLoader
from app.services.embedding_service import EmbeddingService
from app.services.llm_service import LLMService


router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


loader = DocumentLoader()

chunker = DocumentChunker(
    chunk_size=1000,
    chunk_overlap=150,
)

embedding_service = EmbeddingService()

vector_store = FAISSVectorStore(
    dimension=768,
)

indexing_service = IndexingService(
    loader=loader,
    chunker=chunker,
    embedding_service=embedding_service,
    vector_store=vector_store,
)

retrieval_service = RetrievalService(
    embedding_service=embedding_service,
    vector_store=vector_store,
)

llm_service = LLMService()

rag_service = RAGService(
    retrieval_service=retrieval_service,
    llm_service=llm_service,
)


SUPPORTED_EXTENSIONS = {
    ".pdf",
    ".txt",
    ".md",
}


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
):
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required.",
        )

    extension = Path(file.filename).suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported file type. "
                "Supported types: PDF, TXT, Markdown."
            ),
        )

    document_id = str(uuid4())

    try:
        file_content = await file.read()

        max_upload_bytes = settings.max_upload_mb * 1024 * 1024

        if len(file_content) > max_upload_bytes:
            raise HTTPException(
                status_code=413,
                detail=(
                    "File is too large. "
                    f"Maximum upload size is {settings.max_upload_mb} MB."
                ),
            )

        if not file_content:
            raise HTTPException(
                status_code=400,
                detail="Uploaded file is empty.",
            )

        with NamedTemporaryFile(
            suffix=extension,
            delete=False,
        ) as temporary_file:
            temporary_file.write(file_content)
            temporary_file_path = Path(
                temporary_file.name
            )

        try:
            document, chunks = (
                indexing_service.index_document(
                    temporary_file_path,
                    document_id=document_id,
                    original_filename=file.filename,
                )
            )
        finally:
            temporary_file_path.unlink(
                missing_ok=True
            )

    except HTTPException:
        raise

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process document: {exc}",
        ) from exc

    return {
        "document_id": document.document_id,
        "filename": document.filename,
        "file_type": document.file_type,
        "content_length": len(document.content),
        "page_count": len(document.pages),
        "chunk_count": len(chunks),
        "indexed_vectors": vector_store.size,
        "status": "indexed",
    }


@router.get("", response_model=DocumentListResponse)
async def list_documents():
    documents = vector_store.list_documents()

    return DocumentListResponse(
        documents=documents,
        document_count=len(documents),
        indexed_vectors=vector_store.size,
    )


@router.delete(
    "/{document_id}",
    response_model=DeleteDocumentResponse,
)
async def delete_document(document_id: str):
    removed_chunks = vector_store.remove_document(
        document_id
    )

    if removed_chunks == 0:
        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )

    return DeleteDocumentResponse(
        document_id=document_id,
        removed_chunks=removed_chunks,
        indexed_vectors=vector_store.size,
        status="deleted",
    )


@router.post("/search")
async def search_documents(
    request: SearchRequest,
):
    try:
        results = retrieval_service.retrieve(
            query=request.query,
            top_k=request.top_k,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {exc}",
        ) from exc

    return {
        "query": request.query,
        "result_count": len(results),
        "results": [
            result.model_dump()
            for result in results
        ],
    }


@router.post("/chat")
async def chat_with_documents(
    request: ChatRequest,
):
    try:
        response = rag_service.answer(
            query=request.query,
            top_k=request.top_k,
        )

        return response.model_dump()

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"RAG generation failed: {exc}",
        ) from exc


@router.post("/chat/stream")
async def stream_chat_with_documents(
    request: ChatRequest,
):
    try:
        stream, sources = rag_service.stream_answer(
            query=request.query,
            top_k=request.top_k,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"RAG streaming failed: {exc}",
        ) from exc

    async def event_generator():
        metadata = {
            "type": "sources",
            "sources": [
                source.model_dump()
                for source in sources
            ],
        }

        yield (
            f"data: {json.dumps(metadata)}\n\n"
        )

        for token in stream:
            payload = {
                "type": "token",
                "content": token,
            }

            yield (
                f"data: {json.dumps(payload)}\n\n"
            )

        yield (
            f"data: {json.dumps({'type': 'done'})}\n\n"
        )

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get(
    "/stats",
    response_model=KnowledgeBaseStats,
)
async def document_stats():
    return KnowledgeBaseStats(
        document_count=vector_store.document_count,
        indexed_vectors=vector_store.size,
        embedding_dimension=vector_store.dimension,
        persisted=vector_store.is_persisted,
    )
