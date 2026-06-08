export default function Logo({ size = "md", showText = true, className = "" }) {
  const boxSize = size === "lg" ? "h-14 w-14" : size === "sm" ? "h-9 w-9" : "h-11 w-11";
  const textSize = size === "lg" ? "text-2xl" : size === "sm" ? "text-base" : "text-xl";

  return (
    <div className={`flex items-center gap-3 ${className}`}>
      <div
        className={`${boxSize} relative flex shrink-0 items-center justify-center rounded-2xl border border-white/20 bg-gradient-to-br from-accent-primary to-accent-glow shadow-lg shadow-accent-primary/30`}
      >
        <svg viewBox="0 0 32 32" className="h-[55%] w-[55%]" fill="none" aria-hidden="true">
          <path
            d="M8 22V10l8 6 8-6v12"
            stroke="white"
            strokeWidth="2.2"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
          <circle cx="16" cy="16" r="13" stroke="white" strokeOpacity="0.35" strokeWidth="1.2" />
        </svg>
      </div>
      {showText && (
        <div>
          <p className={`${textSize} font-bold leading-tight text-white`}>TechKraft</p>
          <p className="text-xs font-medium uppercase tracking-[0.2em] text-white/50">Recruit</p>
        </div>
      )}
    </div>
  );
}
