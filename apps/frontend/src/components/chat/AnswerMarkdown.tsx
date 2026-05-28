import React, { type ReactNode } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

import type { SourceChunk } from "../../types";
import { CitationChip } from "./CitationChip";
import { tokeniseCitations } from "./citations";

function renderTokens(text: string, sources: SourceChunk[], keyPrefix: string): ReactNode[] {
  const tokens = tokeniseCitations(text, sources);
  if (tokens.length === 0) return [text];
  return tokens.map((token, index) => {
    if (token.type === "text") return token.value;
    return (
      <CitationChip
        key={`${keyPrefix}-${index}`}
        id={token.value}
        source={token.source}
      />
    );
  });
}

function decorate(
  children: ReactNode,
  sources: SourceChunk[],
  keyPrefix = "c"
): ReactNode {
  return React.Children.map(children, (child, childIdx) => {
    if (typeof child === "string") {
      return renderTokens(child, sources, `${keyPrefix}-${childIdx}`);
    }
    if (React.isValidElement(child)) {
      const element = child as React.ReactElement<{ children?: ReactNode }>;
      if (element.props.children !== undefined) {
        return React.cloneElement(element, {
          children: decorate(element.props.children, sources, `${keyPrefix}-${childIdx}`),
        });
      }
    }
    return child;
  });
}

export function AnswerMarkdown({
  content,
  sources,
}: {
  content: string;
  sources: SourceChunk[];
}) {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      components={{
        p: ({ children }) => <p>{decorate(children, sources)}</p>,
        li: ({ children }) => <li>{decorate(children, sources)}</li>,
        strong: ({ children }) => <strong>{decorate(children, sources)}</strong>,
        em: ({ children }) => <em>{decorate(children, sources)}</em>,
        td: ({ children }) => <td>{decorate(children, sources)}</td>,
        th: ({ children }) => <th>{decorate(children, sources)}</th>,
        blockquote: ({ children }) => <blockquote>{decorate(children, sources)}</blockquote>,
      }}
    >
      {content}
    </ReactMarkdown>
  );
}
