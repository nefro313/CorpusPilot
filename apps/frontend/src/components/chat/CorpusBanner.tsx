import type { CorpusDomain } from "../../types";
import { DOMAIN_ICONS, domainLabel } from "./domain";

export function CorpusBanner({ domain }: { domain: CorpusDomain }) {
  const Icon = DOMAIN_ICONS[domain];

  return (
    <div
      className="corpus-banner"
      data-domain={domain}
      role="status"
      aria-label={`Active corpus: ${domainLabel(domain)}`}
    >
      <span className="corpus-banner-pulse" aria-hidden />
      <span className="corpus-banner-icon">
        <Icon size={18} />
      </span>
      <span className="corpus-banner-text">
        <span className="corpus-banner-kicker">Current Domain</span>
        <strong>{domainLabel(domain)}</strong>
      </span>
      <span className="corpus-banner-divider" aria-hidden />
      <span className="corpus-banner-meta">Hybrid · Citations enforced</span>
    </div>
  );
}
