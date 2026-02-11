/**
 * Language Academy - Popup System
 * Handles beautiful modal popups for exam interactions
 */

// ==================== POPUP MANAGER ====================
const PopupManager = {
    currentPopup: null,
    backdrop: null,
    isCloseable: true,

    /**
     * Initialize popup system
     */
    init() {
        this.createBackdrop();
        this.attachBackdropListener();
    },

    /**
     * Create backdrop element
     */
    createBackdrop() {
        if (document.getElementById('popup-backdrop')) return;
        
        const backdrop = document.createElement('div');
        backdrop.id = 'popup-backdrop';
        backdrop.className = 'popup-backdrop';
        document.body.appendChild(backdrop);
        this.backdrop = backdrop;
    },

    /**
     * Attach click listener to backdrop for closing
     */
    attachBackdropListener() {
        if (this.backdrop) {
            this.backdrop.addEventListener('click', (e) => {
                if (e.target === this.backdrop && this.isCloseable) {
                    this.closePopup();
                }
            });
        }
    },

    /**
     * Show a popup
     * @param {HTMLElement} popupElement - The popup element to show
     * @param {Boolean} closeable - Whether the popup can be closed by clicking backdrop (default: true)
     */
    showPopup(popupElement, closeable = true) {
        if (!this.backdrop) this.createBackdrop();
        
        this.isCloseable = closeable;
        
        // Remove any existing popup
        if (this.currentPopup) {
            this.currentPopup.remove();
        }

        // Add new popup to backdrop
        this.backdrop.innerHTML = '';
        this.backdrop.appendChild(popupElement);
        
        // Trigger animation
        this.backdrop.classList.add('active');
        this.currentPopup = popupElement;
    },

    /**
     * Close current popup
     */
    closePopup() {
        if (this.isCloseable && this.backdrop) {
            this.backdrop.classList.remove('active');
        }
        setTimeout(() => {
            if (this.currentPopup && this.isCloseable) {
                this.currentPopup.remove();
                this.currentPopup = null;
            }
        }, 300);
    }
};

// ==================== EXAM START POPUP ====================
/**
 * Show exam start confirmation popup
 * @param {Object} examData - Exam information (title, totalTime, totalQuestions, difficulty, type)
 * @param {Function} onStart - Callback when user clicks start
 */
function showStartExamPopup(examData, onStart) {
    const popup = document.createElement('div');
    popup.className = 'popup-container';
    
    const minutes = Math.floor(examData.totalTime / 60);
    const seconds = examData.totalTime % 60;
    const timeString = `${minutes}:${String(seconds).padStart(2, '0')}`;
    
    // Convert difficulty level (1-5) to stars/text
    let difficultyDisplay = 'متوسط';
    let difficultyColor = 'yellow';
    if (examData.difficulty <= 2) {
        difficultyDisplay = 'آسان';
        difficultyColor = 'green';
    } else if (examData.difficulty >= 4) {
        difficultyDisplay = 'سخت';
        difficultyColor = 'red';
    }
    
    // Determine exam type for display (English to Persian conversion)
    console.log('Popup - Exam data type:', examData.type, 'Type of:', typeof examData.type);
    let examTypeDisplay = 'نوشتاری';
    if (examData.type && examData.type.toLowerCase && examData.type.toLowerCase() === 'speaking') {
        examTypeDisplay = 'گفتاری';
    }
    console.log('Popup - Exam type display:', examTypeDisplay);

    popup.innerHTML = `
        <div class="popup-header">
            <h2 class="popup-title">شروع آزمون</h2>
            <button class="popup-close-btn" onclick="PopupManager.closePopup()">×</button>
        </div>

        <div class="popup-body">
            <p class="popup-body-text">
                شما در حال شروع آزمون <strong>${examData.title}</strong> هستید. لطفاً دستورالعمل‌ها را به دقت مطالعه کنید.
            </p>

            <div class="popup-info-grid">
                <div class="popup-info-item">
                    <span class="popup-info-label">نوع آزمون</span>
                    <p class="popup-info-value">${examTypeDisplay}</p>
                </div>
                <div class="popup-info-item">
                    <span class="popup-info-label">زمان کل</span>
                    <p class="popup-info-value">${timeString}</p>
                </div>
                <div class="popup-info-item">
                    <span class="popup-info-label">تعداد سوالات</span>
                    <p class="popup-info-value">${examData.totalQuestions}</p>
                </div>
                <div class="popup-info-item">
                    <span class="popup-info-label">سطح دشواری</span>
                    <p class="popup-info-value"><span class="difficulty-badge ${difficultyColor}">${difficultyDisplay}</span></p>
                </div>
            </div>

            <div class="popup-features">
                <span class="popup-features-title">نکات مهم:</span>
                <div class="popup-feature-item">
                    <div class="popup-feature-icon">✓</div>
                    <p class="popup-feature-text">زمان آزمون از لحظه شروع شمارش می‌رود</p>
                </div>
                <div class="popup-feature-item">
                    <div class="popup-feature-icon">✓</div>
                    <p class="popup-feature-text">نمی‌توانید از این آزمون منصرف شوید</p>
                </div>
                <div class="popup-feature-item">
                    <div class="popup-feature-icon">✓</div>
                    <p class="popup-feature-text">پاسخ‌های خود را قبل از انتهای زمان ارسال کنید</p>
                </div>
                <div class="popup-feature-item">
                    <div class="popup-feature-icon">✓</div>
                    <p class="popup-feature-text">بازخورد فوری پس از تکمیل آزمون</p>
                </div>
            </div>
        </div>

        <div class="popup-footer">
            <button class="popup-button popup-button-outline" onclick="PopupManager.closePopup()">
                انصراف
            </button>
            <button class="popup-button popup-button-primary" id="startExamBtn">
                شروع آزمون
            </button>
        </div>
    `;

    PopupManager.showPopup(popup);

    // Attach start button listener
    const startBtn = popup.querySelector('#startExamBtn');
    if (startBtn && onStart) {
        startBtn.addEventListener('click', () => {
            PopupManager.closePopup();
            onStart();
        });
    }
}

// ==================== EXAM SUBMIT POPUP ====================
/**
 * Show exam submit confirmation popup
 * @param {Function} onConfirm - Callback when user confirms submission
 */
function showSubmitExamPopup(onConfirm) {
    const popup = document.createElement('div');
    popup.className = 'popup-container';

    popup.innerHTML = `
        <div class="popup-header">
            <h2 class="popup-title">اتمام آزمون</h2>
            <button class="popup-close-btn" onclick="PopupManager.closePopup()">×</button>
        </div>

        <div class="popup-body">
            <p class="popup-body-text">
                آیا مطمئن هستید که می‌خواهید آزمون را پایان داده و پاسخ‌های خود را ارسال کنید؟
            </p>

            <p class="popup-body-text warning">
                ⚠️ پس از ارسال، امکان ویرایش یا بازگشت پاسخ‌ها وجود نخواهد داشت.
            </p>
        </div>

        <div class="popup-footer">
            <button class="popup-button popup-button-outline" onclick="PopupManager.closePopup()">
                بازگشت و ادامه
            </button>
            <button class="popup-button popup-button-primary" id="confirmSubmitBtn">
                تایید و ارسال
            </button>
        </div>
    `;

    PopupManager.showPopup(popup);

    // Attach confirm button listener
    const confirmBtn = popup.querySelector('#confirmSubmitBtn');
    if (confirmBtn && onConfirm) {
        confirmBtn.addEventListener('click', () => {
            PopupManager.closePopup();
            onConfirm();
        });
    }
}

// ==================== EXAM RESULT POPUP ====================
/**
 * Show exam result popup
 * @param {Object} resultData - Result information (score, totalScore, answeredQuestions, timeSpent, type, message)
 */
function showExamResultPopup(resultData) {
    const popup = document.createElement('div');
    popup.className = 'popup-container';

    // Format time spent
    const totalSeconds = resultData.timeSpent || 0;
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = totalSeconds % 60;
    const timeString = `${minutes}:${String(seconds).padStart(2, '0')}`;

    // Get answered questions count
    const answeredCount = resultData.answeredQuestions || 0;
    const totalQuestions = resultData.totalQuestions || 0;

    // Determine score badge color based on score
    let scoreBadgeGradient = 'linear-gradient(135deg, #4caf50 0%, #81c784 100%)'; // Green - Excellent
    let scoreIcon = '★';
    if (resultData.score < 5) {
        scoreBadgeGradient = 'linear-gradient(135deg, #ff6b6b 0%, #ff8787 100%)'; // Red - Poor
        scoreIcon = '!';
    } else if (resultData.score < 6.5) {
        scoreBadgeGradient = 'linear-gradient(135deg, #ffb02d 0%, #ffc966 100%)'; // Orange - Fair
        scoreIcon = '◐';
    }

    popup.innerHTML = `
        <div class="popup-header">
            <h2 class="popup-title">تبریک! آزمون تکمیل شد</h2>
        </div>

        <div class="popup-body">
            <div class="popup-result-container">
                <p class="popup-result-text" style="font-size: 16px; margin-bottom: 32px; color: #0b0754; text-align: center;">
                    نتایج آزمون <strong>${resultData.type}</strong>
                </p>

                <!-- Three Result Badges -->
                <div class="result-badges-grid">
                    <!-- Badge 1: Answered Questions -->
                    <div class="result-badge">
                        <div class="result-badge-inner" style="background: linear-gradient(135deg, #3aa0ca 0%, #80caff 100%);">
                            <div class="result-badge-icon">✓</div>
                        </div>
                        <div class="result-badge-content">
                            <p class="result-badge-label">پاسخ‌های شما</p>
                            <p class="result-badge-value">${answeredCount}/${totalQuestions}</p>
                        </div>
                    </div>

                    <!-- Badge 2: Time Spent -->
                    <div class="result-badge">
                        <div class="result-badge-inner" style="background: linear-gradient(135deg, #fa0b67 0%, #ffb02d 100%);">
                            <div class="result-badge-icon">⏱</div>
                        </div>
                        <div class="result-badge-content">
                            <p class="result-badge-label">زمان سپری شده</p>
                            <p class="result-badge-value">${timeString}</p>
                        </div>
                    </div>

                    <!-- Badge 3: Score -->
                    <div class="result-badge">
                        <div class="result-badge-inner" style="background: ${scoreBadgeGradient};">
                            <div class="result-badge-icon">${scoreIcon}</div>
                        </div>
                        <div class="result-badge-content">
                            <p class="result-badge-label">نمره نهایی</p>
                            <p class="result-badge-value">${resultData.score.toFixed(1)}/9</p>
                        </div>
                    </div>
                </div>

                <p class="popup-result-text" style="margin-top: 32px; text-align: center; font-size: 14px; color: #4a4a6a;">
                    ${resultData.message || 'برای مشاهده تحلیل دقیق‌تر و بازخورد تفصیلی، به صفحه آزمون‌ها بروید.'}
                </p>
                <p class="popup-result-text hint" style="margin-top: 16px;">
                    💡 برای دیدن نتایج کامل و توصیات بهبود، بر روی دکمه زیر کلیک کنید.
                </p>
            </div>
        </div>

        <div class="popup-footer">
            <button class="popup-button popup-button-primary" onclick="window.location.href='/team7/exams/';">
                مشاهده تمام آزمون‌ها
            </button>
        </div>
    `;

    // Show popup as non-closeable (must click a button to close)
    PopupManager.showPopup(popup, false);
}

// ==================== INITIALIZATION ====================
document.addEventListener('DOMContentLoaded', () => {
    PopupManager.init();
});
