"use client";

import { useState } from "react";

import { ChatPanel } from "@/components/chat-panel";
import { UploadPanel } from "@/components/upload-panel";
import type { UploadResponse } from "@/lib/types";

export default function Home() {
  const [uploads, setUploads] = useState<UploadResponse[]>([]);

  return (
    <main className="app-shell">
      <div className="app-backdrop" />

      <header className="topbar">
        <div>
          <p className="brand-kicker">Mehrdad Afshari · AI Project</p>
          <h1>AI Knowledge Assistant</h1>
        </div>

        <div className="topbar-meta">
          <span>Ollama</span>
          <span>FAISS</span>
          <span>FastAPI</span>
          <span>Next.js</span>
        </div>
      </header>

      <section className="hero-copy">
        <p className="eyebrow">Local retrieval-augmented generation</p>
        <h2>Turn your documents into a searchable AI knowledge base.</h2>
        <p>
          Upload documents, retrieve semantically relevant context, and stream grounded
          answers with visible source metadata — all using a local, API-free AI stack.
        </p>
      </section>

      <div className="workspace-grid">
        <aside className="sidebar-stack">
          <UploadPanel
            onUploaded={(result) =>
              setUploads((current) => [result, ...current].slice(0, 5))
            }
          />

          <section className="panel-card">
            <div className="panel-heading">
              <div>
                <p className="eyebrow">Session</p>
                <h2>Indexed documents</h2>
              </div>
              <span className="status-pill">{uploads.length}</span>
            </div>

            {uploads.length > 0 ? (
              <div className="document-list">
                {uploads.map((upload) => (
                  <article className="document-item" key={upload.document_id}>
                    <div className="document-icon">{upload.file_type.toUpperCase()}</div>
                    <div>
                      <strong>{upload.filename}</strong>
                      <span>
                        {upload.chunk_count} chunks · {upload.page_count || "Text"}{" "}
                        {upload.page_count ? "pages" : "document"}
                      </span>
                    </div>
                  </article>
                ))}
              </div>
            ) : (
              <p className="muted-copy">
                Uploads from this browser session will appear here. Persisted FAISS data
                remains available after backend restarts.
              </p>
            )}
          </section>

          <section className="stack-note">
            <span className="status-dot" />
            <div>
              <strong>Private by design</strong>
              <p>Embeddings and answer generation run locally through Ollama.</p>
            </div>
          </section>
        </aside>

        <ChatPanel />
      </div>

      <footer className="app-footer">
        <span>RAG · semantic retrieval · streaming · source grounding</span>
        <span>v0.7 frontend</span>
      </footer>
    </main>
  );
}
