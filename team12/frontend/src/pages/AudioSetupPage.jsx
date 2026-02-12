import { useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { ThemeToggle } from '../components/ThemeToggle';

export function AudioSetupPage() {
  const [searchParams] = useSearchParams();
  const mode = searchParams.get('mode') || 'practice';
  const [volume, setVolume] = useState(70);

  return (
    <div className="min-h-screen bg-[var(--color-surface)] flex flex-col">
      {/* Header: REAL 1, LISTENING / Audio Setup, Quit */}
      <header className="flex items-center justify-between px-6 py-4 border-b border-[var(--color-border)] bg-[var(--color-card)]">
        <div className="flex items-center gap-2 text-sm">
          <svg className="w-5 h-5 text-[var(--color-text-muted)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
          </svg>
          <span className="font-bold text-[var(--color-text)]">REAL 1</span>
          <span className="text-[var(--color-text-muted)]">LISTENING / Audio Setup</span>
        </div>
        <div className="flex items-center gap-2">
          <ThemeToggle />
          <Link
            to="/"
            className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg bg-[var(--color-accent)] text-[var(--color-text)] font-semibold border border-[var(--color-primary)]/20 hover:opacity-90"
          >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /></svg>
          Quit
        </Link>
        </div>
      </header>

      <main className="flex-1 flex flex-col items-center justify-center px-6 py-10">
        {/* Headphone illustration */}
        <div className="w-40 h-40 mb-8 flex items-center justify-center rounded-full bg-[var(--color-card)] border-2 border-[var(--color-border)] shadow-sm">
          <svg className="w-24 h-24 text-[var(--color-primary)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
          </svg>
        </div>

        <h1 className="text-2xl font-bold text-[var(--color-text)] text-center mb-8">
          Let's check your Headphone
        </h1>

        {/* Volume slider */}
        <div className="w-full max-w-md mb-8">
          <div className="flex items-center justify-between gap-4">
            <div className="flex items-center gap-2 text-sm text-[var(--color-text-muted)]">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" /></svg>
              <span className="font-medium">QUIET</span>
            </div>
            <input
              type="range"
              min="0"
              max="100"
              value={volume}
              onChange={(e) => setVolume(Number(e.target.value))}
              className="flex-1 h-3 rounded-full appearance-none bg-[var(--color-border)] [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-5 [&::-webkit-slider-thumb]:h-5 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-[var(--color-primary)]"
            />
            <div className="flex items-center gap-2 text-sm text-[var(--color-text-muted)]">
              <span className="font-medium">LOUD</span>
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" /></svg>
            </div>
          </div>
        </div>

        <Link
          to={`/directions?mode=${mode}`}
          className="inline-flex items-center gap-2 px-8 py-3 rounded-xl bg-[var(--color-accent)] text-[var(--color-text)] font-semibold border border-[var(--color-primary)]/20 hover:opacity-90 mb-6"
        >
          Continue
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" /></svg>
        </Link>

        <p className="text-sm text-[var(--color-text-muted)] text-center max-w-md">
          Click Continue to go to the next screen. If you have any problems, please contact your instructor.
        </p>
      </main>

      {/* Status bar */}
      <footer className="flex items-center justify-center gap-8 py-4 border-t border-[var(--color-border)] bg-[var(--color-card)] text-sm text-[var(--color-text-muted)]">
        <span className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-green-500" />
          System Ready
        </span>
        <span className="flex items-center gap-2">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0V8m0 0V4a7 7 0 0114 0v4z" /></svg>
          Microphone Not Required
        </span>
      </footer>
    </div>
  );
}
