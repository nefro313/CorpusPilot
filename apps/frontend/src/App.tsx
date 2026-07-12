import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { useAuth } from "./auth/AuthContext";
import ChatPanel from "./components/ChatPanel";
import DocumentUpload from "./components/DocumentUpload";
import IndexedCorpus from "./components/IndexedCorpus";
import { Moon, Sun } from "./components/icons";
import { useDeleteDocument, useDocuments, useMetrics } from "./hooks/queries";
import { useTheme } from "./hooks/useTheme";
import type { CorpusDomain } from "./types";

function App() {
  const { theme, toggleTheme } = useTheme();
  const { user, signOut } = useAuth();
  const navigate = useNavigate();
  const [selectedDomain, setSelectedDomain] =
    useState<CorpusDomain>("technical_document");
  const documentsQuery = useDocuments();
  const metricsQuery = useMetrics();
  const deleteDocument = useDeleteDocument();

  const displayName =
    (user?.user_metadata?.full_name as string | undefined) ??
    user?.email ??
    "Signed in";
  const avatarUrl = user?.user_metadata?.avatar_url as string | undefined;

  const handleSignOut = async () => {
    await signOut();
    navigate("/", { replace: true });
  };

  const docs = documentsQuery.data ?? [];
  const metrics = metricsQuery.data ?? null;
  const docCount = docs.length;

  return (
    <div className="shell">
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
                  Ask My Docs for <span>domain-specific corpora</span>, with
                  hybrid retrieval, citation enforcement, and live telemetry.
                </h1>
                <div className="hero-actions">
                  <button
                    type="button"
                    className="theme-toggle"
                    onClick={toggleTheme}
                    aria-label={`Switch to ${theme === "dark" ? "light" : "dark"} mode`}
                  >
                    {theme === "dark" ? <Sun size={16} /> : <Moon size={16} />}
                  </button>
                  <div className="user-chip">
                    {avatarUrl ? (
                      <img
                        className="user-chip-avatar"
                        src={avatarUrl}
                        alt=""
                        referrerPolicy="no-referrer"
                      />
                    ) : (
                      <span
                        className="user-chip-avatar fallback"
                        aria-hidden="true"
                      >
                        {displayName.charAt(0).toUpperCase()}
                      </span>
                    )}
                    <span className="user-chip-name" title={user?.email ?? ""}>
                      {displayName}
                    </span>
                    <button
                      type="button"
                      className="user-chip-signout"
                      onClick={handleSignOut}
                    >
                      Sign out
                    </button>
                  </div>
                </div>
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
