"use client";

import { useState } from "react";

import { ChatPanel } from "@/components/chat-panel";
import { DocumentLibrary } from "@/components/document-library";
import { UploadPanel } from "@/components/upload-panel";

export default function Home() {
  const [libraryRefreshKey, setLibraryRefreshKey] = useState(0);

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
          Upload documents, manage a persistent vector library, retrieve semantically
          relevant context, and stream grounded answers with visible source metadata —
          all using a local, API-free AI stack.
        </p>
      </section>

      <div className="workspace-grid">
        <aside className="sidebar-stack">
          <UploadPanel
            onUploaded={() =>
              setLibraryRefreshKey((current) => current + 1)
            }
          />

          <DocumentLibrary refreshKey={libraryRefreshKey} />

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
        <span>RAG · semantic retrieval · persistence · document management · streaming</span>
        <span>v1.0 portfolio release</span>
      </footer>
    </main>
  );
}
