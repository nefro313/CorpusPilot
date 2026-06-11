import type { Session, User } from "@supabase/supabase-js";
import {
  createContext,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";

import { clearUserId, setUserId } from "../hooks/useUserId";
import { isSupabaseConfigured, supabase } from "../lib/supabase";

interface AuthContextValue {
  session: Session | null;
  user: User | null;
  /** True while the initial session is being restored from storage. */
  loading: boolean;
  configured: boolean;
  /** Error returned by the OAuth provider via redirect params, if any. */
  authError: string | null;
  signInWithGoogle: () => Promise<void>;
  signOut: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

/**
 * Supabase reports OAuth failures by appending error params to the redirect
 * URL (query or hash). Capture them at provider mount, before client-side
 * route redirects strip them from the address bar.
 */
function readAuthErrorFromUrl(): string | null {
  const search = new URLSearchParams(window.location.search);
  const hash = new URLSearchParams(window.location.hash.replace(/^#/, ""));
  return (
    search.get("error_description") ??
    hash.get("error_description") ??
    search.get("error") ??
    hash.get("error")
  );
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<Session | null>(null);
  const [loading, setLoading] = useState(isSupabaseConfigured);
  const [authError, setAuthError] = useState<string | null>(readAuthErrorFromUrl);

  useEffect(() => {
    if (!supabase) return;

    // Surfaces failures from the OAuth-callback token exchange (e.g. PKCE
    // code-verifier mismatch), which never appear in the redirect URL.
    supabase.auth.initialize().then(({ error }) => {
      if (error) {
        console.error("[auth] initialize failed:", error);
        setAuthError(error.message);
      }
    });

    supabase.auth.getSession().then(({ data }) => {
      setSession(data.session);
      if (data.session) setUserId(data.session.user.id);
      setLoading(false);
    });

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, nextSession) => {
      setSession(nextSession);
      if (nextSession) setUserId(nextSession.user.id);
    });

    return () => subscription.unsubscribe();
  }, []);

  const signInWithGoogle = async () => {
    if (!supabase) return;
    const { error } = await supabase.auth.signInWithOAuth({
      provider: "google",
      options: { redirectTo: `${window.location.origin}/workspace` },
    });
    if (error) throw error;
  };

  const signOut = async () => {
    if (!supabase) return;
    await supabase.auth.signOut();
    clearUserId();
    setSession(null);
  };

  return (
    <AuthContext.Provider
      value={{
        session,
        user: session?.user ?? null,
        loading,
        configured: isSupabaseConfigured,
        authError,
        signInWithGoogle,
        signOut,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within an AuthProvider");
  return ctx;
}
