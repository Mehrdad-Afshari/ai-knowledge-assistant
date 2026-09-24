import type { StreamEvent, UploadResponse } from "./types";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

export async function uploadDocument(file: File): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE_URL}/documents/upload`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const payload = await response.json().catch(() => null);
    throw new Error(payload?.detail ?? "Document upload failed.");
  }

  return response.json();
}

export async function streamChat(
  query: string,
  topK: number,
  onEvent: (event: StreamEvent) => void,
): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/documents/chat/stream`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      query,
      top_k: topK,
    }),
  });

  if (!response.ok) {
    const payload = await response.json().catch(() => null);
    throw new Error(payload?.detail ?? "Chat request failed.");
  }

  if (!response.body) {
    throw new Error("Streaming response is unavailable.");
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { value, done } = await reader.read();

    if (done) {
      break;
    }

    buffer += decoder.decode(value, { stream: true });

    const events = buffer.split("\n\n");
    buffer = events.pop() ?? "";

    for (const rawEvent of events) {
      const dataLine = rawEvent
        .split("\n")
        .find((line) => line.startsWith("data:"));

      if (!dataLine) {
        continue;
      }

      const payload = dataLine.slice(5).trim();

      if (!payload) {
        continue;
      }

      onEvent(JSON.parse(payload) as StreamEvent);
    }
  }
}
