import { useState, useEffect, useCallback, useRef } from 'react';
import { useSearchParams, useNavigate, Link } from 'react-router-dom';
import { api } from '../api';
import AudioPlayer from '../components/AudioPlayer';
import { QuestionCard } from '../components/QuestionCard';
import { ScoreReportView } from '../components/ScoreReportView';
import { Modal } from '../components/Modal';
import { SettingsModal } from '../components/SettingsModal';
import { ThemeToggle } from '../components/ThemeToggle';
import { loadSettings } from '../lib/settings';
import { useBackgroundNoise } from '../hooks/useBackgroundNoise';

function flattenQuestions(allItems) {
  const list = [];
  (allItems || []).forEach((item) => {
    (item.questions || []).forEach((q) => list.push({ ...q, itemId: item.id, item }));
  });
  return list;
}

function formatElapsed(seconds) {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
}

const IconButton = ({ onClick, children, label }) => (
  <button
    type="button"
    onClick={onClick}
    className="p-2 rounded-lg text-[var(--color-text-muted)] hover:text-[var(--color-text)] hover:bg-[var(--color-surface)] transition"
    title={label}
    aria-label={label}
  >
    {children}
  </button>
);

function AnalysisModalContent({ feedback, currentQuestion }) {
  const [view, setView] = useState('brief');
  const correctLabel = currentQuestion?.options?.find((o) => o.id === feedback?.correct_option_id)?.label ?? '—';
  const explanation = feedback?.explanation ?? '';

  if (!feedback || !explanation) {
    return (
      <p className="text-[var(--color-text-muted)] text-sm">
        Submit your answer to see the analysis and explanation.
      </p>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex gap-2">
        <button
          type="button"
          onClick={() => setView('brief')}
          className={`px-4 py-2 rounded-full text-sm font-medium transition ${
            view === 'brief'
              ? 'bg-[var(--color-accent)] text-[var(--color-text)] border border-[var(--color-primary)]/20'
              : 'bg-[var(--color-surface)] text-[var(--color-text-muted)] border border-[var(--color-border)]'
          }`}
        >
          brief
        </button>
        <button
          type="button"
          onClick={() => setView('comprehensive')}
          className={`px-4 py-2 rounded-full text-sm font-medium transition ${
            view === 'comprehensive'
              ? 'bg-[var(--color-primary)] text-white border border-[var(--color-primary)]'
              : 'bg-[var(--color-surface)] text-[var(--color-text-muted)] border border-[var(--color-border)]'
          }`}
        >
          comprehensive
        </button>
      </div>
      <p className="text-[var(--color-primary)] font-semibold">Correct Answer: {correctLabel}</p>
      <div className="text-[var(--color-text)] text-sm leading-relaxed whitespace-pre-wrap">
        {view === 'brief' ? explanation.split(/\n\n/)[0] || explanation : explanation}
      </div>
    </div>
  );
}

function AnswerModalContent({ question }) {
  const correctOption = question?.options?.find((o) => o.is_correct);
  if (!question) {
    return <p className="text-[var(--color-text-muted)] text-sm">No question loaded.</p>;
  }
  return (
    <div className="space-y-4">
      <p className="text-[var(--color-text)] font-medium">{question.text}</p>
      {correctOption ? (
        <div className="rounded-xl border-2 border-[var(--color-primary)] bg-[var(--color-surface)] p-4">
          <p className="text-[var(--color-primary)] font-semibold mb-1">Correct Answer: {correctOption.label}</p>
          <p className="text-[var(--color-text)] text-sm">{correctOption.text}</p>
        </div>
      ) : (
        <p className="text-[var(--color-text-muted)] text-sm">No correct answer defined.</p>
      )}
    </div>
  );
}

function ReviewModalContent({ answersForReview }) {
  if (!answersForReview || answersForReview.length === 0) {
    return (
      <p className="text-[var(--color-text-muted)] text-sm">
        Review your answers and notes after completing the questions. Your review will appear here as you submit answers.
      </p>
    );
  }
  return (
    <div className="space-y-4">
      <p className="text-[var(--color-text-muted)] text-sm">
        Review your answers and notes after completing the questions.
      </p>
      <div className="rounded-xl border border-[var(--color-border)] overflow-hidden">
        <table className="w-full text-left text-sm">
          <thead>
            <tr className="bg-[var(--color-surface)] border-b border-[var(--color-border)]">
              <th className="px-3 py-2 font-semibold text-[var(--color-text)]">ID</th>
              <th className="px-3 py-2 font-semibold text-[var(--color-text)]">Question</th>
              <th className="px-3 py-2 font-semibold text-[var(--color-text)]">Correct Answer</th>
              <th className="px-3 py-2 font-semibold text-[var(--color-text)]">Your Answer</th>
              <th className="px-2 py-2 font-semibold text-[var(--color-text)] w-10"></th>
            </tr>
          </thead>
          <tbody>
            {answersForReview.map((row) => (
              <tr key={row.id} className="border-b border-[var(--color-border)] last:border-0">
                <td className="px-3 py-2 text-[var(--color-text-muted)]">{row.id}</td>
                <td className="px-3 py-2 text-[var(--color-text)] max-w-[200px] truncate" title={row.questionText}>{row.questionText}</td>
                <td className="px-3 py-2 text-[var(--color-text-muted)] max-w-[140px] truncate" title={row.correctAnswer}>{row.correctAnswer}</td>
                <td className="px-3 py-2 text-[var(--color-text-muted)] max-w-[140px] truncate" title={row.yourAnswer}>{row.yourAnswer}</td>
                <td className="px-2 py-2">
                  {row.isCorrect ? (
                    <span className="text-green-600 font-medium">✓</span>
                  ) : (
                    <span className="text-red-500">✗</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

// Group answers by stage for the full Review phase page
function groupAnswersByStage(answersForReview) {
  const byStage = new Map();
  (answersForReview || []).forEach((row) => {
    const stageKey = row.stageIndex ?? 0;
    const label = row.stageLabel ?? 'Section';
    if (!byStage.has(stageKey)) byStage.set(stageKey, { label, rows: [] });
    byStage.get(stageKey).rows.push(row);
  });
  return Array.from(byStage.entries())
    .sort((a, b) => a[0] - b[0])
    .map(([idx, { label, rows }]) => ({ stageIndex: idx + 1, stageLabel: label, rows }));
}

export default function ListeningPage() {
  const [searchParams] = useSearchParams();
  const testId = searchParams.get('testId');
  const mode = searchParams.get('mode') || 'practice';
  const navigate = useNavigate();

  const [session, setSession] = useState(null);
  const [allItems, setAllItems] = useState([]);
  const [currentItemIndex, setCurrentItemIndex] = useState(0); // stage index (0-based)
  const [questionIndex, setQuestionIndex] = useState(0);
  const [feedback, setFeedback] = useState(null);
  const [finished, setFinished] = useState(false);
  const [scoreReport, setScoreReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [phase, setPhase] = useState('player'); // 'player' | 'questions' | 'review'
  const [modal, setModal] = useState(null);   // 'review' | 'transcript' | 'settings' | null
  const [settingsSnapshot, setSettingsSnapshot] = useState(() => loadSettings());
  const [answersForReview, setAnswersForReview] = useState([]); // { id, questionText, yourAnswer, correctAnswer, isCorrect, stageIndex, stageLabel }
  const [lastAnalysisFeedback, setLastAnalysisFeedback] = useState(null);
  const [lastAnalysisQuestion, setLastAnalysisQuestion] = useState(null);
  const [elapsedSeconds, setElapsedSeconds] = useState(0);
  const answerStartRef = useRef(null);
  const sessionStartRef = useRef(null);

  const isListeningActive = phase === 'player' || phase === 'questions'; // review phase does not play background
  useBackgroundNoise(
    isListeningActive && settingsSnapshot.exam.playBackgroundNoise,
    settingsSnapshot.exam.backgroundNoiseVolume
  );

  // Per-stage flow: current item and only this stage's questions
  const currentItem = allItems[currentItemIndex] ?? null;
  const questionsList = (currentItem?.questions || []).map((q) => ({ ...q, itemId: currentItem?.id, item: currentItem }));
  const currentQ = questionsList[questionIndex] ?? null;
  const isLastQuestionOfStage = questionsList.length > 0 && questionIndex >= questionsList.length - 1;
  const isLastStage = currentItemIndex >= (allItems.length - 1) && allItems.length > 0;
  const isLastQuestion = isLastQuestionOfStage && isLastStage;

  const logEvent = useCallback((sid, eventType, count, extra) => {
    api.logEvent(sid, eventType, count, extra).catch(() => {});
  }, []);

  useEffect(() => {
    if (!testId) {
      setError('Missing test');
      setLoading(false);
      return;
    }
    api.startSession(Number(testId), mode)
      .then((data) => {
        setSession(data.session);
        setAllItems(data.all_items || []);
        setCurrentItemIndex(0);
        setQuestionIndex(0);
        setPhase('player');
        sessionStartRef.current = Date.now();
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [testId, mode]);

  // Elapsed timer (updates every second while session active and not finished)
  useEffect(() => {
    if (!session?.id || finished) return;
    const interval = setInterval(() => {
      if (sessionStartRef.current) {
        setElapsedSeconds(Math.floor((Date.now() - sessionStartRef.current) / 1000));
      }
    }, 1000);
    return () => clearInterval(interval);
  }, [session?.id, finished]);

  useEffect(() => {
    const handleVisibility = () => {
      if (document.visibilityState === 'hidden' && session?.id) {
        logEvent(session.id, 'focus_loss', 1, { visibility: 'hidden' });
      }
    };
    const handleBlur = () => {
      if (session?.id) logEvent(session.id, 'focus_loss', 1, { event: 'window_blur' });
    };
    document.addEventListener('visibilitychange', handleVisibility);
    window.addEventListener('blur', handleBlur);
    return () => {
      document.removeEventListener('visibilitychange', handleVisibility);
      window.removeEventListener('blur', handleBlur);
    };
  }, [session?.id, logEvent]);

  const handleSubmitAnswer = (optionId) => {
    if (!session || !currentQ) return;
    const responseTimeMs = answerStartRef.current ? Math.round(performance.now() - answerStartRef.current) : null;
    setFeedback(null);
    api.submitAnswer(session.id, currentQ.id, optionId, responseTimeMs)
      .then((res) => {
        setFeedback(res);
        setLastAnalysisFeedback(res);
        setLastAnalysisQuestion(currentQ);
        const options = currentQ.options || [];
        const yourText = options.find((o) => o.id === optionId)?.text ?? '—';
        const correctText = options.find((o) => o.id === res.correct_option_id)?.text ?? '—';
        const stageLabel = currentItem?.item_type === 'lecture' ? 'Lecture' : 'Conversation';
        setAnswersForReview((prev) => [
          ...prev,
          {
            id: prev.length + 1,
            questionText: currentQ.text,
            yourAnswer: yourText,
            correctAnswer: correctText,
            isCorrect: res.is_correct,
            stageIndex: currentItemIndex,
            stageLabel,
          },
        ]);
        // Don't auto-advance from last question of section: show "Continue to next section" so user can see it
        if (isLastQuestionOfStage) {
          // Leave phase as 'questions' and show the continue button; user clicks to advance
          if (currentItemIndex >= allItems.length - 1) {
            // Actually last section; no next section, keep feedback for Finish button
          }
        } else {
          setQuestionIndex((i) => i + 1);
          setFeedback(null);
        }
      })
      .catch((e) => setError(e.message));
  };

  const handleFinish = () => {
    if (!session) return;
    api.finishSession(session.id)
      .then((report) => {
        setFinished(true);
        setScoreReport(report);
      })
      .catch((e) => setError(e.message));
  };

  const goToNext = () => {
    if (questionIndex < questionsList.length - 1) {
      setQuestionIndex((i) => i + 1);
      setFeedback(null);
    }
  };

  const handleAudioEnded = useCallback(() => {
    setPhase('questions');
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-[var(--color-surface)] flex items-center justify-center">
        <p className="text-[var(--color-text-muted)]">Starting session...</p>
      </div>
    );
  }
  if (error) {
    return (
      <div className="min-h-screen bg-[var(--color-surface)] p-6">
        <p className="text-red-600">{error}</p>
        <button type="button" onClick={() => navigate('/')} className="mt-4 text-[var(--color-primary)] hover:underline">Back to home</button>
      </div>
    );
  }

  if (finished && scoreReport) {
    return <ScoreReportView report={scoreReport} />;
  }

  // ---------- Phase: Review (after all 25 questions, before score) ----------
  if (phase === 'review') {
    const stagesGrouped = groupAnswersByStage(answersForReview);
    return (
      <div className="min-h-screen bg-[var(--color-surface)] flex flex-col">
        <header className="flex items-center justify-between px-4 py-3 border-b border-[var(--color-border)] bg-[var(--color-card)]">
          <div className="flex items-center gap-2">
            <span className="text-lg font-bold text-[var(--color-text)]">+ Test Prep Pro</span>
            <span className="text-sm font-mono text-[var(--color-text-muted)] tabular-nums">{formatElapsed(elapsedSeconds)}</span>
          </div>
          <div className="flex items-center gap-2">
            <ThemeToggle />
            <Link to="/" className="px-4 py-2 rounded-lg bg-[var(--color-accent)] text-[var(--color-text)] font-semibold border border-[var(--color-primary)]/20 hover:opacity-90">Quit</Link>
          </div>
        </header>
        <main className="flex-1 p-4 md:p-6 max-w-4xl mx-auto w-full">
          <h1 className="text-xl font-bold text-[var(--color-text)] mb-1">Review your answers</h1>
          <p className="text-sm text-[var(--color-text-muted)] mb-6">
            You answered 25 questions in 5 stages. Review below, then see your score.
          </p>
          <div className="space-y-8">
            {stagesGrouped.map(({ stageIndex, stageLabel, rows }) => (
              <div key={stageIndex} className="rounded-xl border border-[var(--color-border)] overflow-hidden bg-[var(--color-card)]">
                <div className="px-4 py-3 bg-[var(--color-surface)] border-b border-[var(--color-border)]">
                  <span className="font-semibold text-[var(--color-text)]">Stage {stageIndex} of 5 — {stageLabel}</span>
                </div>
                <table className="w-full text-left text-sm">
                  <thead>
                    <tr className="bg-[var(--color-surface)] border-b border-[var(--color-border)]">
                      <th className="px-3 py-2 font-semibold text-[var(--color-text)] w-10">#</th>
                      <th className="px-3 py-2 font-semibold text-[var(--color-text)]">Question</th>
                      <th className="px-3 py-2 font-semibold text-[var(--color-text)]">Correct</th>
                      <th className="px-3 py-2 font-semibold text-[var(--color-text)]">Your answer</th>
                      <th className="px-2 py-2 w-10"></th>
                    </tr>
                  </thead>
                  <tbody>
                    {rows.map((row) => (
                      <tr key={row.id} className="border-b border-[var(--color-border)] last:border-0">
                        <td className="px-3 py-2 text-[var(--color-text-muted)]">{row.id}</td>
                        <td className="px-3 py-2 text-[var(--color-text)] max-w-[240px]" title={row.questionText}>{row.questionText.length > 60 ? row.questionText.slice(0, 60) + '…' : row.questionText}</td>
                        <td className="px-3 py-2 text-[var(--color-text-muted)] max-w-[140px] truncate" title={row.correctAnswer}>{row.correctAnswer}</td>
                        <td className="px-3 py-2 text-[var(--color-text-muted)] max-w-[140px] truncate" title={row.yourAnswer}>{row.yourAnswer}</td>
                        <td className="px-2 py-2">
                          {row.isCorrect ? <span className="text-green-600 font-medium">✓</span> : <span className="text-red-500">✗</span>}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ))}
          </div>
          <div className="mt-8 flex justify-center">
            <button
              type="button"
              onClick={handleFinish}
              className="px-8 py-3 rounded-xl bg-[var(--color-primary)] text-white font-semibold hover:opacity-90"
            >
              See my score
            </button>
          </div>
        </main>
      </div>
    );
  }

  const apiOrigin = (import.meta.env.VITE_API_URL || 'http://localhost:8000/api').replace(/\/api\/?$/, '');
  let audioSrc = currentItem?.audio_source || currentItem?.audio_url || '';
  if (audioSrc && !audioSrc.startsWith('http')) audioSrc = `${apiOrigin}${audioSrc}`;
  let thumbnailUrl = currentItem?.thumbnail_source || '';
  if (thumbnailUrl && !thumbnailUrl.startsWith('http')) thumbnailUrl = `${apiOrigin}${thumbnailUrl}`;
  const testTitle = session?.test?.title || 'Test';
  const itemType = currentItem?.item_type === 'lecture' ? 'Lecture' : 'Conversation';
  const imageLabel = currentItem?.topic_tag || (currentItem?.item_type === 'conversation' ? 'New People Conversation' : itemType);

  // ---------- Phase: Player (listen to audio for this stage) ----------
  if (phase === 'player' && currentItem) {
    return (
      <div className="min-h-screen bg-[var(--color-surface)] flex flex-col">
        {/* Header: REAL 1 + listening • Number 1 | Review, Transcript, Settings | Hamburger */}
        <header className="flex items-center justify-between px-4 py-3 border-b border-[var(--color-border)] bg-[var(--color-card)]">
          <div className="flex items-center gap-3">
            <svg className="w-5 h-5 text-[var(--color-text)] shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" /></svg>
            <div>
              <p className="text-sm font-bold text-[var(--color-text)] leading-tight">{testTitle}</p>
              <p className="text-xs text-[var(--color-text-muted)] leading-tight">Stage {currentItemIndex + 1} of {allItems.length} • {itemType}</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <ThemeToggle />
            <span className="text-sm font-mono text-[var(--color-text-muted)] tabular-nums" title="Elapsed time">{formatElapsed(elapsedSeconds)}</span>
            {mode !== 'exam' && (
              <button type="button" onClick={() => setModal('review')} className="px-3 py-1.5 text-sm font-medium text-[var(--color-text)] hover:bg-[var(--color-surface)] rounded-lg">Review</button>
            )}
            {mode !== 'exam' && (
              <button type="button" onClick={() => setModal('transcript')} className="px-3 py-1.5 text-sm font-medium text-[var(--color-text)] hover:bg-[var(--color-surface)] rounded-lg">Transcript</button>
            )}
            {mode !== 'exam' && (
              <button type="button" onClick={() => setModal('settings')} className="px-3 py-1.5 text-sm font-medium text-[var(--color-text)] hover:bg-[var(--color-surface)] rounded-lg">Settings</button>
            )}
            <button type="button" className="w-9 h-9 rounded-full bg-[var(--color-primary)] text-white flex items-center justify-center hover:opacity-90" aria-label="Menu">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" /></svg>
            </button>
          </div>
        </header>

        <main className="flex-1 p-4 md:p-6 max-w-3xl mx-auto w-full flex flex-col items-center">
          <div className="w-full max-w-2xl">
            <AudioPlayer
              src={audioSrc}
              sessionId={session?.id}
              logEvent={logEvent}
              imageUrl={thumbnailUrl || undefined}
              imageLabel={imageLabel}
              itemType={currentItem?.item_type || 'conversation'}
              onEnded={handleAudioEnded}
              mode={mode}
            />
          </div>
        </main>

        {/* Footer: Back (left) | Continue with yellow arrow (right) */}
        <footer className="flex items-center justify-between px-4 py-4 border-t border-[var(--color-border)] bg-[var(--color-card)]">
          <button
            type="button"
            onClick={() => navigate(-1)}
            className="inline-flex items-center gap-2 text-sm font-medium text-[var(--color-text-muted)] hover:text-[var(--color-text)]"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" /></svg>
            Back
          </button>
          <button
            type="button"
            onClick={() => setPhase('questions')}
            className="inline-flex items-center gap-2 text-sm font-medium text-[var(--color-text)]"
          >
            Continue
            <span className="w-8 h-8 rounded-full bg-[var(--color-accent)] flex items-center justify-center border-2 border-[var(--color-primary)]/20">
              <svg className="w-4 h-4 ml-0.5" fill="currentColor" viewBox="0 0 24 24"><path d="M8 5v14l11-7z" /></svg>
            </span>
          </button>
        </footer>

        {/* Modals (popups with animation) */}
        {mode !== 'exam' && (
          <Modal open={modal === 'transcript'} onClose={() => setModal(null)} title="Transcript">
            <p className="text-sm text-[var(--color-text-muted)] mb-2 underline">Follow the line</p>
            <div className="text-[var(--color-text)] leading-relaxed whitespace-pre-wrap">{currentItem?.transcript || 'No transcript.'}</div>
          </Modal>
        )}
        {mode !== 'exam' && (
          <Modal open={modal === 'review'} onClose={() => setModal(null)} title="Review">
            <ReviewModalContent answersForReview={answersForReview} />
          </Modal>
        )}
        {mode !== 'exam' && (
          <SettingsModal
            open={modal === 'settings'}
            onClose={() => setModal(null)}
            onSave={(s) => setSettingsSnapshot(s)}
          />
        )}
      </div>
    );
  }

  // ---------- Phase: Questions (header with icons like Figma) ----------
  return (
    <div className="min-h-screen bg-[var(--color-surface)] flex flex-col">
      {/* Header: + Test Prep Pro | Quit, Back, icons */}
      <header className="flex items-center justify-between px-4 py-3 border-b border-[var(--color-border)] bg-[var(--color-card)]">
        <div className="flex items-center gap-2">
          <span className="text-lg font-bold text-[var(--color-text)]">+ Test Prep Pro</span>
          <span className="text-sm text-[var(--color-text-muted)]">Stage {currentItemIndex + 1} of {allItems.length} • Question {questionIndex + 1} of {questionsList.length}</span>
          <span className="text-sm font-mono text-[var(--color-text-muted)] tabular-nums" title="Elapsed time">{formatElapsed(elapsedSeconds)}</span>
        </div>
        <div className="flex items-center gap-1">
          <ThemeToggle />
          <Link to="/" className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg bg-[var(--color-accent)] text-[var(--color-text)] font-semibold border border-[var(--color-primary)]/20 hover:opacity-90">Quit</Link>
          <button type="button" onClick={() => setPhase('player')} className="px-3 py-2 text-sm font-medium text-[var(--color-text)] hover:bg-[var(--color-surface)] rounded-lg">Back</button>
          {mode !== 'exam' && (
            <IconButton onClick={() => setModal('help')} label="Help">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={1.8}><path strokeLinecap="round" strokeLinejoin="round" d="M9.879 7.519c1.171-1.025 3.071-1.025 4.242 0 1.172 1.025 1.172 2.687 0 3.712-.203.179-.43.326-.67.442-.745.361-1.45.999-1.45 1.827v.75M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9 5.25h.008v.008H12v-.008z" /></svg>
            </IconButton>
          )}
          {mode !== 'exam' && (
            <IconButton onClick={() => setModal('review')} label="Review answers">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={1.8}><path strokeLinecap="round" strokeLinejoin="round" d="M9 12h3.75M9 15h3.75M9 18h3.75m3 .75H18a2.25 2.25 0 002.25-2.25V6.108c0-1.135-.845-2.098-1.976-2.192a48.424 48.424 0 00-1.123-.08m-5.801 0c-.065.21-.1.433-.1.664 0 .414.336.75.75.75h4.5a.75.75 0 00.75-.75 2.25 2.25 0 00-.1-.664m-5.8 0A2.251 2.251 0 0113.5 2.25H15c1.012 0 1.867.668 2.15 1.586m-5.8 0c-.376.023-.75.05-1.124.08C9.095 4.01 8.25 4.973 8.25 6.108V8.25m0 0H4.875c-.621 0-1.125.504-1.125 1.125v11.25c0 .621.504 1.125 1.125 1.125h9.75c.621 0 1.125-.504 1.125-1.125V9.375c0-.621-.504-1.125-1.125-1.125H8.25z" /></svg>
            </IconButton>
          )}
          {mode !== 'exam' && (
            <IconButton onClick={() => setModal('transcript')} label="Transcript">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={1.8}><path strokeLinecap="round" strokeLinejoin="round" d="M8.625 12a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0H8.25m4.125 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0H12m4.125 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0h-.375M21 12c0 4.556-4.03 8.25-9 8.25a9.764 9.764 0 01-2.555-.337A5.972 5.972 0 015.41 20.97a5.969 5.969 0 01-.474-.065 4.48 4.48 0 00.978-2.025c.09-.457-.133-.901-.467-1.226C3.93 16.178 3 14.189 3 12c0-4.556 4.03-8.25 9-8.25s9 3.694 9 8.25z" /></svg>
            </IconButton>
          )}
          {mode !== 'exam' && (
            <IconButton onClick={() => setModal('analysis')} label="Analysis">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={1.8}><path strokeLinecap="round" strokeLinejoin="round" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 013 19.875v-6.75zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V8.625zM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V4.125z" /></svg>
            </IconButton>
          )}
          {mode !== 'exam' && (
            <IconButton onClick={() => setModal('settings')} label="Settings">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={1.8}><path strokeLinecap="round" strokeLinejoin="round" d="M9.594 3.94c.09-.542.56-.94 1.11-.94h2.593c.55 0 1.02.398 1.11.94l.213 1.281c.063.374.313.686.645.87.074.04.147.083.22.127.324.196.72.257 1.075.124l1.217-.456a1.125 1.125 0 011.37.49l1.296 2.247a1.125 1.125 0 01-.26 1.431l-1.003.827c-.293.24-.438.613-.431.992a6.759 6.759 0 010 .255c-.007.378.138.75.43.99l1.005.828c.424.35.534.954.26 1.43l-1.298 2.247a1.125 1.125 0 01-1.369.491l-1.217-.456c-.355-.133-.75-.072-1.076.124a6.57 6.57 0 01-.22.128c-.331.183-.581.495-.644.869l-.213 1.28c-.09.543-.56.941-1.11.941h-2.594c-.55 0-1.02-.398-1.11-.94l-.213-1.281c-.062-.374-.312-.686-.644-.87a6.52 6.52 0 01-.22-.127c-.325-.196-.72-.257-1.076-.124l-1.217.456a1.125 1.125 0 01-1.369-.49l-1.297-2.247a1.125 1.125 0 01.26-1.431l1.004-.827c.292-.24.437-.613.43-.992a6.932 6.932 0 010-.255c.007-.378-.138-.75-.43-.99l-1.004-.828a1.125 1.125 0 01-.26-1.43l1.297-2.247a1.125 1.125 0 011.37-.491l1.216.456c.356.133.751.072 1.076-.124.072-.044.146-.087.22-.128.332-.183.582-.495.644-.869l.214-1.281z" /><path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
            </IconButton>
          )}
          <IconButton label="Audio">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={1.8}><path strokeLinecap="round" strokeLinejoin="round" d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" /></svg>
          </IconButton>
          {mode !== 'exam' && (
            <button
              type="button"
              onClick={() => setModal('answer')}
              className="px-3 py-2 text-sm font-medium text-[var(--color-text)] hover:bg-[var(--color-surface)] rounded-lg border border-[var(--color-border)]"
            >
              Answer
            </button>
          )}
        </div>
      </header>

      <main className="flex-1 p-4 md:p-6 max-w-3xl mx-auto w-full">
        {currentQ && (
          <div onFocus={() => { answerStartRef.current = performance.now(); }}>
            <QuestionCard
              question={currentQ}
              onSubmit={handleSubmitAnswer}
              disabled={false}
              feedback={feedback}
              mode={mode}
              questionIndex={questionIndex}
              totalQuestions={questionsList.length}
              answeredCount={answersForReview.length}
              onSelectQuestion={setQuestionIndex}
            />
          </div>
        )}

        {mode === 'practice' && feedback && !isLastQuestionOfStage && (
          <div className="flex justify-end mt-4">
            <button type="button" onClick={goToNext} className="px-6 py-2.5 rounded-xl bg-[var(--color-accent)] text-[var(--color-text)] font-semibold border border-[var(--color-primary)]/20 hover:opacity-90">Continue →</button>
          </div>
        )}
        {feedback && isLastQuestionOfStage && !isLastStage && (
          <div className="flex justify-end mt-4">
            <button
              type="button"
              onClick={() => {
                setCurrentItemIndex((i) => i + 1);
                setPhase('player');
                setQuestionIndex(0);
                setFeedback(null);
              }}
              className="px-6 py-2.5 rounded-xl bg-[var(--color-accent)] text-[var(--color-text)] font-semibold border border-[var(--color-primary)]/20 hover:opacity-90"
            >
              {mode === 'practice' ? 'Continue to next lecture →' : 'Next section →'}
            </button>
          </div>
        )}
        {isLastQuestion && (feedback || mode === 'exam') && (
          <div className="flex justify-end mt-4">
            <button
              type="button"
              onClick={() => setPhase('review')}
              className="px-6 py-2.5 rounded-xl bg-[var(--color-accent)] text-[var(--color-text)] font-semibold border border-[var(--color-primary)]/20 hover:opacity-90"
            >
              Review answers
            </button>
          </div>
        )}

        {questionsList.length === 0 && <p className="text-[var(--color-text-muted)]">No questions.</p>}
      </main>

      {mode !== 'exam' && (
        <Modal open={modal === 'transcript'} onClose={() => setModal(null)} title="Transcript">
          <p className="text-sm text-[var(--color-text-muted)] mb-2 underline">Follow the line</p>
          <div className="text-[var(--color-text)] leading-relaxed whitespace-pre-wrap">{currentItem?.transcript || 'No transcript.'}</div>
        </Modal>
      )}
      {mode !== 'exam' && (
        <Modal open={modal === 'review'} onClose={() => setModal(null)} title="Review">
          <ReviewModalContent answersForReview={answersForReview} />
        </Modal>
      )}
      {mode !== 'exam' && (
        <SettingsModal
          open={modal === 'settings'}
          onClose={() => setModal(null)}
          onSave={(s) => setSettingsSnapshot(s)}
        />
      )}
      {mode !== 'exam' && (
        <Modal open={modal === 'help'} onClose={() => setModal(null)} title="Help">
          <p className="text-[var(--color-text-muted)] text-sm leading-relaxed">
            Listen to the audio, then answer each question. Use <strong>Review</strong> to see your answers so far.
            Use <strong>Analysis</strong> after submitting an answer to see why the correct option is right.
            Use <strong>Transcript</strong> to read the audio text. When you finish all questions, click Finish to see your score.
          </p>
        </Modal>
      )}
      {mode !== 'exam' && (
        <Modal open={modal === 'analysis'} onClose={() => setModal(null)} title="Analysis">
          <AnalysisModalContent feedback={lastAnalysisFeedback ?? feedback} currentQuestion={lastAnalysisQuestion ?? currentQ} />
        </Modal>
      )}
      {mode !== 'exam' && (
        <Modal open={modal === 'answer'} onClose={() => setModal(null)} title="Answer">
          <AnswerModalContent question={currentQ} />
        </Modal>
      )}
    </div>
  );
}
