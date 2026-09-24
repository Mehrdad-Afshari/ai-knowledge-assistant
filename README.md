# AI Knowledge Assistant

A full-stack Retrieval-Augmented Generation (RAG) application that turns local documents into a searchable AI knowledge base.

Built as a portfolio and learning project by **Mehrdad Afshari**, the application combines a Next.js frontend with a FastAPI backend, local Ollama models, custom chunking, semantic retrieval with FAISS, persistent vector storage, streaming answers, and visible source metadata.

> **Privacy-first by design:** document embeddings and answer generation run locally through Ollama. No paid AI API is required.

## Highlights

- Upload and index **PDF, TXT, and Markdown** documents
- Extract PDF text with **PyPDF**
- Split documents with a custom overlapping chunking pipeline
- Generate local embeddings with **Ollama + `nomic-embed-text`**
- Search semantically with **FAISS cosine similarity**
- Generate grounded answers with **Ollama + `llama3.2`**
- Stream answers to the browser using **Server-Sent Events (SSE)**
- Display source filename, page number, and relevance score
- Persist FAISS index and chunk metadata across backend restarts
- List and delete indexed documents from the frontend
- Validate backend behavior and frontend builds with **GitHub Actions CI**
- Keep the AI stack fully local and free for development

## Tech Stack

### Frontend

- Next.js 16
- React 19
- TypeScript
- Tailwind CSS 4

### Backend

- FastAPI
- Python
- PyPDF
- NumPy
- FAISS
- Ollama Python client

### Local AI

- Embeddings: `nomic-embed-text` — 768 dimensions
- LLM: `llama3.2`
- Runtime: Ollama

### Quality & Workflow

- Git + GitHub
- Pull-request based development
- GitHub Actions CI
- Python `unittest`
- ESLint
- Next.js production build validation

## Architecture

```text
Browser / Next.js
       |
       | REST + SSE
       v
FastAPI API
       |
       +--> Document Loader --> Custom Chunker --> Ollama Embeddings
       |                                         |
       |                                         v
       |                                  Persistent FAISS
       |                                         |
       +--> Retrieval Service <------------------+
       |        |
       |        v
       |   Relevant Chunks
       |        |
       v        v
    RAG Service --> Ollama LLM --> Streaming Answer + Sources
```

A more detailed architecture description is available in [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

## Project Structure

```text
ai-knowledge-assistant/
├── .github/
│   └── workflows/
│       └── ci.yml
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   ├── rag/
│   │   ├── services/
│   │   └── main.py
│   ├── data/
│   │   └── index/
│   ├── tests/
│   ├── .env.example
│   └── requirements.txt
├── frontend/
│   ├── app/
│   ├── components/
│   ├── lib/
│   └── package.json
├── docs/
│   ├── ARCHITECTURE.md
│   ├── CASE_STUDY.md
│   └── ROADMAP.md
├── CHANGELOG.md
└── README.md
```

## Prerequisites

Install:

- **Ollama**
- **Python** — CI currently validates with Python 3.12
- **Node.js 22**
- **npm**

Pull the required Ollama models:

```bash
ollama pull nomic-embed-text
ollama pull llama3.2
```

Make sure Ollama is running before starting the backend.

## Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/Mehrdad-Afshari/ai-knowledge-assistant.git
cd ai-knowledge-assistant
```

### 2. Backend

On Windows PowerShell:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload
```

Backend API:

```text
http://127.0.0.1:8000
```

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

Health endpoint:

```text
http://127.0.0.1:8000/health
```

### 3. Frontend

Open a second terminal:

```powershell
cd frontend
npm install
Copy-Item .env.example .env.local
npm run dev
```

Frontend:

```text
http://localhost:3000
```

## Environment Variables

Backend `.env`:

```env
OLLAMA_HOST=http://localhost:11434
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
OLLAMA_LLM_MODEL=llama3.2
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
MAX_UPLOAD_MB=20
```

Frontend `.env.local`:

```env
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000
```

## Main API Endpoints

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Application and Ollama health status |
| `POST` | `/documents/upload` | Upload, chunk, embed, and index a document |
| `GET` | `/documents` | List indexed documents |
| `DELETE` | `/documents/{document_id}` | Remove one document and its vectors |
| `GET` | `/documents/stats` | Knowledge-base statistics |
| `POST` | `/documents/search` | Semantic search over indexed chunks |
| `POST` | `/documents/chat` | Non-streaming RAG answer |
| `POST` | `/documents/chat/stream` | SSE streaming RAG answer and sources |

## Testing

Backend unit tests:

```bash
cd backend
python -m unittest discover -s tests -v
```

Frontend checks:

```bash
cd frontend
npm run lint
npm run build
```

GitHub Actions runs the same backend tests and frontend lint/build checks for pull requests and pushes to `main`.

## Key Engineering Decisions

### Direct SDKs instead of LangChain

The first version intentionally avoids LangChain. The ingestion, chunking, retrieval, context construction, persistence, and generation pipeline are implemented directly so the architecture stays transparent and the project demonstrates understanding of the underlying RAG workflow rather than framework-only usage.

### FAISS persistence

FAISS vectors and chunk metadata are written to disk and restored when the backend starts. This keeps the local knowledge base available after restarts without introducing an external database.

### Local AI first

Ollama was chosen so the project can be developed and demonstrated without paid API credits, while keeping documents and model inference local.

### Streaming with SSE

The backend exposes a streaming endpoint that sends source metadata first and then incremental answer tokens. The Next.js frontend consumes the event stream and updates the UI progressively.

## Challenges Solved

- Avoided PyTorch and `sentence-transformers` after Windows native-library compatibility problems by using Ollama embeddings directly
- Fixed Windows temporary-file locking behavior for PDF processing
- Added persistent FAISS storage after discovering that an in-memory index disappeared on backend reload
- Preserved original uploaded filenames instead of temporary filenames
- Added document-level deletion by rebuilding the flat FAISS index from retained vectors
- Added CI that tests backend logic without requiring Ollama to be installed in GitHub Actions

See [`docs/CASE_STUDY.md`](docs/CASE_STUDY.md) for the full project story.

## Current Limitations

This is a portfolio-focused local RAG application, not a multi-tenant production SaaS. Current limitations include:

- No OCR for scanned/image-only PDFs
- No authentication or user accounts
- Local filesystem persistence rather than a managed database
- Local Ollama runtime required for inference
- Flat FAISS index optimized for simplicity rather than very large corpora
- Document deletion rebuilds the retained flat index

These constraints are intentional for v1.0 and are documented in the future roadmap.

## Documentation

- [`Architecture`](docs/ARCHITECTURE.md)
- [`Case Study`](docs/CASE_STUDY.md)
- [`Roadmap`](docs/ROADMAP.md)
- [`Changelog`](CHANGELOG.md)

## Author

**Mehrdad Afshari**  
MSc Computer Science student at the University of Rostock, Germany  
Focus: AI and Software Development

GitHub: [Mehrdad-Afshari](https://github.com/Mehrdad-Afshari)

## Status

**v1.0 — Portfolio Release**

The project is feature-complete for its first portfolio release and ready to be presented as a full-stack AI/RAG case study.
