import type { Source } from "@/lib/types";

type SourceListProps = {
  sources: Source[];
};

export function SourceList({ sources }: SourceListProps) {
  if (sources.length === 0) {
    return null;
  }

  return (
    <div className="source-section">
      <div className="source-section-heading">
        <span>Sources</span>
        <span>{sources.length}</span>
      </div>

      <div className="source-grid">
        {sources.map((source, index) => (
          <article className="source-card" key={source.chunk_id}>
            <div className="source-rank">{index + 1}</div>
            <div className="source-content">
              <strong>{source.filename}</strong>
              <span>
                {source.page_number ? `Page ${source.page_number}` : "Text document"}
              </span>
            </div>
            <span className="source-score">
              {Math.round(source.relevance_score * 100)}%
            </span>
          </article>
        ))}
      </div>
    </div>
  );
}
