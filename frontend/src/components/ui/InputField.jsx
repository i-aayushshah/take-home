export default function InputField({ label, htmlFor, children, error }) {
  return (
    <div className="space-y-1.5">
      {label && (
        <label htmlFor={htmlFor} className="block text-sm font-medium text-white/70">
          {label}
        </label>
      )}
      {children}
      {error && <p className="text-xs text-accent-danger">{error}</p>}
    </div>
  );
}
