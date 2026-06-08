import { useState } from "react";
import { Link, NavLink, Outlet } from "react-router-dom";
import useAuthStore from "../../store/authStore";
import Logo from "../brand/Logo";
import GlassButton from "../ui/GlassButton";

const navLinkClass = ({ isActive }) =>
  `block rounded-xl px-4 py-3 text-sm font-semibold transition ${
    isActive
      ? "bg-accent-primary/30 text-white border border-accent-primary/40"
      : "text-white/70 hover:bg-white/10 hover:text-white"
  }`;

export default function AppShell() {
  const [menuOpen, setMenuOpen] = useState(false);
  const user = useAuthStore((state) => state.user);
  const logout = useAuthStore((state) => state.logout);
  const isAdmin = user?.role === "admin";

  return (
    <div className="relative min-h-screen">
      <div className="orb top-20 left-10 h-40 w-40 bg-accent-primary" />
      <div className="orb orb-delayed bottom-20 right-10 h-52 w-52 bg-accent-glow" />

      <div className="flex min-h-screen">
        <aside
          className={`glass-panel fixed inset-y-0 left-0 z-40 w-72 transform p-4 transition-transform duration-300 lg:static lg:translate-x-0 ${
            menuOpen ? "translate-x-0" : "-translate-x-full"
          }`}
        >
          <div className="mb-8 px-2 pt-2">
            <Link to="/candidates">
              <Logo size="sm" />
            </Link>
          </div>
          <nav className="space-y-2">
            <NavLink to="/candidates" className={navLinkClass} onClick={() => setMenuOpen(false)}>
              Candidates
            </NavLink>
          </nav>
        </aside>

        {menuOpen && (
          <button
            type="button"
            className="fixed inset-0 z-30 bg-black/40 lg:hidden"
            onClick={() => setMenuOpen(false)}
            aria-label="Close menu"
          />
        )}

        <div className="flex min-h-screen flex-1 flex-col">
          <header className="glass-panel sticky top-0 z-20 m-3 mb-0 flex items-center justify-between gap-4 rounded-2xl px-4 py-3 sm:px-6">
            <div className="flex items-center gap-3">
              <button
                type="button"
                className="glass-button-ghost px-3 py-2 lg:hidden"
                onClick={() => setMenuOpen((open) => !open)}
                aria-label="Toggle menu"
              >
                <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              </button>
              <div>
                <p className="text-sm font-semibold text-white sm:text-base">{user?.email}</p>
                <p className="text-xs text-white/50">Signed in</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <span
                className={`rounded-full px-3 py-1 text-xs font-bold uppercase tracking-wide ${
                  isAdmin
                    ? "bg-accent-primary/30 text-accent-glow border border-accent-primary/50"
                    : "bg-white/10 text-white/70 border border-white/10"
                }`}
              >
                {user?.role}
              </span>
              <GlassButton variant="ghost" onClick={logout} className="!w-auto text-sm">
                Logout
              </GlassButton>
            </div>
          </header>

          <main className="mx-auto w-full max-w-7xl flex-1 p-4 sm:p-6">
            <Outlet />
          </main>
        </div>
      </div>
    </div>
  );
}
