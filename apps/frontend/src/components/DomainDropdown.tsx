import { useEffect, useRef, useState } from "react";
import { Book, Chart, Flask, Pulse, Scale } from "./icons";
import type { CorpusDomain, DomainProfile } from "../types";

const DOMAIN_ICONS = {
  technical_document: Book,
  research_paper: Flask,
  legal_contract: Scale,
  healthcare_document: Pulse,
  financial_document: Chart,
} as const;

interface Props {
  domains: DomainProfile[];
  value: CorpusDomain;
  onChange: (domain: CorpusDomain) => void;
  disabled?: boolean;
}

export default function DomainDropdown({ domains, value, onChange, disabled }: Props) {
  const [open, setOpen] = useState(false);
  const wrapperRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    const onDocClick = (e: MouseEvent) => {
      if (!wrapperRef.current?.contains(e.target as Node)) setOpen(false);
    };
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setOpen(false);
    };
    document.addEventListener("mousedown", onDocClick);
    document.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("mousedown", onDocClick);
      document.removeEventListener("keydown", onKey);
    };
  }, [open]);

  const active = domains.find((d) => d.value === value);
  const ActiveIcon = DOMAIN_ICONS[value];

  return (
    <div ref={wrapperRef} className={`domain-dropdown${open ? " open" : ""}`}>
      <button
        type="button"
        className="domain-dropdown-trigger"
        onClick={() => setOpen((v) => !v)}
        disabled={disabled || domains.length === 0}
        aria-haspopup="listbox"
        aria-expanded={open}
      >
        <span className="domain-dropdown-icon">
          <ActiveIcon size={18} />
        </span>
        <span className="domain-dropdown-text">
          <span className="domain-dropdown-label">{active?.label ?? "Select corpus"}</span>
          {active ? (
            <span className="domain-dropdown-sublabel">{active.chunking_strategy}</span>
          ) : null}
        </span>
        <span className={`domain-dropdown-caret${open ? " up" : ""}`} aria-hidden>
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="6 9 12 15 18 9" />
          </svg>
        </span>
      </button>

      {open ? (
        <ul className="domain-dropdown-menu" role="listbox" tabIndex={-1}>
          {domains.map((domain) => {
            const Icon = DOMAIN_ICONS[domain.value];
            const selected = domain.value === value;
            return (
              <li
                key={domain.value}
                role="option"
                aria-selected={selected}
                className={`domain-dropdown-item${selected ? " selected" : ""}`}
                onClick={() => {
                  onChange(domain.value);
                  setOpen(false);
                }}
              >
                <span className="domain-dropdown-item-icon">
                  <Icon size={16} />
                </span>
                <span className="domain-dropdown-item-text">
                  <span className="domain-dropdown-item-label">{domain.label}</span>
                  <span className="domain-dropdown-item-desc">{domain.description}</span>
                </span>
                {selected ? (
                  <span className="domain-dropdown-item-check" aria-hidden>
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                      <polyline points="20 6 9 17 4 12" />
                    </svg>
                  </span>
                ) : null}
              </li>
            );
          })}
        </ul>
      ) : null}
    </div>
  );
}
