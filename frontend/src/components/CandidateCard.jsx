import { Link } from "react-router-dom";
import AvatarInitials from "./ui/AvatarInitials";
import StatusPill from "./ui/StatusPill";

export default function CandidateCard({ candidate }) {
  const topSkills = candidate.skills?.slice(0, 3) || [];
  const extraSkills = Math.max(0, (candidate.skills?.length || 0) - 3);

  return (
    <Link to={`/candidates/${candidate.id}`} className="glass-card-interactive group block h-full">
      <div className="flex items-start gap-4">
        <AvatarInitials name={candidate.name} size="md" />
        <div className="min-w-0 flex-1">
          <div className="flex items-start justify-between gap-2">
            <div className="min-w-0">
              <h3 className="truncate text-base font-bold text-white transition-colors group-hover:text-accent-glow sm:text-lg">
                {candidate.name}
              </h3>
              <p className="mt-0.5 truncate text-sm text-white/45">{candidate.email}</p>
            </div>
            <StatusPill status={candidate.status} />
          </div>

          <p className="mt-3 text-sm font-semibold text-white/90">{candidate.role_applied}</p>

          <div className="mt-3 flex flex-wrap items-center gap-2">
            {topSkills.map((skill) => (
              <span key={skill} className="skill-chip">
                {skill}
              </span>
            ))}
            {extraSkills > 0 && <span className="text-xs font-medium text-white/40">+{extraSkills} more</span>}
          </div>
        </div>
      </div>

      <div className="mt-5 flex items-center justify-between border-t border-white/8 pt-4 text-xs font-semibold text-accent-glow/80">
        <span>View profile</span>
        <svg
          className="h-4 w-4 transition-transform group-hover:translate-x-0.5"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          aria-hidden="true"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
        </svg>
      </div>
    </Link>
  );
}
