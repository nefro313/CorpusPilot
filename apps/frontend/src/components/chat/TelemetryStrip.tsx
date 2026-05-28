import type { ReactNode } from "react";

import { Coins, Radar, Timer } from "../icons";
import type { AnswerTelemetry } from "../../types";

interface PillProps {
  icon: ReactNode;
  label: string;
  value: string;
}

function Pill({ icon, label, value }: PillProps) {
  return (
    <div className="telemetry-pill">
      <span>{icon}</span>
      <strong>{label}</strong>
      <span>{value}</span>
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
      <Pill icon={<Radar size={14} />} label="Grounded" value={grounded ? "Yes" : "No"} />
      <Pill icon={<Timer size={14} />} label="Latency" value={`${Math.round(telemetry.latency_ms)} ms`} />
      <Pill
        icon={<Coins size={14} />}
        label="Cost"
        value={`$${telemetry.estimated_cost_usd.toFixed(4)}`}
      />
    </div>
  );
}
