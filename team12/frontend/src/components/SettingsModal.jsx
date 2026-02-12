import { useEffect, useState } from 'react';
import { loadSettings, saveSettings } from '../lib/settings';

function Toggle({ checked, onChange }) {
  return (
    <button
      type="button"
      role="switch"
      aria-checked={checked}
      onClick={() => onChange(!checked)}
      className={`relative inline-flex h-6 w-11 shrink-0 rounded-full border-2 transition-colors ${checked ? 'bg-[var(--color-accent)] border-[var(--color-accent)]' : 'bg-[var(--color-border)] border-[var(--color-border)]'}`}
    >
      <span
        className={`pointer-events-none inline-block h-5 w-5 rounded-full bg-white shadow ring-0 transition translate-y-0.5 ${checked ? 'translate-x-5' : 'translate-x-0.5'}`}
      />
    </button>
  );
}

export function SettingsModal({ open, onClose, onSave }) {
  const [settings, setSettings] = useState(() => loadSettings());
  const [lastSaved, setLastSaved] = useState(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (open) {
      setSettings(loadSettings());
      setLastSaved(null);
    }
  }, [open]);

  const updateSelectBox = (key, value) => {
    setSettings((s) => ({ ...s, selectBox: { ...s.selectBox, [key]: value } }));
  };
  const updateExam = (key, value) => {
    setSettings((s) => ({ ...s, exam: { ...s.exam, [key]: value } }));
  };
  const updateWriting = (key, value) => {
    setSettings((s) => ({ ...s, writing: { ...s.writing, [key]: value } }));
  };

  const handleSave = () => {
    setSaving(true);
    saveSettings(settings);
    setLastSaved('Just now');
    setSaving(false);
    onSave?.(settings);
  };

  const handleCancel = () => {
    setSettings(loadSettings());
    onClose?.();
  };

  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50"
      style={{ animation: 'modalOverlayIn 0.2s ease-out' }}
      onClick={onClose}
    >
      <div
        className="bg-[var(--color-card)] rounded-2xl shadow-xl w-full max-w-4xl max-h-[90vh] overflow-hidden flex flex-col"
        style={{ animation: 'modalContentIn 0.25s ease-out' }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Yellow bar: AudioMaster | profile */}
        <div className="flex items-center justify-between px-6 py-3 bg-[var(--color-accent)] shrink-0">
          <span className="font-bold text-[var(--color-text)]">AudioMaster</span>
          <button
            type="button"
            onClick={onClose}
            className="p-1.5 rounded-lg hover:bg-black/10 text-[var(--color-text)]"
            aria-label="Close"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /></svg>
          </button>
        </div>

        <div className="px-6 pt-4 pb-2">
          <h2 className="text-2xl font-bold text-[var(--color-primary)]">Settings</h2>
          <p className="text-sm text-[var(--color-text-muted)] mt-1">Manage your learning preferences and exam environment.</p>
        </div>

        <div className="px-6 pb-4 overflow-y-auto flex-1 min-h-0">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Select Box Settings */}
            <div className="rounded-xl border border-[var(--color-border)] bg-[var(--color-card)] p-4">
              <div className="flex items-center gap-2 mb-4">
                <svg className="w-5 h-5 text-[var(--color-primary)]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" /></svg>
                <h3 className="font-semibold text-[var(--color-text)]">Select Box Settings</h3>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {[
                  { key: 'vocabularyCom', label: 'Vocabulary.com' },
                  { key: 'googleTranslate', label: 'Google Translate' },
                  { key: 'selectBox', label: 'Select Box' },
                  { key: 'pronounceOption', label: 'Pronounce Option' },
                  { key: 'highlightOption', label: 'Highlight Option' },
                  { key: 'leitnerOption', label: 'Leitner Option' },
                  { key: 'copyTextOption', label: 'Copy Text Option' },
                ].map(({ key, label }) => (
                  <div key={key} className="flex items-center justify-between gap-2">
                    <span className="text-sm text-[var(--color-text)]">{label}</span>
                    <Toggle checked={settings.selectBox[key]} onChange={(v) => updateSelectBox(key, v)} />
                  </div>
                ))}
              </div>
            </div>

            {/* Exam Settings */}
            <div className="rounded-xl border border-[var(--color-border)] bg-[var(--color-card)] p-4">
              <div className="flex items-center gap-2 mb-4">
                <svg className="w-5 h-5 text-[var(--color-primary)]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 14l9-5-9-5-9 5 9 5z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 14l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14z" /></svg>
                <h3 className="font-semibold text-[var(--color-text)]">Exam Settings</h3>
              </div>
              <div className="space-y-4">
                <div>
                  <div className="flex items-center justify-between gap-2">
                    <span className="text-sm font-medium text-[var(--color-text)]">Play Background Noise</span>
                    <Toggle checked={settings.exam.playBackgroundNoise} onChange={(v) => updateExam('playBackgroundNoise', v)} />
                  </div>
                  <p className="text-xs text-[var(--color-text-muted)] mt-1">Simulates exam room environment</p>
                </div>
                <div>
                  <div className="flex items-center justify-between gap-2 mb-1">
                    <span className="text-sm font-medium text-[var(--color-text)]">Background Noise Volume</span>
                    <span className="text-sm text-[var(--color-text-muted)] tabular-nums">{settings.exam.backgroundNoiseVolume}%</span>
                  </div>
                  <div className="flex items-center gap-2 text-xs text-[var(--color-text-muted)] mb-1">
                    <span>Quiet</span>
                    <input
                      type="range"
                      min="0"
                      max="100"
                      value={settings.exam.backgroundNoiseVolume}
                      onChange={(e) => updateExam('backgroundNoiseVolume', Number(e.target.value))}
                      style={{
                        background: `linear-gradient(to right, var(--color-accent) 0%, var(--color-accent) ${settings.exam.backgroundNoiseVolume}%, var(--color-border) ${settings.exam.backgroundNoiseVolume}%, var(--color-border) 100%)`,
                      }}
                      className="flex-1 h-2 rounded-full appearance-none [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-4 [&::-webkit-slider-thumb]:h-4 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-[var(--color-accent)] [&::-webkit-slider-thumb]:cursor-pointer [&::-moz-range-thumb]:w-4 [&::-moz-range-thumb]:h-4 [&::-moz-range-thumb]:rounded-full [&::-moz-range-thumb]:bg-[var(--color-accent)] [&::-moz-range-thumb]:border-0"
                    />
                    <span>Loud</span>
                  </div>
                  <div className="flex items-start gap-2 mt-3 p-3 rounded-lg bg-[var(--color-accent)]/20 border border-[var(--color-accent)]/40">
                    <svg className="w-5 h-5 text-[var(--color-primary)] shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z" /></svg>
                    <p className="text-sm text-[var(--color-text)]">Enabling background noise is recommended for realistic exam preparation.</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Writing Textarea Settings */}
            <div className="rounded-xl border border-[var(--color-border)] bg-[var(--color-card)] p-4 md:col-span-2">
              <div className="flex items-center gap-2 mb-4">
                <svg className="w-5 h-5 text-[var(--color-primary)]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 10h16M4 14h16M4 18h16" /></svg>
                <h3 className="font-semibold text-[var(--color-text)]">Writing Textarea Settings</h3>
              </div>
              <div>
                <div className="flex items-center justify-between gap-2">
                  <span className="text-sm font-medium text-[var(--color-text)]">Display Export Button</span>
                  <Toggle checked={settings.writing.displayExportButton} onChange={(v) => updateWriting('displayExportButton', v)} />
                </div>
                <p className="text-xs text-[var(--color-text-muted)] mt-1">Allows you to export your writing as a text file</p>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between px-6 py-4 border-t border-[var(--color-border)] bg-[var(--color-surface)] shrink-0">
          <span className="text-sm text-[var(--color-text-muted)]">{lastSaved ? `Last saved: ${lastSaved}` : '\u00A0'}</span>
          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={handleCancel}
              className="px-4 py-2 text-sm font-medium text-[var(--color-text-muted)] hover:text-[var(--color-text)]"
            >
              Cancel
            </button>
            <button
              type="button"
              onClick={handleSave}
              disabled={saving}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-[var(--color-accent)] text-[var(--color-text)] font-semibold border border-[var(--color-primary)]/20 hover:opacity-90 disabled:opacity-70"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4" /></svg>
              Save Changes
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
