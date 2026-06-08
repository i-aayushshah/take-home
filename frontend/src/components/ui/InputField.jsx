export default function InputField({ label, htmlFor, children, error, hint }) {
  return (
    <div className="space-y-1.5">
      {label && (
        <div className="flex items-baseline justify-between gap-2">
          <label htmlFor={htmlFor} className="block text-sm font-semibold text-white/80">
            {label}
          </label>
          {hint && <span className="text-xs text-white/40">{hint}</span>}
        </div>
      )}
      {children}
      {error && <p className="text-xs text-accent-danger">{error}</p>}
    </div>
  );
}
