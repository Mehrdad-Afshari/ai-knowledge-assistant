"use client";

import { FormEvent, useState } from "react";

import { streamChat } from "@/lib/api";
import type { Source } from "@/lib/types";
import { SourceList } from "./source-list";

export function ChatPanel() {
  const [query, setQuery] = useState("");
  const [answer, setAnswer] = useState("");
  const [sources, setSources] = useState<Source[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const trimmedQuery = query.trim();

    if (!trimmedQuery || isStreaming) {
      return;
    }

    setAnswer("");
    setSources([]);
    setError(null);
    setIsStreaming(true);

    try {
      await streamChat(trimmedQuery, 4, (streamEvent) => {
        if (streamEvent.type === "sources") {
          setSources(streamEvent.sources);
        }

        if (streamEvent.type === "token") {
          setAnswer((current) => current + streamEvent.content);
        }
      });
    } catch (chatError) {
      setError(
        chatError instanceof Error
          ? chatError.message
          : "Unable to generate an answer.",
      );
    } finally {
      setIsStreaming(false);
    }
  }

  return (
    <section className="chat-card">
      <div className="panel-heading">
        <div>
          <p className="eyebrow">RAG assistant</p>
          <h2>Ask your documents</h2>
        </div>
        <span className="status-pill status-live">
          <span className="status-dot" /> Local AI
        </span>
      </div>

      <div className="chat-output" aria-live="polite">
        {answer ? (
          <div className="answer-block">
            <div className="assistant-avatar">AI</div>
            <div>
              <p className="message-label">Assistant</p>
              <div className="answer-text">{answer}</div>
            </div>
          </div>
        ) : (
          <div className="empty-state">
            <div className="empty-icon">⌁</div>
            <h3>Ready when your documents are.</h3>
            <p>
              Upload knowledge on the left, then ask a precise question. Answers are
              grounded in retrieved document chunks.
            </p>
          </div>
        )}

        {isStreaming && !answer ? (
          <div className="thinking-row">
            <span /> <span /> <span />
          </div>
        ) : null}

        {error ? <p className="error-message">{error}</p> : null}

        <SourceList sources={sources} />
      </div>

      <form className="chat-form" onSubmit={handleSubmit}>
        <textarea
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === "Enter" && !event.shiftKey) {
              event.preventDefault();
              event.currentTarget.form?.requestSubmit();
            }
          }}
          placeholder="Ask a question about your indexed documents..."
          rows={3}
          disabled={isStreaming}
        />
        <div className="chat-form-footer">
          <span>Enter to send · Shift + Enter for new line</span>
          <button
            className="primary-button"
            type="submit"
            disabled={!query.trim() || isStreaming}
          >
            {isStreaming ? "Generating..." : "Ask"}
          </button>
        </div>
      </form>
    </section>
  );
}
