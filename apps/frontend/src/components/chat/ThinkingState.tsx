export function ThinkingState() {
  return (
    <div className="thinking-shell" aria-live="polite">
      <div className="thinking-copy">
        <strong>Working through the corpus</strong>
        <span>Retrieving evidence, ranking chunks, and drafting a grounded answer.</span>
      </div>
      <div className="thinking-dots" aria-hidden>
        <span className="thinking-dot" />
        <span className="thinking-dot" />
        <span className="thinking-dot" />
      </div>
    </div>
  );
}

export function ThinkingTrail() {
  return (
    <div className="thinking-trail" aria-hidden>
      <span className="thinking-dot" />
      <span className="thinking-dot" />
      <span className="thinking-dot" />
    </div>
  );
}
