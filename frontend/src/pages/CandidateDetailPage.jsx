import { useCallback, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { useQueryClient } from "@tanstack/react-query";
import AISummaryPanel from "../components/AISummaryPanel";
import ApplicationDecisionPanel from "../components/ApplicationDecisionPanel";
import InternalNotesPanel from "../components/InternalNotesPanel";
import ResumePanel from "../components/ResumePanel";
import ScoringForm from "../components/ScoringForm";
import WorkExperienceTimeline from "../components/WorkExperienceTimeline";
import GlassCard from "../components/layout/GlassCard";
import AvatarInitials from "../components/ui/AvatarInitials";
import ConfirmDialog from "../components/ui/ConfirmDialog";
import EmptyState from "../components/ui/EmptyState";
import GlassButton from "../components/ui/GlassButton";
import SectionHeader from "../components/ui/SectionHeader";
import StatusPill from "../components/ui/StatusPill";
import Spinner from "../components/ui/Spinner";
import { deleteCandidate } from "../api/candidates";
import { useCandidate } from "../hooks/useCandidate";
import { useCandidateStream } from "../hooks/useCandidateStream";
import useAuthStore from "../store/authStore";

function formatCategory(category) {
  return category.replace(/_/g, " ");
}

function ScoreIcon() {
  return (
    <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8} d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
    </svg>
  );
}

function ProfileIcon() {
  return (
    <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
    </svg>
  );
}

function BioIcon() {
  return (
    <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
    </svg>
  );
}

function ExperienceIcon() {
  return (
    <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
    </svg>
  );
}

export default function CandidateDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const user = useAuthStore((state) => state.user);
  const { data: candidate, isLoading, isError, error } = useCandidate(id);
  const isAdmin = user?.role === "admin";
  const [deleteOpen, setDeleteOpen] = useState(false);
  const [deleting, setDeleting] = useState(false);

  const handleLiveScore = useCallback(() => {
    queryClient.invalidateQueries({ queryKey: ["candidate", id] });
  }, [id, queryClient]);

  useCandidateStream(id, handleLiveScore);

  async function handleDelete() {
    setDeleting(true);
    try {
      await deleteCandidate(id);
      navigate("/candidates");
    } finally {
      setDeleting(false);
      setDeleteOpen(false);
    }
  }

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center gap-4 py-24">
        <Spinner />
        <p className="text-sm text-white/50">Loading candidate profile…</p>
      </div>
    );
  }

  if (isError || !candidate) {
    return (
      <GlassCard hover={false}>
        <EmptyState
          title="Candidate not found"
          description={error?.response?.data?.detail || "This profile may have been removed or is unavailable."}
        />
        <div className="pb-6 text-center">
          <Link to="/candidates" className="back-link">
            ← Back to candidates
          </Link>
        </div>
      </GlassCard>
    );
  }

  const averageScore =
    candidate.scores?.length > 0
      ? (candidate.scores.reduce((sum, item) => sum + item.score, 0) / candidate.scores.length).toFixed(1)
      : null;

  return (
    <div className="space-y-6">
      <div className="page-header">
        <Link to="/candidates" className="back-link">
          ← Back to candidates
        </Link>

        <div className="mt-4 flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-between">
          <div className="flex min-w-0 items-center gap-4">
            <AvatarInitials name={candidate.name} size="lg" />
            <div className="min-w-0">
              <div className="flex flex-wrap items-center gap-3">
                <h1 className="truncate text-2xl font-extrabold tracking-tight text-white sm:text-3xl">
                  {candidate.name}
                </h1>
                <StatusPill status={candidate.status} />
              </div>
              <p className="mt-1 truncate text-sm text-white/55">{candidate.email}</p>
              <p className="mt-2 text-sm font-semibold text-white/80">{candidate.role_applied}</p>
            </div>
          </div>

          <div className="flex flex-wrap gap-2">
            {averageScore && (
              <span className="stat-badge">
                <ScoreIcon />
                Avg {averageScore}/5
              </span>
            )}
            <span className="stat-badge">
              {candidate.work_experience?.length || 0} roles
            </span>
            <span className="stat-badge">
              Applied {new Date(candidate.created_at).toLocaleDateString()}
            </span>
          </div>
        </div>
      </div>

      <div className="grid gap-6 xl:grid-cols-3">
        <div className="space-y-6 xl:col-span-2">
          <GlassCard hover={false}>
            <SectionHeader
              icon={<BioIcon />}
              title="About"
              description="Candidate summary and career narrative"
            />
            {candidate.description ? (
              <p className="profile-prose mt-6">{candidate.description}</p>
            ) : (
              <div className="mt-4">
                <EmptyState
                  title="No description provided"
                  description="This candidate has not added a personal summary yet."
                />
              </div>
            )}
          </GlassCard>

          <GlassCard hover={false}>
            <SectionHeader
              icon={<ExperienceIcon />}
              title="Work Experience"
              description={`${candidate.work_experience?.length || 0} position${candidate.work_experience?.length === 1 ? "" : "s"} on record`}
            />
            <div className="mt-6">
              <WorkExperienceTimeline experience={candidate.work_experience} />
            </div>
          </GlassCard>

          <ResumePanel
            candidateId={candidate.id}
            resumeFilename={candidate.resume_filename}
            isAdmin={isAdmin}
          />

          <GlassCard hover={false}>
            <SectionHeader
              icon={<ProfileIcon />}
              title="Skills"
              description="Technical and professional competencies"
            />
            <div className="mt-6 flex flex-wrap gap-2">
              {candidate.skills?.length ? (
                candidate.skills.map((skill) => (
                  <span key={skill} className="skill-chip">
                    {skill}
                  </span>
                ))
              ) : (
                <p className="text-sm text-white/45">No skills listed.</p>
              )}
            </div>
          </GlassCard>
        </div>

        <div className="xl:col-span-1">
          <div className="xl:sticky xl:top-24">
            <ScoringForm candidateId={candidate.id} />
          </div>
        </div>
      </div>

      <div className="grid gap-6 xl:grid-cols-2">
        <GlassCard hover={false}>
          <SectionHeader
            icon={<ScoreIcon />}
            title="Scores"
            description={isAdmin ? "All reviewer scores" : "Your submitted scores"}
          />

          {candidate.scores?.length ? (
            <ul className="mt-6 space-y-3">
              {candidate.scores.map((score) => (
                <li
                  key={score.id}
                  className="flex flex-col gap-3 rounded-xl border border-white/8 bg-white/[0.03] p-4 sm:flex-row sm:items-start sm:justify-between"
                >
                  <div className="min-w-0">
                    <p className="text-sm font-bold capitalize text-white">{formatCategory(score.category)}</p>
                    {score.note && <p className="mt-1.5 text-sm leading-relaxed text-white/55">{score.note}</p>}
                    {isAdmin && (
                      <p className="mt-2 text-xs text-white/35">Reviewer ID: {score.reviewer_id}</p>
                    )}
                  </div>
                  <div className="flex items-center gap-2 sm:flex-col sm:items-end">
                    <span className="inline-flex min-w-[3.5rem] items-center justify-center rounded-xl border border-accent-primary/35 bg-accent-primary/15 px-3 py-1.5 text-base font-extrabold text-accent-glow">
                      {score.score}
                    </span>
                    <span className="text-xs font-medium text-white/40">out of 5</span>
                  </div>
                </li>
              ))}
            </ul>
          ) : (
            <div className="mt-4">
              <EmptyState
                title="No scores yet"
                description="Use the scoring form to add your first assessment."
              />
            </div>
          )}
        </GlassCard>

        <AISummaryPanel candidateId={candidate.id} existingSummary={candidate.ai_summary} />
      </div>

      {isAdmin && (
        <>
          <ApplicationDecisionPanel
            candidateId={candidate.id}
            currentStatus={candidate.status}
            rejectionReason={candidate.rejection_reason}
          />
          <InternalNotesPanel candidateId={candidate.id} initialNotes={candidate.internal_notes} />
          <div className="flex justify-end">
            <GlassButton variant="ghost" onClick={() => setDeleteOpen(true)} className="!border-red-400/30 !text-red-200">
              Remove Candidate
            </GlassButton>
          </div>
        </>
      )}

      <ConfirmDialog
        open={deleteOpen}
        title="Remove candidate?"
        description="This soft-deletes the application from the active pipeline. The record is retained for audit purposes."
        confirmLabel="Remove"
        variant="danger"
        onConfirm={handleDelete}
        onCancel={() => setDeleteOpen(false)}
        loading={deleting}
      />
    </div>
  );
}
