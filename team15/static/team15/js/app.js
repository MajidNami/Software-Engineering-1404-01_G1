(function () {
  const basePath = "/team15/api";

  function byId(id) {
    return document.getElementById(id);
  }

  function qs(name) {
    const url = new URL(window.location.href);
    return url.searchParams.get(name);
  }

  function setText(id, value) {
    const el = byId(id);
    if (!el) return;
    el.textContent = value == null || value === "" ? "-" : String(value);
  }

  function fmtSeconds(total) {
    if (!total && total !== 0) return "00:00";
    const hours = Math.floor(total / 3600);
    const minutes = Math.floor((total % 3600) / 60);
    const seconds = total % 60;
    if (hours > 0) {
      return `${String(hours).padStart(2, "0")}:${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;
    }
    return `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;
  }

  function fmtDate(iso) {
    if (!iso) return "-";
    const d = new Date(iso);
    return d.toLocaleDateString();
  }

  function api(path, opts) {
    return fetch(`${basePath}${path}`, {
      credentials: "same-origin",
      headers: {
        "Content-Type": "application/json",
        ...(opts && opts.headers ? opts.headers : {}),
      },
      ...opts,
    }).then(async (res) => {
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        const msg = data && data.detail ? data.detail : "Request failed";
        throw new Error(msg);
      }
      return data;
    });
  }

  function showError(error) {
    const message = error instanceof Error ? error.message : String(error);
    const bar = byId("global-error");
    if (bar) {
      bar.textContent = message;
      bar.classList.remove("hidden");
      return;
    }
    alert(message);
  }

  function typeLabel(type) {
    if (type === "insert_text") return "Insert Sentence";
    return "Multiple Choice";
  }

  function flattenQuestions(test) {
    const rows = [];
    (test.passages || []).forEach((passage) => {
      (passage.questions || []).forEach((q) => {
        rows.push({ ...q, passage });
      });
    });
    return rows.sort((a, b) => a.order - b.order);
  }

  async function initDashboard() {
    const [dashboard, history, practiceTests] = await Promise.all([
      api("/dashboard/"),
      api("/history/"),
      api("/tests/?mode=practice"),
    ]);

    const avgScore = dashboard.average_score || 0;
    const proficiency = Math.round((avgScore / 30) * 100);

    setText("metric-proficiency", `${proficiency}%`);
    setText("metric-average", `${avgScore || 0}/30`);
    setText("metric-attempts", String(dashboard.completed_attempts || 0));

    const recent = history.slice(0, 5);
    const tbody = byId("recent-activity");
    if (tbody) {
      tbody.innerHTML = "";
      if (!recent.length) {
        tbody.innerHTML = `<tr><td colspan="4" class="px-4 py-6 text-center text-slate-500">No attempts yet.</td></tr>`;
      } else {
        recent.forEach((item) => {
          const tr = document.createElement("tr");
          tr.className = "border-t border-slate-200";
          tr.innerHTML = `
            <td class="px-4 py-3 font-medium">${item.test_title}</td>
            <td class="px-4 py-3">${item.score == null ? "-" : `${item.score}/30`}</td>
            <td class="px-4 py-3">${fmtDate(item.started_at)}</td>
            <td class="px-4 py-3"><a class="text-pink-600 font-semibold" href="/team15/exam-result/?attempt_id=${item.id}">Review</a></td>
          `;
          tbody.appendChild(tr);
        });
      }
    }

    const examBtn = byId("btn-start-exam");
    if (examBtn) {
      examBtn.addEventListener("click", () => {
        window.location.href = "/team15/exam-setup/";
      });
    }

    const practiceBtn = byId("btn-start-practice");
    if (practiceBtn) {
      practiceBtn.addEventListener("click", async () => {
        if (!practiceTests.length) throw new Error("No active practice test.");
        const first = practiceTests[0];
        const start = await api("/attempts/start/", {
          method: "POST",
          body: JSON.stringify({ test_id: first.id }),
        });
        window.location.href = `/team15/practice-reading/?test_id=${first.id}&attempt_id=${start.attempt_id}`;
      });
    }
  }

  async function initExamSetup() {
    const tests = await api("/tests/?mode=exam");
    const box = byId("exam-test-options");
    const eta = byId("estimated-time");
    const startBtn = byId("btn-start-selected-exam");
    const check = byId("setup-confirm");

    if (!tests.length) {
      if (box) box.innerHTML = "<p class='text-sm text-red-600'>No exam tests available.</p>";
      if (startBtn) startBtn.disabled = true;
      return;
    }

    let selected = tests[0];

    function renderOptions() {
      if (!box) return;
      box.innerHTML = "";
      tests.forEach((test, idx) => {
        const label = document.createElement("label");
        label.className = "cursor-pointer flex items-center justify-between rounded-lg border border-slate-200 bg-white px-4 py-3";
        label.innerHTML = `
          <span class="font-medium">${test.title}</span>
          <span class="text-sm text-slate-500">${test.passage_count} passages</span>
          <input type="radio" name="exam-test" value="${test.id}" ${idx === 0 ? "checked" : ""}>
        `;
        box.appendChild(label);
      });

      box.querySelectorAll("input[name='exam-test']").forEach((input) => {
        input.addEventListener("change", () => {
          selected = tests.find((t) => t.id === Number(input.value)) || tests[0];
          if (eta) eta.textContent = `${selected.time_limit || 0} minutes`;
        });
      });
    }

    renderOptions();
    if (eta) eta.textContent = `${selected.time_limit || 0} minutes`;

    const syncStartState = () => {
      if (startBtn) startBtn.disabled = !check.checked;
    };
    if (check) check.addEventListener("change", syncStartState);
    syncStartState();

    if (startBtn) {
      startBtn.addEventListener("click", async () => {
        const start = await api("/attempts/start/", {
          method: "POST",
          body: JSON.stringify({ test_id: selected.id }),
        });
        window.location.href = `/team15/exam-reading/?test_id=${selected.id}&attempt_id=${start.attempt_id}`;
      });
    }
  }

  function setupQuestionMap(container, total, active, answered, onJump) {
    if (!container) return;
    container.innerHTML = "";
    for (let i = 0; i < total; i += 1) {
      const btn = document.createElement("button");
      const isActive = i === active;
      const isAnswered = answered.has(i);
      btn.className = `h-8 w-8 rounded border text-sm font-semibold ${isActive ? "bg-pink-600 text-white border-pink-600" : isAnswered ? "bg-pink-100 text-pink-700 border-pink-300" : "bg-white text-slate-700 border-slate-200"}`;
      btn.textContent = String(i + 1);
      btn.addEventListener("click", () => onJump(i));
      container.appendChild(btn);
    }
  }

  function renderPassageInto(id, title, content, highlightText) {
    const h = byId(id + "-title");
    const c = byId(id + "-content");
    if (h) h.textContent = title;
    if (!c) return;
    let html = String(content || "").replace(/\n\n/g, "</p><p class='mb-4'>");
    html = `<p class='mb-4'>${html}</p>`;
    if (highlightText) {
      const escaped = highlightText.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
      html = html.replace(new RegExp(escaped, "i"), `<mark class='bg-amber-200 rounded px-1'>$&</mark>`);
    }
    c.innerHTML = html;
  }

  async function initExamReading() {
    const testId = Number(qs("test_id"));
    const attemptId = Number(qs("attempt_id"));
    if (!testId || !attemptId) throw new Error("Missing test_id or attempt_id in URL.");

    const test = await api(`/tests/${testId}/`);
    const questions = flattenQuestions(test);
    if (!questions.length) throw new Error("No questions found in this test.");

    const answers = new Map();
    const answeredIdx = new Set();
    let current = 0;
    let secondsLeft = (test.time_limit || 0) * 60;

    const timerHours = byId("timer-hours");
    const timerMinutes = byId("timer-minutes");
    const timerSeconds = byId("timer-seconds");

    function renderTimer() {
      const h = Math.floor(secondsLeft / 3600);
      const m = Math.floor((secondsLeft % 3600) / 60);
      const s = secondsLeft % 60;
      if (timerHours) timerHours.textContent = String(h).padStart(2, "0");
      if (timerMinutes) timerMinutes.textContent = String(m).padStart(2, "0");
      if (timerSeconds) timerSeconds.textContent = String(s).padStart(2, "0");
    }

    function saveCurrentSelection() {
      const checked = document.querySelector("input[name='exam-choice']:checked");
      if (!checked) return;
      answers.set(questions[current].id, checked.value);
      answeredIdx.add(current);
    }

    function renderCurrent() {
      const q = questions[current];
      renderPassageInto("exam-passage", q.passage.title, q.passage.content, q.question_text.split(" ")[1] || "");
      setText("exam-question-counter", `Question ${current + 1} of ${questions.length}`);
      const prompt = byId("exam-question-text");
      if (prompt) prompt.textContent = q.question_text;

      const options = byId("exam-options");
      if (options) {
        options.innerHTML = "";
        (q.choices || []).forEach((choice, idx) => {
          const label = document.createElement("label");
          label.className = "block rounded-lg border border-slate-200 bg-white p-3 hover:border-pink-400";
          const checked = answers.get(q.id) === choice ? "checked" : "";
          label.innerHTML = `<input class="mr-2" type="radio" name="exam-choice" value="${choice}" ${checked}>${choice}`;
          options.appendChild(label);
        });
      }

      setupQuestionMap(byId("exam-question-map"), questions.length, current, answeredIdx, (idx) => {
        saveCurrentSelection();
        current = idx;
        renderCurrent();
      });
    }

    function next() {
      saveCurrentSelection();
      if (current < questions.length - 1) {
        current += 1;
        renderCurrent();
      }
    }

    function prev() {
      saveCurrentSelection();
      if (current > 0) {
        current -= 1;
        renderCurrent();
      }
    }

    byId("btn-exam-next")?.addEventListener("click", next);
    byId("btn-exam-prev")?.addEventListener("click", prev);

    byId("btn-submit-exam")?.addEventListener("click", async () => {
      saveCurrentSelection();
      const payload = {
        attempt_id: attemptId,
        answers: questions.map((q) => ({
          question_id: q.id,
          selected_answer: answers.get(q.id) || "",
        })),
      };
      const res = await api("/attempts/submit/", {
        method: "POST",
        body: JSON.stringify(payload),
      });
      window.location.href = `/team15/exam-result/?attempt_id=${res.attempt_id}`;
    });

    const hidePassageBtn = byId("btn-hide-passage");
    hidePassageBtn?.addEventListener("click", () => {
      const panel = byId("exam-passage-panel");
      if (!panel) return;
      panel.classList.toggle("hidden");
      hidePassageBtn.textContent = panel.classList.contains("hidden") ? "Show" : "Hide";
    });

    renderCurrent();
    renderTimer();

    if (secondsLeft > 0) {
      setInterval(async () => {
        secondsLeft -= 1;
        renderTimer();
        if (secondsLeft <= 0) {
          const payload = {
            attempt_id: attemptId,
            answers: questions.map((q) => ({
              question_id: q.id,
              selected_answer: answers.get(q.id) || "",
            })),
          };
          const res = await api("/attempts/submit/", {
            method: "POST",
            body: JSON.stringify(payload),
          });
          window.location.href = `/team15/exam-result/?attempt_id=${res.attempt_id}`;
        }
      }, 1000);
    }
  }

  async function initPracticeReading() {
    const testId = Number(qs("test_id"));
    const attemptId = Number(qs("attempt_id"));
    if (!testId || !attemptId) throw new Error("Missing test_id or attempt_id in URL.");

    const test = await api(`/tests/${testId}/`);
    const questions = flattenQuestions(test);
    if (!questions.length) throw new Error("No questions found in this test.");

    let current = 0;
    const local = new Map();

    function renderCurrent() {
      const q = questions[current];
      renderPassageInto("practice-passage", q.passage.title, q.passage.content, "");
      setText("practice-counter", `Question ${current + 1} of ${questions.length}`);
      const progress = Math.round(((current + 1) / questions.length) * 100);
      setText("practice-progress", `${progress}%`);
      byId("practice-progress-bar")?.style.setProperty("width", `${progress}%`);
      setText("practice-question", q.question_text);

      const options = byId("practice-options");
      if (options) {
        options.innerHTML = "";
        (q.choices || []).forEach((choice) => {
          const row = document.createElement("button");
          row.type = "button";
          row.className = "w-full rounded-lg border border-slate-200 bg-white p-3 text-left hover:border-sky-400";
          row.textContent = choice;
          row.addEventListener("click", async () => {
            const res = await api("/attempts/answer/", {
              method: "POST",
              body: JSON.stringify({
                attempt_id: attemptId,
                question_id: q.id,
                selected_answer: choice,
              }),
            });
            local.set(q.id, res);
            renderFeedback(q, choice, res);
          });
          options.appendChild(row);
        });
      }

      const saved = local.get(q.id);
      if (saved) {
        renderFeedback(q, saved.selected_answer, saved);
      } else {
        byId("practice-feedback").classList.add("hidden");
      }
    }

    function renderFeedback(q, selected, res) {
      const box = byId("practice-feedback");
      const title = byId("practice-feedback-title");
      const summary = byId("practice-feedback-summary");
      const explain = byId("practice-feedback-explain");
      if (!box || !title || !summary || !explain) return;

      box.classList.remove("hidden");
      title.textContent = res.is_correct ? "Correct" : "Incorrect";
      title.className = res.is_correct ? "text-lg font-bold text-emerald-600" : "text-lg font-bold text-red-600";
      summary.textContent = `Your answer: ${selected}`;
      explain.textContent = res.is_correct
        ? "Great job. Your selected option matches the correct answer."
        : `Correct answer: ${res.correct_answer}`;

      const options = byId("practice-options");
      if (options) {
        [...options.children].forEach((node) => {
          const text = node.textContent;
          node.className = "w-full rounded-lg border p-3 text-left";
          if (text === res.correct_answer) {
            node.classList.add("border-emerald-500", "bg-emerald-50");
          } else if (text === selected && text !== res.correct_answer) {
            node.classList.add("border-red-500", "bg-red-50");
          } else {
            node.classList.add("border-slate-200", "bg-white");
          }
        });
      }
    }

    byId("btn-practice-prev")?.addEventListener("click", () => {
      if (current > 0) {
        current -= 1;
        renderCurrent();
      }
    });

    byId("btn-practice-next")?.addEventListener("click", () => {
      if (current < questions.length - 1) {
        current += 1;
        renderCurrent();
      }
    });

    byId("btn-finish-practice")?.addEventListener("click", async () => {
      const res = await api("/attempts/finish/", {
        method: "POST",
        body: JSON.stringify({ attempt_id: attemptId }),
      });
      window.location.href = `/team15/exam-result/?attempt_id=${res.attempt_id}`;
    });

    renderCurrent();
  }

  function estimateSkillName(question) {
    const text = `${question.question_text || ""}`.toLowerCase();
    if (text.includes("inference")) return "Inference";
    if (text.includes("vocabulary") || text.includes("word")) return "Vocabulary";
    if (text.includes("detail")) return "Detail";
    if (text.includes("purpose")) return "Purpose";
    if (text.includes("main idea")) return "Main Idea";
    if (question.question_type === "insert_text") return "Insert Sentence";
    return "Multiple Choice";
  }

  async function initResult() {
    const attemptId = Number(qs("attempt_id"));
    if (!attemptId) throw new Error("Missing attempt_id in URL.");

    const data = await api(`/attempts/${attemptId}/result/`);

    setText("result-title", `Test Report: ${data.test_title}`);
    setText("result-score", `${data.score || 0} / 30`);
    setText("result-accuracy", `${data.accuracy || 0}%`);
    setText("result-total-time", fmtSeconds(data.total_time || 0));

    const avg = data.total ? Math.round((data.total_time || 0) / data.total) : 0;
    setText("result-avg-time", fmtSeconds(avg));

    const skillAgg = new Map();
    (data.answers || []).forEach((ans) => {
      const skill = estimateSkillName(ans.question || {});
      const prev = skillAgg.get(skill) || { total: 0, correct: 0 };
      prev.total += 1;
      if (ans.is_correct) prev.correct += 1;
      skillAgg.set(skill, prev);
    });

    const perf = byId("result-skill-bars");
    if (perf) {
      perf.innerHTML = "";
      [...skillAgg.entries()].forEach(([skill, row]) => {
        const percent = row.total ? Math.round((row.correct / row.total) * 100) : 0;
        const item = document.createElement("div");
        item.className = "space-y-1";
        item.innerHTML = `
          <div class="flex justify-between text-sm"><span>${skill}</span><span>${percent}%</span></div>
          <div class="h-2 rounded bg-slate-200"><div class="h-2 rounded bg-pink-600" style="width:${percent}%"></div></div>
        `;
        perf.appendChild(item);
      });
    }

    const rows = byId("result-review");
    if (rows) {
      rows.innerHTML = "";
      (data.answers || []).forEach((ans, idx) => {
        const tr = document.createElement("tr");
        tr.className = "border-t border-slate-200";
        tr.innerHTML = `
          <td class="px-4 py-3">${idx + 1}</td>
          <td class="px-4 py-3">${typeLabel(ans.question.question_type)}</td>
          <td class="px-4 py-3 ${ans.is_correct ? "text-emerald-600" : "text-red-600"}">${ans.selected_answer || "-"}</td>
          <td class="px-4 py-3">${ans.question.correct_answer || "-"}</td>
          <td class="px-4 py-3">${fmtSeconds(ans.time_spent || 0)}</td>
          <td class="px-4 py-3"><a class="text-sky-600" href="/team15/progress/">Review</a></td>
        `;
        rows.appendChild(tr);
      });
    }
  }

  async function initProgress() {
    const [dashboard, history] = await Promise.all([api("/dashboard/"), api("/history/")]);

    const recent = history.slice(0, 8);
    const results = await Promise.all(
      recent.map((h) => api(`/attempts/${h.id}/result/`).catch(() => null))
    );

    const completed = recent.filter((x) => x.status === "completed");
    const avgScore = completed.length
      ? (completed.reduce((acc, x) => acc + (x.score || 0), 0) / completed.length)
      : (dashboard.average_score || 0);

    setText("progress-avg-score", `${avgScore.toFixed(1)}/30`);
    setText("progress-accuracy", `${Math.round((avgScore / 30) * 100)}%`);
    setText("progress-total-sessions", String(dashboard.total_attempts || 0));

    const avgTime = completed.length
      ? Math.round(completed.reduce((acc, x) => acc + (x.total_time || 0), 0) / completed.length)
      : 0;
    const avgQuestions = results
      .filter(Boolean)
      .reduce((acc, x) => acc + (x.total || 0), 0) || 1;
    setText("progress-time-per-q", fmtSeconds(Math.round(avgTime / Math.max(1, avgQuestions / Math.max(1, completed.length)))));

    const trend = byId("trend-bars");
    if (trend) {
      trend.innerHTML = "";
      const values = completed.slice(0, 6).reverse().map((x) => Math.round((x.score || 0) / 30 * 100));
      if (!values.length) values.push(0);
      values.forEach((v, i) => {
        const col = document.createElement("div");
        col.className = "flex flex-col items-center gap-1";
        col.innerHTML = `<div class="w-8 rounded-t bg-pink-500/70" style="height:${Math.max(12, v * 1.2)}px"></div><span class="text-xs text-slate-500">W${i + 1}</span>`;
        trend.appendChild(col);
      });
    }

    const typeAgg = new Map();
    results.filter(Boolean).forEach((r) => {
      (r.answers || []).forEach((ans) => {
        const key = estimateSkillName(ans.question || {});
        const old = typeAgg.get(key) || { total: 0, correct: 0 };
        old.total += 1;
        if (ans.is_correct) old.correct += 1;
        typeAgg.set(key, old);
      });
    });

    const typeList = byId("progress-by-type");
    if (typeList) {
      typeList.innerHTML = "";
      [...typeAgg.entries()].forEach(([name, row]) => {
        const pct = row.total ? Math.round((row.correct / row.total) * 100) : 0;
        const li = document.createElement("li");
        li.className = "flex justify-between";
        li.innerHTML = `<span>${name}</span><strong>${pct}%</strong>`;
        typeList.appendChild(li);
      });
    }

    const insights = byId("progress-insights");
    if (insights) {
      insights.innerHTML = "";
      const ranked = [...typeAgg.entries()].map(([name, row]) => ({
        name,
        pct: row.total ? Math.round((row.correct / row.total) * 100) : 0,
      })).sort((a, b) => b.pct - a.pct);

      if (ranked.length) {
        const best = ranked[0];
        const weak = ranked[ranked.length - 1];
        insights.innerHTML = `
          <li class="text-emerald-700">Strength: ${best.name} (${best.pct}%)</li>
          <li class="text-slate-700">Trend: ${dashboard.completed_attempts} completed attempts</li>
          <li class="text-amber-700">Improve: ${weak.name} (${weak.pct}%)</li>
        `;
      } else {
        insights.innerHTML = "<li>No enough data yet.</li>";
      }
    }

    const table = byId("progress-history");
    if (table) {
      table.innerHTML = "";
      recent.forEach((item) => {
        const tr = document.createElement("tr");
        tr.className = "border-t border-slate-200";
        tr.innerHTML = `
          <td class="px-4 py-3">${fmtDate(item.started_at)}</td>
          <td class="px-4 py-3">${item.test_mode}</td>
          <td class="px-4 py-3">${item.score == null ? "-" : `${item.score}/30`}</td>
          <td class="px-4 py-3">${fmtSeconds(item.total_time || 0)}</td>
          <td class="px-4 py-3"><a class="text-pink-600 font-semibold" href="/team15/exam-result/?attempt_id=${item.id}">View</a></td>
        `;
        table.appendChild(tr);
      });
    }
  }

  async function boot() {
    const root = document.body;
    const page = root ? root.dataset.page : "";
    try {
      if (page === "dashboard") await initDashboard();
      if (page === "exam-setup") await initExamSetup();
      if (page === "exam-reading") await initExamReading();
      if (page === "practice-reading") await initPracticeReading();
      if (page === "exam-result") await initResult();
      if (page === "progress") await initProgress();
    } catch (error) {
      showError(error);
    }
  }

  boot();
})();
