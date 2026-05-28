import { AnswerMarkdown } from "./AnswerMarkdown";
import { FeedbackBar } from "./FeedbackBar";
import { FollowUpChips } from "./FollowUpChips";
import { SourceCard } from "./SourceCard";
import { TelemetryStrip } from "./TelemetryStrip";
import { ThinkingState, ThinkingTrail } from "./ThinkingState";
import type { ChatMessage } from "./types";

interface Props {
  message: ChatMessage;
  questionForFeedback: string;
  onFollowUp: (question: string) => void;
  onFeedback: (rating: -1 | 1 | null) => void;
}

export function MessageCard({ message, questionForFeedback, onFollowUp, onFeedback }: Props) {
  const assistant = message.role === "assistant";
  const telemetry = message.response?.telemetry;
  const followUps = message.response?.follow_up_questions ?? [];

  return (
    <article className={assistant ? "message assistant" : "message user"}>
      <div className="message-role">{assistant ? "Assistant" : "You"}</div>

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
          {!message.streaming ? (
            <FeedbackBar
              response={message.response}
              question={questionForFeedback}
              initialRating={message.feedback ?? null}
              onChange={onFeedback}
            />
          ) : null}
        </>
      ) : null}
    </article>
  );
}
