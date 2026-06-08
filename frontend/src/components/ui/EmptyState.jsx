export default function EmptyState({ title, description, icon }) {
  return (
    <div className="empty-state">
      {icon && <div className="empty-state-icon">{icon}</div>}
      <h3 className="text-base font-semibold text-white">{title}</h3>
      {description && <p className="mt-2 max-w-sm text-sm text-white/55">{description}</p>}
    </div>
  );
}
