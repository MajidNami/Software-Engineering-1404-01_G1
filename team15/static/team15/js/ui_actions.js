(function () {
  const basePath = "/team15/api";
  const refreshPath = "/api/auth/refresh/";
  const refreshIntervalMs = 5 * 60 * 1000;
  let refreshTimerId = null;
  let refreshInFlight = false;

  function getBody() {
    return document.body || null;
  }

  function byId(id) {
    return document.getElementById(id);
  }

  function toInt(value, fallback) {
    const parsed = Number.parseInt(String(value || ""), 10);
    return Number.isFinite(parsed) ? parsed : fallback;
  }

  function showError(error) {
    const message = error instanceof Error ? error.message : String(error);
    window.alert(message || "Request failed");
  }

  async function api(path, opts) {
    const res = await fetch(`${basePath}${path}`, {
      credentials: "same-origin",
      headers: {
        "Content-Type": "application/json",
        ...(opts && opts.headers ? opts.headers : {}),
      },
      ...(opts || {}),
    });

    let data = {};
    try {
      data = await res.json();
    } catch (err) {
      data = {};
    }

    if (!res.ok) {
      if (res.status === 401) {
        const next = `${window.location.pathname}${window.location.search}`;
        window.location.href = `/auth/?next=${encodeURIComponent(next)}`;
      }
      throw new Error(data.detail || data.error || "Request failed");
    }
    return data;
  }

  async function refreshSession() {
    if (refreshInFlight) return;
    refreshInFlight = true;
    try {
      const res = await fetch(refreshPath, {
        method: "POST",
        credentials: "same-origin",
      });
      if (!res.ok && res.status !== 401) {
        throw new Error("Session refresh failed");
      }
    } catch (error) {
      // Keep silent to avoid interrupting user flow.
    } finally {
      refreshInFlight = false;
    }
  }

  function startSessionRefreshHeartbeat() {
    refreshSession();
    if (refreshTimerId) {
      window.clearInterval(refreshTimerId);
    }
    refreshTimerId = window.setInterval(refreshSession, refreshIntervalMs);
    document.addEventListener("visibilitychange", function () {
      if (!document.hidden) {
        refreshSession();
      }
    });
  }

  async function startFirstPracticeAttempt() {
    const tests = await api("/tests/?mode=practice");
    if (!Array.isArray(tests) || tests.length === 0) {
      throw new Error("No active practice test found.");
    }

    const test = tests[0];
    const start = await api("/attempts/start/", {
      method: "POST",
      body: JSON.stringify({ test_id: test.id }),
    });

    window.location.href = `/team15/practice-reading/?test_id=${test.id}&attempt_id=${start.attempt_id}&q=1`;
  }

  function setBusy(button, isBusy, busyText) {
    if (!button) return;
    if (isBusy) {
      button.dataset.originalText = button.textContent || "";
      button.textContent = busyText;
      button.disabled = true;
      return;
    }
    if (button.dataset.originalText) {
      button.textContent = button.dataset.originalText;
    }
    button.disabled = false;
  }

  function initDashboard() {
    const fullExamBtn = byId("dash-start-exam");
    const quickPracticeBtn = byId("dash-start-practice");
    const suggestPracticeBtn = byId("dash-suggest-practice");
    const readNowBtn = byId("dash-read-now");

    if (fullExamBtn) {
      fullExamBtn.addEventListener("click", function () {
        window.location.href = "/team15/exam-setup/";
      });
    }

    async function handleStartPractice(btn) {
      try {
        setBusy(btn, true, "Starting...");
        await startFirstPracticeAttempt();
      } catch (error) {
        window.location.href = "/team15/practice-reading/";
      }
    }

    if (quickPracticeBtn) {
      quickPracticeBtn.addEventListener("click", function () {
        handleStartPractice(quickPracticeBtn);
      });
    }

    if (suggestPracticeBtn) {
      suggestPracticeBtn.addEventListener("click", function () {
        handleStartPractice(suggestPracticeBtn);
      });
    }

    if (readNowBtn) {
      readNowBtn.addEventListener("click", function () {
        window.location.href = "/team15/progress/";
      });
    }
  }

  function initExamSetup() {
    const radios = Array.from(document.querySelectorAll("input[name='passage-selection']"));
    const estimatedTime = byId("exam-estimated-time");
    const confirmRules = byId("confirm-rules");
    const startBtn = byId("exam-start-button");

    function getSelectedRadio() {
      return document.querySelector("input[name='passage-selection']:checked");
    }

    function updateEstimatedTime() {
      const selected = getSelectedRadio();
      if (!selected || !estimatedTime) return;
      const minutes = selected.dataset.timeLimit || "0";
      estimatedTime.textContent = `${minutes} minutes`;
    }

    function updateStartDisabled() {
      if (!startBtn) return;
      const allowed = Boolean(confirmRules && confirmRules.checked);
      startBtn.disabled = !allowed;
    }

    radios.forEach(function (radio) {
      radio.addEventListener("change", updateEstimatedTime);
    });

    if (confirmRules) {
      confirmRules.addEventListener("change", updateStartDisabled);
    }

    updateEstimatedTime();
    updateStartDisabled();

    if (startBtn) {
      startBtn.addEventListener("click", async function () {
        const selected = getSelectedRadio();
        const selectedTestId = selected ? toInt(selected.dataset.testId || selected.value, 0) : 0;
        try {
          if (!selectedTestId) {
            throw new Error("Please select an exam option.");
          }

          setBusy(startBtn, true, "Starting...");
          const start = await api("/attempts/start/", {
            method: "POST",
            body: JSON.stringify({ test_id: selectedTestId }),
          });
          window.location.href = `/team15/exam-reading/?test_id=${selectedTestId}&attempt_id=${start.attempt_id}&q=1`;
        } catch (error) {
          if (selectedTestId) {
            window.location.href = `/team15/exam-reading/?test_id=${selectedTestId}&q=1`;
            return;
          }
          setBusy(startBtn, false, "Starting...");
          showError(error);
        }
      });
    }
  }

  function initExamReading() {
    const body = getBody();
    if (!body) return;

    const testId = toInt(body.dataset.testId, 0);
    const attemptId = toInt(body.dataset.attemptId, 0);
    const questionId = toInt(body.dataset.questionId, 0);
    const questionNumber = toInt(body.dataset.questionNumber, 0);
    const answeredCount = toInt(body.dataset.answeredCount, 0);
    const remainingFromServer = toInt(body.dataset.remainingSeconds, 0);
    const isTimeLimited = body.dataset.timeLimited === "1";

    const hideBtn = byId("exam-toggle-passage");
    const formatSizeBtn = byId("exam-format-size");
    const borderColorBtn = byId("exam-border-color");
    const passagePanel = byId("exam-passage-panel");
    const readingParagraphs = Array.from(document.querySelectorAll("[data-exam-paragraph='1']"));
    const timerHours = byId("exam-timer-hours");
    const timerMinutes = byId("exam-timer-minutes");
    const timerSeconds = byId("exam-timer-seconds");

    if (hideBtn && passagePanel) {
      hideBtn.addEventListener("click", function () {
        passagePanel.classList.toggle("hidden");
      });
    }

    const fontSizeStorageKey = "team15_exam_font_size_index";
    const highlightStorageKey = attemptId && questionId ? `team15_exam_highlight_${attemptId}_${questionId}` : "";
    const fontSizes = ["1rem", "1.1rem", "1.2rem"];
    let fontSizeIndex = toInt(localStorage.getItem(fontSizeStorageKey), 0);
    fontSizeIndex = Math.max(0, Math.min(fontSizeIndex, fontSizes.length - 1));
    let highlightModeEnabled = false;
    let highlightedParagraphIndices = new Set();

    if (highlightStorageKey) {
      try {
        const parsed = JSON.parse(localStorage.getItem(highlightStorageKey) || "[]");
        if (Array.isArray(parsed)) {
          highlightedParagraphIndices = new Set(parsed.map(String));
        }
      } catch (err) {
        highlightedParagraphIndices = new Set();
      }
    }

    function applyReadingFontSize() {
      readingParagraphs.forEach(function (paragraph) {
        paragraph.style.fontSize = fontSizes[fontSizeIndex];
      });
    }

    function applyReadingHighlights() {
      readingParagraphs.forEach(function (paragraph) {
        const paragraphIndex = String(paragraph.dataset.paragraphIndex || "");
        if (highlightedParagraphIndices.has(paragraphIndex)) {
          paragraph.style.backgroundColor = "rgba(255, 189, 46, 0.22)";
          paragraph.style.borderRadius = "0.5rem";
        } else {
          paragraph.style.backgroundColor = "";
          paragraph.style.borderRadius = "";
        }
      });
    }

    function syncHighlightButton() {
      if (!borderColorBtn) return;
      if (highlightModeEnabled) {
        borderColorBtn.classList.add("bg-primary/20", "border-primary/50");
      } else {
        borderColorBtn.classList.remove("bg-primary/20", "border-primary/50");
      }
      readingParagraphs.forEach(function (paragraph) {
        paragraph.style.cursor = highlightModeEnabled ? "pointer" : "text";
      });
    }

    applyReadingFontSize();
    applyReadingHighlights();
    syncHighlightButton();

    if (formatSizeBtn) {
      formatSizeBtn.addEventListener("click", function () {
        fontSizeIndex = (fontSizeIndex + 1) % fontSizes.length;
        localStorage.setItem(fontSizeStorageKey, String(fontSizeIndex));
        applyReadingFontSize();
      });
    }

    if (borderColorBtn) {
      borderColorBtn.addEventListener("click", function () {
        highlightModeEnabled = !highlightModeEnabled;
        syncHighlightButton();
      });
    }

    readingParagraphs.forEach(function (paragraph) {
      paragraph.addEventListener("click", function () {
        if (!highlightModeEnabled) return;
        const paragraphIndex = String(paragraph.dataset.paragraphIndex || "");
        if (!paragraphIndex) return;
        if (highlightedParagraphIndices.has(paragraphIndex)) {
          highlightedParagraphIndices.delete(paragraphIndex);
        } else {
          highlightedParagraphIndices.add(paragraphIndex);
        }
        applyReadingHighlights();
        if (highlightStorageKey) {
          localStorage.setItem(highlightStorageKey, JSON.stringify(Array.from(highlightedParagraphIndices)));
        }
      });
    });

    const inputs = Array.from(document.querySelectorAll("input[name='exam-choice']"));
    const storageKey = attemptId ? `team15_exam_answers_${attemptId}` : "";
    const timeStorageKey = attemptId ? `team15_exam_times_${attemptId}` : "";
    const questionStartKey = attemptId && questionId ? `team15_exam_qstart_${attemptId}_${questionId}` : "";

    let savedAnswers = {};
    if (storageKey) {
      try {
        savedAnswers = JSON.parse(localStorage.getItem(storageKey) || "{}");
      } catch (err) {
        savedAnswers = {};
      }
    }

    let savedTimes = {};
    if (timeStorageKey) {
      try {
        savedTimes = JSON.parse(localStorage.getItem(timeStorageKey) || "{}");
      } catch (err) {
        savedTimes = {};
      }
    }

    if (attemptId && questionNumber === 1 && answeredCount === 0) {
      if (storageKey) localStorage.removeItem(storageKey);
      if (timeStorageKey) localStorage.removeItem(timeStorageKey);
      savedAnswers = {};
      savedTimes = {};
    }

    const mapButtons = Array.from(document.querySelectorAll("[data-question-map-item='1']"));
    function setMapButtonState(button, isAnswered, isCurrent) {
      if (!button) return;
      button.classList.remove(
        "bg-primary/20",
        "text-primary",
        "border",
        "border-primary/50",
        "bg-background-light",
        "dark:bg-background-dark",
        "border-border-light",
        "dark:border-border-dark",
        "hover:border-primary/50",
        "ring-2",
        "ring-primary",
        "ring-offset-2",
        "ring-offset-card-light",
        "dark:ring-offset-card-dark"
      );

      if (isAnswered) {
        button.classList.add("bg-primary/20", "text-primary", "border", "border-primary/50");
      } else {
        button.classList.add(
          "bg-background-light",
          "dark:bg-background-dark",
          "border",
          "border-border-light",
          "dark:border-border-dark",
          "hover:border-primary/50"
        );
      }

      if (isCurrent) {
        button.classList.add("ring-2", "ring-primary", "ring-offset-2", "ring-offset-card-light", "dark:ring-offset-card-dark");
      }
    }

    function refreshQuestionMap() {
      if (!mapButtons.length) return;
      mapButtons.forEach(function (button) {
        const questionKey = String(toInt(button.dataset.questionId, 0));
        const backendState = button.dataset.mapState || "pending";
        const isCurrent = button.dataset.isCurrent === "1";
        const isAnswered = Boolean(savedAnswers[questionKey]) || backendState === "answered";
        setMapButtonState(button, isAnswered, isCurrent);
      });
    }

    refreshQuestionMap();

    if (questionStartKey) {
      sessionStorage.setItem(questionStartKey, String(Date.now()));
    }

    function flushCurrentQuestionTime() {
      if (!questionStartKey || !questionId || !timeStorageKey) return;
      const startRaw = sessionStorage.getItem(questionStartKey);
      if (!startRaw) return;

      const startedAt = toInt(startRaw, Date.now());
      const elapsed = Math.max(0, Math.floor((Date.now() - startedAt) / 1000));
      const existing = toInt(savedTimes[String(questionId)], 0);
      savedTimes[String(questionId)] = existing + elapsed;
      localStorage.setItem(timeStorageKey, JSON.stringify(savedTimes));
      sessionStorage.setItem(questionStartKey, String(Date.now()));
    }

    if (questionId && inputs.length) {
      const savedChoice = savedAnswers[String(questionId)] || "";
      if (savedChoice) {
        inputs.forEach(function (input) {
          input.checked = input.value === savedChoice;
        });
      }
    }

    inputs.forEach(function (input) {
      input.addEventListener("change", function () {
        if (!storageKey || !questionId) return;
        savedAnswers[String(questionId)] = input.value;
        flushCurrentQuestionTime();
        localStorage.setItem(storageKey, JSON.stringify(savedAnswers));
        refreshQuestionMap();
      });
    });

    const navButtons = Array.from(document.querySelectorAll("[data-exam-nav='1']"));
    navButtons.forEach(function (button) {
      button.addEventListener("click", function () {
        flushCurrentQuestionTime();
      });
    });
    window.addEventListener("beforeunload", flushCurrentQuestionTime);

    const submitBtn = byId("exam-submit-button");
    let timerIntervalId = null;
    let examSubmitInFlight = false;

    function pad2(value) {
      const normalized = Math.max(0, toInt(value, 0));
      return String(normalized).padStart(2, "0");
    }

    function renderTimer(totalSeconds) {
      const safeTotal = Math.max(0, toInt(totalSeconds, 0));
      const hours = Math.floor(safeTotal / 3600);
      const minutes = Math.floor((safeTotal % 3600) / 60);
      const seconds = safeTotal % 60;
      if (timerHours) timerHours.textContent = pad2(hours);
      if (timerMinutes) timerMinutes.textContent = pad2(minutes);
      if (timerSeconds) timerSeconds.textContent = pad2(seconds);
    }

    async function submitExam(triggeredByTimeout) {
      if (examSubmitInFlight) return;
      examSubmitInFlight = true;
      if (timerIntervalId) {
        window.clearInterval(timerIntervalId);
        timerIntervalId = null;
      }

      try {
        if (!attemptId || !testId) {
          throw new Error("Missing attempt/test id.");
        }

        if (submitBtn) {
          setBusy(submitBtn, true, "Submitting...");
        }

        const detail = await api(`/tests/${testId}/`);
        const questionIds = [];
        (detail.passages || []).forEach(function (passage) {
          (passage.questions || []).forEach(function (question) {
            questionIds.push(question.id);
          });
        });

        const payload = {
          attempt_id: attemptId,
          answers: questionIds.map(function (id) {
            return {
              question_id: id,
              selected_answer: savedAnswers[String(id)] || "",
              time_spent: toInt(savedTimes[String(id)], 0) || null,
            };
          }),
        };

        const res = await api("/attempts/submit/", {
          method: "POST",
          body: JSON.stringify(payload),
        });

        if (storageKey) {
          localStorage.removeItem(storageKey);
        }
        if (timeStorageKey) {
          localStorage.removeItem(timeStorageKey);
        }
        window.location.href = `/team15/exam-result/?attempt_id=${res.attempt_id}`;
      } catch (error) {
        const message = error instanceof Error ? error.message.toLowerCase() : String(error).toLowerCase();
        if (triggeredByTimeout && (message.includes("already completed") || message.includes("attempt not found"))) {
          window.location.href = `/team15/exam-result/?attempt_id=${attemptId}`;
          return;
        }
        if (submitBtn) {
          setBusy(submitBtn, false, "Submitting...");
        }
        examSubmitInFlight = false;
        showError(error);
      }
    }

    if (submitBtn) {
      submitBtn.addEventListener("click", async function () {
        flushCurrentQuestionTime();
        await submitExam(false);
      });
    }

    if (isTimeLimited && attemptId > 0) {
      let secondsLeft = Math.max(0, remainingFromServer);
      renderTimer(secondsLeft);
      if (secondsLeft === 0) {
        submitExam(true);
        return;
      }

      timerIntervalId = window.setInterval(function () {
        secondsLeft -= 1;
        if (secondsLeft <= 0) {
          flushCurrentQuestionTime();
          renderTimer(0);
          window.clearInterval(timerIntervalId);
          timerIntervalId = null;
          submitExam(true);
          return;
        }
        renderTimer(secondsLeft);
      }, 1000);
    }
  }

  function initPracticeReading() {
    const body = getBody();
    if (!body) return;

    const attemptId = toInt(body.dataset.attemptId, 0);
    const questionId = toInt(body.dataset.questionId, 0);
    const isLocked = body.dataset.answerLocked === "1";
    const questionStartKey = attemptId && questionId ? `team15_practice_qstart_${attemptId}_${questionId}` : "";
    if (questionStartKey && !isLocked) {
      sessionStorage.setItem(questionStartKey, String(Date.now()));
    }

    const optionRows = Array.from(document.querySelectorAll("[data-option-row]"));
    const formatSizeBtn = byId("practice-format-size");
    const borderColorBtn = byId("practice-border-color");
    const readingParagraphs = Array.from(document.querySelectorAll("[data-practice-paragraph='1']"));
    const fontSizeStorageKey = "team15_practice_font_size_index";
    const highlightStorageKey = attemptId && questionId ? `team15_practice_highlight_${attemptId}_${questionId}` : "";
    const fontSizes = ["1rem", "1.1rem", "1.2rem"];
    let fontSizeIndex = toInt(localStorage.getItem(fontSizeStorageKey), 0);
    fontSizeIndex = Math.max(0, Math.min(fontSizeIndex, fontSizes.length - 1));
    let highlightModeEnabled = false;
    let highlightedParagraphIndices = new Set();

    if (highlightStorageKey) {
      try {
        const parsed = JSON.parse(localStorage.getItem(highlightStorageKey) || "[]");
        if (Array.isArray(parsed)) {
          highlightedParagraphIndices = new Set(parsed.map(String));
        }
      } catch (err) {
        highlightedParagraphIndices = new Set();
      }
    }

    function applyReadingFontSize() {
      readingParagraphs.forEach(function (paragraph) {
        paragraph.style.fontSize = fontSizes[fontSizeIndex];
      });
    }

    function applyReadingHighlights() {
      readingParagraphs.forEach(function (paragraph) {
        const paragraphIndex = String(paragraph.dataset.paragraphIndex || "");
        if (highlightedParagraphIndices.has(paragraphIndex)) {
          paragraph.style.backgroundColor = "rgba(255, 189, 46, 0.22)";
          paragraph.style.borderRadius = "0.5rem";
        } else {
          paragraph.style.backgroundColor = "";
          paragraph.style.borderRadius = "";
        }
      });
    }

    function syncHighlightButton() {
      if (!borderColorBtn) return;
      if (highlightModeEnabled) {
        borderColorBtn.classList.add("bg-primary/20", "border", "border-primary/50");
      } else {
        borderColorBtn.classList.remove("bg-primary/20", "border", "border-primary/50");
      }
      readingParagraphs.forEach(function (paragraph) {
        paragraph.style.cursor = highlightModeEnabled ? "pointer" : "text";
      });
    }

    applyReadingFontSize();
    applyReadingHighlights();
    syncHighlightButton();

    if (formatSizeBtn) {
      formatSizeBtn.addEventListener("click", function () {
        fontSizeIndex = (fontSizeIndex + 1) % fontSizes.length;
        localStorage.setItem(fontSizeStorageKey, String(fontSizeIndex));
        applyReadingFontSize();
      });
    }

    if (borderColorBtn) {
      borderColorBtn.addEventListener("click", function () {
        highlightModeEnabled = !highlightModeEnabled;
        syncHighlightButton();
      });
    }

    readingParagraphs.forEach(function (paragraph) {
      paragraph.addEventListener("click", function () {
        if (!highlightModeEnabled) return;
        const paragraphIndex = String(paragraph.dataset.paragraphIndex || "");
        if (!paragraphIndex) return;
        if (highlightedParagraphIndices.has(paragraphIndex)) {
          highlightedParagraphIndices.delete(paragraphIndex);
        } else {
          highlightedParagraphIndices.add(paragraphIndex);
        }
        applyReadingHighlights();
        if (highlightStorageKey) {
          localStorage.setItem(highlightStorageKey, JSON.stringify(Array.from(highlightedParagraphIndices)));
        }
      });
    });

    if (!isLocked) {
      optionRows.forEach(function (row) {
        row.addEventListener("click", async function () {
          try {
            const choice = row.dataset.choice || "";
            if (!attemptId || !questionId || !choice) return;

            const startedAt = questionStartKey ? toInt(sessionStorage.getItem(questionStartKey), Date.now()) : Date.now();
            const timeSpent = Math.max(1, Math.floor((Date.now() - startedAt) / 1000));

            await api("/attempts/answer/", {
              method: "POST",
              body: JSON.stringify({
                attempt_id: attemptId,
                question_id: questionId,
                selected_answer: choice,
                time_spent: timeSpent,
              }),
            });

            if (questionStartKey) {
              sessionStorage.removeItem(questionStartKey);
            }
            window.location.reload();
          } catch (error) {
            showError(error);
          }
        });
      });
    }

    async function finishPractice() {
      if (!attemptId) {
        throw new Error("Missing practice attempt id.");
      }
      const res = await api("/attempts/finish/", {
        method: "POST",
        body: JSON.stringify({ attempt_id: attemptId }),
      });
      window.location.href = `/team15/exam-result/?attempt_id=${res.attempt_id}`;
    }

    const finishBtn = byId("practice-finish-button");
    if (finishBtn) {
      finishBtn.addEventListener("click", async function () {
        try {
          setBusy(finishBtn, true, "Finishing...");
          await finishPractice();
        } catch (error) {
          setBusy(finishBtn, false, "Finishing...");
          showError(error);
        }
      });
    }

    const nextBtn = byId("practice-next-button");
    if (nextBtn && nextBtn.dataset.finishOnClick === "1") {
      nextBtn.addEventListener("click", async function () {
        try {
          setBusy(nextBtn, true, "Finishing...");
          await finishPractice();
        } catch (error) {
          setBusy(nextBtn, false, "Finishing...");
          showError(error);
        }
      });
    }
  }

  function initExamResult() {
    const btn = byId("result-practice-weakest");
    if (!btn) return;
    btn.addEventListener("click", async function () {
      try {
        setBusy(btn, true, "Starting...");
        await startFirstPracticeAttempt();
      } catch (error) {
        window.location.href = "/team15/practice-reading/";
      }
    });
  }

  function initProgress() {
    const startBtn = byId("progress-start-session");
    if (startBtn) {
      startBtn.addEventListener("click", function () {
        window.location.href = "/team15/exam-setup/";
      });
    }
  }

  function boot() {
    const body = getBody();
    if (!body) return;
    startSessionRefreshHeartbeat();
    const page = body.dataset.page || "";

    if (page === "dashboard") initDashboard();
    if (page === "exam-setup") initExamSetup();
    if (page === "exam-reading") initExamReading();
    if (page === "practice-reading") initPracticeReading();
    if (page === "exam-result") initExamResult();
    if (page === "progress") initProgress();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
