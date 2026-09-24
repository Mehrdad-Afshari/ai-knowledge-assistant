"use client";

import { useEffect, useState } from "react";

import {
  deleteDocument,
  getDocuments,
  getKnowledgeBaseStats,
} from "@/lib/api";
import type {
  IndexedDocument,
  KnowledgeBaseStats,
} from "@/lib/types";

type DocumentLibraryProps = {
  refreshKey: number;
};

export function DocumentLibrary({ refreshKey }: DocumentLibraryProps) {
  const [documents, setDocuments] = useState<IndexedDocument[]>([]);
  const [stats, setStats] = useState<KnowledgeBaseStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isCancelled = false;

    async function loadLibrary() {
      setIsLoading(true);
      setError(null);

      try {
        const [documentResponse, statsResponse] = await Promise.all([
          getDocuments(),
          getKnowledgeBaseStats(),
        ]);

        if (!isCancelled) {
          setDocuments(documentResponse.documents);
          setStats(statsResponse);
        }
      } catch (loadError) {
        if (!isCancelled) {
          setError(
            loadError instanceof Error
              ? loadError.message
              : "Failed to load knowledge base.",
          );
        }
      } finally {
        if (!isCancelled) {
          setIsLoading(false);
        }
      }
    }

    void loadLibrary();

    return () => {
      isCancelled = true;
    };
  }, [refreshKey]);

  async function handleDelete(documentId: string) {
    setDeletingId(documentId);
    setError(null);

    try {
      await deleteDocument(documentId);

      const [documentResponse, statsResponse] = await Promise.all([
        getDocuments(),
        getKnowledgeBaseStats(),
      ]);

      setDocuments(documentResponse.documents);
      setStats(statsResponse);
    } catch (deleteError) {
      setError(
        deleteError instanceof Error
          ? deleteError.message
          : "Document deletion failed.",
      );
    } finally {
      setDeletingId(null);
    }
  }

  return (
    <section className="panel-card">
      <div className="panel-heading">
        <div>
          <p className="eyebrow">Knowledge base</p>
          <h2>Indexed documents</h2>
        </div>
        <span className="status-pill">
          {stats ? `${stats.document_count} docs · ${stats.indexed_vectors} vectors` : "—"}
        </span>
      </div>

      {stats ? (
        <div className="mb-4 flex flex-wrap gap-2 text-xs text-slate-400">
          <span className="rounded-full border border-white/10 px-2.5 py-1">
            {stats.embedding_dimension}D embeddings
          </span>
          <span className="rounded-full border border-white/10 px-2.5 py-1">
            {stats.persisted ? "Persisted" : "In memory"}
          </span>
        </div>
      ) : null}

      {isLoading ? (
        <p className="muted-copy">Loading indexed documents...</p>
      ) : documents.length > 0 ? (
        <div className="document-list">
          {documents.map((document) => (
            <article className="document-item" key={document.document_id}>
              <div className="document-icon">{document.file_type.toUpperCase()}</div>

              <div className="min-w-0 flex-1">
                <strong className="block overflow-hidden text-ellipsis whitespace-nowrap">
                  {document.filename}
                </strong>
                <span>
                  {document.chunk_count} chunks · {document.page_count || "Text"}{" "}
                  {document.page_count ? "pages" : "document"}
                </span>
              </div>

              <button
                className="shrink-0 rounded-lg border border-red-300/20 bg-red-400/5 px-2.5 py-1.5 text-xs font-semibold text-red-300 transition hover:border-red-300/40 hover:bg-red-400/10 disabled:cursor-wait disabled:opacity-50"
                type="button"
                disabled={deletingId === document.document_id}
                onClick={() => void handleDelete(document.document_id)}
                aria-label={`Delete ${document.filename}`}
              >
                {deletingId === document.document_id ? "…" : "Delete"}
              </button>
            </article>
          ))}
        </div>
      ) : (
        <p className="muted-copy">
          No indexed documents yet. Upload a PDF, TXT, or Markdown file to build your knowledge base.
        </p>
      )}

      {error ? <p className="error-message">{error}</p> : null}
    </section>
  );
}
