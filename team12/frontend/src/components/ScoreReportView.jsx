import { Link } from 'react-router-dom';

export function ScoreReportView({ report }) {
  if (!report) return null;

  const totalQuestions = report.total_questions ?? 0;
  const answeredCount = report.answered_count ?? 0;
  const correctCount = report.correct_count ?? 0;
  const score = report.total_score ?? 0;
  const maxScore = 30;
  const detailed = report.detailed_answers || [];

  return (
    <div className="min-h-screen bg-[var(--color-surface)]">
      {/* Header: Test Prep Pro (left) | bell + Quit (right) */}
      <header className="flex items-center justify-between px-6 py-4 border-b border-[var(--color-border)] bg-[var(--color-card)]">
        <div className="flex items-center gap-2">
          <span className="text-xl font-bold text-[var(--color-text)]">+ Test Prep Pro</span>
        </div>
        <div className="flex items-center gap-3">
          <Link
            to="/"
            className="inline-flex items-center gap-1.5 px-5 py-2.5 rounded-lg bg-[var(--color-accent)] text-[var(--color-text)] font-semibold border border-[var(--color-primary)]/20 hover:opacity-90 transition"
          >
            Quit
          </Link>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-6 py-8">
        <h1 className="text-2xl font-bold text-[var(--color-text)] text-center mb-1">
          Test Results Review
        </h1>
        <p className="text-[var(--color-text-muted)] text-center text-sm mb-8">
          Review your performance on the recent practice test.
        </p>

        {/* Summary cards */}
        <div className="grid grid-cols-3 gap-4 mb-8">
          <div className="rounded-xl bg-[var(--color-card)] border border-[var(--color-border)] shadow-sm p-5 text-center">
            <p className="text-sm font-medium text-[var(--color-text-muted)] mb-1">Answered Questions</p>
            <p className="text-xl font-bold text-[var(--color-text)]">
              {answeredCount}/{totalQuestions || '—'}
            </p>
          </div>
          <div className="rounded-xl bg-[var(--color-card)] border border-[var(--color-border)] shadow-sm p-5 text-center">
            <p className="text-sm font-medium text-[var(--color-text-muted)] mb-1">Correct Answers</p>
            <p className="text-xl font-bold text-[var(--color-text)]">
              {correctCount}/{totalQuestions || '—'}
            </p>
          </div>
          <div className="rounded-xl bg-[var(--color-card)] border border-[var(--color-border)] shadow-sm p-5 text-center">
            <p className="text-sm font-medium text-[var(--color-text-muted)] mb-1">Score</p>
            <p className="text-xl font-bold text-[var(--color-text)]">
              {score}/{maxScore}
            </p>
          </div>
        </div>

        {/* Detailed Review table */}
        <h3 className="text-lg font-bold text-[var(--color-text)] mb-4">Detailed Review</h3>
        <div className="rounded-xl bg-[var(--color-card)] border border-[var(--color-border)] shadow-sm overflow-hidden">
          <table className="w-full text-left">
            <thead>
              <tr className="border-b border-[var(--color-border)] bg-[var(--color-surface)]">
                <th className="px-4 py-3 text-sm font-semibold text-[var(--color-text)]">ID</th>
                <th className="px-4 py-3 text-sm font-semibold text-[var(--color-text)]">Question</th>
                <th className="px-4 py-3 text-sm font-semibold text-[var(--color-text)]">Correct Answer</th>
                <th className="px-4 py-3 text-sm font-semibold text-[var(--color-text)]">Your Answer</th>
              </tr>
            </thead>
            <tbody>
              {detailed.length > 0 ? (
                detailed.map((row) => (
                  <tr key={row.id} className="border-b border-[var(--color-border)] last:border-0">
                    <td className="px-4 py-3 text-sm text-[var(--color-text-muted)]">{row.id}</td>
                    <td className="px-4 py-3 text-sm text-[var(--color-text)]">{row.question_text}</td>
                    <td className="px-4 py-3 text-sm text-[var(--color-text-muted)]">{row.correct_answer}</td>
                    <td className="px-4 py-3 text-sm text-[var(--color-text-muted)]">{row.your_answer}</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={4} className="px-4 py-8 text-center text-[var(--color-text-muted)] text-sm">
                    No answers to review.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        <div className="mt-8 text-center">
          <Link
            to="/"
            className="inline-block text-[var(--color-text-muted)] font-medium hover:text-[var(--color-text)]"
          >
            Back to home
          </Link>
        </div>
      </main>
    </div>
  );
}
