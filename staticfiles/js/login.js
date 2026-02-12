const LOGIN_API_URL = "/api/auth/login/";

const loginForm = document.getElementById("loginForm");
const emailInput = document.getElementById("email");
const passwordInput = document.getElementById("password");
const togglePasswordBtn = document.getElementById("togglePassword");
const loginBtn = document.getElementById("loginBtn");
const alertBox = document.getElementById("alertBox");

function validateEmail(email) {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

function showError(inputElement, errorElement, message) {
  inputElement.classList.add("error");
  errorElement.textContent = message;
  errorElement.classList.add("show");
}

function hideError(inputElement, errorElement) {
  inputElement.classList.remove("error");
  errorElement.textContent = "";
  errorElement.classList.remove("show");
}

function showAlert(message, type) {
  alertBox.textContent = message;
  alertBox.className = "alert-box show " + type;

  setTimeout(() => {
    alertBox.classList.remove("show");
  }, 5000);
}

function setLoading(isLoading) {
  if (isLoading) {
    loginBtn.classList.add("loading");
    loginBtn.disabled = true;
  } else {
    loginBtn.classList.remove("loading");
    loginBtn.disabled = false;
  }
}

function validateForm() {
  let isValid = true;
  const emailError = document.getElementById("emailError");
  const passwordError = document.getElementById("passwordError");

  hideError(emailInput, emailError);
  hideError(passwordInput, passwordError);

  const email = emailInput.value.trim();
  const password = passwordInput.value;

  if (!email) {
    showError(emailInput, emailError, "لطفاً ایمیل خود را وارد کنید");
    isValid = false;
  } else if (!validateEmail(email)) {
    showError(emailInput, emailError, "فرمت ایمیل صحیح نیست");
    isValid = false;
  }

  if (!password.trim()) {
    showError(passwordInput, passwordError, "لطفاً رمز عبور خود را وارد کنید");
    isValid = false;
  }

  return isValid;
}

function getNextUrl() {
  // Supports /auth/?next=/team1/...
  const params = new URLSearchParams(window.location.search);
  const next = params.get("next");
  // basic safety: only allow same-origin relative paths
  if (next && next.startsWith("/")) return next;
  return "/";
}

if (togglePasswordBtn) {
  togglePasswordBtn.addEventListener("click", () => {
    const type = passwordInput.type === "password" ? "text" : "password";
    passwordInput.type = type;
    togglePasswordBtn.textContent = type === "password" ? "👁️" : "🙈";
  });
}

emailInput.addEventListener("input", () => {
  hideError(emailInput, document.getElementById("emailError"));
});

passwordInput.addEventListener("input", () => {
  hideError(passwordInput, document.getElementById("passwordError"));
});

try {
  const el = document.getElementById("serverLoginError");
  if (el && el.textContent) {
    const msg = JSON.parse(el.textContent);
    if (msg) showAlert(msg, "error");
  }
} catch (_) {
}

loginForm.addEventListener("submit", async (e) => {
  e.preventDefault();

  if (!validateForm()) return;

  const email = emailInput.value.trim().toLowerCase();
  const password = passwordInput.value;

  setLoading(true);

  try {
    const resp = await fetch(LOGIN_API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      credentials: "include",
      body: JSON.stringify({ email, password }),
    });

    const data = await resp.json().catch(() => ({}));

    if (resp.ok && data && data.ok) {
      showAlert("ورود با موفقیت انجام شد! در حال انتقال...", "success");
      setTimeout(() => {
        window.location.href = getNextUrl();
      }, 700);
      return;
    }

    if (resp.status === 401) {
      showAlert("ایمیل یا رمز عبور اشتباه است.", "error");
    } else if (resp.status === 403) {
      showAlert("حساب کاربری غیرفعال است.", "error");
    } else if (data && data.error) {
      showAlert(String(data.error), "error");
    } else {
      showAlert("خطا در ورود. لطفاً دوباره تلاش کنید.", "error");
    }
  } catch (err) {
    console.error(err);
    showAlert("خطا در برقراری ارتباط با سرور. لطفاً دوباره تلاش کنید.", "error");
  } finally {
    setLoading(false);
  }
});

