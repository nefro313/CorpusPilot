import "@testing-library/jest-dom/vitest";
import { vi } from "vitest";

// Node 21+ ships an experimental global `localStorage` that resolves to
// `undefined` without `--localstorage-file`, shadowing the one jsdom provides.
// CI runs on Node 20 (real jsdom storage) so this only bites on newer local
// Node. Install an in-memory shim when storage is missing so `getUserId()` and
// friends work regardless of Node version.
if (typeof globalThis.localStorage === "undefined") {
  const store = new Map<string, string>();
  const shim: Storage = {
    get length() {
      return store.size;
    },
    clear: () => store.clear(),
    getItem: (key) => (store.has(key) ? store.get(key)! : null),
    key: (index) => [...store.keys()][index] ?? null,
    removeItem: (key) => void store.delete(key),
    setItem: (key, value) => void store.set(key, String(value)),
  };
  Object.defineProperty(globalThis, "localStorage", {
    value: shim,
    writable: true,
    configurable: true,
  });
}

// Tests must not depend on a developer's local `.env`. When the real Supabase
// keys are present, `lib/supabase.ts` builds a live client and `api/client.ts`
// calls `supabase.auth.getSession()`, which crashes under jsdom. Pin the module
// to its unconfigured (null) state so requests take the X-User-ID path — the
// same state CI runs in, where no `.env` exists.
vi.mock("../lib/supabase", () => ({
  supabase: null,
  isSupabaseConfigured: false,
}));
