export default function AvatarInitials({ name, size = "md", className = "" }) {
  const initials = name
    .split(" ")
    .map((part) => part[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();

  const sizeClass =
    size === "lg" ? "h-16 w-16 text-xl" : size === "sm" ? "h-9 w-9 text-xs" : "h-12 w-12 text-sm";

  return (
    <div
      className={`avatar-ring flex shrink-0 items-center justify-center rounded-2xl bg-gradient-to-br from-accent-primary/80 to-indigo-600/80 font-bold text-white shadow-lg shadow-accent-primary/20 ${sizeClass} ${className}`}
      aria-hidden="true"
    >
      {initials}
    </div>
  );
}
