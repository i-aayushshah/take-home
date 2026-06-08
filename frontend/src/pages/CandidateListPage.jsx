import GlassCard from "../components/layout/GlassCard";

export default function CandidateListPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white sm:text-3xl">Candidates</h1>
        <p className="mt-2 max-w-2xl text-sm text-white/60 sm:text-base">
          Review applications, submit scores, and generate AI summaries from one workspace.
        </p>
      </div>
      <GlassCard>
        <p className="text-sm text-white/70 sm:text-base">
          Candidate list, filters, and detail views arrive in Phase 5.
        </p>
      </GlassCard>
    </div>
  );
}
