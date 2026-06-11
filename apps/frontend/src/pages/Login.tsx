import { Link, Navigate, useLocation } from "react-router-dom";

import { useAuth } from "../auth/AuthContext";
import { GoogleSignInButton } from "../auth/GoogleSignInButton";
import { Crosshair, Doc, Moon, Radar, Sun } from "../components/icons";
import { useTheme } from "../hooks/useTheme";

export default function Login() {
  const { theme, toggleTheme } = useTheme();
  const { session, loading, authError } = useAuth();
  const location = useLocation();
  const from = (location.state as { from?: string } | null)?.from ?? "/workspace";

  if (!loading && session) {
    return <Navigate to={from} replace />;
  }

  return (
    <div className="login-shell">
      <div className="ambient ambient-a" />
      <div className="ambient ambient-b" />
      <div className="ambient ambient-c" />
      <div className="landing-grid" aria-hidden="true" />

      <nav className="landing-nav login-nav">
        <Link to="/" className="landing-nav-brand" aria-label="Back to home">
          <img src="/main_left_top_logo.svg" alt="Ask My Docs" />
        </Link>
        <button
          type="button"
          className="theme-toggle"
          onClick={toggleTheme}
          aria-label={`Switch to ${theme === "dark" ? "light" : "dark"} mode`}
        >
          {theme === "dark" ? <Sun size={16} /> : <Moon size={16} />}
        </button>
      </nav>

      <main className="login-stage">
        <div className="login-card reveal">
          <span className="eyebrow">
            <span className="eyebrow-mark">
              <Crosshair size={12} />
            </span>
            Secure access
          </span>

          <h1>
            Your corpus is waiting.
            <br />
            <span>Sign in</span> to open it.
          </h1>
          <p className="login-sub">
            One Google account, one private workspace. Your documents, chats,
            and indexes are yours alone.
          </p>

          {authError && (
            <p className="google-signin-error" role="alert">
              Sign-in failed: {authError.replace(/\+/g, " ")}
            </p>
          )}

          <GoogleSignInButton label="Continue with Google" className="login-google" />

          <div className="login-divider" role="presentation">
            <span>what's inside</span>
          </div>

          <ul className="login-points">
            <li>
              <span className="login-point-icon">
                <Doc size={15} />
              </span>
              <span>
                <strong>Private corpus</strong> — uploads are isolated to your
                account, invisible to everyone else.
              </span>
            </li>
            <li>
              <span className="login-point-icon">
                <Radar size={15} />
              </span>
              <span>
                <strong>Hybrid retrieval</strong> — BM25 + semantic vectors,
                fused and reranked on every question.
              </span>
            </li>
            <li>
              <span className="login-point-icon">
                <Crosshair size={15} />
              </span>
              <span>
                <strong>Grounded answers</strong> — inline citations on every
                claim, or no answer at all.
              </span>
            </li>
          </ul>

          <p className="login-fineprint">
            We only read your name, email, and avatar from Google — nothing
            else. <Link to="/">Back to home</Link>
          </p>
        </div>
      </main>
    </div>
  );
}
