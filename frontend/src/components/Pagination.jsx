import GlassButton from "./ui/GlassButton";

export default function Pagination({ offset, limit, total, onPageChange }) {
  const currentPage = Math.floor(offset / limit) + 1;
  const totalPages = Math.max(1, Math.ceil(total / limit));
  const canPrev = offset > 0;
  const canNext = offset + limit < total;
  const rangeStart = total === 0 ? 0 : offset + 1;
  const rangeEnd = Math.min(offset + limit, total);

  return (
    <div className="glass-panel flex flex-col gap-4 p-4 sm:flex-row sm:items-center sm:justify-between sm:p-5">
      <div>
        <p className="text-sm font-semibold text-white">
          Page {currentPage} of {totalPages}
        </p>
        <p className="mt-1 text-xs text-white/50">
          Showing {rangeStart}–{rangeEnd} of {total} candidates
        </p>
      </div>

      <div className="flex w-full gap-2 sm:w-auto">
        <GlassButton
          variant="ghost"
          disabled={!canPrev}
          onClick={() => onPageChange(Math.max(0, offset - limit))}
          className="flex-1 sm:flex-none"
        >
          ← Previous
        </GlassButton>
        <span className="hidden items-center rounded-xl border border-white/10 bg-white/5 px-4 text-sm font-semibold text-white/70 sm:inline-flex">
          {currentPage}
        </span>
        <GlassButton
          variant="ghost"
          disabled={!canNext}
          onClick={() => onPageChange(offset + limit)}
          className="flex-1 sm:flex-none"
        >
          Next →
        </GlassButton>
      </div>
    </div>
  );
}
