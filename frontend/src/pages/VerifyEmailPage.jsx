import { useEffect, useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { verifyEmailRequest } from "../api/auth";
import Logo from "../components/brand/Logo";
import GlassButton from "../components/ui/GlassButton";
import Spinner from "../components/ui/Spinner";
import useAuthStore from "../store/authStore";
import { toast } from "../store/toastStore";

export default function VerifyEmailPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const login = useAuthStore((state) => state.login);
  const token = searchParams.get("token");
  const email = searchParams.get("email") || "";
  const [status, setStatus] = useState(token ? "loading" : "missing");
  const [error, setError] = useState("");

  useEffect(() => {
    if (!token) return undefined;

    let cancelled = false;
    verifyEmailRequest(token)
      .then((data) => {
        if (cancelled) return;
        login(data.access_token, email);
        toast("Email verified — welcome to TechKraft.");
        setStatus("success");
        navigate("/candidates", { replace: true });
      })
      .catch((err) => {
        if (cancelled) return;
        setStatus("error");
        setError(err.response?.data?.detail || "Verification failed. Request a new link.");
      });

    return () => {
      cancelled = true;
    };
  }, [token, login, navigate]);

  return (
    <div className="login-page relative min-h-screen px-4 py-10">
      <div className="login-grid pointer-events-none absolute inset-0" />
      <div className="relative mx-auto w-full max-w-md text-center">
        <Logo size="md" className="justify-center" />
        <div className="login-card mt-8 p-8">
          {status === "loading" && (
            <div className="flex flex-col items-center gap-4">
              <Spinner />
              <p className="text-sm font-semibold text-white">Verifying your email…</p>
            </div>
          )}

          {status === "missing" && (
            <>
              <p className="text-lg font-bold text-white">Missing verification link</p>
              <p className="mt-2 text-sm text-white/60">Open the link from your email or request a new one.</p>
              <GlassButton onClick={() => navigate("/register/check-email")} className="mt-6 w-full">
                Resend verification
              </GlassButton>
            </>
          )}

          {status === "error" && (
            <>
              <p className="text-lg font-bold text-accent-danger">Verification failed</p>
              <p className="mt-2 text-sm text-white/70">{error}</p>
              <GlassButton onClick={() => navigate("/register/check-email")} className="mt-6 w-full">
                Request new link
              </GlassButton>
            </>
          )}

          <p className="mt-6 text-sm text-white/45">
            <Link to="/login" className="font-semibold text-accent-glow hover:text-white">
              Back to sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
