import { useState } from "react";
import { Link, NavLink, Outlet } from "react-router-dom";
import useAuthStore from "../../store/authStore";
import Logo from "../brand/Logo";
import AvatarInitials from "../ui/AvatarInitials";
import GlassButton from "../ui/GlassButton";

const navLinkClass = ({ isActive }) =>
  `flex items-center gap-3 rounded-xl px-4 py-3 text-sm font-semibold transition ${
    isActive
      ? "border border-accent-primary/40 bg-accent-primary/25 text-white shadow-lg shadow-accent-primary/10"
      : "text-white/65 hover:border hover:border-white/10 hover:bg-white/8 hover:text-white"
  }`;

function CandidatesIcon() {
  return (
    <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={1.8}
        d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z"
      />
    </svg>
  );
}

export default function AppShell() {
  const [menuOpen, setMenuOpen] = useState(false);
  const user = useAuthStore((state) => state.user);
  const logout = useAuthStore((state) => state.logout);
  const isAdmin = user?.role === "admin";
  const displayName = user?.email?.split("@")[0] || "User";

  return (
    <div className="app-shell-bg relative min-h-screen">
      <div className="orb top-16 left-6 h-44 w-44 bg-accent-primary opacity-25" />
      <div className="orb orb-delayed bottom-16 right-6 h-56 w-56 bg-accent-glow opacity-20" />

      <div className="flex min-h-screen">
        <aside
          className={`glass-panel fixed inset-y-0 left-0 z-40 flex w-[min(18rem,88vw)] flex-col p-4 transition-transform duration-300 lg:static lg:translate-x-0 ${
            menuOpen ? "translate-x-0" : "-translate-x-full"
          }`}
        >
          <div className="mb-8 px-1 pt-1">
            <Link to="/candidates" onClick={() => setMenuOpen(false)}>
              <Logo size="sm" />
            </Link>
          </div>

          <nav className="space-y-2">
            <NavLink to="/candidates" className={navLinkClass} onClick={() => setMenuOpen(false)}>
              <CandidatesIcon />
              Candidates
            </NavLink>
          </nav>

          <div className="mt-auto rounded-2xl border border-white/10 bg-white/[0.04] p-4">
            <div className="flex items-center gap-3">
              <AvatarInitials name={displayName} size="sm" />
              <div className="min-w-0">
                <p className="truncate text-sm font-semibold text-white">{displayName}</p>
                <p className="truncate text-xs text-white/45">{user?.email}</p>
              </div>
            </div>
            <span
              className={`mt-3 inline-flex rounded-full px-2.5 py-1 text-[10px] font-bold uppercase tracking-wider ${
                isAdmin
                  ? "border border-accent-primary/40 bg-accent-primary/20 text-accent-glow"
                  : "border border-white/10 bg-white/5 text-white/60"
              }`}
            >
              {user?.role}
            </span>
          </div>
        </aside>

        {menuOpen && (
          <button
            type="button"
            className="fixed inset-0 z-30 bg-black/50 backdrop-blur-[2px] lg:hidden"
            onClick={() => setMenuOpen(false)}
            aria-label="Close menu"
          />
        )}

        <div className="flex min-h-screen min-w-0 flex-1 flex-col">
          <header className="glass-panel sticky top-0 z-20 mx-3 mt-3 flex items-center justify-between gap-3 rounded-2xl px-4 py-3 sm:mx-4 sm:px-5">
            <div className="flex min-w-0 items-center gap-3">
              <button
                type="button"
                className="glass-button-ghost !px-3 !py-2 lg:hidden"
                onClick={() => setMenuOpen((open) => !open)}
                aria-label="Toggle menu"
              >
                <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              </button>
              <div className="min-w-0 lg:hidden">
                <p className="truncate text-sm font-semibold text-white">{user?.email}</p>
                <p className="text-xs text-white/45">Recruitment workspace</p>
              </div>
              <div className="hidden lg:block">
                <p className="text-sm font-semibold text-white">Recruitment Dashboard</p>
                <p className="text-xs text-white/45">Review, score, and summarize candidates</p>
              </div>
            </div>

            <GlassButton variant="ghost" onClick={logout} className="shrink-0">
              Logout
            </GlassButton>
          </header>

          <main className="page-enter mx-auto w-full max-w-7xl flex-1 px-3 py-5 sm:px-5 sm:py-6 lg:px-6">
            <Outlet />
          </main>
        </div>
      </div>
    </div>
  );
}
