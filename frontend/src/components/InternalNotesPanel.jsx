import { useEffect, useState } from "react";
import GlassCard from "./layout/GlassCard";
import GlassButton from "./ui/GlassButton";
import InputField from "./ui/InputField";
import SectionHeader from "./ui/SectionHeader";
import { useUpdateNotes } from "../hooks/useUpdateNotes";

function NotesIcon() {
  return (
    <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
    </svg>
  );
}

export default function InternalNotesPanel({ candidateId, initialNotes }) {
  const [notes, setNotes] = useState(initialNotes || "");
  const { mutate, isPending, isSuccess, isError, error } = useUpdateNotes(candidateId);

  useEffect(() => {
    setNotes(initialNotes || "");
  }, [initialNotes]);

  function handleSave() {
    mutate(notes.trim() || null);
  }

  return (
    <GlassCard hover={false} className="border-amber-400/20">
      <SectionHeader
        icon={<NotesIcon />}
        title="Internal Notes"
        description="Admin-only — not visible to reviewers."
      />

      <div className="mt-6 space-y-4">
        <InputField label="Private notes" htmlFor="internal-notes">
          <div className="field !h-auto min-h-[6rem] items-start py-2">
            <textarea
              id="internal-notes"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              rows={4}
              placeholder="Private hiring notes, interview feedback, or next steps…"
              className="field-input min-h-[5rem] resize-y px-4 py-2"
            />
          </div>
        </InputField>

        {isError && (
          <div className="glass-error">
            {error?.response?.data?.detail || "Failed to save notes."}
          </div>
        )}
        {isSuccess && (
          <p className="rounded-xl border border-accent-success/30 bg-accent-success/10 px-4 py-3 text-sm text-accent-success">
            Notes saved.
          </p>
        )}

        <GlassButton onClick={handleSave} loading={isPending} className="w-full sm:w-auto">
          Save Notes
        </GlassButton>
      </div>
    </GlassCard>
  );
}
