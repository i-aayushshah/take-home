/** Strip markdown artifacts from stored AI summaries for display. */
export function normalizeSummary(text) {
  if (!text) return "";
  let cleaned = text.trim();
  cleaned = cleaned.replace(/\*\*(.+?)\*\*/g, "$1");
  cleaned = cleaned.replace(/__(.+?)__/g, "$1");
  cleaned = cleaned.replace(/(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)/g, "$1");
  cleaned = cleaned.replace(/^#{1,6}\s+/gm, "");
  cleaned = cleaned.replace(/^[-*]\s+/gm, "");
  cleaned = cleaned.replace(/^Hiring Brief:\s*.+?\s*(?:\n|$)/gim, "");
  cleaned = cleaned.replace(/\n{3,}/g, "\n\n");
  return cleaned.trim();
}

/** Split summary into display paragraphs. */
export function summaryParagraphs(text) {
  return normalizeSummary(text)
    .split(/\n{2,}|\n/)
    .map((part) => part.trim())
    .filter(Boolean);
}
