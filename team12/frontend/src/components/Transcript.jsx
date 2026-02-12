export function Transcript({ text, className = '' }) {
  if (!text) return null;
  return (
    <div className={`rounded-2xl bg-[var(--color-card)] shadow-md border border-[var(--color-border)] overflow-hidden ${className}`}>
      <div className="px-6 py-3 border-b border-[var(--color-border)] flex items-center justify-between">
        <h3 className="text-lg font-bold text-[var(--color-text)]">Listening Transcript</h3>
      </div>
      <p className="text-sm text-[var(--color-text-muted)] px-6 pt-2 underline">Follow the line</p>
      <div className="p-6 pt-2 text-[var(--color-text)] leading-relaxed whitespace-pre-wrap">
        {text}
      </div>
    </div>
  );
}
