import { useState } from "react";
import GlassCard from "./layout/GlassCard";
import GlassButton from "./ui/GlassButton";
import InputField from "./ui/InputField";
import SectionHeader from "./ui/SectionHeader";
import { useSubmitScore } from "../hooks/useSubmitScore";

const CATEGORIES = [
  { value: "technical", label: "Technical" },
  { value: "communication", label: "Communication" },
  { value: "culture_fit", label: "Culture Fit" },
];

function FormIcon() {
  return (
    <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
    </svg>
  );
}

export default function ScoringForm({ candidateId }) {
  const [category, setCategory] = useState("technical");
  const [score, setScore] = useState(3);
  const [note, setNote] = useState("");
  const { mutate, isPending, isSuccess, isError, error, reset } = useSubmitScore(candidateId);

  function handleSubmit(event) {
    event.preventDefault();
    reset();
    mutate(
      { category, score, note: note.trim() || null },
      {
        onSuccess: () => {
          setNote("");
          setScore(3);
        },
      }
    );
  }

  return (
    <GlassCard hover={false}>
      <SectionHeader
        icon={<FormIcon />}
        title="Submit Score"
        description="Rate this candidate on a structured category."
      />

      <form onSubmit={handleSubmit} className="mt-6 space-y-5">
        <InputField label="Category" htmlFor="score-category">
          <div className="field">
            <select
              id="score-category"
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="field-input px-4"
            >
              {CATEGORIES.map((item) => (
                <option key={item.value} value={item.value} className="bg-surface-800">
                  {item.label}
                </option>
              ))}
            </select>
          </div>
        </InputField>

        <InputField label="Score" htmlFor="score-value">
          <div className="grid grid-cols-5 gap-2">
            {[1, 2, 3, 4, 5].map((value) => (
              <label
                key={value}
                className={`flex h-11 cursor-pointer items-center justify-center rounded-xl border text-sm font-bold transition ${
                  score === value
                    ? "border-accent-primary/60 bg-accent-primary/25 text-accent-glow shadow-lg shadow-accent-primary/15"
                    : "border-white/10 bg-white/5 text-white/60 hover:border-white/20 hover:bg-white/10"
                }`}
              >
                <input
                  type="radio"
                  name="score"
                  value={value}
                  checked={score === value}
                  onChange={() => setScore(value)}
                  className="sr-only"
                />
                {value}
              </label>
            ))}
          </div>
        </InputField>

        <InputField label="Note (optional)" htmlFor="score-note">
          <div className="field !h-auto min-h-[4.5rem] items-start py-2">
            <textarea
              id="score-note"
              value={note}
              onChange={(e) => setNote(e.target.value)}
              rows={3}
              placeholder="Add context for this score…"
              className="field-input min-h-[3.5rem] resize-y px-4 py-2"
            />
          </div>
        </InputField>

        {isError && (
          <div className="glass-error">
            {error?.response?.data?.detail || "Failed to submit score."}
          </div>
        )}
        {isSuccess && (
          <p className="rounded-xl border border-accent-success/30 bg-accent-success/10 px-4 py-3 text-sm text-accent-success">
            Score submitted successfully.
          </p>
        )}

        <GlassButton type="submit" loading={isPending} className="w-full">
          Submit Score
        </GlassButton>
      </form>
    </GlassCard>
  );
}
