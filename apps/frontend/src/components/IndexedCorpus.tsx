import { useState } from "react";
import { Book, Chart, Flask, Pulse, Scale, Trash } from "./icons";
import type { CorpusDomain, DocumentItem } from "../types";

const DOMAIN_ICONS = {
  technical_document: Book,
  research_paper: Flask,
  legal_contract: Scale,
  healthcare_document: Pulse,
  financial_document: Chart,
} as const;

interface Props {
  docs: DocumentItem[];
  selectedDomain?: CorpusDomain;
  onDelete?: (doc: DocumentItem) => Promise<void> | void;
}

export default function IndexedCorpus({ docs, selectedDomain, onDelete }: Props) {
  const [pendingId, setPendingId] = useState<string | null>(null);
  // The viewer filter is independent of selectedDomain so users can browse a
  // different domain's docs without losing the active chat scope. Default to
  // whatever the chat is scoped to, with `null` meaning "show all".
  const [filterDomain, setFilterDomain] = useState<CorpusDomain | null>(
    selectedDomain ?? null,
  );

  const handleDelete = async (doc: DocumentItem) => {
    if (!onDelete || pendingId) return;
    const confirmed = window.confirm(
      `Delete "${doc.title}" from the corpus? This removes its ${doc.chunk_count} chunks and vector embeddings.`,
    );
    if (!confirmed) return;
    try {
      setPendingId(doc.id);
      await onDelete(doc);
    } finally {
      setPendingId(null);
    }
  };

  const togglePill = (domain: CorpusDomain) => {
    setFilterDomain((current) => (current === domain ? null : domain));
  };

  const visibleDocs = filterDomain
    ? docs.filter((doc) => doc.domain === filterDomain)
    : docs;
  const tally = countByDomain(docs);
  const totalDocs = docs.length;
  const headline =
    visibleDocs.length === 0
      ? filterDomain
        ? `No ${prettyDomain(filterDomain)} documents yet`
        : "No documents yet"
      : `${visibleDocs.length} ${filterDomain ? prettyDomain(filterDomain) + " " : ""}` +
        `document${visibleDocs.length === 1 ? "" : "s"} ready for retrieval`;
  const emptyMessage = filterDomain
    ? `No documents indexed for the ${prettyDomain(filterDomain)} domain yet — upload one on the left or pick another domain.`
    : "Upload a document on the left to start building your corpus.";

  return (
    <section className="indexed-panel">
      <div className="indexed-head">
        <div>
          <span className="panel-kicker">Indexed Corpus</span>
          <h2>{headline}</h2>
          {filterDomain ? (
            <p className="indexed-sub">
              Filtered by <strong>{prettyDomain(filterDomain)}</strong> · click
              the pill again or “All” to clear.
            </p>
          ) : (
            <p className="indexed-sub">
              Click a domain pill to see only documents in that corpus.
            </p>
          )}
        </div>
        <div className="indexed-domain-tally" role="tablist" aria-label="Filter by domain">
          <button
            type="button"
            role="tab"
            aria-selected={filterDomain === null}
            className={`indexed-domain-pill all${filterDomain === null ? " active" : ""}`}
            onClick={() => setFilterDomain(null)}
          >
            All · {totalDocs}
          </button>
          {tally.map(({ domain, count }) => {
            const Icon = DOMAIN_ICONS[domain];
            const active = domain === filterDomain;
            return (
              <button
                key={domain}
                type="button"
                role="tab"
                aria-selected={active}
                className={`indexed-domain-pill${active ? " active" : ""}`}
                onClick={() => togglePill(domain)}
                title={`Show ${prettyDomain(domain)} documents`}
              >
                <Icon size={12} />
                {prettyDomain(domain)} · {count}
              </button>
            );
          })}
        </div>
      </div>

      {visibleDocs.length === 0 ? (
        <div className="empty-card">{emptyMessage}</div>
      ) : (
        <div className="indexed-doc-grid">
          {visibleDocs.map((doc) => {
            const Icon = DOMAIN_ICONS[doc.domain];
            const isPending = pendingId === doc.id;
            return (
              <article key={doc.id} className="indexed-doc-card">
                <div className="indexed-doc-top">
                  <span className="indexed-doc-icon">
                    <Icon size={14} />
                  </span>
                  <span className="indexed-doc-domain">{prettyDomain(doc.domain)}</span>
                  <span className="indexed-doc-chunks">{doc.chunk_count} chunks</span>
                  {onDelete ? (
                    <button
                      type="button"
                      className="indexed-doc-delete"
                      onClick={() => handleDelete(doc)}
                      disabled={isPending}
                      aria-label={`Delete ${doc.title}`}
                      title={isPending ? "Deleting…" : "Delete from corpus"}
                    >
                      <Trash size={14} />
                    </button>
                  ) : null}
                </div>
                <div className="indexed-doc-title" title={doc.title}>
                  {doc.title}
                </div>
                <div className="indexed-doc-name" title={doc.filename}>
                  {doc.filename}
                </div>
              </article>
            );
          })}
        </div>
      )}
    </section>
  );
}

function countByDomain(docs: DocumentItem[]) {
  const counts = new Map<CorpusDomain, number>();
  for (const doc of docs) counts.set(doc.domain, (counts.get(doc.domain) ?? 0) + 1);
  return Array.from(counts.entries()).map(([domain, count]) => ({ domain, count }));
}

function prettyDomain(domain: CorpusDomain): string {
  switch (domain) {
    case "technical_document":
      return "Technical";
    case "research_paper":
      return "Research";
    case "legal_contract":
      return "Legal";
    case "healthcare_document":
      return "Healthcare";
    case "financial_document":
      return "Financial";
  }
}
