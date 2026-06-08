import { useState } from "react";

const STEPS = [
  {
    status: "new",
    label: "New",
    detail: "Application received — awaiting reviewer scores.",
    tone: "pipeline-new",
  },
  {
    status: "reviewed",
    label: "Reviewed",
    detail: "Auto-set when the first score is submitted.",
    tone: "pipeline-reviewed",
  },
  {
    status: "hired",
    label: "Hired",
    detail: "Admin decision — offer extended.",
    tone: "pipeline-hired",
  },
  {
    status: "rejected",
    label: "Rejected",
    detail: "Admin decision — requires a documented reason.",
    tone: "pipeline-rejected",
  },
];

export default function HiringPipelineInfo() {
  const [expanded, setExpanded] = useState(false);

  return (
    <section className="surface-panel">
      <div className="flex items-center justify-between gap-3 border-b border-white/8 px-4 py-3 sm:px-5">
        <div>
          <h2 className="text-sm font-bold text-white">Hiring pipeline</h2>
          <p className="mt-0.5 text-xs text-white/50">Four stages from application to final decision</p>
        </div>
        <button
          type="button"
          className="pipeline-expand-btn lg:hidden"
          onClick={() => setExpanded((open) => !open)}
          aria-expanded={expanded}
        >
          {expanded ? "Hide" : "Details"}
        </button>
      </div>

      <div className="pipeline-stepper px-4 py-4 sm:px-5 sm:py-5">
        {STEPS.map((step, index) => (
          <div key={step.status} className="pipeline-step">
            {index > 0 && <div className="pipeline-connector" aria-hidden="true" />}
            <div className={`pipeline-node ${step.tone}`}>
              <span className="pipeline-index">{index + 1}</span>
            </div>
            <div className="pipeline-copy">
              <p className="pipeline-label">{step.label}</p>
              <p className={`pipeline-detail ${expanded ? "block" : "hidden lg:block"}`}>{step.detail}</p>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
