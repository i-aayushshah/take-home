import { useState } from "react";
import EditInterviewModal from "./EditInterviewModal";
import GlassCard from "./layout/GlassCard";
import GlassButton from "./ui/GlassButton";
import InputField from "./ui/InputField";
import SectionHeader from "./ui/SectionHeader";
import Spinner from "./ui/Spinner";
import { useCancelInterview, useCandidateInterviews, useScheduleInterview } from "../hooks/useInterviews";
import { useTeam } from "../hooks/useTeam";

const TYPE_OPTIONS = [
  { value: "video", label: "Video call" },
  { value: "in_person", label: "In person" },
  { value: "phone", label: "Phone" },
];

function toLocalInputValue(date) {
  const pad = (n) => String(n).padStart(2, "0");
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
}

export default function InterviewSchedulePanel({ candidateId }) {
  const { data, isLoading } = useCandidateInterviews(candidateId);
  const { data: team } = useTeam();
  const { mutate: schedule, isPending, isError, error } = useScheduleInterview(candidateId);
  const { mutate: cancel, isPending: cancelling } = useCancelInterview(candidateId);

  const [editingInterview, setEditingInterview] = useState(null);
  const defaultWhen = toLocalInputValue(new Date(Date.now() + 86400000));
  const [reviewerId, setReviewerId] = useState("");
  const [scheduledAt, setScheduledAt] = useState(defaultWhen);
  const [interviewType, setInterviewType] = useState("video");
  const [locationOrLink, setLocationOrLink] = useState("");
  const [notes, setNotes] = useState("");

  function handleSchedule(event) {
    event.preventDefault();
    schedule(
      {
        reviewer_id: reviewerId,
        scheduled_at: new Date(scheduledAt).toISOString(),
        interview_type: interviewType,
        location_or_link: locationOrLink.trim() || null,
        notes: notes.trim() || null,
      },
      {
        onSuccess: () => {
          setLocationOrLink("");
          setNotes("");
        },
      }
    );
  }

  return (
    <>
      <GlassCard hover={false}>
        <SectionHeader
          title="Interviews"
          description="Schedule, edit, and manage interview sessions"
        />

        {isLoading ? (
          <div className="mt-6 flex justify-center py-4">
            <Spinner />
          </div>
        ) : (
          <ul className="mt-6 space-y-3">
            {data?.items?.length ? (
              data.items.map((item) => (
                <li
                  key={item.id}
                  className="flex flex-col gap-3 rounded-xl border border-white/8 bg-white/[0.03] p-4 sm:flex-row sm:items-center sm:justify-between"
                >
                  <div>
                    <p className="text-sm font-bold capitalize text-white">{item.interview_type.replace("_", " ")}</p>
                    <p className="mt-1 text-sm text-white/60">{new Date(item.scheduled_at).toLocaleString()}</p>
                    {item.location_or_link && (
                      <p className="mt-1 text-xs text-white/45">{item.location_or_link}</p>
                    )}
                  </div>
                  <div className="flex flex-col gap-2 sm:flex-row">
                    <GlassButton
                      variant="ghost"
                      onClick={() => setEditingInterview(item)}
                      className="w-full sm:w-auto"
                    >
                      Edit
                    </GlassButton>
                    <GlassButton
                      variant="ghost"
                      onClick={() => cancel(item.id)}
                      loading={cancelling}
                      className="w-full sm:w-auto !text-red-200"
                    >
                      Cancel
                    </GlassButton>
                  </div>
                </li>
              ))
            ) : (
              <p className="text-sm text-white/50">No interviews scheduled.</p>
            )}
          </ul>
        )}

        <form onSubmit={handleSchedule} className="mt-6 space-y-4 border-t border-white/8 pt-6">
          <p className="text-sm font-semibold text-white">Schedule interview</p>

          <InputField label="Interviewer" htmlFor="interviewer">
            <div className="field">
              <select
                id="interviewer"
                value={reviewerId}
                onChange={(e) => setReviewerId(e.target.value)}
                required
                className="field-input px-4"
              >
                <option value="" className="bg-surface-800">
                  Select reviewer…
                </option>
                {team?.items?.map((member) => (
                  <option key={member.id} value={member.id} className="bg-surface-800">
                    {member.email} ({member.role})
                  </option>
                ))}
              </select>
            </div>
          </InputField>

          <div className="grid gap-4 sm:grid-cols-2">
            <InputField label="Date & time" htmlFor="scheduled-at">
              <div className="field">
                <input
                  id="scheduled-at"
                  type="datetime-local"
                  value={scheduledAt}
                  onChange={(e) => setScheduledAt(e.target.value)}
                  required
                  className="field-input px-4"
                />
              </div>
            </InputField>

            <InputField label="Type" htmlFor="interview-type">
              <div className="field">
                <select
                  id="interview-type"
                  value={interviewType}
                  onChange={(e) => setInterviewType(e.target.value)}
                  className="field-input px-4"
                >
                  {TYPE_OPTIONS.map((opt) => (
                    <option key={opt.value} value={opt.value} className="bg-surface-800">
                      {opt.label}
                    </option>
                  ))}
                </select>
              </div>
            </InputField>
          </div>

          <InputField label="Location or meeting link" htmlFor="location">
            <div className="field">
              <input
                id="location"
                value={locationOrLink}
                onChange={(e) => setLocationOrLink(e.target.value)}
                placeholder="Zoom link or office room"
                className="field-input px-4"
              />
            </div>
          </InputField>

          <InputField label="Notes" htmlFor="interview-notes">
            <div className="field !h-auto min-h-[4rem] items-start py-2">
              <textarea
                id="interview-notes"
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                rows={2}
                className="field-input min-h-[3rem] resize-y px-4 py-2"
              />
            </div>
          </InputField>

          {isError && (
            <p className="text-sm text-accent-danger">{error?.response?.data?.detail || "Failed to schedule."}</p>
          )}

          <GlassButton type="submit" loading={isPending} className="w-full sm:w-auto">
            Schedule
          </GlassButton>
        </form>
      </GlassCard>

      <EditInterviewModal
        open={Boolean(editingInterview)}
        onClose={() => setEditingInterview(null)}
        candidateId={candidateId}
        interview={editingInterview}
      />
    </>
  );
}
