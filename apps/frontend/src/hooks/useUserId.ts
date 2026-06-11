const USER_ID_KEY = "ask-my-docs-user-id";

export function getUserId(): string {
  let id = localStorage.getItem(USER_ID_KEY);
  if (!id) {
    id = crypto.randomUUID();
    localStorage.setItem(USER_ID_KEY, id);
  }
  return id;
}

/**
 * Pin the workspace identity to the authenticated Supabase user so every
 * request (X-User-ID header) is scoped to the Google account rather than a
 * per-browser random UUID.
 */
export function setUserId(id: string): void {
  localStorage.setItem(USER_ID_KEY, id);
}

export function clearUserId(): void {
  localStorage.removeItem(USER_ID_KEY);
}
