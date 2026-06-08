import { useEffect, useMemo, useState } from "react";
import GlassCard from "./layout/GlassCard";
import GlassButton from "./ui/GlassButton";
import SectionHeader from "./ui/SectionHeader";
import Spinner from "./ui/Spinner";
import { useAISummary } from "../hooks/useAISummary";
import { normalizeSummary, summaryParagraphs } from "../utils/summaryText";

function AIIcon() {
  return (
    <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
    </svg>
  );
}

export default function AISummaryPanel({ candidateId, existingSummary }) {
  const [summary, setSummary] = useState(existingSummary || "");
  const { mutate, isPending, isError, error, reset } = useAISummary(candidateId);

  useEffect(() => {
    setSummary(existingSummary || "");
  }, [existingSummary]);

  const displaySummary = useMemo(() => normalizeSummary(summary), [summary]);
  const paragraphs = useMemo(() => summaryParagraphs(summary), [summary]);

  function handleGenerate() {
    reset();
    mutate(undefined, {
      onSuccess: (data) => setSummary(data.summary),
    });
  }

  return (
    <GlassCard hover={false}>
      <SectionHeader
        icon={<AIIcon />}
        title="AI Summary"
        description="Generate a concise hiring brief via GitHub AI."
        action={
          <GlassButton
            variant="ghost"
            onClick={handleGenerate}
            loading={isPending}
            disabled={isPending}
            className="w-full sm:w-auto"
          >
            Generate
          </GlassButton>
        }
      />

      <div className="mt-6">
        {isPending && (
          <div className="flex items-center gap-4 rounded-xl border border-white/10 bg-white/[0.04] p-5">
            <Spinner />
            <div>
              <p className="text-sm font-semibold text-white">Generating summary…</p>
              <p className="mt-1 text-xs text-white/50">This may take a few seconds via GitHub AI.</p>
            </div>
          </div>
        )}

        {isError && !isPending && (
          <div className="rounded-xl border border-red-400/30 bg-red-500/10 p-5">
            <p className="text-sm leading-relaxed text-red-100">
              {error?.response?.data?.detail || "Failed to generate summary. Check your GitHub token."}
            </p>
            <GlassButton variant="ghost" onClick={handleGenerate} className="mt-4 w-full sm:w-auto">
              Retry
            </GlassButton>
          </div>
        )}

        {!isPending && !isError && displaySummary && (
          <div className="ai-summary-prose rounded-xl border border-white/10 bg-white/[0.04] p-5">
            {paragraphs.map((paragraph, index) => (
              <p key={index} className={index > 0 ? "mt-4" : ""}>
                {paragraph}
              </p>
            ))}
          </div>
        )}

        {!isPending && !isError && !displaySummary && (
          <div className="rounded-xl border border-dashed border-white/15 bg-white/[0.02] px-5 py-8 text-center">
            <p className="text-sm font-medium text-white/55">No summary yet</p>
            <p className="mt-1 text-xs text-white/40">Click Generate to create an AI-powered hiring brief.</p>
          </div>
        )}
      </div>
    </GlassCard>
  );
}
