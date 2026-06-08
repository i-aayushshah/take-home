export default function GlassCard({ children, className = "", hover = true }) {
  const hoverClass = hover ? "glass-card" : "glass-panel p-4 sm:p-6";
  return <div className={`${hoverClass} ${className}`}>{children}</div>;
}
