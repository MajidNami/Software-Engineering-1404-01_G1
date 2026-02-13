(() => {
  const body = document.body;
  const themeBtn = document.getElementById("themeBtn");

  // ---------- Theme ----------
  const setTheme = (isDark) => {
    body.classList.toggle("dark-mode", isDark);
    localStorage.setItem("theme", isDark ? "dark" : "light");
    if (themeBtn) themeBtn.textContent = isDark ? "☀️" : "🌙";
  };

  setTheme(localStorage.getItem("theme") !== "light"); // default dark
  if (themeBtn) {
    themeBtn.addEventListener("click", () =>
      setTheme(!body.classList.contains("dark-mode"))
    );
  }

  // ---------- Page transition (enter) ----------
  body.classList.add("page-enter");

  // ---------- Navigation with delay (exit animation + click feel) ----------
  const NAV_DELAY_MS = 160;

  const go = (fn) => {
    body.classList.remove("page-enter");
    body.classList.add("page-exit");
    setTimeout(fn, NAV_DELAY_MS);
  };

  // all internal links
  document.querySelectorAll('a[href]').forEach((a) => {
    const href = a.getAttribute("href");
    if (!href || href.startsWith("http") || href.startsWith("#")) return;

    a.addEventListener("click", (e) => {
      e.preventDefault();
      go(() => (window.location.href = href));
    });
  });

  // optional: any element with data-back uses history.back with delay
  document.querySelectorAll("[data-back]").forEach((el) => {
    el.addEventListener("click", (e) => {
      e.preventDefault();
      go(() => history.back());
    });
  });
})();
