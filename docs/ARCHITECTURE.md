# Architecture

## Overview

AI Knowledge Assistant is a local-first Retrieval-Augmented Generation (RAG) application with a clear separation between presentation, API orchestration, retrieval, persistence, and local model inference.

The design goal for v1.0 is not maximum abstraction. It is architectural transparency: each RAG step is visible in the codebase and can be explained independently.

## System Diagram

```text
┌──────────────────────────────────────────────┐
│               Next.js Frontend              │
│                                              │
│  Upload UI  Document Library  Chat UI        │
└──────────────────────┬───────────────────────┘
                       │
                 REST + SSE
                       │
                       v
┌──────────────────────────────────────────────┐
│                FastAPI Backend               │
│                                              │
│  /documents/upload                           │
│  /documents                                  │
│  /documents/{id}                             │
│  /documents/search                           │
│  /documents/chat                             │
│  /documents/chat/stream                      │
│  /documents/stats                            │
│  /health                                     │
└───────────────┬──────────────────────────────┘
                │
      ┌─────────┴──────────┐
      │                    │
      v                    v
Document Pipeline       Query Pipeline
      │                    │
      v                    v
DocumentLoader       EmbeddingService
      │                    │
      v                    v
DocumentChunker      RetrievalService
      │                    │
      v                    v
EmbeddingService     FAISSVectorStore
      │                    │
      v                    v
FAISSVectorStore      RAGService
                           │
                           v
                       LLMService
                           │
                           v
                      Ollama LLM
```

## Document Ingestion Pipeline

### 1. Upload validation

The FastAPI upload endpoint accepts PDF, TXT, and Markdown files. It validates the file extension, rejects empty files, and enforces the configured upload-size limit.

### 2. Normalization

`DocumentLoader` converts supported file types into one normalized document representation.

- PDF pages are extracted with PyPDF.
- TXT and Markdown are read as UTF-8 text.
- The original uploaded filename is preserved for later source attribution.

### 3. Chunking

`DocumentChunker` applies custom overlapping chunking.

The implementation intentionally remains in the project instead of delegating to a framework so that chunk-size, overlap, normalization, page metadata, and chunk indexing are explicit and testable.

### 4. Embeddings

`EmbeddingService` sends chunk text to Ollama using `nomic-embed-text`.

The current vector dimension is **768**.

### 5. Vector indexing

Embeddings are L2-normalized and stored in `faiss.IndexFlatIP`.

Because both stored and query vectors are normalized, inner product acts as cosine similarity.

## Persistence

The vector store writes two runtime artifacts under `backend/data/index/`:

```text
index.faiss
chunks.json
```

`index.faiss` contains vectors and `chunks.json` contains validated chunk metadata.

On backend startup, the vector store loads both files and verifies:

- persistence version
- embedding dimension
- FAISS dimension
- number of vectors equals number of metadata records

Runtime index data is ignored by Git.

## Retrieval Pipeline

A user query follows this path:

```text
Question
  -> Ollama query embedding
  -> FAISS similarity search
  -> top-k DocumentChunk matches
  -> SearchResult objects
```

Each search result carries:

- chunk ID
- document ID
- original filename
- chunk text
- page number when available
- chunk index
- relevance score

## RAG Generation

`RAGService` converts retrieved results into a structured context and passes that context with the user question to `LLMService`.

The system prompt constrains the model to answer only from retrieved context and to state when the requested information is not found.

The current local generation model is `llama3.2` through Ollama.

## Streaming

The streaming chat endpoint uses Server-Sent Events.

The event sequence is:

```text
sources -> token -> token -> ... -> done
```

This allows the frontend to render source cards immediately and progressively append generated answer text.

## Document Management

Document-level deletion is implemented on top of the flat FAISS index.

Because `IndexFlatIP` does not provide the document abstraction used by the application, deleting a document works by:

1. finding chunk positions belonging to the document
2. reconstructing vectors that should remain
3. creating a fresh flat index
4. re-adding retained vectors
5. updating chunk metadata
6. persisting the new index and metadata

This is intentionally simple and appropriate for the current local portfolio-scale workload.

## Configuration

`backend/app/core/config.py` is the central configuration entry point.

It loads `.env` and exposes:

- Ollama host
- embedding model
- LLM model
- CORS origins
- maximum upload size

No API secrets are required by the default local stack.

## Frontend Architecture

The frontend uses the Next.js App Router and TypeScript.

Primary responsibilities are separated into:

- upload component
- persisted document library component
- chat component
- source rendering component
- typed API client
- shared response/event types

The browser communicates directly with FastAPI during local development using a configurable public API base URL.

## Health and Diagnostics

`GET /health` reports application status and attempts to reach Ollama.

If Ollama is unavailable, the service reports a degraded state rather than pretending inference is healthy.

Knowledge-base statistics are exposed separately through `/documents/stats`.

## Testing Strategy

The release contains automated tests for deterministic application logic that does not require a running Ollama instance, including:

- custom chunking behavior
- FAISS persistence
- document listing/deletion behavior

GitHub Actions validates:

- backend unit tests on Python 3.12
- frontend dependency installation
- ESLint
- Next.js production build on Node.js 22

Ollama-dependent integration behavior is validated locally because GitHub Actions does not install and run the local model runtime.

## Why No LangChain in v1.0?

The project deliberately uses direct SDKs and custom services instead of a RAG framework.

This makes the core mechanics visible:

- document ingestion
- chunk construction
- embedding requests
- vector normalization
- similarity search
- context assembly
- prompt construction
- persistence
- streaming

For a learning and portfolio project, this transparency is a feature.

## Scaling Path

If the application evolves beyond local portfolio use, likely architectural changes include:

- provider abstractions for local/remote embeddings and LLMs
- an approximate-nearest-neighbor index or managed vector database
- durable document metadata storage
- background ingestion jobs
- authentication and tenant isolation
- object storage for original files
- observability and tracing
- OCR for scanned documents

Those are intentionally outside the v1.0 scope.
