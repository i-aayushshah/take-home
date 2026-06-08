import { useState } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";
import { registerRequest } from "../api/auth";
import Logo from "../components/brand/Logo";
import GlassButton from "../components/ui/GlassButton";
import GlassInput from "../components/ui/GlassInput";
import PasswordInput from "../components/ui/PasswordInput";
import useAuthStore from "../store/authStore";
import { toast } from "../store/toastStore";

function EmailIcon() {
  return (
    <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={1.8}
        d="M21.75 6.75v10.5a2.25 2.25 0 01-2.25 2.25H4.5a2.25 2.25 0 01-2.25-2.25V6.75m19.5 0A2.25 2.25 0 0019.5 4.5h-15a2.25 2.25 0 00-2.25 2.25m19.5 0v.243a2.25 2.25 0 01-1.07 1.916l-7.5 4.615a2.25 2.25 0 01-2.36 0L3.32 8.91a2.25 2.25 0 01-1.07-1.916V6.75"
      />
    </svg>
  );
}

export default function RegisterPage() {
  const navigate = useNavigate();
  const token = useAuthStore((state) => state.token);
  const login = useAuthStore((state) => state.login);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  if (token) {
    return <Navigate to="/candidates" replace />;
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");

    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    if (password.length < 8) {
      setError("Password must be at least 8 characters.");
      return;
    }

    const normalizedEmail = email.trim().toLowerCase();
    setLoading(true);
    try {
      const data = await registerRequest(normalizedEmail, password);
      if (data.requires_verification) {
        toast(data.message || "Check your email to verify your account.");
        navigate(`/register/check-email?email=${encodeURIComponent(normalizedEmail)}`);
        return;
      }
      login(data.access_token, normalizedEmail);
      toast("Reviewer account created — welcome to TechKraft.");
      navigate("/candidates");
    } catch (err) {
      const message = err.response?.data?.detail || "Registration failed. Try a different email.";
      setError(typeof message === "string" ? message : "Registration failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="login-page relative min-h-screen overflow-hidden">
      <div className="login-grid pointer-events-none absolute inset-0" />
      <div className="orb top-10 left-[10%] h-56 w-56 bg-accent-primary" />
      <div className="orb orb-delayed bottom-10 right-[8%] h-64 w-64 bg-accent-glow" />

      <div className="relative z-10 mx-auto flex min-h-screen w-full max-w-6xl flex-col items-center justify-center gap-8 p-4 sm:p-8 lg:flex-row lg:gap-12">
        <section className="w-full max-w-lg text-center lg:text-left">
          <Logo size="lg" className="justify-center lg:justify-start" />
          <h1 className="mt-8 text-3xl font-bold leading-tight text-white sm:text-4xl">
            Join the review team
          </h1>
          <p className="mt-4 text-base leading-relaxed text-white/65 sm:text-lg">
            Create a reviewer account to score candidates, generate AI summaries, and collaborate
            on hiring decisions.
          </p>
          <p className="mt-6 rounded-xl border border-white/10 bg-white/[0.04] px-4 py-3 text-sm text-white/60">
            New accounts are always assigned the <strong className="text-white/80">reviewer</strong>{" "}
            role. Admin access is provisioned separately.
          </p>
        </section>

        <section className="login-card w-full max-w-md p-6 sm:p-8">
          <div className="mb-8">
            <h2 className="text-2xl font-bold text-white">Create account</h2>
            <p className="mt-2 text-sm text-white/55">Register as a TechKraft reviewer</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <GlassInput
              id="email"
              label="Work email"
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              placeholder="reviewer@techkraft.com"
              required
              autoComplete="email"
              icon={<EmailIcon />}
            />
            <PasswordInput
              id="password"
              label="Password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              placeholder="At least 8 characters"
              required
              autoComplete="new-password"
              minLength={8}
            />
            <PasswordInput
              id="confirmPassword"
              label="Confirm password"
              value={confirmPassword}
              onChange={(event) => setConfirmPassword(event.target.value)}
              placeholder="Re-enter your password"
              required
              autoComplete="new-password"
              minLength={8}
            />

            {error && (
              <div className="glass-error flex items-center gap-2">
                <svg className="h-4 w-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                {error}
              </div>
            )}

            <GlassButton type="submit" loading={loading} className="w-full !py-3.5">
              Create reviewer account
            </GlassButton>
          </form>

          <p className="mt-4 text-center text-sm text-white/50">
            Already have an account?{" "}
            <Link to="/login" className="font-semibold text-accent-glow hover:text-white">
              Sign in
            </Link>
          </p>
        </section>
      </div>
    </div>
  );
}
