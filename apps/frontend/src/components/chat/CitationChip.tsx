import type { SourceChunk } from "../../types";
import { prettyDomain } from "./domain";

export function CitationChip({ id, source }: { id: string; source?: SourceChunk }) {
  return (
    <span className={`citation-inline${source ? "" : " missing"}`} tabIndex={0}>
      <span className="citation-inline-chip">{id}</span>
      {source ? (
        <span className="citation-popover" role="tooltip">
          <span className="citation-popover-top">
            <span className="citation-popover-id">{id}</span>
            <span className="citation-popover-file" title={source.document_filename}>
              {source.document_filename}
            </span>
          </span>
          <span className="citation-popover-meta">
            <span>{prettyDomain(source.domain)}</span>
            {source.page_number ? <span>p. {source.page_number}</span> : null}
            {source.section_title ? <span>{source.section_title}</span> : null}
          </span>
          <span className="citation-popover-body">{source.content}</span>
          {source.rerank_score != null ? (
            <span className="citation-popover-score">
              rerank · {source.rerank_score.toFixed(3)}
            </span>
          ) : null}
        </span>
      ) : null}
    </span>
  );
}
