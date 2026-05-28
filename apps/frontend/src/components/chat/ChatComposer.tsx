import { useEffect, useRef } from "react";

import { Send } from "../icons";
import type { CorpusDomain } from "../../types";
import { prettyDomain } from "./domain";

interface Props {
  value: string;
  onChange: (next: string) => void;
  onSubmit: () => void;
  loading: boolean;
  selectedDomain: CorpusDomain;
}

export function ChatComposer({ value, onChange, onSubmit, loading, selectedDomain }: Props) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, 220)}px`;
  }, [value]);

  return (
    <form
      className="composer"
      onSubmit={(e) => {
        e.preventDefault();
        onSubmit();
      }}
    >
      <textarea
        ref={textareaRef}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            onSubmit();
          }
        }}
        placeholder={`Ask within ${prettyDomain(selectedDomain)}...`}
        rows={1}
        disabled={loading}
        aria-label="Ask a question"
      />
      <button type="submit" className="composer-send" disabled={loading || !value.trim()}>
        <Send size={16} />
      </button>
    </form>
  );
}
