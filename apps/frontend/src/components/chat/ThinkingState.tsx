import { useEffect, useState } from "react";

// Cycled while the answer streams in. A blend of pipeline-flavoured steps
// (retrieve → rerank → reason) and a few playful beats so the wait reads as
// "thinking" rather than "stuck", à la Claude's shimmering status word.
const THINKING_WORDS = [
  "Summoning knowledge",
  "Retrieving evidence",
  "Connecting dots",
  "Reranking chunks",
  "Pondering",
  "Reasoning it out",
  "Brewing ideas",
  "Illuminating",
  "Cooking",
  "Scheming",
];

export function ThinkingState() {
  // Start somewhere random so back-to-back questions don't always open on the
  // same word.
  const [index, setIndex] = useState(() =>
    Math.floor(Math.random() * THINKING_WORDS.length)
  );

  useEffect(() => {
    const id = window.setInterval(() => {
      setIndex((i) => (i + 1) % THINKING_WORDS.length);
    }, 1900);
    return () => window.clearInterval(id);
  }, []);

  return (
    <div className="thinking-shell" role="status" aria-label="Generating answer">
      <span className="thinking-orb" aria-hidden />
      <span className="thinking-word-wrap" aria-hidden>
        <span key={index} className="thinking-word">
          {THINKING_WORDS[index]}
        </span>
      </span>
    </div>
  );
}

export function ThinkingTrail() {
  return (
    <span className="thinking-trail" aria-hidden>
      <span className="thinking-dot" />
      <span className="thinking-dot" />
      <span className="thinking-dot" />
    </span>
  );
}
