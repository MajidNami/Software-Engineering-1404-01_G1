import { useEffect, useState } from 'react';
import { Link, useSearchParams, useNavigate } from 'react-router-dom';
import { api } from '../api';
import { ThemeToggle } from '../components/ThemeToggle';

export function DirectionsPage() {
  const [searchParams] = useSearchParams();
  const mode = searchParams.get('mode') || 'practice';
  const navigate = useNavigate();
  const [firstTestId, setFirstTestId] = useState(null);

  useEffect(() => {
    api.getTests()
      .then((tests) => {
        if (tests && tests.length > 0) setFirstTestId(tests[0].id);
      })
      .catch(() => {});
  }, []);

  const handleContinue = () => {
    if (firstTestId) {
      navigate(`/listening?testId=${firstTestId}&mode=${mode}`);
    }
  };

  return (
    <div className="min-h-screen bg-[var(--color-surface)] flex flex-col">
      {/* Header: Practice mode / Exam Mode, REAL 1, TEST SECTION, Volume, Quit */}
      <header className="flex items-center justify-between px-6 py-4 border-b border-[var(--color-border)] bg-[var(--color-card)]">
        <div>
          <h1 className="text-lg font-bold text-[var(--color-text)]">
            {mode === 'practice' ? 'Practice mode' : 'Exam Mode'}
          </h1>
          <p className="text-sm text-[var(--color-text-muted)] mt-0.5 flex items-center gap-1.5">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" /></svg>
            REAL 1 · TEST SECTION
          </p>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-sm text-[var(--color-text-muted)]">Volume</span>
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

      <main className="flex-1 px-4 py-6 max-w-3xl mx-auto w-full">
        <div className="rounded-2xl bg-[var(--color-card)] shadow-md border border-[var(--color-border)] p-6 md:p-8">
          {/* Title with headphone icon and line */}
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 rounded-full bg-[var(--color-accent)] flex items-center justify-center">
              <svg className="w-5 h-5 text-[var(--color-text)]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" /></svg>
            </div>
            <div className="flex-1 h-px bg-[var(--color-accent)]" />
          </div>
          <h2 className="text-xl font-bold text-[var(--color-text)] mb-2">Listening Section Directions</h2>
          <p className="text-[var(--color-text-muted)] mb-6">
            This section measures your ability to understand conversations and lectures in English.
          </p>

          {/* 4 instruction blocks - 2x2 grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6">
            <div className="rounded-xl bg-[var(--color-selected)]/50 border border-[var(--color-border)] p-4">
              <div className="flex items-start gap-3">
                <svg className="w-6 h-6 text-[var(--color-primary)] shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" /></svg>
                <div>
                  <p className="text-sm font-medium text-[var(--color-text)]">Audio Structure</p>
                  <p className="text-sm text-[var(--color-text-muted)] mt-1">You will listen to <strong className="text-[var(--color-text)]">1 conversation</strong> and <strong className="text-[var(--color-text)]">2 lectures</strong> per part.</p>
                </div>
              </div>
            </div>
            <div className="rounded-xl bg-[var(--color-selected)]/50 border border-[var(--color-border)] p-4">
              <div className="flex items-start gap-3">
                <svg className="w-6 h-6 text-[var(--color-primary)] shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" /></svg>
                <div>
                  <p className="text-sm font-medium text-[var(--color-text)]">Playback</p>
                  <p className="text-sm text-[var(--color-text-muted)] mt-1">You will hear each audio clip <strong className="text-[var(--color-text)]">only one time</strong>.</p>
                </div>
              </div>
            </div>
            <div className="rounded-xl bg-[var(--color-selected)]/50 border border-[var(--color-border)] p-4">
              <div className="flex items-start gap-3">
                <svg className="w-6 h-6 text-[var(--color-primary)] shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" /></svg>
                <div>
                  <p className="text-sm font-medium text-[var(--color-text)]">Note Taking</p>
                  <p className="text-sm text-[var(--color-text-muted)] mt-1">You may <strong className="text-[var(--color-text)]">take notes</strong> while you listen to help you answer.</p>
                </div>
              </div>
            </div>
            <div className="rounded-xl bg-[var(--color-selected)]/50 border border-[var(--color-border)] p-4">
              <div className="flex items-start gap-3">
                <svg className="w-6 h-6 text-[var(--color-primary)] shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                <div>
                  <p className="text-sm font-medium text-[var(--color-text)]">Questions</p>
                  <p className="text-sm text-[var(--color-text-muted)] mt-1">Answer based on what is stated or implied by speakers.</p>
                </div>
              </div>
            </div>
          </div>

          {/* Timer Rule */}
          <div className="rounded-xl bg-[var(--color-accent)]/20 border border-[var(--color-accent)]/50 p-4 mb-8">
            <div className="flex items-start gap-3">
              <svg className="w-5 h-5 text-[var(--color-primary)] shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
              <div>
                <p className="text-sm font-semibold text-[var(--color-text)]">TIMER RULE</p>
                <p className="text-sm text-[var(--color-text-muted)] mt-1">The clock does <strong className="text-[var(--color-coral)]">not run</strong> while you are listening to the conversations and lectures. The clock only runs while you are answering the questions.</p>
              </div>
            </div>
          </div>

          {/* Navigation */}
          <div className="flex items-center justify-between pt-4 border-t border-[var(--color-border)]">
            <Link
              to={`/audio-setup?mode=${mode}`}
              className="inline-flex items-center gap-1.5 text-[var(--color-text-muted)] hover:text-[var(--color-text)] font-medium"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" /></svg>
              BACK
            </Link>
            <button
              type="button"
              onClick={handleContinue}
              disabled={!firstTestId}
              className="inline-flex items-center gap-2 px-6 py-2.5 rounded-xl bg-[var(--color-accent)] text-[var(--color-text)] font-semibold border border-[var(--color-primary)]/20 hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Continue
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" /></svg>
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}
