import { useEffect, useRef, useState } from "react";
import DomainDropdown from "./DomainDropdown";
import { Check, Close, Doc, Upload, Warning } from "./icons";
import type {
  BatchUploadSummary,
  CorpusDomain,
  DomainProfile,
  UploadFileResult,
  UploadProgressEvent,
} from "../types";
import { getUserId } from "../hooks/useUserId";

interface Props {
  onUpload: () => void;
  selectedDomain: CorpusDomain;
  onDomainChange: (domain: CorpusDomain) => void;
}

const ACCEPTED_EXTENSIONS = [".txt", ".md", ".pdf", ".docx", ".pptx", ".xlsx", ".html", ".htm", ".csv"];
const MAX_FILE_BYTES = 15 * 1024 * 1024;

export default function DocumentUpload({ onUpload, selectedDomain, onDomainChange }: Props) {
  const [domains, setDomains] = useState<DomainProfile[]>([]);
  const [files, setFiles] = useState<File[]>([]);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState<{ text: string; type: "ok" | "err" } | null>(null);
  const [isDrag, setIsDrag] = useState(false);
  const [progress, setProgress] = useState<UploadProgressEvent | null>(null);
  const [results, setResults] = useState<UploadFileResult[]>([]);
  const [batchSummary, setBatchSummary] = useState<BatchUploadSummary | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const loadDomains = async () => {
      try {
        const res = await fetch("/api/documents/domains");
        if (!res.ok) return;
        const data: DomainProfile[] = await res.json();
        setDomains(data);
      } catch {
        /* ignore */
      }
    };
    loadDomains();
  }, []);

  const commitFiles = (incoming: FileList | File[]) => {
    const candidates = Array.from(incoming);
    const accepted: File[] = [];
    const skipped: string[] = [];
    for (const candidate of candidates) {
      const lower = candidate.name.toLowerCase();
      const extOk = ACCEPTED_EXTENSIONS.some((ext) => lower.endsWith(ext));
      if (!extOk) {
        skipped.push(`${candidate.name} (unsupported type)`);
        continue;
      }
      if (candidate.size === 0) {
        skipped.push(`${candidate.name} (empty file)`);
        continue;
      }
      if (candidate.size > MAX_FILE_BYTES) {
        skipped.push(`${candidate.name} (over 15 MB)`);
        continue;
      }
      accepted.push(candidate);
    }
    if (accepted.length) {
      setFiles((current) => dedupeFiles([...current, ...accepted]));
    }
    setBatchSummary(null);
    setResults([]);
    setProgress(null);
    if (skipped.length) {
      setMessage({
        text: `Skipped ${skipped.length} file(s): ${skipped.join(", ")}.`,
        type: "err",
      });
    } else if (accepted.length) {
      setMessage(null);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!files.length) return;

    setUploading(true);
    setMessage(null);
    setResults([]);
    setBatchSummary(null);
    setProgress({
      file_index: 0,
      total_files: files.length,
      file_name: files[0].name,
      stage: "queued",
      stage_label: "Queued",
      file_progress: 0,
      overall_progress: 0,
    });

    const formData = new FormData();
    formData.append("domain", selectedDomain);
    for (const file of files) formData.append("files", file);

    try {
      const res = await fetch("/api/documents/upload/stream", {
        method: "POST",
        headers: { "X-User-ID": getUserId() },
        body: formData,
      });
      if (!res.ok || !res.body) throw new Error("Upload failed");

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const packets = buffer.split("\n\n");
        buffer = packets.pop() || "";

        for (const packet of packets) {
          const eventMatch = packet.match(/^event: (.+)$/m);
          const dataMatch = packet.match(/^data: (.+)$/m);
          if (!eventMatch || !dataMatch) continue;

          const eventType = eventMatch[1];
          const data = JSON.parse(dataMatch[1]);

          if (eventType === "file_progress") {
            setProgress(data as UploadProgressEvent);
          }

          if (eventType === "file_result") {
            const result = data as UploadFileResult;
            setResults((current) => [...current, result]);
          }

          if (eventType === "batch_complete") {
            const summary = data as BatchUploadSummary;
            setBatchSummary(summary);
            setMessage({
              text: buildBatchMessage(summary, selectedDomain),
              type: summary.indexed_count > 0 || summary.duplicate_count > 0 ? "ok" : "err",
            });
            setFiles([]);
            if (inputRef.current) inputRef.current.value = "";
            onUpload();
          }

          if (eventType === "error") {
            throw new Error(data.message || "Upload failed");
          }
        }
      }
    } catch {
      setMessage({
        text: "Batch indexing failed. Check parsing support, file size, backend health, and API credentials.",
        type: "err",
      });
    } finally {
      setUploading(false);
    }
  };

  const activeDomain = domains.find((item) => item.value === selectedDomain);

  return (
    <div className="sidebar-stack">
      <section className="panel ingest-panel">
        <div className="panel-head">
          <span className="panel-kicker">Corpus Ingestion</span>
          <h2>Pick a domain profile before indexing.</h2>
        </div>

        <DomainDropdown
          domains={domains}
          value={selectedDomain}
          onChange={onDomainChange}
          disabled={uploading}
        />

        {activeDomain && (
          <div className="profile-card">
            <div className="profile-line">
              <span>Chunking</span>
              <strong>{activeDomain.chunking_strategy}</strong>
            </div>
            <div className="profile-line">
              <span>Retrieval</span>
              <strong>{activeDomain.retrieval_strategy}</strong>
            </div>
            <div className="profile-line">
              <span>Guardrail</span>
              <strong>Each file is checked from page one before full parsing starts.</strong>
            </div>
          </div>
        )}

        <form onSubmit={handleSubmit} className="upload-form">
          <label
            className={`upload-drop${isDrag ? " drag" : ""}${files.length ? " has-file" : ""}`}
            onDragOver={(e) => {
              e.preventDefault();
              setIsDrag(true);
            }}
            onDragLeave={() => setIsDrag(false)}
            onDrop={(e) => {
              e.preventDefault();
              setIsDrag(false);
              if (e.dataTransfer.files?.length) commitFiles(e.dataTransfer.files);
            }}
          >
            <input
              ref={inputRef}
              type="file"
              accept={ACCEPTED_EXTENSIONS.join(",")}
              multiple
              onChange={(e) => {
                if (e.target.files?.length) commitFiles(e.target.files);
                if (inputRef.current) inputRef.current.value = "";
              }}
              aria-label="Upload documents"
            />
            <span className="upload-badge">
              <Upload size={18} />
            </span>
            <div>
              <div className="upload-title">
                {files.length ? `${files.length} files ready for indexing` : "Drop files or browse"}
              </div>
              <div className="upload-subtitle">
                PDF, DOCX, PPTX, XLSX, HTML, TXT, MD, CSV up to 15 MB each. The first page is
                classified before indexing — files outside the five supported domains are rejected.
              </div>
            </div>
          </label>

          {files.length > 0 && (
            <div className="file-pill-list">
              {files.map((file) => (
                <div key={fileKey(file)} className="file-pill">
                  <Doc size={14} />
                  <span>{file.name}</span>
                  <button
                    type="button"
                    onClick={() => {
                      setFiles((current) => current.filter((item) => fileKey(item) !== fileKey(file)));
                    }}
                    aria-label={`Remove ${file.name}`}
                  >
                    <Close size={14} />
                  </button>
                </div>
              ))}
            </div>
          )}

          {progress && (
            <div className="progress-card" role="status" aria-live="polite">
              <div className="progress-top">
                <strong>{progress.stage_label}</strong>
                <span>{progress.overall_progress}%</span>
              </div>
              <div className="progress-meta">
                <span>{progress.file_name}</span>
                <span>
                  {progress.file_index + 1} / {progress.total_files}
                </span>
              </div>
              <div className="progress-bar">
                <div className="progress-fill" style={{ width: `${progress.overall_progress}%` }} />
              </div>
              {progress.detail ? <div className="progress-detail">{progress.detail}</div> : null}
            </div>
          )}

          <button type="submit" className="primary-button" disabled={!files.length || uploading}>
            {uploading ? "Indexing corpus..." : `Index ${prettyDomain(selectedDomain)} batch`}
          </button>
        </form>

        {message && (
          <div className={message.type === "ok" ? "status good" : "status bad"} role="status">
            {message.type === "ok" ? <Check size={14} /> : <Warning size={14} />}
            <span>{message.text}</span>
          </div>
        )}

        {results.length > 0 && (
          <div className="result-list">
            {results.map((result, index) => {
              const suggested = result.suggested_domain ?? null;
              const canSwitch =
                result.status === "rejected" &&
                !!suggested &&
                suggested !== selectedDomain &&
                !uploading;
              return (
                <div
                  key={`${result.filename}-${index}`}
                  className={`result-card ${result.status}`}
                >
                  <div className="result-top">
                    <span className={`result-badge ${result.status}`}>{result.status}</span>
                    <strong>{result.filename}</strong>
                  </div>
                  <p>{result.message}</p>
                  {result.rejection_reason ? (
                    <p className="result-detail">Why: {result.rejection_reason}</p>
                  ) : null}
                  {canSwitch && suggested ? (
                    <button
                      type="button"
                      className="link-button"
                      onClick={() => onDomainChange(suggested)}
                    >
                      Switch to {prettyDomain(suggested)} and re-upload
                    </button>
                  ) : null}
                </div>
              );
            })}
          </div>
        )}

        {batchSummary && batchSummary.rejected_count > 0 ? (
          <div className="empty-card compact">
            Rejected files were skipped instead of blocking the whole batch. Re-upload them after
            inspecting the message above.
          </div>
        ) : null}
      </section>
    </div>
  );
}

function buildBatchMessage(summary: BatchUploadSummary, domain: CorpusDomain) {
  if (summary.indexed_count === 0 && summary.duplicate_count === 0) {
    return `No ${prettyDomain(domain).toLowerCase()} files were indexed. Review the messages above.`;
  }
  const parts = [
    `${summary.indexed_count} indexed`,
    `${summary.duplicate_count} duplicates reused`,
  ];
  if (summary.rejected_count > 0) parts.push(`${summary.rejected_count} rejected during parsing`);
  return parts.join(" · ");
}

function dedupeFiles(files: File[]) {
  const seen = new Map<string, File>();
  for (const file of files) seen.set(fileKey(file), file);
  return Array.from(seen.values());
}

function fileKey(file: File) {
  return `${file.name}:${file.size}:${file.lastModified}`;
}

function prettyDomain(domain: CorpusDomain) {
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
