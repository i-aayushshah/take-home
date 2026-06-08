import { useRef, useState } from "react";
import { Link } from "react-router-dom";
import { submitApplication } from "../api/applications";
import Logo from "../components/brand/Logo";
import GlassButton from "../components/ui/GlassButton";
import { toast } from "../store/toastStore";

export default function ApplyPage() {
  const fileRef = useRef(null);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [roleApplied, setRoleApplied] = useState("");
  const [skills, setSkills] = useState("");
  const [description, setDescription] = useState("");
  const [resume, setResume] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(null);

  async function handleSubmit(event) {
    event.preventDefault();
    setLoading(true);
    setError("");

    const formData = new FormData();
    formData.append("name", name.trim());
    formData.append("email", email.trim().toLowerCase());
    formData.append("role_applied", roleApplied.trim());
    formData.append("skills", skills.trim());
    if (description.trim()) formData.append("description", description.trim());
    if (resume) formData.append("resume", resume);

    try {
      const result = await submitApplication(formData);
      setSuccess(result.message);
      toast(result.message || "Application submitted successfully.");
      setName("");
      setEmail("");
      setRoleApplied("");
      setSkills("");
      setDescription("");
      setResume(null);
      if (fileRef.current) fileRef.current.value = "";
    } catch (err) {
      const detail = err.response?.data?.detail;
      const message = typeof detail === "string" ? detail : "Unable to submit application. Please try again.";
      setError(message);
      toast(message, "error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="login-page relative min-h-screen px-4 py-10 sm:px-6">
      <div className="login-grid pointer-events-none absolute inset-0" />
      <div className="relative mx-auto w-full max-w-xl">
        <div className="mb-8 text-center">
          <Link to="/login">
            <Logo size="md" />
          </Link>
          <h1 className="mt-6 text-2xl font-extrabold text-white">Apply to TechKraft</h1>
          <p className="mt-2 text-sm text-white/55">
            Submit your application — no account required. Our team will review and follow up by email.
          </p>
        </div>

        <div className="login-card p-6 sm:p-8">
          {success ? (
            <div className="text-center">
              <p className="text-lg font-bold text-accent-success">Application received</p>
              <p className="mt-2 text-sm leading-relaxed text-white/70">{success}</p>
              <GlassButton onClick={() => setSuccess(null)} className="mt-6 w-full">
                Submit another
              </GlassButton>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid gap-4 sm:grid-cols-2">
                <label className="block space-y-1.5">
                  <span className="text-sm font-semibold text-white/80">Full name</span>
                  <input
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    required
                    className="glass-input"
                    placeholder="Jane Smith"
                  />
                </label>
                <label className="block space-y-1.5">
                  <span className="text-sm font-semibold text-white/80">Email</span>
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    className="glass-input"
                    placeholder="jane@company.com"
                  />
                </label>
              </div>

              <label className="block space-y-1.5">
                <span className="text-sm font-semibold text-white/80">Role</span>
                <input
                  value={roleApplied}
                  onChange={(e) => setRoleApplied(e.target.value)}
                  required
                  className="glass-input"
                  placeholder="Frontend Engineer"
                />
              </label>

              <label className="block space-y-1.5">
                <span className="text-sm font-semibold text-white/80">Skills (comma-separated)</span>
                <input
                  value={skills}
                  onChange={(e) => setSkills(e.target.value)}
                  required
                  className="glass-input"
                  placeholder="React, TypeScript, Node.js"
                />
              </label>

              <label className="block space-y-1.5">
                <span className="text-sm font-semibold text-white/80">About you (optional)</span>
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  rows={3}
                  className="glass-input min-h-[5rem] resize-y"
                  placeholder="Brief background…"
                />
              </label>

              <label className="block space-y-1.5">
                <span className="text-sm font-semibold text-white/80">Resume (optional, PDF/DOC)</span>
                <input
                  ref={fileRef}
                  type="file"
                  accept=".pdf,.doc,.docx"
                  onChange={(e) => setResume(e.target.files?.[0] || null)}
                  className="block w-full text-sm text-white/60 file:mr-4 file:rounded-lg file:border-0 file:bg-accent-primary/80 file:px-4 file:py-2 file:text-sm file:font-semibold file:text-white"
                />
              </label>

              {error && <p className="glass-error">{error}</p>}

              <GlassButton type="submit" loading={loading} className="w-full">
                Submit application
              </GlassButton>
            </form>
          )}

          <p className="mt-6 text-center text-sm text-white/45">
            Already on the team?{" "}
            <Link to="/login" className="font-semibold text-accent-glow hover:text-white">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
