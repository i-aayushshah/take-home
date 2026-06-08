import { useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";
import { loginRequest } from "../api/auth";
import Logo from "../components/brand/Logo";
import GlassButton from "../components/ui/GlassButton";
import GlassInput from "../components/ui/GlassInput";
import PasswordInput from "../components/ui/PasswordInput";
import useAuthStore from "../store/authStore";

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

const highlights = [
  "Score candidates across technical and culture dimensions",
  "AI-assisted summaries powered by GitHub Models",
  "Role-based access for reviewers and admins",
];

export default function LoginPage() {
  const navigate = useNavigate();
  const token = useAuthStore((state) => state.token);
  const login = useAuthStore((state) => state.login);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  if (token) {
    return <Navigate to="/candidates" replace />;
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setLoading(true);
    try {
      const data = await loginRequest(email, password);
      login(data.access_token, email);
      navigate("/candidates");
    } catch (err) {
      const message = err.response?.data?.detail || "Login failed. Check your credentials.";
      setError(typeof message === "string" ? message : "Login failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="login-page relative min-h-screen overflow-hidden">
      <div className="login-grid pointer-events-none absolute inset-0" />
      <div className="orb top-10 left-[10%] h-56 w-56 bg-accent-primary" />
      <div className="orb orb-delayed bottom-10 right-[8%] h-64 w-64 bg-accent-glow" />
      <div className="orb top-1/2 right-1/3 h-40 w-40 bg-accent-success opacity-20" />

      <div className="relative z-10 mx-auto flex min-h-screen w-full max-w-6xl flex-col items-center justify-center gap-8 p-4 sm:p-8 lg:flex-row lg:gap-12">
        <section className="w-full max-w-lg text-center lg:text-left">
          <Logo size="lg" className="justify-center lg:justify-start" />
          <h1 className="mt-8 text-3xl font-bold leading-tight text-white sm:text-4xl lg:text-5xl">
            Hire smarter with
            <span className="block bg-gradient-to-r from-accent-glow to-accent-success bg-clip-text text-transparent">
              candidate intelligence
            </span>
          </h1>
          <p className="mt-4 text-base leading-relaxed text-white/65 sm:text-lg">
            Internal recruitment dashboard for structured reviews, collaborative scoring, and
            AI-powered candidate insights.
          </p>
          <ul className="mt-8 hidden space-y-3 text-left sm:block">
            {highlights.map((item) => (
              <li key={item} className="flex items-start gap-3 text-sm text-white/75 sm:text-base">
                <span className="mt-1 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-accent-primary/25 text-accent-glow">
                  <svg className="h-3 w-3" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
                    <path
                      fillRule="evenodd"
                      d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                      clipRule="evenodd"
                    />
                  </svg>
                </span>
                {item}
              </li>
            ))}
          </ul>
        </section>

        <section className="login-card w-full max-w-md p-6 sm:p-8">
          <div className="mb-8">
            <h2 className="text-2xl font-bold text-white">Welcome back</h2>
            <p className="mt-2 text-sm text-white/55">Sign in to access your recruitment workspace</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <GlassInput
              id="email"
              label="Work email"
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              placeholder="name@techkraft.com"
              required
              autoComplete="email"
              icon={<EmailIcon />}
            />
            <PasswordInput
              id="password"
              label="Password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              placeholder="Enter your password"
              required
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
              Sign in to dashboard
            </GlassButton>
          </form>

          <div className="mt-6 rounded-xl border border-white/10 bg-white/5 px-4 py-3">
            <p className="text-xs font-semibold uppercase tracking-wider text-white/45">Demo access</p>
            <p className="mt-1 text-sm text-white/75">
              <span className="font-semibold text-white">admin@techkraft.com</span>
              <span className="text-white/40"> · </span>
              <span className="font-mono text-accent-glow">admin12345</span>
            </p>
          </div>
        </section>
      </div>
    </div>
  );
}
