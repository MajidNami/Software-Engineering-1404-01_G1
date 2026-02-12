import { useState, useEffect } from 'react';

export function QuestionCard({
  question,
  onSubmit,
  disabled,
  feedback,
  mode,
  questionIndex,
  totalQuestions,
  answeredCount = 0,
  onSelectQuestion,
}) {
  const [selectedId, setSelectedId] = useState(null);
  const [submitted, setSubmitted] = useState(false);

  // Reset selection when the question changes (e.g. moving to next question)
  useEffect(() => {
    setSelectedId(null);
    setSubmitted(false);
  }, [question?.id]);

  const handleSelect = (optionId) => {
    if (submitted || disabled) return;
    setSelectedId(optionId);
  };

  const handleSubmit = () => {
    if (!selectedId || submitted) return;
    onSubmit(selectedId);
    setSubmitted(true);
  };

  const options = question?.options || [];
  const showFeedback = mode === 'practice' && submitted && feedback;

  return (
    <div className="rounded-2xl bg-[var(--color-card)] shadow-md border border-[var(--color-border)] p-6">
      <p className="text-[var(--color-text)] font-bold text-lg mb-5">{question?.text}</p>
      <div className="space-y-2">
        {options.map((opt) => {
          const isSelected = selectedId === opt.id;
          const showCorrect = showFeedback && feedback.correct_option_id === opt.id;
          const showWrong = showFeedback && isSelected && !feedback.is_correct;
          let bg = 'bg-[var(--color-surface)] hover:bg-[var(--color-selected)] border-[var(--color-border)]';
          let ring = '';
          if (showCorrect) {
            bg = 'bg-green-500/15 border-green-500 dark:bg-green-500/20';
            ring = 'ring-2 ring-green-500';
          } else if (showWrong) {
            bg = 'bg-red-500/15 border-red-400 dark:bg-red-500/20';
            ring = 'ring-2 ring-red-400';
          } else if (isSelected) {
            bg = 'bg-[var(--color-selected)] border-[var(--color-primary)]';
            ring = 'ring-2 ring-[var(--color-primary)]';
          }

          return (
            <button
              key={opt.id}
              type="button"
              disabled={submitted || disabled}
              onClick={() => handleSelect(opt.id)}
              className={`w-full text-left px-4 py-3 rounded-xl border-2 transition flex items-center gap-3 ${bg} ${ring}`}
            >
              <span className={`flex-shrink-0 w-5 h-5 rounded-full border-2 flex items-center justify-center ${
                isSelected || showCorrect ? 'border-[var(--color-primary)] bg-[var(--color-primary)]' : 'border-[var(--color-text-muted)]'
              }`}>
                {(isSelected || showCorrect) && <span className="w-2 h-2 rounded-full bg-white" />}
              </span>
              <span className="font-medium text-[var(--color-text-muted)]">{opt.label}.</span>
              <span className="text-[var(--color-text)]">{opt.text}</span>
              {showCorrect && <span className="ml-2 text-green-600 dark:text-green-400 font-medium">✓ Correct</span>}
              {showWrong && <span className="ml-2 text-red-600 dark:text-red-400">✗</span>}
            </button>
          );
        })}
      </div>
      {showFeedback && feedback.explanation && (
        <div className="mt-5 p-4 rounded-xl bg-[var(--color-surface)] border border-[var(--color-border)]">
          <p className="text-sm font-semibold text-[var(--color-text)] mb-1">Why this is correct</p>
          <p className="text-[var(--color-text-muted)] text-sm">{feedback.explanation}</p>
        </div>
      )}
      {!submitted && selectedId && (
        <div className="mt-5 flex justify-end">
          <button
            type="button"
            onClick={handleSubmit}
            disabled={disabled}
            className="px-6 py-2.5 bg-[var(--color-primary)] text-white rounded-xl font-semibold hover:opacity-90 disabled:opacity-50 transition"
          >
            Submit Answer
          </button>
        </div>
      )}

      {/* Navigatable question numbers: answered = filled, unanswered = hollow; current has ring */}
      {totalQuestions > 0 && (
        <div className="flex flex-wrap gap-2 mt-6 pt-4 border-t border-[var(--color-border)]">
          {Array.from({ length: totalQuestions }, (_, i) => {
            const isAnswered = i < answeredCount;
            const isCurrent = i === questionIndex;
            return (
              <button
                key={i}
                type="button"
                onClick={() => onSelectQuestion?.(i)}
                className={`w-9 h-9 rounded-full flex items-center justify-center text-sm font-medium transition border-2 ring-offset-2 ring-offset-[var(--color-card)] ${
                  isAnswered
                    ? 'bg-[var(--color-primary)] text-white border-[var(--color-primary)]'
                    : 'bg-[var(--color-surface)] text-[var(--color-text)] border-[var(--color-border)] hover:border-[var(--color-primary)] hover:text-[var(--color-text)]'
                } ${isCurrent ? 'ring-2 ring-[var(--color-primary)]' : ''}`}
                aria-label={`Question ${i + 1}`}
              >
                {i + 1}
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}
