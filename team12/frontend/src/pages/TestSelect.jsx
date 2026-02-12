import { useState, useEffect } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { api } from '../api';
import { PageHeader } from '../components/PageHeader';

export function TestSelect() {
  const [searchParams] = useSearchParams();
  const mode = searchParams.get('mode') || 'practice';
  const [tests, setTests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    api.getTests()
      .then(setTests)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-[var(--color-surface)] flex items-center justify-center">
        <p className="text-[var(--color-text-muted)]">Loading tests...</p>
      </div>
    );
  }
  if (error) {
    return (
      <div className="min-h-screen bg-[var(--color-surface)] p-6">
        <p className="text-red-600">{error}</p>
        <Link to="/" className="mt-4 inline-block text-[var(--color-primary)] hover:underline">Back to mode</Link>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[var(--color-surface)] p-6">
      <div className="max-w-2xl mx-auto">
        <PageHeader
          title="Select a test"
          subtitle={`${mode === 'practice' ? 'Practice' : 'Exam'} mode`}
          showBack
          backTo="/"
        />
        <div className="rounded-2xl bg-[var(--color-card)] shadow-md border border-[var(--color-border)] overflow-hidden">
          <ul className="divide-y divide-[var(--color-border)]">
            {tests.map((t) => (
              <li key={t.id}>
                <Link
                  to={`/listening?testId=${t.id}&mode=${mode}`}
                  className="block px-6 py-4 hover:bg-[var(--color-surface)] transition text-[var(--color-text)] font-medium"
                >
                  {t.title}
                  {t.total_items > 0 && (
                    <span className="text-[var(--color-text-muted)] text-sm font-normal ml-2">({t.total_items} items)</span>
                  )}
                </Link>
              </li>
            ))}
          </ul>
          {tests.length === 0 && (
            <p className="px-6 py-8 text-[var(--color-text-muted)] text-center">No tests available. Create tests in the admin.</p>
          )}
        </div>
      </div>
    </div>
  );
}
