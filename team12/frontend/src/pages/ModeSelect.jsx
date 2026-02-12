import { Link } from 'react-router-dom';
import { PageHeader } from '../components/PageHeader';

export function ModeSelect() {
  return (
    <div className="min-h-screen bg-[var(--color-surface)] p-6">
      <div className="max-w-4xl mx-auto">
        <PageHeader showBack={false} />
        <h1 className="text-2xl font-bold text-[var(--color-text)] text-center mb-2">
          Select Your Learning Mode
        </h1>
        <p className="text-[var(--color-text-muted)] text-center mb-10 max-w-xl mx-auto">
          Choose how you want to prepare today. Select Exam Mode to test your readiness or Practice Mode to learn at your own pace.
        </p>

        <div className="grid gap-6 sm:grid-cols-2">
          {/* Exam Mode card */}
          <div className="rounded-2xl bg-[var(--color-card)] shadow-md border border-[var(--color-border)] p-6 flex flex-col">
            <div className="flex items-start justify-between mb-4">
              <div className="w-12 h-12 rounded-full bg-[var(--color-primary)] flex items-center justify-center">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
              </div>
              <span className="px-3 py-1 rounded-full text-xs font-semibold bg-[var(--color-primary)] text-white">STRICT MODE</span>
            </div>
            <h2 className="text-lg font-bold text-[var(--color-text)] mb-2">Exam Mode</h2>
            <p className="text-[var(--color-text-muted)] text-sm mb-6 flex-1">
              Simulate the real testing environment. Strict timing, no do-overs. Best for assessing your final readiness.
            </p>
            <Link
              to="/audio-setup?mode=exam"
              className="inline-flex items-center justify-center gap-2 w-full py-3 rounded-xl bg-[var(--color-primary)] text-white font-semibold hover:opacity-90 transition"
            >
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M8 5v14l11-7z" /></svg>
              Start Exam Mode
            </Link>
            <div className="mt-6 pt-4 border-t border-[var(--color-border)]">
              <p className="text-xs font-medium text-[var(--color-text-muted)] uppercase tracking-wide mb-3">Key features</p>
              <ul className="space-y-2 text-sm text-[var(--color-text)]">
                {['Timed conditions', 'Real interface', 'Strict navigation', 'One-time audio', 'AI correction'].map((f, i) => (
                  <li key={i} className="flex items-center gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-[var(--color-primary)]" />
                    {f}
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Practice Mode card */}
          <div className="rounded-2xl bg-[var(--color-card)] shadow-md border border-[var(--color-border)] p-6 flex flex-col">
            <div className="flex items-start justify-between mb-4">
              <div className="w-12 h-12 rounded-full bg-[var(--color-practice)] flex items-center justify-center">
                <svg className="w-6 h-6 text-[var(--color-text)]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 14l9-5-9-5-9 5 9 5z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 14l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14z" /></svg>
              </div>
              <span className="px-3 py-1 rounded-full text-xs font-semibold bg-[var(--color-accent)] text-[var(--color-text)] border border-[var(--color-primary)]/20">FLEXIBLE</span>
            </div>
            <h2 className="text-lg font-bold text-[var(--color-text)] mb-2">Practice Mode</h2>
            <p className="text-[var(--color-text-muted)] text-sm mb-6 flex-1">
              Review the test without any time limits and access helpful learning tools. Learn at your own pace.
            </p>
            <Link
              to="/audio-setup?mode=practice"
              className="inline-flex items-center justify-center gap-2 w-full py-3 rounded-xl border-2 border-[var(--color-practice-border)] text-[var(--color-practice-border)] font-semibold bg-white hover:bg-[var(--color-practice)]/10 transition"
            >
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M8 5v14l11-7z" /></svg>
              Start Practice Mode
            </Link>
            <div className="mt-6 pt-4 border-t border-[var(--color-border)]">
              <p className="text-xs font-medium text-[var(--color-text-muted)] uppercase tracking-wide mb-3">Key features</p>
              <ul className="space-y-2 text-sm text-[var(--color-text)]">
                {['No pressure', 'Instant dictionary', 'Leitner box'].map((f, i) => (
                  <li key={i} className="flex items-center gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-[var(--color-practice-border)]" />
                    {f}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
