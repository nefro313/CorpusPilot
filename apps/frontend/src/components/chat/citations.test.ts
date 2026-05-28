import { describe, expect, it } from "vitest";

import { tokeniseCitations } from "./citations";
import type { SourceChunk } from "../../types";

const source = (id: string): SourceChunk => ({
  citation_id: id,
  content: `body of ${id}`,
  chunk_index: 0,
  document_id: "doc",
  document_filename: "doc.pdf",
  domain: "technical_document",
  page_number: 1,
  section_title: null,
});

describe("tokeniseCitations", () => {
  it("returns a single text token when there are no citations", () => {
    const tokens = tokeniseCitations("plain text", []);
    expect(tokens).toEqual([{ type: "text", value: "plain text" }]);
  });

  it("splits a string into text and citation tokens", () => {
    const tokens = tokeniseCitations("see [C1] and [C2]", [source("C1"), source("C2")]);
    expect(tokens.map((t) => t.type)).toEqual(["text", "citation", "text", "citation"]);
    expect(tokens[1]).toMatchObject({ value: "C1", source: { citation_id: "C1" } });
    expect(tokens[3]).toMatchObject({ value: "C2", source: { citation_id: "C2" } });
  });

  it("marks citations with no matching source as undefined", () => {
    const tokens = tokeniseCitations("[C9] ghost", []);
    expect(tokens[0]).toEqual({ type: "citation", value: "C9", source: undefined });
  });

  it("returns an empty array for empty input", () => {
    expect(tokeniseCitations("", [])).toEqual([]);
  });
});
