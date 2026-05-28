import { useState } from "react";

import { drainSseBuffer } from "../components/chat/sse";
import type { ChatMessage } from "../components/chat/types";
import type { ChatResponse, CorpusDomain } from "../types";
import { getUserId } from "./useUserId";

interface SendArgs {
  question: string;
  domain: CorpusDomain;
  sessionId: string;
  onSessionId: (id: string) => void;
}

interface ChatStreamApi {
  messages: ChatMessage[];
  loading: boolean;
  send: (args: SendArgs) => Promise<void>;
  reset: () => void;
  setFeedback: (index: number, rating: -1 | 1 | null) => void;
}

export function useChatStream(): ChatStreamApi {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);

  const send = async ({ question, domain, sessionId, onSessionId }: SendArgs) => {
    const trimmed = question.trim();
    if (!trimmed || loading) return;

    setMessages((current) => [
      ...current,
      { role: "user", content: trimmed },
      { role: "assistant", content: "", streaming: true },
    ]);
    setLoading(true);

    try {
      const res = await fetch("/api/chat/stream", {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-User-ID": getUserId() },
        body: JSON.stringify({ question: trimmed, domain, session_id: sessionId }),
      });
      if (!res.ok || !res.body) throw new Error(`Stream rejected (status ${res.status})`);

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const { packets, rest } = drainSseBuffer(buffer);
        buffer = rest;

        for (const packet of packets) {
          if (packet.event === "text_delta") {
            const delta = (packet.data as { delta: string }).delta;
            setMessages((current) => {
              const next = [...current];
              const last = next[next.length - 1];
              next[next.length - 1] = { ...last, content: `${last.content}${delta}` };
              return next;
            });
          } else if (packet.event === "response") {
            const response = packet.data as ChatResponse;
            if (response.session_id && response.session_id !== sessionId) {
              onSessionId(response.session_id);
            }
            setMessages((current) => {
              const next = [...current];
              next[next.length - 1] = {
                role: "assistant",
                content: response.answer,
                response,
                streaming: false,
              };
              return next;
            });
          } else if (packet.event === "error") {
            const message = (packet.data as { message?: string }).message ?? "The request failed.";
            setMessages((current) => {
              const next = [...current];
              next[next.length - 1] = { role: "assistant", content: message, streaming: false };
              return next;
            });
          }
        }
      }
    } catch (error) {
      const message =
        error instanceof Error
          ? error.message
          : "The request failed. Check backend health and credentials.";
      setMessages((current) => {
        const next = [...current];
        next[next.length - 1] = { role: "assistant", content: message, streaming: false };
        return next;
      });
    } finally {
      setLoading(false);
    }
  };

  const reset = () => setMessages([]);

  const setFeedback = (index: number, rating: -1 | 1 | null) =>
    setMessages((current) => {
      if (index < 0 || index >= current.length) return current;
      const next = [...current];
      next[index] = { ...next[index], feedback: rating };
      return next;
    });

  return { messages, loading, send, reset, setFeedback };
}
