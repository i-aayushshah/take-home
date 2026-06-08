import { useMemo } from "react";
import { Link, Navigate } from "react-router-dom";
import useAuthStore from "../store/authStore";
import GlassCard from "../components/layout/GlassCard";
import PageHeader from "../components/ui/PageHeader";
import Spinner from "../components/ui/Spinner";
import { useInterviewsCalendar } from "../hooks/useInterviews";

function weekRange() {
  const now = new Date();
  const start = new Date(now);
  start.setHours(0, 0, 0, 0);
  const day = start.getDay();
  const diff = day === 0 ? -6 : 1 - day;
  start.setDate(start.getDate() + diff);
  const end = new Date(start);
  end.setDate(end.getDate() + 13);
  end.setHours(23, 59, 59, 999);
  return { start: start.toISOString(), end: end.toISOString() };
}

function groupByDay(items) {
  return items.reduce((acc, item) => {
    const key = new Date(item.scheduled_at).toLocaleDateString(undefined, {
      weekday: "long",
      month: "short",
      day: "numeric",
    });
    if (!acc[key]) acc[key] = [];
    acc[key].push(item);
    return acc;
  }, {});
}

export default function InterviewsPage() {
  const isAdmin = useAuthStore((state) => state.user?.role === "admin");
  const range = useMemo(() => weekRange(), []);

  if (!isAdmin) {
    return <Navigate to="/candidates" replace />;
  }
  const { data, isLoading, isError } = useInterviewsCalendar(range.start, range.end);

  const grouped = useMemo(() => groupByDay(data?.items || []), [data]);

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Scheduling"
        title="Interview calendar"
        description="Upcoming interviews for the next two weeks."
      />

      {isLoading && (
        <div className="flex justify-center py-16">
          <Spinner />
        </div>
      )}

      {isError && (
        <GlassCard hover={false}>
          <p className="text-sm text-accent-danger">Failed to load interviews.</p>
        </GlassCard>
      )}

      {!isLoading && !isError && (
        <div className="space-y-4">
          {Object.keys(grouped).length === 0 ? (
            <GlassCard hover={false}>
              <p className="text-sm text-white/55">No interviews scheduled in this period.</p>
            </GlassCard>
          ) : (
            Object.entries(grouped).map(([day, items]) => (
              <GlassCard key={day} hover={false}>
                <h2 className="text-sm font-bold uppercase tracking-wide text-white/45">{day}</h2>
                <ul className="mt-4 space-y-3">
                  {items.map((item) => (
                    <li
                      key={item.id}
                      className="flex flex-col gap-2 rounded-xl border border-white/8 bg-white/[0.03] p-4 sm:flex-row sm:items-center sm:justify-between"
                    >
                      <div>
                        <p className="text-sm font-bold text-white">
                          {new Date(item.scheduled_at).toLocaleTimeString([], {
                            hour: "2-digit",
                            minute: "2-digit",
                          })}{" "}
                          · <span className="capitalize">{item.interview_type.replace("_", " ")}</span>
                        </p>
                        {item.location_or_link && (
                          <p className="mt-1 text-xs text-white/50">{item.location_or_link}</p>
                        )}
                      </div>
                      <Link
                        to={`/candidates/${item.candidate_id}`}
                        className="text-sm font-semibold text-accent-glow hover:text-white"
                      >
                        View candidate →
                      </Link>
                    </li>
                  ))}
                </ul>
              </GlassCard>
            ))
          )}
        </div>
      )}
    </div>
  );
}
