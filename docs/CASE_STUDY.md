# Case Study — AI Knowledge Assistant

## Project Summary

AI Knowledge Assistant is a full-stack local RAG application built to turn personal documents into a searchable AI knowledge base.

The project began as a practical learning exercise and evolved into a portfolio-ready system with document ingestion, semantic retrieval, grounded answer generation, persistence, streaming, document management, automated tests, and CI.

The central goal was to understand and implement the RAG pipeline directly instead of hiding the core mechanics behind a high-level framework.

## Problem

General-purpose language models are useful, but they do not automatically know the contents of a user's private or newly uploaded documents.

A useful document assistant needs to:

1. ingest documents
2. split them into retrievable units
3. represent those units as embeddings
4. search for relevant context when a user asks a question
5. constrain generation to the retrieved context
6. show where the answer came from
7. retain indexed knowledge across restarts

The project also needed to remain low-cost and practical for local development.

## Constraints

The implementation was shaped by several deliberate constraints:

- local-first AI inference
- no paid API requirement
- Windows development environment
- Python 3.14 locally during early development
- no PyTorch dependency
- no LangChain in the first architecture
- transparent, explainable RAG pipeline
- frontend and backend kept as separate application layers

## Solution

The final v1.0 architecture uses:

- **Next.js + TypeScript + Tailwind CSS** for the frontend
- **FastAPI + Python** for the backend
- **PyPDF** for PDF extraction
- custom overlapping chunking
- **Ollama `nomic-embed-text`** for local embeddings
- **FAISS** for semantic vector search
- **Ollama `llama3.2`** for local answer generation
- **SSE** for streaming responses
- filesystem persistence for the FAISS index and chunk metadata
- GitHub Actions for automated quality checks

## Development Journey

### Phase 1 — Foundation

The project was split into `frontend` and `backend` from the beginning. This kept UI concerns separate from ingestion, retrieval, and model orchestration.

### Phase 2 — Document ingestion

Support was added for PDF, TXT, and Markdown. PDF text extraction is page-aware so later source cards can display page numbers.

### Phase 3 — Custom chunking

A custom chunker was implemented with configurable chunk size and overlap. Building this directly made the effect of normalization, paragraph boundaries, overlap, and page metadata explicit.

### Phase 4 — Local embeddings

The initial direction considered common embedding libraries, but Windows native-library issues made PyTorch-based tooling undesirable for this environment.

The architecture was changed to use Ollama embeddings directly. This removed the PyTorch requirement and kept inference local.

### Phase 5 — FAISS retrieval

FAISS was introduced using a normalized `IndexFlatIP`. Query and stored vectors are normalized so inner-product search functions as cosine similarity.

### Phase 6 — End-to-end indexing

Upload, loading, chunking, embedding, and indexing were combined into one service pipeline.

### Phase 7 — Retrieval

Semantic search was exposed as a backend service and API endpoint, returning chunk text and relevance metadata.

### Phase 8 — RAG generation

Retrieved chunks were assembled into model context and passed to a local Ollama LLM with explicit grounding instructions.

### Phase 9 — Streaming and sources

A streaming SSE endpoint was added. Source metadata is emitted before answer tokens, allowing the frontend to render attribution alongside a progressively generated response.

### Phase 10 — Persistence

A major behavior issue appeared during development: FAISS was initially in memory, so backend reloads erased the knowledge base.

Persistence was added using:

- `index.faiss` for vectors
- `chunks.json` for application metadata

The vector store validates both files on startup before accepting them.

### Phase 11 — Full-stack frontend

The default Next.js starter interface was replaced by a responsive AI dashboard with:

- drag-and-drop upload
- streaming chat
- source cards
- persisted document list
- local-AI status presentation

### Phase 12 — Document management

The backend gained document listing, statistics, and deletion. The frontend was upgraded from a session-only upload list to a real persisted knowledge-base view.

### Phase 13 — Release hardening

The final pre-release work added:

- centralized environment configuration
- upload-size and empty-file validation
- richer Ollama health reporting
- automated unit tests
- GitHub Actions CI
- frontend lint and production-build checks

## Notable Engineering Problems

### Windows temporary-file locking

Using a temporary file with automatic deletion caused permission problems when PyPDF attempted to reopen the file on Windows.

The solution was to create a named temporary file with `delete=False`, close it, process it, and delete it explicitly afterward.

### PyTorch compatibility

The development machine encountered Windows code-integrity/native-DLL problems with PyTorch-based tooling.

Rather than fighting the environment, the project architecture was simplified: embeddings moved to Ollama and the application no longer depends on PyTorch or `sentence-transformers`.

### Lost vector state after reload

In-memory FAISS worked during one server process but failed as soon as development reloads restarted the backend.

That failure directly motivated the persistence layer and turned the project from a demo into a usable local application.

### Temporary filenames leaking into sources

The ingestion pipeline originally used the temporary processing filename as document metadata.

The indexing service was updated to preserve the original upload filename so source cards show meaningful document names.

### Deleting documents from a flat index

The application needs document-level operations, while the simple flat FAISS index stores vectors by position.

For v1.0, deletion is implemented by reconstructing retained vectors and rebuilding the flat index. This is simple, deterministic, and appropriate for the intended dataset size.

## Why This Project Is Portfolio-Relevant

The project demonstrates more than calling an LLM API. It includes:

- full-stack TypeScript/Python integration
- document parsing
- custom text processing
- embedding generation
- vector mathematics and semantic search
- RAG context construction
- prompt constraints
- persistent state
- streaming protocols
- frontend state management
- API design
- error handling
- automated testing
- CI workflow design
- iterative architectural decisions based on real debugging constraints

## What I Learned

The most important lesson was that a working RAG application is a system, not a single model call.

Retrieval quality depends on ingestion, chunking, embeddings, metadata, indexing, and query flow. Product quality also depends on persistence, meaningful sources, error states, document lifecycle management, and a frontend that makes the retrieval process understandable to users.

The project also reinforced the value of adapting architecture to real platform constraints instead of adding dependencies by default.

## Result

The v1.0 result is a fully local document assistant that can:

- index supported documents
- persist them across restarts
- perform semantic retrieval
- answer questions grounded in retrieved context
- stream answers
- show source metadata
- manage the indexed knowledge base
- validate deterministic logic through automated tests
- pass backend and frontend CI checks

It is ready to be presented as a portfolio case study and used as a foundation for future AI application work.
