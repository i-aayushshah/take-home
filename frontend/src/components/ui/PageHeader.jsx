export default function PageHeader({ eyebrow, title, description, children }) {
  return (
    <div className="page-header">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
        <div className="min-w-0">
          {eyebrow && <p className="page-eyebrow">{eyebrow}</p>}
          <h1 className="page-title">{title}</h1>
          {description && <p className="page-description">{description}</p>}
        </div>
        {children && <div className="flex shrink-0 flex-wrap items-center gap-2">{children}</div>}
      </div>
    </div>
  );
}
