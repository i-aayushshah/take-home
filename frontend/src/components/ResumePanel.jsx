import { useRef, useState } from "react";
import GlassCard from "./layout/GlassCard";
import GlassButton from "./ui/GlassButton";
import SectionHeader from "./ui/SectionHeader";
import ParseResumeModal from "./ParseResumeModal";
import { downloadResume } from "../api/candidates";
import { useUploadResume } from "../hooks/useUploadResume";

export default function ResumePanel({ candidateId, resumeFilename, isAdmin }) {
  const inputRef = useRef(null);
  const [parseOpen, setParseOpen] = useState(false);
  const { mutate, isPending, isError, error } = useUploadResume(candidateId);

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

  const isPdf = resumeFilename?.toLowerCase().endsWith(".pdf");

  return (
    <>
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
              <div className="flex flex-col gap-2 sm:flex-row">
                <GlassButton variant="ghost" onClick={handleDownload} className="w-full sm:w-auto">
                  Download
                </GlassButton>
                {isAdmin && isPdf && (
                  <GlassButton variant="ghost" onClick={() => setParseOpen(true)} className="w-full sm:w-auto">
                    Parse with AI
                  </GlassButton>
                )}
              </div>
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
        </div>
      </GlassCard>

      {isAdmin && (
        <ParseResumeModal open={parseOpen} onClose={() => setParseOpen(false)} candidateId={candidateId} />
      )}
    </>
  );
}
