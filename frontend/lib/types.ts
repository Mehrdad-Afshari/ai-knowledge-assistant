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

export type IndexedDocument = {
  document_id: string;
  filename: string;
  file_type: string;
  chunk_count: number;
  page_count: number;
};

export type DocumentListResponse = {
  documents: IndexedDocument[];
  document_count: number;
  indexed_vectors: number;
};

export type DeleteDocumentResponse = {
  document_id: string;
  removed_chunks: number;
  indexed_vectors: number;
  status: string;
};

export type KnowledgeBaseStats = {
  document_count: number;
  indexed_vectors: number;
  embedding_dimension: number;
  persisted: boolean;
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
