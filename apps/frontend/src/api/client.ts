import type {
  AnomalyResponse,
  ChatResponse,
  DocumentItem,
  FeedbackAck,
  FeedbackRequest,
  FeedbackSummary,
  ObservabilityResponse,
} from "../types";
import { getUserId } from "../hooks/useUserId";

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    message: string,
    public readonly body?: unknown
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, {
    ...init,
    headers: {
      Accept: "application/json",
      "X-User-ID": getUserId(),
      ...(init?.body && !(init?.body instanceof FormData)
        ? { "Content-Type": "application/json" }
        : {}),
      ...init?.headers,
    },
  });
  if (!response.ok) {
    let body: unknown;
    try {
      body = await response.json();
    } catch {
      body = await response.text().catch(() => undefined);
    }
    const detail =
      body && typeof body === "object" && "detail" in body
        ? String((body as { detail?: unknown }).detail)
        : response.statusText;
    throw new ApiError(response.status, detail, body);
  }
  if (response.status === 204) {
    return undefined as T;
  }
  return (await response.json()) as T;
}

export const api = {
  listDocuments: () => request<DocumentItem[]>("/api/documents/"),
  deleteDocument: (id: string) =>
    request<void>(`/api/documents/${id}`, { method: "DELETE" }),

  observabilitySummary: () =>
    request<ObservabilityResponse>("/api/observability/summary"),
  anomalies: (threshold = 2.5) =>
    request<AnomalyResponse>(`/api/observability/anomalies?threshold=${threshold}`),
  feedbackSummary: () => request<FeedbackSummary>("/api/observability/feedback"),

  postFeedback: (payload: FeedbackRequest) =>
    request<FeedbackAck>("/api/chat/feedback", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  // Chat streaming is a `fetch` against `/api/chat/stream` and is consumed
  // through `useChatStream` rather than a JSON helper because the body is SSE.
  chatNonStreaming: (payload: {
    question: string;
    domain: string;
    session_id?: string;
    top_k?: number;
  }) =>
    request<ChatResponse>("/api/chat/", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  endChatSession: (sessionId: string) =>
    request<{ session_id: string; cleared: boolean }>(
      `/api/chat/session/${encodeURIComponent(sessionId)}`,
      { method: "DELETE" }
    ),
};
