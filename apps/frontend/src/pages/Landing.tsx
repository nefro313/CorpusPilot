import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { useAuth } from "../auth/AuthContext";
import { GoogleSignInButton } from "../auth/GoogleSignInButton";
import {
  Book,
  Chart,
  Crosshair,
  Doc,
  Flask,
  Moon,
  Pulse,
  Radar,
  Scale,
  Sparkle,
  Sun,
  Timer,
} from "../components/icons";
import { useTheme } from "../hooks/useTheme";

const PIPELINE_STAGES = [
  {
    num: "01",
    title: "Ingest & parse",
    copy: "PDF, DOCX, PPTX, XLSX, and HTML are parsed with LlamaParse, chunked, and embedded on upload.",
  },
  {
    num: "02",
    title: "Hybrid retrieve",
    copy: "Every question fans out to BM25 lexical search in PostgreSQL and semantic vectors in Milvus.",
  },
  {
    num: "03",
    title: "RRF fusion",
    copy: "Both result lists are fused with Reciprocal Rank Fusion using weights tuned per corpus domain.",
  },
  {
    num: "04",
    title: "Cohere rerank",
    copy: "The fused candidates are reordered by Cohere rerank-v3.5 so only the strongest evidence survives.",
  },
  {
    num: "05",
    title: "Cited answer",
    copy: "The model must ground every claim — answers ship with inline [S#] citations or they don't ship.",
  },
];

const FEATURES = [
  {
    icon: Doc,
    title: "Five expert corpora",
    copy: "Technical docs, research papers, legal contracts, healthcare records, and financial filings — each domain gets its own retrieval profile and prompt discipline.",
  },
  {
    icon: Radar,
    title: "Hybrid retrieval",
    copy: "BM25 lexical precision meets Milvus semantic recall. RRF fusion with domain-aware weights takes the best of both on every query.",
  },
  {
    icon: Crosshair,
    title: "Citation enforcement",
    copy: "Hard grounding, not vibes. Every sentence in an answer is pinned to a retrieved chunk with hoverable inline citations.",
  },
  {
    icon: Sparkle,
    title: "Streaming chat",
    copy: "Token-by-token SSE streaming with follow-up suggestions, per-session memory, and one-tap feedback on every answer.",
  },
  {
    icon: Timer,
    title: "Live telemetry",
    copy: "Latency percentiles, token spend, grounding rates, and retrieval scores — observable from inside the workspace itself.",
  },
  {
    icon: Pulse,
    title: "Private workspaces",
    copy: "Sign in with Google and your documents, chats, and indexes are isolated to your account — invisible to every other user.",
  },
];

const DOMAINS = [
  { id: "technical_document", label: "Technical", icon: Book },
  { id: "research_paper", label: "Research", icon: Flask },
  { id: "legal_contract", label: "Legal", icon: Scale },
  { id: "healthcare_document", label: "Healthcare", icon: Pulse },
  { id: "financial_document", label: "Financial", icon: Chart },
];

const DEMO_INTERVAL_MS = 6500;

const DEMO_TRACE_ICONS = [Radar, Sparkle, Crosshair, Timer];

const DEMO_SCENES = [
  {
    domain: "technical_document",
    label: "technical",
    icon: Book,
    question: "How do we rotate API keys without breaking live clients?",
    answer: (
      <>
        Issue a secondary key first — both keys stay valid during the{" "}
        <strong>24-hour grace window</strong>
        <span className="citation-inline-chip demo-chip">S1</span>, so clients
        can be swapped over before the old key is revoked
        <span className="citation-inline-chip demo-chip">S2</span>. Every
        rotation is recorded in the audit log
        <span className="citation-inline-chip demo-chip">S3</span>.
      </>
    ),
    trace: ["hybrid · 14 chunks", "reranked · top 5", "3 citations", "1.6s"],
  },
  {
    domain: "research_paper",
    label: "research",
    icon: Flask,
    question: "Does the paper ablate the retrieval head, and what happens?",
    answer: (
      <>
        Yes — removing the retrieval head drops exact-match by{" "}
        <strong>4.2 points</strong>
        <span className="citation-inline-chip demo-chip">S1</span>, and Table 6
        shows recall@5 falling from 91% to 78% on the long-context split
        <span className="citation-inline-chip demo-chip">S2</span>.
      </>
    ),
    trace: ["hybrid · 18 chunks", "reranked · top 5", "2 citations", "2.1s"],
  },
  {
    domain: "legal_contract",
    label: "legal",
    icon: Scale,
    question: "What are the termination clauses in the vendor agreement?",
    answer: (
      <>
        Either party may terminate with <strong>30 days written notice</strong>
        <span className="citation-inline-chip demo-chip">S1</span>; immediate
        termination is permitted on material breach left uncured for 15 days
        <span className="citation-inline-chip demo-chip">S2</span>.
        Confidentiality obligations survive for 3 years
        <span className="citation-inline-chip demo-chip">S1</span>.
      </>
    ),
    trace: ["hybrid · 12 chunks", "reranked · top 5", "3 citations", "1.9s"],
  },
  {
    domain: "healthcare_document",
    label: "healthcare",
    icon: Pulse,
    question: "What follow-up was recommended after the March echo?",
    answer: (
      <>
        A repeat echocardiogram in <strong>6 months</strong>
        <span className="citation-inline-chip demo-chip">S1</span>; continue
        the beta-blocker at the current dose and recheck BNP at the next
        cardiology visit
        <span className="citation-inline-chip demo-chip">S2</span>.
      </>
    ),
    trace: ["hybrid · 9 chunks", "reranked · top 5", "2 citations", "1.4s"],
  },
  {
    domain: "financial_document",
    label: "financial",
    icon: Chart,
    question: "What drove the margin change in the latest 10-Q?",
    answer: (
      <>
        Gross margin expanded <strong>180 bps QoQ</strong>, driven by cloud mix
        shift
        <span className="citation-inline-chip demo-chip">S1</span> and lower
        logistics costs
        <span className="citation-inline-chip demo-chip">S2</span>; management
        flags FX as a headwind for next quarter
        <span className="citation-inline-chip demo-chip">S3</span>.
      </>
    ),
    trace: ["hybrid · 16 chunks", "reranked · top 5", "3 citations", "2.0s"],
  },
];

export default function Landing() {
  const { theme, toggleTheme } = useTheme();
  const { session } = useAuth();
  const navigate = useNavigate();
  const [demoIndex, setDemoIndex] = useState(0);
  const [demoPaused, setDemoPaused] = useState(false);

  useEffect(() => {
    if (demoPaused) return;
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    const timer = setTimeout(
      () => setDemoIndex((i) => (i + 1) % DEMO_SCENES.length),
      DEMO_INTERVAL_MS,
    );
    return () => clearTimeout(timer);
  }, [demoIndex, demoPaused]);

  const scene = DEMO_SCENES[demoIndex];

  return (
    <div className="landing-shell">
      <div className="ambient ambient-a" />
      <div className="ambient ambient-b" />
      <div className="ambient ambient-c" />
      <div className="landing-grid" aria-hidden="true" />

      <nav className="landing-nav">
        <Link
          to="/"
          className="landing-nav-brand"
          aria-label="Ask My Docs home"
        >
          <img src="/landing-nav-logo.svg" alt="Ask My Docs" />
        </Link>
        <div className="landing-nav-actions">
          <button
            type="button"
            className="theme-toggle"
            onClick={toggleTheme}
            aria-label={`Switch to ${theme === "dark" ? "light" : "dark"} mode`}
          >
            {theme === "dark" ? <Sun size={16} /> : <Moon size={16} />}
          </button>
          {session ? (
            <button
              type="button"
              className="landing-cta-btn"
              onClick={() => navigate("/workspace")}
            >
              Open workspace
            </button>
          ) : (
            <Link to="/login" className="landing-signin-link">
              Sign in
            </Link>
          )}
        </div>
      </nav>

      <header className="landing-hero">
        <div className="landing-hero-copy">
          <span className="eyebrow reveal" style={{ animationDelay: "0ms" }}>
            <span className="eyebrow-mark">
              <Crosshair size={12} />
            </span>
            Retrieval-augmented · Citation-enforced
          </span>
          <h1 className="reveal" style={{ animationDelay: "80ms" }}>
            Ask anything.
            <br />
            <span>Your documents</span> answer — with receipts.
          </h1>
          <p className="reveal" style={{ animationDelay: "160ms" }}>
            CorpusPilot turns your PDFs, contracts, papers, and filings into a
            domain-aware knowledge engine. Hybrid retrieval finds the evidence,
            Cohere reranks it, and every answer arrives pinned to its sources.
          </p>
          <div
            className="landing-hero-actions reveal"
            style={{ animationDelay: "240ms" }}
          >
            {session ? (
              <button
                type="button"
                className="landing-cta-btn large"
                onClick={() => navigate("/workspace")}
              >
                Open your workspace
              </button>
            ) : (
              <GoogleSignInButton label="Get started with Google" />
            )}
            <a href="#features" className="landing-ghost-btn">
              Explore the pipeline
            </a>
          </div>
        </div>

        <div
          className={`landing-demo reveal${demoPaused ? " is-paused" : ""}`}
          style={{ animationDelay: "200ms" }}
          data-domain={scene.domain}
          onMouseEnter={() => setDemoPaused(true)}
          onMouseLeave={() => setDemoPaused(false)}
        >
          <div className="landing-demo-bar">
            <span className="demo-dot" />
            <span className="demo-dot" />
            <span className="demo-dot" />
            <span className="landing-demo-title" key={scene.domain}>
              {scene.label} corpus · live session
            </span>
          </div>
          <div className="landing-demo-scene" key={`scene-${scene.domain}`}>
            <div className="landing-demo-msg user">{scene.question}</div>
            <div className="landing-demo-msg assistant">{scene.answer}</div>
            <div className="landing-demo-trace">
              {scene.trace.map((text, i) => {
                const TraceIcon = DEMO_TRACE_ICONS[i];
                return (
                  <span
                    key={text}
                    className="telemetry-pill demo-pill"
                    style={{ animationDelay: `${380 + i * 90}ms` }}
                  >
                    <TraceIcon size={13} /> {text}
                  </span>
                );
              })}
            </div>
          </div>
          <div className="landing-demo-tabs">
            {DEMO_SCENES.map((s, i) => {
              const TabIcon = s.icon;
              const active = i === demoIndex;
              return (
                <button
                  key={s.domain}
                  type="button"
                  className={`demo-tab${active ? " active" : ""}`}
                  data-domain={s.domain}
                  aria-label={`Show ${s.label} corpus demo`}
                  aria-pressed={active}
                  onClick={() => setDemoIndex(i)}
                >
                  {active && (
                    <span
                      key={`${demoIndex}-${demoPaused}`}
                      className="demo-tab-progress"
                      style={{ animationDuration: `${DEMO_INTERVAL_MS}ms` }}
                    />
                  )}
                  <TabIcon size={13} />
                  <span className="demo-tab-label">{s.label}</span>
                </button>
              );
            })}
          </div>
        </div>
      </header>

      <section className="landing-section" id="features">
        <span className="panel-kicker">How it answers</span>
        <h2 className="landing-section-title">
          One question, five stages, zero unsourced claims.
        </h2>
        <ol className="landing-pipeline">
          {PIPELINE_STAGES.map((stage, i) => (
            <li
              key={stage.num}
              className="landing-stage reveal"
              style={{ animationDelay: `${i * 70}ms` }}
            >
              <span className="guide-num">{stage.num}</span>
              <div>
                <h3>{stage.title}</h3>
                <p>{stage.copy}</p>
              </div>
            </li>
          ))}
        </ol>
      </section>

      <section className="landing-section">
        <span className="panel-kicker">What you get</span>
        <h2 className="landing-section-title">
          Built like a retrieval system, not a chat toy.
        </h2>
        <div className="landing-feature-grid">
          {FEATURES.map((feature, i) => {
            const Icon = feature.icon;
            return (
              <article
                key={feature.title}
                className="landing-feature-card reveal"
                style={{ animationDelay: `${i * 60}ms` }}
              >
                <span className="landing-feature-icon">
                  <Icon size={18} />
                </span>
                <h3>{feature.title}</h3>
                <p>{feature.copy}</p>
              </article>
            );
          })}
        </div>
      </section>

      <section className="landing-section landing-domains">
        <span className="panel-kicker">Corpus domains</span>
        <h2 className="landing-section-title">
          Tuned retrieval for the documents that matter.
        </h2>
        <div className="landing-domain-row">
          {DOMAINS.map((domain) => {
            const Icon = domain.icon;
            return (
              <span
                key={domain.id}
                className="corpus-banner landing-domain-chip"
                data-domain={domain.id}
              >
                <span className="corpus-banner-icon">
                  <Icon size={15} />
                </span>
                <strong>{domain.label}</strong>
              </span>
            );
          })}
        </div>
      </section>

      <section className="landing-final">
        <div className="landing-final-card">
          <h2>
            Stop searching your documents.
            <br />
            Start <span>interrogating</span> them.
          </h2>
          <p>
            Sign in with Google, drop in a document, and get grounded answers in
            under a minute.
          </p>
          {session ? (
            <button
              type="button"
              className="landing-cta-btn large"
              onClick={() => navigate("/workspace")}
            >
              Open your workspace
            </button>
          ) : (
            <GoogleSignInButton
              label="Sign in with Google"
              className="centered"
            />
          )}
        </div>
      </section>

      <section className="landing-section landing-coffee-section">
        <a
          className="landing-coffee"
          href="https://www.buymeacoffee.com/Nefero"
          target="_blank"
          rel="noreferrer"
        >
          <span className="coffee-cup" aria-hidden="true">
            <span className="coffee-steam" />
            <span className="coffee-steam" />
            <span className="coffee-steam" />
            ☕
          </span>
          <span className="landing-coffee-copy">
            <strong>Fuel the next release.</strong>
            <span>
              CorpusPilot is independently built and maintained — if it saved
              you a re-read, ground that claim with a coffee.
            </span>
          </span>
          <span className="landing-coffee-cta">
            Buy me a coffee
            <span className="citation-inline-chip demo-chip">S☕</span>
          </span>
        </a>
      </section>

      <footer className="landing-footer">
        <span>CorpusPilot · Ask My Docs</span>
        <span className="landing-footer-meta">
          PostgreSQL BM25 · Milvus vectors · RRF fusion · Cohere rerank
        </span>
      </footer>
    </div>
  );
}
