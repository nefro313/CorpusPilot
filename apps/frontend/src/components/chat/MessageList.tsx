import { useEffect, useRef } from "react";

import { MessageCard } from "./MessageCard";
import type { ChatMessage } from "./types";

interface Props {
  messages: ChatMessage[];
  loading: boolean;
  onFollowUp: (question: string) => void;
  onFeedback: (index: number, rating: -1 | 1 | null) => void;
}

export function MessageList({ messages, loading, onFollowUp, onFeedback }: Props) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  return (
    <div className="message-list">
      {messages.map((message, index) => {
        const previous = index > 0 ? messages[index - 1] : null;
        const questionForFeedback = previous?.role === "user" ? previous.content : "";
        return (
          <MessageCard
            key={index}
            message={message}
            questionForFeedback={questionForFeedback}
            onFollowUp={onFollowUp}
            onFeedback={(rating) => onFeedback(index, rating)}
          />
        );
      })}
      <div ref={bottomRef} />
    </div>
  );
}
