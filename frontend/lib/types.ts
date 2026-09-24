export type UploadResponse = {
  document_id: string;
  filename: string;
  file_type: string;
  content_length: number;
  page_count: number;
  chunk_count: number;
  indexed_vectors: number;
  status: string;
};

export type Source = {
  chunk_id: string;
  document_id: string;
  filename: string;
  page_number: number | null;
  relevance_score: number;
};

export type StreamEvent =
  | {
      type: "sources";
      sources: Source[];
    }
  | {
      type: "token";
      content: string;
    }
  | {
      type: "done";
    };
