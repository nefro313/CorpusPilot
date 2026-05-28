import { useEffect, useRef, useState } from "react";

import { api } from "../api/client";
import { useChatStream } from "../hooks/useChatStream";
import type { CorpusDomain, ObservabilityResponse } from "../types";
import { ChatComposer } from "./chat/ChatComposer";
import { CorpusBanner } from "./chat/CorpusBanner";
import { DOMAIN_SUGGESTIONS, newSessionId, prettyDomain } from "./chat/domain";
import { MessageList } from "./chat/MessageList";
import { Coins, Crosshair, Radar, Sparkle, Timer } from "./icons";

interface Props {
  selectedDomain: CorpusDomain;
  onInteractionComplete: () => void;
  metrics: ObservabilityResponse | null;
  docCount: number;
}

function fmt(v: number | null | undefined, fn: (n: number) => string) {
  return v == null ? "--" : fn(v);
}

export default function ChatPanel({ selectedDomain, onInteractionComplete, metrics, docCount }: Props) {
  const [question, setQuestion] = useState("");
  const [sessionId, setSessionId] = useState<string>(() => newSessionId());
  const [statsOpen, setStatsOpen] = useState(false);
  const { messages, loading, send, reset, setFeedback } = useChatStream();
  const lastDomainRef = useRef<CorpusDomain>(selectedDomain);

  useEffect(() => {
    if (!loading && messages.length > 0 && messages[messages.length - 1].role === "assistant") {
      onInteractionComplete();
    }
    // We only want to fire the parent callback after a streamed answer settles,
    // not when the local question text changes.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [loading]);

  // Switching the active corpus domain (from sidebar dropdown OR the chat
  // composer) resets the chat: the LangGraph thread is bound to a session_id,
  // and conversation history collected against the old domain is unhelpful
  // — and often wrong — when applied to a different corpus.
  useEffect(() => {
    if (lastDomainRef.current === selectedDomain) return;
    lastDomainRef.current = selectedDomain;
    const abandoned = sessionId;
    reset();
    setQuestion("");
    setSessionId(newSessionId());
    void api.endChatSession(abandoned).catch(() => {
      /* best-effort cleanup; safe to ignore */
    });
    // reset / setSessionId are stable; we intentionally key only on domain.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedDomain]);

  const submit = async (text: string) => {
    const trimmed = text.trim();
    if (!trimmed) return;
    setQuestion("");
    await send({
      question: trimmed,
      domain: selectedDomain,
      sessionId,
      onSessionId: setSessionId,
    });
  };

  const startNewChat = () => {
    if (loading) return;
    const abandoned = sessionId;
    reset();
    setQuestion("");
    setSessionId(newSessionId());
    void api.endChatSession(abandoned).catch(() => {
      /* best-effort cleanup */
    });
  };

  const s = metrics?.summary;

  const handleBodyWheel = (e: React.WheelEvent<HTMLDivElement>) => {
    const el = e.currentTarget;
    const atTop = el.scrollTop <= 0;
    const atBottom = el.scrollTop + el.clientHeight >= el.scrollHeight - 1;
    const scrollingUp = e.deltaY < 0;
    const scrollingDown = e.deltaY > 0;
    if ((scrollingUp && !atTop) || (scrollingDown && !atBottom)) {
      e.stopPropagation();
    }
  };

  return (
    <div className="chat-shell">
      <div className="chat-topbar">
        <div className="chat-topbar-main">
          <div className="panel-kicker">Grounded QA</div>
          <h2>Hybrid retrieval scoped to the active corpus.</h2>
          <CorpusBanner domain={selectedDomain} />
        </div>
        <div className="chat-topbar-actions">
          <button
            type="button"
            className={`stats-toggle-button${statsOpen ? " active" : ""}`}
            onClick={() => setStatsOpen((o) => !o)}
            title="Toggle pipeline stats"
          >
            <Radar size={13} />
            Stats
          </button>
          <button
            type="button"
            className="new-chat-button"
            onClick={startNewChat}
            disabled={loading || messages.length === 0}
            title="Start a new chat session"
          >
            <span className="new-chat-glyph" aria-hidden>
              +
            </span>
            New chat
          </button>
        </div>
      </div>

      {statsOpen && (
        <div className="chat-stats-strip">
          <div className="chat-stat-item">
            <span className="chat-stat-icon"><Radar size={12} /></span>
            <span className="chat-stat-label">Grounded Rate</span>
            <span className="chat-stat-value">
              {fmt(s?.grounded_rate, (n) => `${Math.round(n * 100)}%`)}
            </span>
          </div>
          <div className="chat-stat-item">
            <span className="chat-stat-icon"><Timer size={12} /></span>
            <span className="chat-stat-label">P95 Latency</span>
            <span className="chat-stat-value">
              {fmt(s?.p95_latency_ms, (n) => `${Math.round(n)} ms`)}
            </span>
          </div>
          <div className="chat-stat-item">
            <span className="chat-stat-icon"><Coins size={12} /></span>
            <span className="chat-stat-label">Avg Cost</span>
            <span className="chat-stat-value">
              {fmt(s?.average_cost_usd, (n) => `$${n.toFixed(4)}`)}
            </span>
          </div>
          <div className="chat-stat-item">
            <span className="chat-stat-icon"><Crosshair size={12} /></span>
            <span className="chat-stat-label">Indexed Docs</span>
            <span className="chat-stat-value">{String(docCount).padStart(2, "0")}</span>
          </div>
        </div>
      )}

      <div className="chat-body" onWheel={handleBodyWheel}>
        {messages.length === 0 ? (
          <div className="chat-empty">
            <div className="empty-chip">
              <Sparkle size={12} />
              Ready for search
            </div>
            <h3>Ask a question and force the answer to earn its citations.</h3>
            <p>
              Questions are scoped to the {prettyDomain(selectedDomain)} corpus selected in the
              sidebar.
            </p>
            <div className="suggestions">
              {DOMAIN_SUGGESTIONS[selectedDomain].map((suggestion) => (
                <button
                  key={suggestion}
                  type="button"
                  className="suggestion-card"
                  onClick={() => submit(suggestion)}
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <MessageList
            messages={messages}
            loading={loading}
            onFollowUp={submit}
            onFeedback={setFeedback}
          />
        )}
      </div>

      <ChatComposer
        value={question}
        onChange={setQuestion}
        onSubmit={() => submit(question)}
        loading={loading}
        selectedDomain={selectedDomain}
      />
    </div>
  );
}
