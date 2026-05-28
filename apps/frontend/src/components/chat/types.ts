import type { ChatResponse } from "../../types";

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  response?: ChatResponse;
  streaming?: boolean;
  feedback?: -1 | 1 | null;
}

export interface ChatStreamPacket {
  event: string;
  data: unknown;
}
