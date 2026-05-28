import { useEffect, useState } from "react";

import ChatPanel from "./components/ChatPanel";
import DocumentUpload from "./components/DocumentUpload";
import { GitHubStarButton } from "./components/GitHubStarButton";
import IndexedCorpus from "./components/IndexedCorpus";
import { Moon, Sun } from "./components/icons";
import { TelemetryTabs } from "./components/observability/TelemetryTabs";
import { useDeleteDocument, useDocuments, useMetrics } from "./hooks/queries";
import { getUserId } from "./hooks/useUserId";
import type { CorpusDomain } from "./types";

type Theme = "dark" | "light";

function getInitialTheme(): Theme {
  if (typeof window === "undefined") return "dark";
  const stored = window.localStorage.getItem(
    "ask-my-docs-theme",
  ) as Theme | null;
  if (stored === "dark" || stored === "light") return stored;
  return window.matchMedia("(prefers-color-scheme: light)").matches
    ? "light"
    : "dark";
}

const SHORT_ID = getUserId().slice(0, 8);

function App() {
  const [theme, setTheme] = useState<Theme>(getInitialTheme);
  const [guideOpen, setGuideOpen] = useState(false);
  const [selectedDomain, setSelectedDomain] =
    useState<CorpusDomain>("technical_document");
  const documentsQuery = useDocuments();
  const metricsQuery = useMetrics();
  const deleteDocument = useDeleteDocument();

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    window.localStorage.setItem("ask-my-docs-theme", theme);
  }, [theme]);

  const docs = documentsQuery.data ?? [];
  const metrics = metricsQuery.data ?? null;
  const docCount = docs.length;

  return (
    <div className="shell">
      <div className="session-notice" role="note">
        <span className="session-notice-dot" aria-hidden="true" />
        Your workspace is <strong>private to this browser</strong> — documents
        and chats are isolated from all other users.&nbsp;
        <span className="session-notice-id">Session&nbsp;{SHORT_ID}</span>
      </div>

      <div className="ambient ambient-a" />
      <div className="ambient ambient-b" />
      <div className="ambient ambient-c" />

      <header className="hero">
        <div className="hero-card">
          <div className="hero-content">
            <div className="hero-left">
              <img
                className="brand-logo"
                src="/main_left_top_logo.svg"
                alt="Ask My Docs"
              />
            </div>

            <div className="hero-right">
              <div className="hero-right-top">
                <h1>
                  Ask My Docs for{" "}
                  <span>domain-specific corpora</span>, with hybrid retrieval,
                  citation enforcement, and live telemetry.
                </h1>
                <div className="hero-actions">
                  <GitHubStarButton />
                  <button
                    type="button"
                    className="theme-toggle"
                    onClick={() =>
                      setTheme((current) =>
                        current === "dark" ? "light" : "dark",
                      )
                    }
                    aria-label={`Switch to ${theme === "dark" ? "light" : "dark"} mode`}
                  >
                    {theme === "dark" ? <Sun size={16} /> : <Moon size={16} />}
                  </button>
                </div>
              </div>

              <div className="hero-get-started">
                <button
                  type="button"
                  className={`get-started-btn${guideOpen ? " open" : ""}`}
                  onClick={() => setGuideOpen((o) => !o)}
                >
                  <span className="get-started-arrow" aria-hidden>
                    {guideOpen ? "▲" : "▼"}
                  </span>
                  How to Get Started
                </button>

                {guideOpen && (
                  <div className="hero-guide">
                    <div className="guide-step">
                      <span className="guide-num">01</span>
                      <span className="guide-text">
                        Your workspace is <strong>private to this browser</strong> — no
                        sign-in needed. A unique session ID is stored locally so your
                        documents and chat history are invisible to everyone else.
                      </span>
                    </div>
                    <div className="guide-step">
                      <span className="guide-num">02</span>
                      <span className="guide-text">
                        Drop your PDFs and documents into the{" "}
                        <strong>Corpus Ingestion Panel</strong> on the left —
                        we'll chunk, embed, and index them instantly.
                      </span>
                    </div>
                    <div className="guide-step">
                      <span className="guide-num">03</span>
                      <span className="guide-text">
                        Open the <strong>Chat Panel</strong> to the right, ask
                        anything on your docs — every answer arrives with
                        grounded citations and live pipeline stats.
                      </span>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="workspace">
        <aside className="sidebar">
          <DocumentUpload
            onUpload={() => {
              documentsQuery.refetch();
              metricsQuery.refetch();
            }}
            selectedDomain={selectedDomain}
            onDomainChange={setSelectedDomain}
          />
          <TelemetryTabs />
          <a
            href="https://www.buymeacoffee.com/Nefero"
            target="_blank"
            rel="noreferrer"
            className="bmc-inline"
            aria-label="Buy Me a Coffee"
          >
            <span className="bmc-icon">☕</span>
            <span className="bmc-text">Buy me a coffee</span>
          </a>
        </aside>

        <div className="workspace-right">
          <section className="content-panel">
            <ChatPanel
              selectedDomain={selectedDomain}
              onInteractionComplete={() => metricsQuery.refetch()}
              metrics={metrics}
              docCount={docCount}
            />
          </section>

          <IndexedCorpus
            docs={docs}
            selectedDomain={selectedDomain}
            onDelete={async (doc) => {
              try {
                await deleteDocument.mutateAsync(doc.id);
              } catch (error) {
                const message =
                  error instanceof Error ? error.message : "Unknown error";
                window.alert(`Failed to delete the document: ${message}`);
              }
            }}
          />
        </div>
      </main>
    </div>
  );
}

export default App;
