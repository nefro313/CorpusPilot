import { useEffect, useState } from "react";
import { GitHub } from "./icons";

const REPO = "nefro313/CorpusPilot";
const REPO_URL = "https://github.com/nefro313/CorpusPilot";

function formatStars(n: number): string {
  if (n >= 1000) return `${(n / 1000).toFixed(1)}k`;
  return String(n);
}

export function GitHubStarButton() {
  const [stars, setStars] = useState<number | null>(null);

  useEffect(() => {
    fetch(`https://api.github.com/repos/${REPO}`)
      .then((r) => r.json())
      .then((data) => {
        if (typeof data.stargazers_count === "number") {
          setStars(data.stargazers_count);
        }
      })
      .catch(() => {});
  }, []);

  return (
    <a
      href={REPO_URL}
      target="_blank"
      rel="noreferrer"
      className="github-star-btn"
      aria-label="View source on GitHub"
    >
      <GitHub size={16} />
      <span className="github-star-label">Star</span>
      {stars !== null && (
        <span className="github-star-count">{formatStars(stars)}</span>
      )}
    </a>
  );
}
