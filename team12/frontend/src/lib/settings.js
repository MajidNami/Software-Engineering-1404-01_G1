const STORAGE_KEY = 'toefl_listening_settings';

export const defaultSettings = {
  selectBox: {
    vocabularyCom: false,
    googleTranslate: true,
    selectBox: true,
    pronounceOption: false,
    highlightOption: true,
    leitnerOption: false,
    copyTextOption: true,
  },
  exam: {
    playBackgroundNoise: true,
    backgroundNoiseVolume: 45,
  },
  writing: {
    displayExportButton: true,
  },
};

export function loadSettings() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return { ...defaultSettings };
    const parsed = JSON.parse(raw);
    return {
      selectBox: { ...defaultSettings.selectBox, ...parsed.selectBox },
      exam: { ...defaultSettings.exam, ...parsed.exam },
      writing: { ...defaultSettings.writing, ...parsed.writing },
    };
  } catch {
    return { ...defaultSettings };
  }
}

export function saveSettings(settings) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(settings));
    return true;
  } catch {
    return false;
  }
}
