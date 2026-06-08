import { useEffect, useState } from "react";
import Modal from "./ui/Modal";
import { useTeam } from "../hooks/useTeam";
import { useUpdateInterview } from "../hooks/useInterviews";

const TYPE_OPTIONS = [
  { value: "video", label: "Video call" },
  { value: "in_person", label: "In person" },
  { value: "phone", label: "Phone" },
];

function toLocalInputValue(isoString) {
  const date = new Date(isoString);
  const pad = (n) => String(n).padStart(2, "0");
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
}

export default function EditInterviewModal({ open, onClose, candidateId, interview }) {
  const { data: team } = useTeam(open);
  const { mutate, isPending, isError, error } = useUpdateInterview(candidateId);

  const [reviewerId, setReviewerId] = useState("");
  const [scheduledAt, setScheduledAt] = useState("");
  const [interviewType, setInterviewType] = useState("video");
  const [locationOrLink, setLocationOrLink] = useState("");
  const [notes, setNotes] = useState("");

  useEffect(() => {
    if (!interview) return;
    setReviewerId(interview.reviewer_id);
    setScheduledAt(toLocalInputValue(interview.scheduled_at));
    setInterviewType(interview.interview_type);
    setLocationOrLink(interview.location_or_link || "");
    setNotes(interview.notes || "");
  }, [interview]);

  function handleSubmit(event) {
    event.preventDefault();
    mutate(
      {
        interviewId: interview.id,
        payload: {
          reviewer_id: reviewerId,
          scheduled_at: new Date(scheduledAt).toISOString(),
          interview_type: interviewType,
          location_or_link: locationOrLink.trim() || null,
          notes: notes.trim() || null,
        },
      },
      { onSuccess: () => onClose() }
    );
  }

  if (!interview) return null;

  return (
    <Modal
      open={open}
      onClose={onClose}
      title="Edit interview"
      description="Update appointment details. The candidate will receive an updated email."
      size="lg"
      footer={
        <div className="modal-actions">
          <button type="button" className="modal-btn-secondary" onClick={onClose} disabled={isPending}>
            Cancel
          </button>
          <button type="submit" form="edit-interview-form" className="modal-btn-primary" disabled={isPending}>
            {isPending ? "Saving…" : "Save changes"}
          </button>
        </div>
      }
    >
      <form id="edit-interview-form" onSubmit={handleSubmit} className="modal-form space-y-4">
        <label className="modal-field">
          <span className="modal-label">Interviewer</span>
          <select
            value={reviewerId}
            onChange={(e) => setReviewerId(e.target.value)}
            required
            className="modal-input"
          >
            <option value="">Select reviewer…</option>
            {team?.items?.map((member) => (
              <option key={member.id} value={member.id}>
                {member.email} ({member.role})
              </option>
            ))}
          </select>
        </label>

        <div className="modal-field-grid">
          <label className="modal-field">
            <span className="modal-label">Date & time</span>
            <input
              type="datetime-local"
              value={scheduledAt}
              onChange={(e) => setScheduledAt(e.target.value)}
              required
              className="modal-input"
            />
          </label>
          <label className="modal-field">
            <span className="modal-label">Type</span>
            <select
              value={interviewType}
              onChange={(e) => setInterviewType(e.target.value)}
              className="modal-input"
            >
              {TYPE_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </label>
        </div>

        <label className="modal-field">
          <span className="modal-label">Location or meeting link</span>
          <input
            value={locationOrLink}
            onChange={(e) => setLocationOrLink(e.target.value)}
            placeholder="Zoom link or office room"
            className="modal-input"
          />
        </label>

        <label className="modal-field">
          <span className="modal-label">Notes</span>
          <textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            rows={3}
            className="modal-input modal-textarea"
          />
        </label>

        {isError && (
          <p className="modal-error">{error?.response?.data?.detail || "Failed to update interview."}</p>
        )}
      </form>
    </Modal>
  );
}
