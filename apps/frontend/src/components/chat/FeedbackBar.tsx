import { useState } from "react";

import { usePostFeedback } from "../../hooks/queries";
import type { ChatResponse } from "../../types";

interface Props {
  response: ChatResponse;
  question: string;
  initialRating: -1 | 1 | null | undefined;
  onChange: (rating: -1 | 1 | null) => void;
}

export function FeedbackBar({ response, question, initialRating, onChange }: Props) {
  const [rating, setRating] = useState<-1 | 1 | null>(initialRating ?? null);
  const [comment, setComment] = useState("");
  const [commentOpen, setCommentOpen] = useState(false);
  const [acknowledged, setAcknowledged] = useState(false);
  const mutation = usePostFeedback();

  const submit = (next: -1 | 1) => {
    // Treat a second click on the same button as "undo" for fast HR demos.
    const target = rating === next ? null : next;
    setRating(target);
    onChange(target);
    if (target === null) return;

    mutation.mutate(
      {
        question,
        answer: response.answer,
        rating: target,
        session_id: response.session_id,
        domain: response.domain ?? null,
        citations: response.citations,
        comment: comment.trim() || undefined,
      },
      {
        onSuccess: () => setAcknowledged(true),
      }
    );
  };

  return (
    <div className="feedback-bar" aria-label="Rate this answer">
      <div className="feedback-buttons">
        <button
          type="button"
          className={`feedback-button${rating === 1 ? " active" : ""}`}
          onClick={() => submit(1)}
          aria-pressed={rating === 1}
          disabled={mutation.isPending}
        >
          👍 Helpful
        </button>
        <button
          type="button"
          className={`feedback-button${rating === -1 ? " active" : ""}`}
          onClick={() => submit(-1)}
          aria-pressed={rating === -1}
          disabled={mutation.isPending}
        >
          👎 Off
        </button>
        <button
          type="button"
          className="feedback-comment-toggle"
          onClick={() => setCommentOpen((open) => !open)}
        >
          {commentOpen ? "Hide comment" : "Add comment"}
        </button>
      </div>
      {commentOpen ? (
        <textarea
          className="feedback-comment"
          placeholder="What was right or wrong about this answer?"
          value={comment}
          onChange={(e) => setComment(e.target.value)}
          rows={2}
        />
      ) : null}
      {acknowledged && rating !== null ? (
        <div className="feedback-status" role="status">
          Recorded — thanks. This will show up in `/api/observability/feedback`.
        </div>
      ) : null}
      {mutation.isError ? (
        <div className="feedback-status error" role="alert">
          Couldn't save feedback: {(mutation.error as Error).message}
        </div>
      ) : null}
    </div>
  );
}
