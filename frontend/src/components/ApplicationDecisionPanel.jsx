import { useEffect, useState } from "react";
import GlassCard from "./layout/GlassCard";
import GlassButton from "./ui/GlassButton";
import InputField from "./ui/InputField";
import SectionHeader from "./ui/SectionHeader";
import { useUpdateStatus } from "../hooks/useUpdateStatus";

const STATUS_OPTIONS = [
  { value: "new", label: "New" },
  { value: "reviewed", label: "Reviewed" },
  { value: "hired", label: "Hired" },
  { value: "rejected", label: "Rejected" },
];

export default function ApplicationDecisionPanel({ candidateId, currentStatus, rejectionReason }) {
  const [status, setStatus] = useState(currentStatus);
  const [reason, setReason] = useState(rejectionReason || "");
  const { mutate, isPending, isError, error, isSuccess } = useUpdateStatus(candidateId);

  useEffect(() => {
    setStatus(currentStatus);
    setReason(rejectionReason || "");
  }, [currentStatus, rejectionReason]);

  function handleSave() {
    mutate({
      status,
      rejection_reason: status === "rejected" ? reason.trim() : null,
    });
  }

  return (
    <GlassCard hover={false} className="border-emerald-400/15">
      <SectionHeader
        title="Hiring Decision"
        description="Admin-only — move candidates through the pipeline or reject with reason."
      />

      <div className="mt-6 space-y-4">
        <InputField label="Status" htmlFor="hiring-status">
          <div className="field">
            <select
              id="hiring-status"
              value={status}
              onChange={(e) => setStatus(e.target.value)}
              className="field-input px-4"
            >
              {STATUS_OPTIONS.map((option) => (
                <option key={option.value} value={option.value} className="bg-surface-800">
                  {option.label}
                </option>
              ))}
            </select>
          </div>
        </InputField>

        {status === "rejected" && (
          <InputField label="Rejection reason" htmlFor="rejection-reason">
            <div className="field !h-auto min-h-[5rem] items-start py-2">
              <textarea
                id="rejection-reason"
                value={reason}
                onChange={(e) => setReason(e.target.value)}
                rows={3}
                placeholder="Explain why this application was rejected (min 10 characters)…"
                className="field-input min-h-[4rem] resize-y px-4 py-2"
              />
            </div>
          </InputField>
        )}

        {currentStatus === "rejected" && rejectionReason && (
          <div className="rounded-xl border border-red-400/20 bg-red-500/10 p-4">
            <p className="text-xs font-bold uppercase tracking-wide text-red-200/80">Current rejection reason</p>
            <p className="mt-2 text-sm leading-relaxed text-red-100">{rejectionReason}</p>
          </div>
        )}

        {isError && (
          <p className="text-sm text-accent-danger">{error?.response?.data?.detail || "Failed to update status."}</p>
        )}
        {isSuccess && <p className="text-sm text-accent-success">Hiring decision saved.</p>}

        <GlassButton onClick={handleSave} loading={isPending} className="w-full sm:w-auto">
          Save Decision
        </GlassButton>
      </div>
    </GlassCard>
  );
}
