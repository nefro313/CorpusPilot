import { Sparkle, User } from "../icons";
import { AnswerMarkdown } from "./AnswerMarkdown";
import { FollowUpChips } from "./FollowUpChips";
import { SourceCard } from "./SourceCard";
import { TelemetryStrip } from "./TelemetryStrip";
import { ThinkingState, ThinkingTrail } from "./ThinkingState";
import type { ChatMessage } from "./types";

interface Props {
  message: ChatMessage;
  onFollowUp: (question: string) => void;
}

export function MessageCard({ message, onFollowUp }: Props) {
  const assistant = message.role === "assistant";
  const telemetry = message.response?.telemetry;
  const followUps = message.response?.follow_up_questions ?? [];
  const sourceCount = message.response?.sources.length ?? 0;
  // Before the first token arrives the only thing to show is the cycling
  // "thinking" pill. Drop the full answer-card chrome so it reads as a compact
  // status line instead of a tiny pill marooned in a big empty box.
  const thinkingOnly = assistant && !message.content;

  return (
    <article
      className={
        assistant
          ? `message assistant${thinkingOnly ? " thinking-only" : ""}`
          : "message user"
      }
    >
      <header className="message-head">
        <span
          className={`message-avatar ${assistant ? "assistant" : "user"}`}
          aria-hidden
        >
          {assistant ? <Sparkle size={13} /> : <User size={13} />}
        </span>
        <span className="message-author">{assistant ? "Assistant" : "You"}</span>
        {assistant && sourceCount > 0 ? (
          <span className="message-source-count">
            {sourceCount} source{sourceCount === 1 ? "" : "s"}
          </span>
        ) : null}
      </header>

      <div className={assistant ? "message-body markdown" : "message-body"}>
        {assistant ? (
          <>
            {message.content ? (
              <AnswerMarkdown
                content={message.content}
                sources={message.response?.sources ?? []}
              />
            ) : (
              <ThinkingState />
            )}
            {message.streaming && message.content ? <ThinkingTrail /> : null}
          </>
        ) : (
          message.content
        )}
      </div>

      {assistant && message.response && telemetry ? (
        <>
          <TelemetryStrip telemetry={telemetry} grounded={message.response.grounded} />
          <FollowUpChips questions={followUps} onPick={onFollowUp} />
          <div className="source-grid">
            {message.response.sources.map((source) => (
              <SourceCard
                key={`${source.document_id}-${source.chunk_index}`}
                source={source}
              />
            ))}
          </div>
        </>
      ) : null}
    </article>
  );
}
