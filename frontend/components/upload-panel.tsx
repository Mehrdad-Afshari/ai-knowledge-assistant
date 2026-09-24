"use client";

import { useRef, useState } from "react";

import { uploadDocument } from "@/lib/api";
import type { UploadResponse } from "@/lib/types";

type UploadPanelProps = {
  onUploaded: (result: UploadResponse) => void;
};

export function UploadPanel({ onUploaded }: UploadPanelProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleFile(file: File | undefined) {
    if (!file) {
      return;
    }

    setIsUploading(true);
    setError(null);

    try {
      const result = await uploadDocument(file);
      onUploaded(result);
    } catch (uploadError) {
      setError(
        uploadError instanceof Error
          ? uploadError.message
          : "Document upload failed.",
      );
    } finally {
      setIsUploading(false);
      if (inputRef.current) {
        inputRef.current.value = "";
      }
    }
  }

  return (
    <section className="panel-card">
      <div className="panel-heading">
        <div>
          <p className="eyebrow">Knowledge base</p>
          <h2>Upload a document</h2>
        </div>
        <span className="status-pill">PDF · TXT · MD</span>
      </div>

      <button
        className="upload-zone"
        type="button"
        disabled={isUploading}
        onClick={() => inputRef.current?.click()}
        onDragOver={(event) => event.preventDefault()}
        onDrop={(event) => {
          event.preventDefault();
          void handleFile(event.dataTransfer.files[0]);
        }}
      >
        <span className="upload-icon" aria-hidden="true">↑</span>
        <span className="upload-title">
          {isUploading ? "Indexing document..." : "Drop a file here"}
        </span>
        <span className="upload-copy">
          or click to browse. Documents are processed locally.
        </span>
      </button>

      <input
        ref={inputRef}
        className="sr-only"
        type="file"
        accept=".pdf,.txt,.md,application/pdf,text/plain,text/markdown"
        onChange={(event) => void handleFile(event.target.files?.[0])}
      />

      {error ? <p className="error-message">{error}</p> : null}
    </section>
  );
}
