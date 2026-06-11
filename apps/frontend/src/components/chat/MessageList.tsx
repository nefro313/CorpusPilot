import { useEffect, useRef } from "react";

import { MessageCard } from "./MessageCard";
import type { ChatMessage } from "./types";

interface Props {
  messages: ChatMessage[];
  loading: boolean;
  onFollowUp: (question: string) => void;
}

export function MessageList({ messages, loading, onFollowUp }: Props) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  return (
    <div className="message-list">
      {messages.map((message, index) => (
        <MessageCard key={index} message={message} onFollowUp={onFollowUp} />
      ))}
      <div ref={bottomRef} />
    </div>
  );
}
