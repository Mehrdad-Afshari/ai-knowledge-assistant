# Changelog

All notable changes to this project are documented here.

## [1.0.0] - 2026-09-24

### Added

- portfolio-ready root README
- architecture documentation
- portfolio case study
- project roadmap
- centralized environment configuration
- upload-size and empty-file validation
- richer application/Ollama health diagnostics
- automated backend unit tests
- GitHub Actions CI for backend tests and frontend lint/build

### Included in the v1.0 feature set

- PDF, TXT, and Markdown ingestion
- custom overlapping text chunking
- Ollama `nomic-embed-text` embeddings
- FAISS semantic retrieval
- Ollama `llama3.2` grounded answer generation
- Server-Sent Events streaming
- source cards with filename, page, and relevance
- persistent FAISS index and chunk metadata
- persisted document listing and deletion
- responsive Next.js frontend

## [0.9.0]

### Added

- release hardening
- centralized settings
- configurable upload limits
- improved health endpoint
- unit tests
- CI workflow

## [0.8.0]

### Added

- persistent document library
- document listing API
- document deletion API
- knowledge-base statistics
- frontend document management

## [0.7.0]

### Added

- production-style Next.js application UI
- drag-and-drop upload
- full-stack frontend/backend integration
- streaming chat interface
- source cards
- CORS configuration
- original upload filename preservation

## [0.6.0]

### Added

- persistent FAISS index
- persisted chunk metadata
- automatic index restoration after backend restart

## [0.5.0]

### Added

- local RAG generation with Ollama
- SSE streaming responses
- source metadata

## Earlier development

The initial phases established document loading, custom chunking, Ollama embeddings, FAISS indexing, semantic retrieval, and the end-to-end upload-to-index pipeline.
