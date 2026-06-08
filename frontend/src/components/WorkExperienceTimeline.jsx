import EmptyState from "./ui/EmptyState";

function BriefcaseIcon() {
  return (
    <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={1.8}
        d="M20 7H4a2 2 0 00-2 2v10a2 2 0 002 2h16a2 2 0 002-2V9a2 2 0 00-2-2zM16 7V5a2 2 0 00-2-2h-4a2 2 0 00-2 2v2"
      />
    </svg>
  );
}

export default function WorkExperienceTimeline({ experience = [] }) {
  if (!experience.length) {
    return (
      <EmptyState
        title="No work history"
        description="This candidate has not added employment details yet."
        icon={<BriefcaseIcon />}
      />
    );
  }

  return (
    <ol className="relative space-y-0">
      {experience.map((entry, index) => (
        <li key={`${entry.company}-${entry.title}-${index}`} className="experience-item">
          <div className="experience-marker" aria-hidden="true">
            <span className="experience-dot" />
          </div>

          <div className="experience-content">
            <div className="flex flex-col gap-1 sm:flex-row sm:items-start sm:justify-between">
              <div className="min-w-0">
                <h3 className="text-base font-bold text-white">{entry.title}</h3>
                <p className="text-sm font-semibold text-accent-glow/90">{entry.company}</p>
              </div>
              <p className="shrink-0 text-xs font-medium text-white/45 sm:text-right">
                {entry.start}
                {entry.end ? ` – ${entry.end}` : " – Present"}
              </p>
            </div>
            {entry.summary && (
              <p className="mt-3 text-sm leading-relaxed text-white/65">{entry.summary}</p>
            )}
          </div>
        </li>
      ))}
    </ol>
  );
}
