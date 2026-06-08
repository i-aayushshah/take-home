const statusStyles = {
  new: "bg-blue-500/20 border-blue-400/30 text-blue-200",
  reviewed: "bg-amber-500/20 border-amber-400/30 text-amber-200",
  hired: "bg-emerald-500/20 border-emerald-400/30 text-emerald-200",
  rejected: "bg-red-500/20 border-red-400/30 text-red-200",
};

const statusDots = {
  new: "bg-blue-400",
  reviewed: "bg-amber-400",
  hired: "bg-emerald-400",
  rejected: "bg-red-400",
};

export default function StatusPill({ status }) {
  const style = statusStyles[status] || "bg-white/10 border-white/20 text-white/70";
  const dot = statusDots[status] || "bg-white/50";

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-[11px] font-bold uppercase tracking-wide ${style}`}
    >
      <span className={`h-1.5 w-1.5 rounded-full ${dot}`} />
      {status}
    </span>
  );
}
