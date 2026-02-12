import { useRef, useState, useEffect, useCallback } from 'react';

const SPEEDS = [1, 1.25, 1.5];

// Illustration: two people in conversation
function ConversationIllustration({ className }) {
  return (
    <svg className={className} viewBox="0 0 120 80" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden>
      {/* Left person */}
      <circle cx="38" cy="26" r="12" fill="currentColor" opacity="0.85" />
      <ellipse cx="38" cy="52" rx="14" ry="18" fill="currentColor" opacity="0.85" />
      {/* Right person */}
      <circle cx="82" cy="26" r="12" fill="currentColor" opacity="0.85" />
      <ellipse cx="82" cy="52" rx="14" ry="18" fill="currentColor" opacity="0.85" />
      {/* Speech/dialogue hint between them */}
      <path d="M52 32c0-2 2-3 4-3s4 1 4 3" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" opacity="0.5" fill="none" />
      <path d="M64 32c0-2 2-3 4-3s4 1 4 3" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" opacity="0.5" fill="none" />
    </svg>
  );
}

// Illustration: single person (lecturer at podium)
function LectureIllustration({ className }) {
  return (
    <svg className={className} viewBox="0 0 120 80" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden>
      {/* Podium / board */}
      <rect x="18" y="36" width="36" height="28" rx="3" fill="currentColor" opacity="0.12" />
      <line x1="22" y1="44" x2="50" y2="44" stroke="currentColor" strokeWidth="1.5" opacity="0.25" />
      <line x1="22" y1="52" x2="48" y2="52" stroke="currentColor" strokeWidth="1.5" opacity="0.25" />
      <line x1="22" y1="58" x2="44" y2="58" stroke="currentColor" strokeWidth="1.5" opacity="0.25" />
      {/* Lecturer */}
      <circle cx="78" cy="28" r="14" fill="currentColor" opacity="0.9" />
      <path d="M66 46v6c0 4 6 8 12 8s12-4 12-8v-6" fill="currentColor" opacity="0.9" />
      <rect x="72" y="68" width="12" height="4" rx="1" fill="currentColor" opacity="0.35" />
    </svg>
  );
}

export default function AudioPlayer({
  src,
  sessionId,
  logEvent,
  imageUrl,
  imageLabel = 'Conversation',
  itemType = 'conversation',
  onEnded,
  showContinueButton,
  mode = 'practice',
}) {
  const audioRef = useRef(null);
  const [playing, setPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [speedIndex, setSpeedIndex] = useState(0);
  const [volume, setVolume] = useState(100); // 0-100
  // Blob URL so seeking works without server Range support
  const [blobSrc, setBlobSrc] = useState(null);
  const [blobReady, setBlobReady] = useState(false);
  const blobUrlRef = useRef(null);

  const updateTime = useCallback(() => {
    const el = audioRef.current;
    if (el) {
      setCurrentTime(el.currentTime);
      setDuration(el.duration || 0);
    }
  }, []);

  useEffect(() => {
    const el = audioRef.current;
    if (!el) return;
    el.playbackRate = SPEEDS[speedIndex];
  }, [speedIndex]);

  useEffect(() => {
    const el = audioRef.current;
    if (!el) return;
    el.volume = volume / 100;
    el.muted = volume === 0;
  }, [volume]);

  // Fetch audio as blob so seeking works when server doesn't support Range requests
  useEffect(() => {
    if (!src) {
      if (blobUrlRef.current) {
        URL.revokeObjectURL(blobUrlRef.current);
        blobUrlRef.current = null;
      }
      setBlobSrc(null);
      setBlobReady(true);
      return;
    }
    setBlobReady(false);
    let cancelled = false;
    fetch(src, { mode: 'cors' })
      .then((res) => res.blob())
      .then((blob) => {
        if (cancelled) return;
        if (blobUrlRef.current) URL.revokeObjectURL(blobUrlRef.current);
        blobUrlRef.current = URL.createObjectURL(blob);
        setBlobSrc(blobUrlRef.current);
        setBlobReady(true);
      })
      .catch(() => {
        if (!cancelled) {
          setBlobSrc(null);
          setBlobReady(true); // fallback to direct src
        }
      });
    return () => {
      cancelled = true;
      if (blobUrlRef.current) {
        URL.revokeObjectURL(blobUrlRef.current);
        blobUrlRef.current = null;
      }
      setBlobSrc(null);
    };
  }, [src]);

  useEffect(() => {
    const el = audioRef.current;
    if (!el) return;
    const handleEnded = () => {
      setPlaying(false);
      onEnded?.();
    };
    el.addEventListener('timeupdate', updateTime);
    el.addEventListener('loadedmetadata', updateTime);
    el.addEventListener('ended', handleEnded);
    return () => {
      el.removeEventListener('timeupdate', updateTime);
      el.removeEventListener('loadedmetadata', updateTime);
      el.removeEventListener('ended', handleEnded);
    };
  }, [updateTime, blobSrc, src, onEnded]);

  const togglePlay = () => {
    const el = audioRef.current;
    if (!el) return;
    if (playing) el.pause();
    else el.play();
    setPlaying(!playing);
  };

  const handleReplay = () => {
    const el = audioRef.current;
    if (el) {
      el.currentTime = 0;
      el.play();
      setPlaying(true);
    }
    if (sessionId && logEvent) logEvent(sessionId, 'replay', 1);
  };

  const skip = (e, delta) => {
    e.preventDefault();
    e.stopPropagation();
    const el = audioRef.current;
    if (!el) return;
    // Use Infinity when duration not yet loaded so we don't clamp to 0 and restart
    const dur = Number.isFinite(el.duration) && el.duration > 0 ? el.duration : Infinity;
    const next = Math.max(0, Math.min(dur, el.currentTime + delta));
    if (Number.isFinite(next)) {
      el.currentTime = next;
      setCurrentTime(next);
    }
  };

  const setVolumeFromInput = (value) => {
    const n = Math.max(0, Math.min(100, Number(value)));
    setVolume(n);
  };

  const handleDownload = async (e) => {
    e.preventDefault();
    if (!src) return;
    try {
      const res = await fetch(src, { mode: 'cors' });
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = src.split('/').pop() || 'audio.mp3';
      a.click();
      URL.revokeObjectURL(url);
    } catch {
      window.open(src, '_blank');
    }
  };

  const cycleSpeed = () => {
    setSpeedIndex((i) => (i + 1) % SPEEDS.length);
  };

  const handleSeek = (e) => {
    const el = audioRef.current;
    if (!el) return;
    const rect = e.currentTarget.getBoundingClientRect();
    const p = (e.clientX - rect.left) / rect.width;
    el.currentTime = p * el.duration;
    setCurrentTime(el.currentTime);
  };

  const formatTime = (t) => {
    if (!t || isNaN(t)) return '00:00';
    const m = Math.floor(t / 60);
    const s = Math.floor(t % 60);
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  if (!src) return null;

  const displayLabel = imageLabel || 'Conversation';
  const audioSrc = blobSrc || src;

  if (!blobReady) {
    return (
      <div className="rounded-2xl bg-[var(--color-card)] shadow-lg border-2 border-[var(--color-selected)] overflow-hidden p-8 text-center">
        <p className="text-[var(--color-text-muted)]">Loading audio...</p>
      </div>
    );
  }

  return (
    <>
      <audio ref={audioRef} src={audioSrc} preload="auto" />
      <div className="rounded-2xl bg-[var(--color-card)] shadow-lg border-2 border-[var(--color-selected)] overflow-hidden">
        {/* Image area with overlay label – thumbnail shown smaller inside container */}
        <div className="relative aspect-video bg-[var(--color-surface)] overflow-hidden flex items-center justify-center p-4">
          {imageUrl ? (
            <img src={imageUrl} alt="" className="max-w-full max-h-full w-auto h-auto object-contain rounded-lg" />
          ) : (
            <div className="absolute inset-0 flex items-center justify-center bg-gradient-to-br from-[var(--color-primary)]/10 to-[var(--color-primary)]/5">
              {itemType === 'lecture' ? (
                <LectureIllustration className="w-32 h-full max-h-28 text-[var(--color-primary)]/40 object-contain" />
              ) : (
                <ConversationIllustration className="w-32 h-full max-h-28 text-[var(--color-primary)]/40 object-contain" />
              )}
            </div>
          )}
          <span className="absolute bottom-3 left-3 px-3 py-1.5 rounded-lg bg-black/70 text-white text-sm font-medium">
            {displayLabel}
          </span>
        </div>

        {/* Progress bar */}
        <div className="px-4 pt-3">
          <div className="flex items-center gap-3">
            <span className="text-sm text-[var(--color-text-muted)] tabular-nums w-10">{formatTime(currentTime)}</span>
            <div
              className="flex-1 h-2 bg-[var(--color-border)] rounded-full cursor-pointer overflow-hidden"
              onClick={handleSeek}
              role="progressbar"
            >
              <div
                className="h-full bg-[var(--color-primary)] rounded-full transition-all"
                style={{ width: duration ? `${(currentTime / duration) * 100}%` : 0 }}
              />
            </div>
            <span className="text-sm text-[var(--color-text-muted)] tabular-nums w-10">{formatTime(duration)}</span>
          </div>
        </div>

        {/* Controls: Volume slider | Speed 1x | Rewind 10 | Play | Forward 10 | Download */}
        <div className="px-4 pb-4 pt-2 flex items-center justify-center gap-3 flex-wrap">
          <div className="flex items-center gap-2 min-w-[100px] max-w-[120px]" title="Volume">
            <span className="text-[var(--color-text-muted)] shrink-0" aria-hidden>
              {volume === 0 ? (
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 9l6 6m0-6l-6 6" /></svg>
              ) : (
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" /></svg>
              )}
            </span>
            <input
              type="range"
              min={0}
              max={100}
              value={volume}
              onChange={(e) => setVolumeFromInput(e.target.value)}
              className="w-full h-1.5 accent-[var(--color-primary)] bg-[var(--color-border)] rounded-full appearance-none cursor-pointer [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-3 [&::-webkit-slider-thumb]:h-3 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-[var(--color-primary)] [&::-webkit-slider-thumb]:cursor-pointer [&::-moz-range-thumb]:w-3 [&::-moz-range-thumb]:h-3 [&::-moz-range-thumb]:rounded-full [&::-moz-range-thumb]:bg-[var(--color-primary)] [&::-moz-range-thumb]:border-0"
              aria-label="Volume"
            />
          </div>
          {mode !== 'exam' && (
            <button
              type="button"
              onClick={cycleSpeed}
              className="px-3 py-1.5 rounded-lg bg-[var(--color-surface)] text-[var(--color-text)] text-sm font-medium hover:bg-[var(--color-border)]"
            >
              {SPEEDS[speedIndex]}x
            </button>
          )}
          <button
            type="button"
            onClick={(e) => skip(e, -10)}
            className="w-12 h-12 rounded-full border-2 border-[var(--color-border)] text-[var(--color-text-muted)] hover:text-[var(--color-text)] hover:border-[var(--color-primary)] flex flex-col items-center justify-center gap-0"
            title="Back 10s"
          >
            <svg className="w-5 h-5 -mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12.066 11.2a1 1 0 000 1.6l5.334 4A1 1 0 0019 16V8a1 1 0 00-1.6-.8l-5.333 4zM4.066 11.2a1 1 0 000 1.6l5.334 4A1 1 0 0011 16V8a1 1 0 00-1.6-.8l-5.334 4z" /></svg>
            <span className="text-[10px] font-medium leading-none">10</span>
          </button>
          <button
            type="button"
            onClick={togglePlay}
            className="w-14 h-14 rounded-full bg-[var(--color-accent)] text-[var(--color-text)] flex items-center justify-center hover:opacity-90 transition shadow-md border-2 border-[var(--color-primary)]/20"
            aria-label={playing ? 'Pause' : 'Play'}
          >
            {playing ? (
              <svg className="w-7 h-7" fill="currentColor" viewBox="0 0 24 24"><rect x="6" y="4" width="4" height="16" /><rect x="14" y="4" width="4" height="16" /></svg>
            ) : (
              <svg className="w-7 h-7 ml-0.5" fill="currentColor" viewBox="0 0 24 24"><path d="M8 5v14l11-7z" /></svg>
            )}
          </button>
          <button
            type="button"
            onClick={(e) => skip(e, 10)}
            className="w-12 h-12 rounded-full border-2 border-[var(--color-border)] text-[var(--color-text-muted)] hover:text-[var(--color-text)] hover:border-[var(--color-primary)] flex flex-col items-center justify-center gap-0"
            title="Forward 10s"
          >
            <svg className="w-5 h-5 -mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11.933 12.8a1 1 0 000-1.6L6.6 7.2A1 1 0 005 8v8a1 1 0 001.6.8l5.333-4zM19.933 12.8a1 1 0 000-1.6l-5.333-4A1 1 0 0013 8v8a1 1 0 001.6.8l5.333-4z" /></svg>
            <span className="text-[10px] font-medium leading-none">10</span>
          </button>
          {mode !== 'exam' && (
            <button
              type="button"
              onClick={handleDownload}
              className="p-2 text-[var(--color-text-muted)] hover:text-[var(--color-text)]"
              title="Download"
              aria-label="Download"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" /></svg>
            </button>
          )}
        </div>

        {showContinueButton && (
          <div className="px-4 pb-4 pt-0 border-t border-[var(--color-border)] flex justify-end">
            {showContinueButton}
          </div>
        )}
      </div>
    </>
  );
}
