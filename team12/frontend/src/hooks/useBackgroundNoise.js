import { useEffect, useRef } from 'react';

/**
 * Plays looping white noise via Web Audio API when enabled.
 * @param {boolean} enabled
 * @param {number} volumePercent 0-100
 */
export function useBackgroundNoise(enabled, volumePercent = 50) {
  const ctxRef = useRef(null);
  const sourceRef = useRef(null);

  useEffect(() => {
    if (!enabled) {
      if (sourceRef.current) {
        try { sourceRef.current.stop(); } catch (_) {}
        sourceRef.current = null;
      }
      if (ctxRef.current) {
        ctxRef.current.close();
        ctxRef.current = null;
      }
      return;
    }

    const ctx = new (window.AudioContext || window.webkitAudioContext)();
    ctxRef.current = ctx;

    const bufferSize = 2 * ctx.sampleRate;
    const buffer = ctx.createBuffer(1, bufferSize, ctx.sampleRate);
    const data = buffer.getChannelData(0);
    for (let i = 0; i < bufferSize; i++) {
      data[i] = (Math.random() * 2 - 1) * 0.5;
    }

    const source = ctx.createBufferSource();
    source.buffer = buffer;
    source.loop = true;

    const gainNode = ctx.createGain();
    gainNode.gain.value = (volumePercent / 100) * 0.2;
    source.connect(gainNode);
    gainNode.connect(ctx.destination);

    source.start(0);
    sourceRef.current = source;

    if (ctx.state === 'suspended') {
      ctx.resume().catch(() => {});
    }

    return () => {
      try { source.stop(); } catch (_) {}
      ctx.close();
      ctxRef.current = null;
      sourceRef.current = null;
    };
  }, [enabled, volumePercent]);

  return null;
}
