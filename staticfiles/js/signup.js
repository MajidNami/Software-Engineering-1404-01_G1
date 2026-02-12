const SIGNUP_API_URL = "/api/auth/signup/";

const signupForm = document.getElementById("signupForm");
const firstNameInput = document.getElementById("first_name");
const lastNameInput = document.getElementById("last_name");
const emailInput = document.getElementById("email");
const ageInput = document.getElementById("age");
const passwordInput = document.getElementById("password");
const confirmPasswordInput = document.getElementById("confirmPassword");
const acceptTermsInput = document.getElementById("acceptTerms");
const togglePasswordBtn = document.getElementById("togglePassword");
const toggleConfirmPasswordBtn = document.getElementById("toggleConfirmPassword");
const signupBtn = document.getElementById("signupBtn");
const alertBox = document.getElementById("alertBox");

function validateEmail(email) {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

function validateName(name) {
  const nameRegex = /^[\u0600-\u06FFa-zA-Z\s]+$/;
  return nameRegex.test(name) && name.length >= 2;
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
    signupBtn.classList.add("loading");
    signupBtn.disabled = true;
  } else {
    signupBtn.classList.remove("loading");
    signupBtn.disabled = false;
  }
}

function getNextUrl() {
  const params = new URLSearchParams(window.location.search);
  const next = params.get("next");
  if (next && next.startsWith("/")) return next;
  return "/auth/";
}

function validateForm() {
  let isValid = true;

  const firstNameError = document.getElementById("firstNameError");
  hideError(firstNameInput, firstNameError);
  const firstName = firstNameInput.value.trim();
  if (!firstName) {
    showError(firstNameInput, firstNameError, "لطفاً نام خود را وارد کنید");
    isValid = false;
  } else if (!validateName(firstName)) {
    showError(firstNameInput, firstNameError, "نام باید حداقل 2 حرف و فقط شامل حروف باشد");
    isValid = false;
  }

  const lastNameError = document.getElementById("lastNameError");
  hideError(lastNameInput, lastNameError);
  const lastName = lastNameInput.value.trim();
  if (!lastName) {
    showError(lastNameInput, lastNameError, "لطفاً نام خانوادگی خود را وارد کنید");
    isValid = false;
  } else if (!validateName(lastName)) {
    showError(lastNameInput, lastNameError, "نام خانوادگی باید حداقل 2 حرف و فقط شامل حروف باشد");
    isValid = false;
  }

  const emailError = document.getElementById("emailError");
  hideError(emailInput, emailError);
  const email = emailInput.value.trim();
  if (!email) {
    showError(emailInput, emailError, "لطفاً ایمیل خود را وارد کنید");
    isValid = false;
  } else if (!validateEmail(email)) {
    showError(emailInput, emailError, "فرمت ایمیل صحیح نیست");
    isValid = false;
  }

  const ageError = document.getElementById("ageError");
  hideError(ageInput, ageError);
  const ageStr = ageInput.value;
  const age = parseInt(ageStr, 10);
  if (!ageStr) {
    showError(ageInput, ageError, "لطفاً سن خود را وارد کنید");
    isValid = false;
  } else if (Number.isNaN(age) || age < 10 || age > 100) {
    showError(ageInput, ageError, "سن باید بین 10 تا 100 سال باشد");
    isValid = false;
  }

  const passwordError = document.getElementById("passwordError");
  hideError(passwordInput, passwordError);
  const password = passwordInput.value || "";
  if (!password) {
    showError(passwordInput, passwordError, "لطفاً رمز عبور خود را وارد کنید");
    isValid = false;
  } else if (password.length < 8) {
    showError(passwordInput, passwordError, "رمز عبور باید حداقل 8 کاراکتر باشد");
    isValid = false;
  }

  const confirmPasswordError = document.getElementById("confirmPasswordError");
  hideError(confirmPasswordInput, confirmPasswordError);
  const confirmPassword = confirmPasswordInput.value || "";
  if (!confirmPassword) {
    showError(confirmPasswordInput, confirmPasswordError, "لطفاً رمز عبور را دوباره وارد کنید");
    isValid = false;
  } else if (password !== confirmPassword) {
    showError(confirmPasswordInput, confirmPasswordError, "رمز عبور و تکرار آن یکسان نیستند");
    isValid = false;
  }

  const termsError = document.getElementById("termsError");
  hideError(acceptTermsInput, termsError);
  if (!acceptTermsInput.checked) {
    showError(acceptTermsInput, termsError, "لطفاً قوانین و مقررات را بپذیرید");
    isValid = false;
  }

  return isValid;
}

togglePasswordBtn.addEventListener("click", () => {
  const type = passwordInput.type === "password" ? "text" : "password";
  passwordInput.type = type;
  togglePasswordBtn.textContent = type === "password" ? "👁️" : "🙈";
});

toggleConfirmPasswordBtn.addEventListener("click", () => {
  const type = confirmPasswordInput.type === "password" ? "text" : "password";
  confirmPasswordInput.type = type;
  toggleConfirmPasswordBtn.textContent = type === "password" ? "👁️" : "🙈";
});

try {
  const el = document.getElementById("serverSignupError");
  if (el && el.textContent) {
    const msg = JSON.parse(el.textContent);
    if (msg) showAlert(msg, "error");
  }
} catch (_) {}

signupForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  if (!validateForm()) return;

  const payload = {
    first_name: firstNameInput.value.trim(),
    last_name: lastNameInput.value.trim(),
    email: emailInput.value.trim().toLowerCase(),
    age: parseInt(ageInput.value, 10),
    password: passwordInput.value,
  };

  setLoading(true);

  try {
    const resp = await fetch(SIGNUP_API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify(payload),
    });

    const data = await resp.json().catch(() => ({}));

    if (resp.ok && data && data.ok) {
      showAlert("ثبت نام با موفقیت انجام شد! در حال انتقال...", "success");
      signupForm.reset();
      setTimeout(() => {
        window.location.href = getNextUrl();
      }, 900);
      return;
    }

    if (resp.status === 409) {
      showAlert("این ایمیل قبلاً ثبت شده است.", "error");
    } else if (resp.status === 400) {
      showAlert((data && data.error) ? String(data.error) : "اطلاعات ارسالی نامعتبر است.", "error");
    } else if (data && data.error) {
      showAlert(String(data.error), "error");
    } else {
      showAlert("خطا در ثبت نام. لطفاً دوباره تلاش کنید.", "error");
    }
  } catch (err) {
    console.error(err);
    showAlert("خطا در برقراری ارتباط با سرور. لطفاً دوباره تلاش کنید.", "error");
  } finally {
    setLoading(false);
  }
});

firstNameInput.addEventListener("input", () => hideError(firstNameInput, document.getElementById("firstNameError")));
lastNameInput.addEventListener("input", () => hideError(lastNameInput, document.getElementById("lastNameError")));
emailInput.addEventListener("input", () => hideError(emailInput, document.getElementById("emailError")));
ageInput.addEventListener("input", () => hideError(ageInput, document.getElementById("ageError")));
passwordInput.addEventListener("input", () => hideError(passwordInput, document.getElementById("passwordError")));
confirmPasswordInput.addEventListener("input", () => hideError(confirmPasswordInput, document.getElementById("confirmPasswordError")));
acceptTermsInput.addEventListener("change", () => hideError(acceptTermsInput, document.getElementById("termsError")));

