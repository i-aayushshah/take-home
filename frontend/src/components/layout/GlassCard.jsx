export default function GlassCard({ children, className = "", hover = true }) {
  const hoverClass = hover ? "glass-card-interactive" : "glass-card";
  return <div className={`${hoverClass} ${className}`}>{children}</div>;
}
