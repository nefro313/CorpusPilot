import { Book, Chart, Flask, Pulse, Scale } from "../icons";
import type { CorpusDomain } from "../../types";

export const DOMAIN_ICONS = {
  technical_document: Book,
  research_paper: Flask,
  legal_contract: Scale,
  healthcare_document: Pulse,
  financial_document: Chart,
} as const;

export const DOMAIN_SUGGESTIONS: Record<CorpusDomain, string[]> = {
  technical_document: [
    "What implementation constraints or operating procedures are documented?",
    "Summarize the architecture decisions and cite the strongest evidence.",
    "Which dependencies or APIs are explicitly required?",
  ],
  research_paper: [
    "What methodology and main findings are reported?",
    "Summarize the benchmark or evaluation setup with citations.",
    "What limitations or future work are mentioned?",
  ],
  legal_contract: [
    "What obligations, dates, or termination clauses should I know?",
    "Summarize the payment and liability terms with citations.",
    "Which sections define notice periods or renewal conditions?",
  ],
  healthcare_document: [
    "Summarize the documented assessment and plan.",
    "What medications, diagnoses, or follow-up steps are recorded?",
    "What findings are explicitly supported by the uploaded record?",
  ],
  financial_document: [
    "What are the reported revenue, operating income, and net income for the latest period?",
    "Summarize the key risk factors and management's discussion of results.",
    "Which line items or footnotes changed materially year over year?",
  ],
};

export function prettyDomain(domain: CorpusDomain): string {
  switch (domain) {
    case "technical_document":
      return "technical corpus";
    case "research_paper":
      return "research corpus";
    case "legal_contract":
      return "legal corpus";
    case "healthcare_document":
      return "healthcare corpus";
    case "financial_document":
      return "financial corpus";
  }
}

export function domainLabel(domain: CorpusDomain): string {
  switch (domain) {
    case "technical_document":
      return "Technical";
    case "research_paper":
      return "Research";
    case "legal_contract":
      return "Legal";
    case "healthcare_document":
      return "Healthcare";
    case "financial_document":
      return "Financial";
  }
}

export function newSessionId(): string {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return crypto.randomUUID();
  }
  return `s-${Date.now()}-${Math.random().toString(36).slice(2, 10)}`;
}
