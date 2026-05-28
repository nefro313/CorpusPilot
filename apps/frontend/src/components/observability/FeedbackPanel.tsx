import { useFeedbackSummary } from "../../hooks/queries";

function pct(rate: number): string {
  return `${(rate * 100).toFixed(0)}%`;
}

export function FeedbackPanel() {
  const query = useFeedbackSummary();

  if (query.isLoading) return <div className="telemetry-card empty">Loading feedback…</div>;
  if (query.isError) {
    return (
      <div className="telemetry-card empty">
        Couldn't load feedback ({(query.error as Error).message}).
      </div>
    );
  }
  const data = query.data!;

  return (
    <div className="telemetry-card">
      <div className="telemetry-card-head">
        <h3>User feedback</h3>
        <span className="telemetry-card-meta">{data.total} ratings</span>
      </div>
      {data.total === 0 ? (
        <div className="telemetry-card-empty">
          No feedback yet. Click 👍 / 👎 below an answer to start the loop.
        </div>
      ) : (
        <>
          <div className="feedback-aggregate">
            <div className="feedback-bucket positive">
              <strong>{pct(data.positive_rate)}</strong>
              <span>helpful ({data.positive})</span>
            </div>
            <div className="feedback-bucket negative">
              <strong>{pct(data.negative_rate)}</strong>
              <span>off ({data.negative})</span>
            </div>
            <div className="feedback-bucket neutral">
              <strong>{data.neutral}</strong>
              <span>neutral</span>
            </div>
          </div>
          {Object.keys(data.by_domain).length > 0 ? (
            <table className="anomaly-table">
              <thead>
                <tr>
                  <th>Domain</th>
                  <th>Total</th>
                  <th>👍</th>
                  <th>👎</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(data.by_domain).map(([domain, bucket]) => (
                  <tr key={domain}>
                    <td>{domain}</td>
                    <td>{bucket.total}</td>
                    <td>{bucket.positive}</td>
                    <td>{bucket.negative}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : null}
        </>
      )}
    </div>
  );
}
