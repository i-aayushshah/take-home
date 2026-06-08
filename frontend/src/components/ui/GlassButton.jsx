import Spinner from "./Spinner";

export default function GlassButton({
  children,
  type = "button",
  variant = "primary",
  loading = false,
  disabled = false,
  className = "",
  onClick,
}) {
  const baseClass = variant === "ghost" ? "glass-button-ghost" : "glass-button";
  const gradientClass =
    variant === "primary" ? "bg-gradient-to-r from-accent-primary to-indigo-500 hover:from-indigo-500 hover:to-accent-primary" : "";
  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled || loading}
      className={`${baseClass} ${gradientClass} w-full sm:w-auto ${className}`}
    >
      {loading && <Spinner size="sm" />}
      {children}
    </button>
  );
}
