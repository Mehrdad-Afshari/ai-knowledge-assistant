# Roadmap

## v1.0 — Portfolio Release

Status: **Complete**

- PDF, TXT, and Markdown ingestion
- custom chunking with overlap
- local Ollama embeddings
- FAISS semantic retrieval
- local RAG generation
- streaming answers with SSE
- source metadata
- persistent FAISS + chunk metadata
- persisted document library
- document deletion
- health diagnostics
- centralized environment configuration
- automated backend tests
- frontend lint and production build validation
- GitHub Actions CI
- portfolio-ready documentation

## Near-Term Improvements

### Better retrieval quality

- experiment with chunk-size/overlap evaluation
- add optional score thresholding
- add query/result diagnostics
- evaluate reranking for difficult queries

### Better document support

- OCR pipeline for scanned PDFs
- DOCX ingestion
- richer Markdown structure awareness
- duplicate-document detection

### Better UX

- chat history within a session
- source text previews
- clearer upload progress for larger documents
- explicit backend/Ollama status in the UI
- confirmation flow before destructive deletion

## Architecture Evolution

### Provider abstraction

Introduce interfaces that preserve the local-first default while allowing optional providers later:

```text
EmbeddingProvider
├── Ollama
└── Remote provider (optional)

LLMProvider
├── Ollama
└── Remote provider (optional)
```

Any remote provider should remain optional so the project can still run without paid API access.

### Storage evolution

For larger datasets or multi-user use:

- separate durable document metadata store
- object storage for original files
- approximate-nearest-neighbor vector index or managed vector database
- background ingestion jobs

### Production deployment

The Next.js frontend can be hosted independently, but the current Ollama backend requires a machine capable of running the local model runtime. A future public demo architecture may therefore separate frontend hosting from an AI-capable backend host.

## Advanced Features

Potential future work:

- authentication and user accounts
- multi-tenant knowledge bases
- per-document filtering
- conversational memory
- citations inside generated answer text
- structured extraction mode
- evaluation dataset and retrieval metrics
- observability/tracing
- Docker-based local development
- end-to-end integration tests with a model runtime

## Portfolio Integration

The project will be presented on Mehrdad Afshari's personal portfolio as a case study covering:

- the problem
- architecture
- technical decisions
- development challenges
- implementation highlights
- lessons learned
- GitHub source code

The portfolio website itself remains a separate codebase so this project can be evaluated independently as a complete AI application.
