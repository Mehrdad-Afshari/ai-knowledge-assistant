# Portfolio Integration Copy

This file contains concise copy that can be reused when the AI Knowledge Assistant is added to Mehrdad Afshari's portfolio website.

## Project Title

AI Knowledge Assistant

## Short Label

Local RAG · Full-Stack AI Application

## One-Line Summary

A privacy-first document assistant that uses local embeddings, FAISS retrieval, and an Ollama LLM to answer questions from uploaded documents with streaming responses and visible sources.

## Portfolio Card Description

Built a full-stack Retrieval-Augmented Generation application with Next.js, TypeScript, FastAPI, Ollama, and FAISS. The system supports PDF/TXT/Markdown ingestion, custom chunking, local embeddings, persistent semantic search, streamed grounded answers, source attribution, document management, automated tests, and GitHub Actions CI.

## Key Highlights

- Built the RAG pipeline directly without LangChain to keep ingestion, chunking, retrieval, context construction, and generation transparent.
- Implemented local `nomic-embed-text` embeddings and `llama3.2` generation through Ollama, requiring no paid AI API for development.
- Added persistent FAISS storage so indexed knowledge survives backend restarts.
- Built a responsive Next.js interface for upload, knowledge-base management, streaming chat, and source cards.
- Added automated backend tests and frontend lint/build validation through GitHub Actions.
- Adapted the architecture around real Windows/PyTorch compatibility constraints rather than adding unnecessary dependencies.

## Tech Tags

`Next.js` · `React` · `TypeScript` · `Tailwind CSS` · `FastAPI` · `Python` · `RAG` · `Ollama` · `FAISS` · `PyPDF` · `SSE` · `GitHub Actions`

## Problem / Solution Copy

### Problem

LLMs cannot automatically answer from private or newly uploaded documents, and many RAG demos depend on paid APIs or hide the retrieval pipeline behind high-level frameworks.

### Solution

I built a local-first RAG system that parses documents, creates overlapping chunks, generates local embeddings, retrieves semantically relevant context with FAISS, and streams grounded answers from a local Ollama model while showing source metadata.

## Engineering Decisions

### Why direct SDKs?

I intentionally avoided LangChain in v1.0 so I could implement and understand the underlying RAG flow directly: chunking, embeddings, vector normalization, retrieval, context assembly, persistence, and streaming.

### Why Ollama?

Ollama keeps the default application local and avoids a paid API dependency. It also solved compatibility problems I encountered with PyTorch-based embedding tooling on Windows.

### Why FAISS?

FAISS provides a lightweight and efficient semantic search layer for a local portfolio-scale knowledge base without requiring an external vector database.

## Challenges Worth Mentioning in an Interview

- Windows temporary-file locking during PDF ingestion
- PyTorch/native-DLL compatibility and the decision to switch to Ollama embeddings
- persistence after discovering development reloads erased the in-memory FAISS index
- preserving original filenames through temporary-file processing
- rebuilding a flat FAISS index for document-level deletion
- designing CI so deterministic backend logic can be tested without running Ollama in GitHub Actions

## Suggested CV Bullet

**AI Knowledge Assistant — Full-Stack RAG Project**  
Developed a local-first RAG application using Next.js, TypeScript, FastAPI, Ollama, and FAISS; implemented document ingestion, custom chunking, semantic retrieval, persistent vector storage, SSE streaming, source attribution, document management, automated tests, and GitHub Actions CI.

## Suggested Interview Summary

I built the project to understand RAG beyond framework abstractions. The frontend is Next.js and the backend is FastAPI. Documents are parsed and chunked by my own pipeline, embedded locally through Ollama, normalized and stored in FAISS, then retrieved for a grounded local LLM prompt. I added persistence, streaming, document lifecycle management, health diagnostics, tests, and CI as the project evolved from a prototype into a usable portfolio application.
