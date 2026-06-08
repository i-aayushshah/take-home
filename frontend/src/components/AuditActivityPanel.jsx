import GlassCard from "./layout/GlassCard";
import SectionHeader from "./ui/SectionHeader";
import Spinner from "./ui/Spinner";
import { useAuditEvents } from "../hooks/useAuditEvents";

const ACTION_LABELS = {
  status_changed: "Status changed",
  notes_updated: "Notes updated",
  soft_deleted: "Removed from pipeline",
  resume_uploaded: "Resume uploaded",
  profile_updated: "Profile updated",
  candidate_created: "Candidate created",
  application_submitted: "Application submitted",
  interview_scheduled: "Interview scheduled",
  interview_updated: "Interview updated",
  interview_cancelled: "Interview cancelled",
};

function formatPayload(action, payload) {
  if (action === "status_changed") {
    const auto = payload.auto ? " (auto)" : "";
    return `${payload.from} → ${payload.to}${auto}`;
  }
  if (action === "resume_uploaded") return payload.filename;
  if (action === "interview_scheduled" || action === "interview_updated") {
    return `${payload.interview_type} · ${new Date(payload.scheduled_at).toLocaleString()}`;
  }
  if (action === "application_submitted" || action === "candidate_created") {
    return payload.role_applied;
  }
  return null;
}

export default function AuditActivityPanel({ candidateId }) {
  const { data, isLoading, isError } = useAuditEvents(candidateId);

  return (
    <GlassCard hover={false}>
      <SectionHeader
        title="Activity"
        description="Audit trail of changes to this application"
      />

      {isLoading && (
        <div className="mt-6 flex justify-center py-6">
          <Spinner />
        </div>
      )}

      {isError && <p className="mt-4 text-sm text-accent-danger">Failed to load activity.</p>}

      {!isLoading && !isError && (
        <ul className="mt-6 space-y-3">
          {data?.items?.length ? (
            data.items.map((event) => {
              const detail = formatPayload(event.action, event.payload);
              return (
                <li
                  key={event.id}
                  className="rounded-xl border border-white/8 bg-white/[0.03] px-4 py-3"
                >
                  <div className="flex flex-wrap items-baseline justify-between gap-2">
                    <p className="text-sm font-semibold text-white">
                      {ACTION_LABELS[event.action] || event.action}
                    </p>
                    <time className="text-xs text-white/40">
                      {new Date(event.created_at).toLocaleString()}
                    </time>
                  </div>
                  {detail && <p className="mt-1 text-sm text-white/55">{detail}</p>}
                  {event.actor_id && (
                    <p className="mt-1 text-xs text-white/35">Actor: {event.actor_id.slice(0, 8)}…</p>
                  )}
                </li>
              );
            })
          ) : (
            <p className="text-sm text-white/50">No activity recorded yet.</p>
          )}
        </ul>
      )}
    </GlassCard>
  );
}
