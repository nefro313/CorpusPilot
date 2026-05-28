import { useState } from "react";

import { AnomaliesPanel } from "./AnomaliesPanel";
import { FeedbackPanel } from "./FeedbackPanel";

type Tab = "anomalies" | "feedback";

export function TelemetryTabs() {
  const [tab, setTab] = useState<Tab>("anomalies");
  return (
    <section className="telemetry-tabs">
      <div className="telemetry-tabs-head" role="tablist">
        <button
          type="button"
          role="tab"
          aria-selected={tab === "anomalies"}
          className={`telemetry-tab${tab === "anomalies" ? " active" : ""}`}
          onClick={() => setTab("anomalies")}
        >
          Anomalies
        </button>
        <button
          type="button"
          role="tab"
          aria-selected={tab === "feedback"}
          className={`telemetry-tab${tab === "feedback" ? " active" : ""}`}
          onClick={() => setTab("feedback")}
        >
          Feedback
        </button>
      </div>
      <div className="telemetry-tabs-body" role="tabpanel">
        {tab === "anomalies" ? <AnomaliesPanel /> : <FeedbackPanel />}
      </div>
    </section>
  );
}
