import type { ReactNode } from "react";
import { Navigate, useLocation } from "react-router-dom";

import { useAuth } from "./AuthContext";

export function ProtectedRoute({ children }: { children: ReactNode }) {
  const { session, loading, configured } = useAuth();
  const location = useLocation();

  if (!configured) {
    return <Navigate to="/login" replace />;
  }

  if (loading) {
    return (
      <div className="auth-loading" role="status" aria-live="polite">
        <span className="auth-loading-ring" aria-hidden="true" />
        Restoring your session…
      </div>
    );
  }

  if (!session) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  }

  return <>{children}</>;
}
