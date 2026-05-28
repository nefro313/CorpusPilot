import { useAnomalies } from "../../hooks/queries";
import type { Anomaly } from "../../types";

const METRIC_LABEL: Record<string, string> = {
  latency_ms: "Latency",
  total_cost_usd: "Cost",
};

function formatValue(metric: string, value: number): string {
  if (metric === "latency_ms") return `${Math.round(value)} ms`;
  if (metric === "total_cost_usd") return `$${value.toFixed(4)}`;
  return value.toFixed(3);
}

export function AnomaliesPanel() {
  const query = useAnomalies(2.5);

  if (query.isLoading) {
    return <div className="telemetry-card empty">Computing anomalies…</div>;
  }
  if (query.isError) {
    return (
      <div className="telemetry-card empty">
        Couldn't load anomalies ({(query.error as Error).message}).
      </div>
    );
  }

  const { threshold, sample_size, anomalies } = query.data!;

  return (
    <div className="telemetry-card">
      <div className="telemetry-card-head">
        <h3>Anomalies</h3>
        <span className="telemetry-card-meta">
          z ≥ {threshold} · {sample_size} samples
        </span>
      </div>
      {anomalies.length === 0 ? (
        <div className="telemetry-card-empty">No outliers in the recent window.</div>
      ) : (
        <table className="anomaly-table">
          <thead>
            <tr>
              <th>Metric</th>
              <th>Domain</th>
              <th>Value</th>
              <th>z-score</th>
              <th>Baseline</th>
              <th>When</th>
            </tr>
          </thead>
          <tbody>
            {anomalies.slice(0, 10).map((a: Anomaly) => (
              <tr key={`${a.trace_id}-${a.metric}`}>
                <td>{METRIC_LABEL[a.metric] ?? a.metric}</td>
                <td>{a.domain ?? "—"}</td>
                <td>{formatValue(a.metric, a.value)}</td>
                <td className={a.z_score > 0 ? "z-pos" : "z-neg"}>{a.z_score.toFixed(2)}</td>
                <td>
                  {formatValue(a.metric, a.baseline_mean)} ± {formatValue(a.metric, a.baseline_std)}
                </td>
                <td>{new Date(a.created_at).toLocaleTimeString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
