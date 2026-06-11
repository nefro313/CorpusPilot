import type { ReactNode } from "react";

import { Check, Coins, Timer, Warning } from "../icons";
import type { AnswerTelemetry } from "../../types";

interface PillProps {
  icon: ReactNode;
  label: string;
  value: string;
  tone?: "positive" | "negative";
}

function Pill({ icon, label, value, tone }: PillProps) {
  return (
    <div className={`telemetry-pill${tone ? ` ${tone}` : ""}`}>
      <span className="telemetry-pill-icon">{icon}</span>
      <strong>{label}</strong>
      <span className="telemetry-pill-value">{value}</span>
    </div>
  );
}

export function TelemetryStrip({
  telemetry,
  grounded,
}: {
  telemetry: AnswerTelemetry;
  grounded: boolean;
}) {
  return (
    <div className="telemetry-row">
      <Pill
        icon={grounded ? <Check size={14} /> : <Warning size={14} />}
        label="Grounded"
        value={grounded ? "Yes" : "No"}
        tone={grounded ? "positive" : "negative"}
      />
      <Pill icon={<Timer size={14} />} label="Latency" value={`${Math.round(telemetry.latency_ms)} ms`} />
      <Pill
        icon={<Coins size={14} />}
        label="Cost"
        value={`$${telemetry.estimated_cost_usd.toFixed(4)}`}
      />
    </div>
  );
}
