import { useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { resendVerificationRequest } from "../api/auth";
import Logo from "../components/brand/Logo";
import GlassButton from "../components/ui/GlassButton";
import GlassInput from "../components/ui/GlassInput";
import { toast } from "../store/toastStore";

export default function CheckEmailPage() {
  const [searchParams] = useSearchParams();
  const [email, setEmail] = useState(searchParams.get("email") || "");
  const [loading, setLoading] = useState(false);

  async function handleResend() {
    if (!email.trim()) return;
    setLoading(true);
    try {
      const data = await resendVerificationRequest(email.trim().toLowerCase());
      toast(data.message || "Verification email sent.");
    } catch (err) {
      toast(err.response?.data?.detail || "Could not resend verification email.", "error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="login-page relative min-h-screen px-4 py-10">
      <div className="login-grid pointer-events-none absolute inset-0" />
      <div className="relative mx-auto w-full max-w-md">
        <div className="text-center">
          <Logo size="md" className="justify-center" />
        </div>
        <div className="login-card mt-8 p-8 text-center">
          <p className="text-xl font-bold text-accent-success">Check your email</p>
          <p className="mt-3 text-sm leading-relaxed text-white/70">
            We sent a verification link to your inbox. Click it to activate your reviewer account,
            then sign in.
          </p>

          <div className="mt-6 space-y-4 text-left">
            <GlassInput
              id="resend-email"
              label="Email"
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              placeholder="reviewer@techkraft.com"
              required
            />
            <GlassButton onClick={handleResend} loading={loading} className="w-full">
              Resend verification email
            </GlassButton>
          </div>

          <p className="mt-6 text-sm text-white/45">
            Verified already?{" "}
            <Link to="/login" className="font-semibold text-accent-glow hover:text-white">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
