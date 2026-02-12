import { Link } from 'react-router-dom';
import { ThemeToggle } from './ThemeToggle';

export function PageHeader({ title, subtitle, showQuit = true, showBack = false, backTo = '/' }) {
  return (
    <header className="flex items-center justify-between mb-6">
      <div>
        {showBack && (
          <Link
            to={backTo}
            className="text-[var(--color-text-muted)] hover:text-[var(--color-text)] text-sm font-medium mb-1 inline-block"
          >
            ← Back
          </Link>
        )}
        {title && <h1 className="text-xl font-bold text-[var(--color-text)]">{title}</h1>}
        {subtitle && <p className="text-sm text-[var(--color-text-muted)] mt-0.5">{subtitle}</p>}
      </div>
      <div className="flex items-center gap-2">
        <ThemeToggle />
        {showQuit && (
          <Link
            to="/"
            className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg bg-[var(--color-accent)] text-[var(--color-text)] font-semibold border border-[var(--color-primary)]/20 hover:bg-[var(--color-accent-hover)] transition"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /></svg>
            Quit
          </Link>
        )}
      </div>
    </header>
  );
}
