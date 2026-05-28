import type { ReactNode } from "react";

import type { SourceChunk } from "../../types";

interface CitationToken {
  type: "text" | "citation";
  value: string;
  source?: SourceChunk;
}

/**
 * Walk a string and return an alternating list of text segments and citation
 * tokens, looking up each `[Cn]` tag against the provided `sources`. Pure
 * helper so the markdown wrapper can stay a thin component.
 */
export function tokeniseCitations(text: string, sources: SourceChunk[]): CitationToken[] {
  const re = /\[(C\d+)\]/g;
  const tokens: CitationToken[] = [];
  let cursor = 0;
  let match: RegExpExecArray | null;
  while ((match = re.exec(text)) !== null) {
    if (match.index > cursor) {
      tokens.push({ type: "text", value: text.slice(cursor, match.index) });
    }
    const id = match[1];
    tokens.push({
      type: "citation",
      value: id,
      source: sources.find((s) => s.citation_id === id),
    });
    cursor = re.lastIndex;
  }
  if (cursor < text.length) {
    tokens.push({ type: "text", value: text.slice(cursor) });
  }
  return tokens;
}

export type { CitationToken, ReactNode };
