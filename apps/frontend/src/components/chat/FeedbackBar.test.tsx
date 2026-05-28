import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import { FeedbackBar } from "./FeedbackBar";
import type { ChatResponse } from "../../types";

const baseResponse: ChatResponse = {
  answer: "answer body",
  domain: "technical_document",
  grounded: true,
  citations: ["C1"],
  sources: [],
  follow_up_questions: [],
  telemetry: {
    latency_ms: 100,
    prompt_tokens: 10,
    completion_tokens: 10,
    total_tokens: 20,
    estimated_cost_usd: 0.0001,
    semantic_candidates: 5,
    lexical_candidates: 5,
    fused_candidates: 5,
    reranked_candidates: 5,
    citation_valid: true,
  },
  session_id: "s-1",
};

afterEach(() => {
  vi.restoreAllMocks();
});

function renderBar(initialRating: -1 | 1 | null = null, onChange = vi.fn()) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  render(
    <QueryClientProvider client={queryClient}>
      <FeedbackBar
        response={baseResponse}
        question="what is x"
        initialRating={initialRating}
        onChange={onChange}
      />
    </QueryClientProvider>
  );
  return { onChange };
}

describe("FeedbackBar", () => {
  it("renders both rating buttons", () => {
    renderBar();
    expect(screen.getByRole("button", { name: /helpful/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /off/i })).toBeInTheDocument();
  });

  it("submits a positive rating and acknowledges", async () => {
    const fetchSpy = vi.fn(async () => ({
      ok: true,
      status: 201,
      statusText: "",
      json: async () => ({ id: "1", created_at: "now" }),
      text: async () => "",
    }));
    vi.stubGlobal("fetch", fetchSpy);

    const { onChange } = renderBar();
    await userEvent.click(screen.getByRole("button", { name: /helpful/i }));

    expect(onChange).toHaveBeenCalledWith(1);
    await waitFor(() => expect(fetchSpy).toHaveBeenCalledOnce());
    const call = fetchSpy.mock.calls[0] as unknown as [string, RequestInit];
    expect(call[1].method).toBe("POST");
    expect(JSON.parse(call[1].body as string)).toMatchObject({
      rating: 1,
      question: "what is x",
    });
    await screen.findByRole("status");
  });

  it("treats a second click on the same button as undo (no POST)", async () => {
    const fetchSpy = vi.fn(async () => ({
      ok: true,
      status: 201,
      statusText: "",
      json: async () => ({ id: "1", created_at: "now" }),
      text: async () => "",
    }));
    vi.stubGlobal("fetch", fetchSpy);

    const { onChange } = renderBar();
    const helpful = screen.getByRole("button", { name: /helpful/i });

    await userEvent.click(helpful);
    await waitFor(() => expect(fetchSpy).toHaveBeenCalledOnce());
    await userEvent.click(helpful);

    expect(fetchSpy).toHaveBeenCalledTimes(1);
    expect(onChange).toHaveBeenLastCalledWith(null);
  });

  it("toggles the comment textarea", async () => {
    renderBar();
    expect(screen.queryByRole("textbox")).not.toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: /add comment/i }));
    expect(screen.getByRole("textbox")).toBeInTheDocument();
  });
});
