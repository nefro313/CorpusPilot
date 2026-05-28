export type CorpusDomain =
  | "technical_document"
  | "research_paper"
  | "legal_contract"
  | "healthcare_document"
  | "financial_document";

export interface DomainProfile {
  value: CorpusDomain;
  label: string;
  description: string;
  chunking_strategy: string;
  retrieval_strategy: string;
}

export interface DocumentItem {
  id: string;
  filename: string;
  title: string;
  domain: CorpusDomain;
  mime_type: string;
  created_at: string;
  chunk_count: number;
}

export interface UploadFileResult {
  filename: string;
  status: "indexed" | "duplicate" | "rejected";
  message: string;
  document?: (DocumentItem & {
    chunking_strategy: string;
    retrieval_strategy: string;
  }) | null;
  suggested_domain?: CorpusDomain | null;
  rejection_reason?: string | null;
}

export interface BatchUploadSummary {
  total_files: number;
  indexed_count: number;
  duplicate_count: number;
  rejected_count: number;
  items: UploadFileResult[];
}

export interface UploadProgressEvent {
  file_index: number;
  total_files: number;
  file_name: string;
  stage:
    | "queued"
    | "validating"
    | "parsing"
    | "chunking"
    | "embedding"
    | "storing"
    | "done"
    | "rejected";
  stage_label: string;
  file_progress: number;
  overall_progress: number;
  detail?: string;
}

export interface SourceChunk {
  citation_id: string;
  content: string;
  chunk_index: number;
  document_id: string;
  document_filename: string;
  domain: CorpusDomain;
  page_number?: number | null;
  section_title?: string | null;
  semantic_score?: number | null;
  lexical_score?: number | null;
  fusion_score?: number | null;
  rerank_score?: number | null;
}

export interface AnswerTelemetry {
  latency_ms: number;
  prompt_tokens: number;
  completion_tokens: number;
  total_tokens: number;
  estimated_cost_usd: number;
  semantic_candidates: number;
  lexical_candidates: number;
  fused_candidates: number;
  reranked_candidates: number;
  citation_valid: boolean;
}

export interface ChatResponse {
  answer: string;
  domain?: CorpusDomain | null;
  grounded: boolean;
  citations: string[];
  sources: SourceChunk[];
  follow_up_questions: string[];
  telemetry: AnswerTelemetry;
  session_id: string;
}

export interface ObservabilitySummary {
  total_requests: number;
  grounded_rate: number;
  citation_valid_rate: number;
  p50_latency_ms: number;
  p95_latency_ms: number;
  average_cost_usd: number;
  latest_updated_at?: string | null;
}

export interface DomainMetric {
  domain: CorpusDomain;
  requests: number;
  p50_latency_ms: number;
  p95_latency_ms: number;
  average_cost_usd: number;
  grounded_rate: number;
}

export interface ObservabilityResponse {
  summary: ObservabilitySummary;
  by_domain: DomainMetric[];
}

export interface Anomaly {
  trace_id: string;
  domain: CorpusDomain | null;
  created_at: string;
  metric: string;
  value: number;
  z_score: number;
  baseline_mean: number;
  baseline_std: number;
}

export interface AnomalyResponse {
  threshold: number;
  sample_size: number;
  anomalies: Anomaly[];
}

export interface FeedbackRequest {
  question: string;
  answer: string;
  rating: -1 | 0 | 1;
  session_id?: string | null;
  domain?: CorpusDomain | null;
  comment?: string | null;
  citations?: string[];
}

export interface FeedbackAck {
  id: string;
  created_at: string;
}

export interface FeedbackDomainBucket {
  total: number;
  positive: number;
  negative: number;
  neutral: number;
}

export interface FeedbackSummary {
  total: number;
  positive: number;
  negative: number;
  neutral: number;
  positive_rate: number;
  negative_rate: number;
  by_domain: Record<string, FeedbackDomainBucket>;
}
