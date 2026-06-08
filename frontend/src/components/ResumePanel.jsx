import { useRef } from "react";
import GlassCard from "./layout/GlassCard";
import GlassButton from "./ui/GlassButton";
import SectionHeader from "./ui/SectionHeader";
import { downloadResume } from "../api/candidates";
import { useUploadResume } from "../hooks/useUploadResume";

export default function ResumePanel({ candidateId, resumeFilename, isAdmin }) {
  const inputRef = useRef(null);
  const { mutate, isPending, isError, error, isSuccess } = useUploadResume(candidateId);

  function handleFileChange(event) {
    const file = event.target.files?.[0];
    if (file) mutate(file);
    event.target.value = "";
  }

  async function handleDownload() {
    const response = await downloadResume(candidateId);
    const url = window.URL.createObjectURL(response.data);
    const link = document.createElement("a");
    link.href = url;
    link.download = resumeFilename || "resume.pdf";
    link.click();
    window.URL.revokeObjectURL(url);
  }

  return (
    <GlassCard hover={false}>
      <SectionHeader
        title="Resume"
        description={isAdmin ? "Upload PDF, DOC, or DOCX (max 5 MB)." : "Download the candidate resume."}
      />

      <div className="mt-6 space-y-4">
        {resumeFilename ? (
          <div className="flex flex-col gap-3 rounded-xl border border-white/10 bg-white/[0.04] p-4 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p className="text-sm font-semibold text-white">{resumeFilename}</p>
              <p className="mt-1 text-xs text-white/45">Stored securely for this application</p>
            </div>
            <GlassButton variant="ghost" onClick={handleDownload} className="w-full sm:w-auto">
              Download
            </GlassButton>
          </div>
        ) : (
          <p className="text-sm text-white/50">No resume uploaded yet.</p>
        )}

        {isAdmin && (
          <>
            <input
              ref={inputRef}
              type="file"
              accept=".pdf,.doc,.docx"
              className="hidden"
              onChange={handleFileChange}
            />
            <GlassButton
              variant="ghost"
              onClick={() => inputRef.current?.click()}
              loading={isPending}
              className="w-full sm:w-auto"
            >
              {resumeFilename ? "Replace Resume" : "Upload Resume"}
            </GlassButton>
          </>
        )}

        {isError && (
          <p className="text-sm text-accent-danger">{error?.response?.data?.detail || "Upload failed."}</p>
        )}
        {isSuccess && <p className="text-sm text-accent-success">Resume uploaded.</p>}
      </div>
    </GlassCard>
  );
}
