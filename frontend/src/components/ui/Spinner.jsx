export default function Spinner({ size = "md", className = "" }) {
  const sizeClass = size === "sm" ? "h-4 w-4 border-2" : "h-5 w-5 border-2";
  return (
    <span
      className={`inline-block animate-spin rounded-full border-white/30 border-t-white ${sizeClass} ${className}`}
      aria-hidden="true"
    />
  );
}
