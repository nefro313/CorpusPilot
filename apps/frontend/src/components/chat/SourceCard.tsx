import type { SourceChunk } from "../../types";
import { prettyDomain } from "./domain";

export function SourceCard({ source }: { source: SourceChunk }) {
  return (
    <div className="source-card">
      <div className="source-top">
        <span className="citation-chip">{source.citation_id}</span>
        <span className="source-file">{source.document_filename}</span>
      </div>
      <div className="source-meta">
        <span>{prettyDomain(source.domain)}</span>
        {source.page_number ? <span>p. {source.page_number}</span> : null}
        {source.section_title ? <span>{source.section_title}</span> : null}
      </div>
      <p>{source.content}</p>
    </div>
  );
}
