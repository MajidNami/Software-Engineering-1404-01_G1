/**
 * Language Academy - Exam Template JavaScript
 * Handles AJAX loading of exam questions and exam flow
 */

// ==================== MOCK DATA FOR EXAMS ====================
/**
 * Mock exam questions data - Replace with API calls later
 */
const mockExamData = {
    'write-1': {
        title: 'نامه رسمی',
        type: 'نوشتاری',
        totalQuestions: 2,
        totalTime: 1200, // 20 minutes in seconds
        questions: [
            {
                id: 'q1',
                title: 'Task 1: نامه رسمی',
                type: 'نوشتاری',
                badge: 'آزمون نوشتاری تافل',
                instruction: 'دستورالعمل: در این بخش باید یک نامه رسمی بنویسید. موضوع را با دقت بخوانید و نامه خود را به صورت حرفه‌ای تنظیم کنید.',
                content: 'شما می‌خواهید برای بورسیه تحصیلی در دانشگاه بین‌المللی درخواست دهید. یک نامه رسمی برای درخواست اطلاعات بیشتر درباره برنامه‌های بورسیه بنویسید.',
                requirements: [
                    'حداقل 150 کلمه بنویسید',
                    'نامه را با سلام و الفاظ مناسب شروع کنید',
                    'منظور خود را به وضوح بیان کنید',
                    'نامه را با الفاظ احترام‌آمیز پایان دهید'
                ],
                tips: [
                    'ساختار نامه رسمی را رعایت کنید',
                    'از زبان رسمی و احترام‌آمیز استفاده کنید',
                    'نامه را منظم و خوانا بنویسید',
                    'قبل از ارسال، نامه را بررسی کنید'
                ]
            },
            {
                id: 'q2',
                title: 'Task 2: نامه شکایت',
                type: 'نوشتاری',
                badge: 'آزمون نوشتاری تافل',
                instruction: 'دستورالعمل: در این بخش باید یک نامه شکایت بنویسید. وضعیت مسئله را به وضوح شرح دهید و راه‌حل مناسب پیشنهاد کنید.',
                content: 'شما اخیراً یک محصول آنلاین خریده‌اید اما محصول معیوب است. نامه‌ای رسمی برای فروشنده بنویسید و مسئله را شرح دهید و درخواست تعویض یا بازگشت پول کنید.',
                requirements: [
                    'حداقل 180 کلمه بنویسید',
                    'مسئله را به تفصیل توضیح دهید',
                    'راه‌حل مناسب پیشنهاد کنید',
                    'نامه را به صورت رسمی پایان دهید'
                ],
                tips: [
                    'ابتدا وضعیت فعلی را شرح دهید',
                    'مراحل مورد انتظار را مشخص کنید',
                    'از عبارات پلیت و محترمانه استفاده کنید',
                    'فاصله زمانی معقولی برای پاسخ درنظر بگیرید'
                ]
            }
        ]
    },
    'write-2': {
        title: 'تحلیل متن آکادمیک',
        type: 'نوشتاری',
        totalQuestions: 2,
        totalTime: 1500, // 25 minutes in seconds
        questions: [
            {
                id: 'q1',
                title: 'Task 1: تحلیل متن آکادمیک',
                type: 'نوشتاری',
                badge: 'آزمون نوشتاری تافل',
                instruction: 'دستورالعمل: متن آکادمیک زیر را بخوانید و تحلیل آن را بنویسید. اصلی‌ترین ایده‌ها و نتایج گیری را مشخص کنید.',
                content: 'تحقیقات اخیر نشان می‌دهد که فناوری هوش مصنوعی تأثیری عمیق بر نظام آموزشی دارد. این فناوری نه تنها روش تدریس را تغییر داده بلکه شیوه یادگیری دانشجویان را نیز دگرگون کرده است. از یک طرف، استفاده از سیستم‌های هوشمند مدرسی، سفارشی‌سازی یادگیری را ممکن ساخته است. از طرف دیگر، افزایش وابستگی به فناوری می‌تواند مهارت‌های اجتماعی دانشجویان را تحت تأثیر قرار دهد.',
                requirements: [
                    'حداقل 200 کلمه بنویسید',
                    'اصلی‌ترین ایده را مشخص کنید',
                    'شواهد و مستندات را بررسی کنید',
                    'نتیجه‌گیری منطقی ارائه دهید'
                ],
                tips: [
                    'متن را دقیق بخوانید و اصلی‌ترین ایده‌ها را یادداشت کنید',
                    'بین ایده‌های اصلی و فرعی تفریق قایل شوید',
                    'موضع خود را با شواهد پشتیبانی کنید',
                    'تحلیل خود را منطقی و منسجم نوشته کنید'
                ]
            }
        ]
    },
    'write-3': {
        title: 'نوشتن پیشنهاد بهبود',
        type: 'نوشتاری',
        totalQuestions: 2,
        totalTime: 1200, // 20 minutes in seconds
        questions: [
            {
                id: 'q1',
                title: 'Task 1: نوشتن پیشنهاد بهبود',
                type: 'نوشتاری',
                badge: 'آزمون نوشتاری تافل',
                instruction: 'دستورالعمل: یک پیشنهاد برای بهبود سرویس یا محصول بنویسید. مشکل فعلی و راه‌حل پیشنهادی خود را به صورت واضح ارائه دهید.',
                content: 'شما در یک شرکت کاری می‌کنید. سیستم مدیریت زمان شرکت بسیار قدیمی است و کارمندان را با مشکلات زیادی روبرو می‌کند. یک پیشنهاه برای بهبود این سیستم بنویسید.',
                requirements: [
                    'حداقل 150 کلمه بنویسید',
                    'مشاکل فعلی را تشریح کنید',
                    'راه‌حل مفصل پیشنهاد کنید',
                    'مزایای پیشنهاد را بیان کنید'
                ],
                tips: [
                    'با درخواست توجه شروع کنید',
                    'مشاکل را با مثال‌های واقعی توضیح دهید',
                    'راه‌حل را مرحله به مرحله ارائه دهید',
                    'با درخواست ملاقات برای بحث بیشتر بپایان برسانید'
                ]
            },
            {
                id: 'q2',
                title: 'Task 2: نامه توصیه‌ای',
                type: 'نوشتاری',
                badge: 'آزمون نوشتاری تافل',
                instruction: 'دستورالعمل: یک نامه توصیه‌ای برای یکی از دوستان خود که برای شغل جدید درخواست داده است، بنویسید.',
                content: 'دوست شما برای کار در یک شرکت معروف اپلیکیشن داده است. از شما خواسته شده که یک نامه توصیه‌ای برای او بنویسید. در این نامه توانایی‌ها و صفات مثبت او را بیان کنید.',
                requirements: [
                    'حداقل 180 کلمه بنویسید',
                    'درباره صفات و توانایی‌های دوست صحبت کنید',
                    'مثال‌های خاص از کار او ارائه دهید',
                    'نامه را با توصیه قوی پایان دهید'
                ],
                tips: [
                    'نامه را رسمی و احترام‌آمیز بنویسید',
                    'تجربه و مهارت‌های خاص را برجسته کنید',
                    'مثال‌های واقعی از عملکرد خوب ارائه دهید',
                    'نامه را با درخواست پیگیری پایان دهید'
                ]
            }
        ]
    },
    'write-4': {
        title: 'توضیح و دفاع از نظر شخصی',
        type: 'نوشتاری',
        totalQuestions: 2,
        totalTime: 1400, // 23 minutes in seconds
        questions: [
            {
                id: 'q1',
                title: 'Task 1: دفاع از یک ادعا',
                type: 'نوشتاری',
                badge: 'آزمون نوشتاری تافل',
                instruction: 'دستورالعمل: موضوع زیر را بخوانید و نظر خود را بیان کنید. نظرتان را با شواهد قوی دفاع کنید.',
                content: 'آیا شما بر این باور هستید که آموزش آنلاین به اندازه آموزش حضوری مؤثر است؟ نظر خود را بیان کنید.',
                requirements: [
                    'حداقل 200 کلمه بنویسید',
                    'نظر خود را واضح بیان کنید',
                    'حداقل سه دلیل برای پشتیبانی از نظر ارائه دهید',
                    'احتمال اعتراضات را پاسخ دهید'
                ],
                tips: [
                    'موضع واضح و قاطع اتخاذ کنید',
                    'دلایل منطقی ارائه دهید',
                    'مثال‌های عملی استفاده کنید',
                    'نتیجه‌گیری قوی نوشته کنید'
                ]
            },
            {
                id: 'q2',
                title: 'Task 2: مقایسه دو راه‌حل',
                type: 'نوشتاری',
                badge: 'آزمون نوشتاری تافل',
                instruction: 'دستورالعمل: دو راه‌حل مختلف برای یک مسئله ارائه می‌شود. بهتری را انتخاب کنید و دلایل خود را توضیح دهید.',
                content: 'برای کاهش ترافیک شهری، دو راه‌حل وجود دارد: 1) افزایش و بهبود حمل‌ونقل عمومی، 2) محدود کردن ورود خودروهای شخصی به مرکز شهر. کدام راه‌حل بهتر است؟',
                requirements: [
                    'حداقل 210 کلمه بنویسید',
                    'هر دو راه‌حل را تحلیل کنید',
                    'مزایا و معایب را مقایسه کنید',
                    'انتخاب خود را توجیه کنید'
                ],
                tips: [
                    'هر دو طرف را بی‌طرفانه بررسی کنید',
                    'معایب و مزایای واقعی را نام ببرید',
                    'از مثال‌های واقع نزدیک استفاده کنید',
                    'نتیجه‌گیری را با استدلال منطقی پشتیبانی کنید'
                ]
            }
        ]
    }
};

// ==================== EXAM STATE MANAGEMENT ====================
const examState = {
    currentExamId: null,
    currentQuestionIndex: 0,
    totalQuestions: 0,
    currentExam: null,
    answers: {},
    startTime: null,
    timeRemaining: 0,
    timerInterval: null,
    timeElapsedInterval: null,
    userAnswers: {}
};

// ==================== FONT SIZE STATE ====================
let currentFontSize = 16;
const minFontSize = 12;
const maxFontSize = 24;

// ==================== INITIALIZATION ====================
/**
 * Initialize exam with mock data
 * @param {string} examId - The exam ID to load
 */
function initializeExam(examId) {
    // Load mock data (replace with API call later)
    if (!mockExamData[examId]) {
        console.error('Exam not found:', examId, 'Available:', Object.keys(mockExamData));
        return;
    }

    console.log('Setting up exam state for:', examId);
    examState.currentExamId = examId;
    examState.currentExam = mockExamData[examId];
    examState.totalQuestions = examState.currentExam.questions.length;
    examState.timeRemaining = examState.currentExam.totalTime;
    examState.startTime = Date.now();
    examState.userAnswers = {};

    console.log('Exam State:', examState);
    console.log('Total Questions:', examState.totalQuestions);
    console.log('First Question:', examState.currentExam.questions[0]);

    // Initialize first question (popup was shown in exam.js)
    loadQuestion(0);
    startTimer();
    attachEventListeners();
    
    console.log('Exam initialized successfully');
}

// ==================== QUESTION LOADING ====================
/**
 * Load a specific question via AJAX
 * @param {number} questionIndex - Index of the question to load
 */
function loadQuestion(questionIndex) {
    if (questionIndex < 0 || questionIndex >= examState.totalQuestions) {
        console.error('Invalid question index:', questionIndex);
        return;
    }

    console.log('Loading question:', questionIndex);
    examState.currentQuestionIndex = questionIndex;
    const question = examState.currentExam.questions[questionIndex];

    // Show loading state
    const questionPanel = document.getElementById('questionPanel');
    if (!questionPanel) {
        console.error('Question panel not found in DOM');
        return;
    }
    
    questionPanel.innerHTML = '<div class="loading-spinner"><p>درحال بارگذاری سوال...</p></div>';

    // Simulate AJAX delay
    setTimeout(() => {
        console.log('Rendering question:', question);
        renderQuestion(question);
        updateQuestionCounter();
        updateNavigationButtons();
    }, 300);
}

/**
 * Render question content in the question panel
 * @param {Object} question - Question object to render
 */
function renderQuestion(question) {
    const questionPanel = document.getElementById('questionPanel');
    
    if (!questionPanel) {
        console.error('Question panel not found in DOM');
        return;
    }

    if (!question) {
        console.error('Question object is null or undefined');
        questionPanel.innerHTML = '<div class="error-message"><p>خطا: سوال یافت نشد</p></div>';
        return;
    }
    
    let tipsHTML = '';
    if (question.tips && question.tips.length > 0) {
        tipsHTML = `
            <div class="question-tips">
                <p class="tips-title">نکات مهم:</p>
                ${question.tips.map(tip => `
                    <div class="tip">
                        <p>${tip}</p>
                        <div class="tip-icon">✓</div>
                    </div>
                `).join('')}
            </div>
        `;
    }

    const html = `
        <div class="question-header">
            <div class="question-type-badge">
                <p>${question.badge}</p>
            </div>
            <p class="question-title">${question.title}</p>
        </div>

        <div class="question-body">
            <div class="question-instruction">
                <p class="instruction-title">دستورالعمل:</p>
                <p class="instruction-text">${question.instruction}</p>
            </div>

            <div class="question-content">
                <p>${question.content}</p>
            </div>

            <div class="question-requirements">
                <p class="requirements-title">الزامات:</p>
                ${question.requirements.map(req => `
                    <div class="requirement">
                        <p>${req}</p>
                        <div class="bullet"></div>
                    </div>
                `).join('')}
            </div>

            ${tipsHTML}
        </div>
    `;

    questionPanel.innerHTML = html;
    
    // Load previous answer if exists
    const answerTextarea = document.getElementById('answerTextarea');
    if (answerTextarea) {
        if (examState.userAnswers[question.id]) {
            answerTextarea.value = examState.userAnswers[question.id];
            updateWordCount();
            updateProgress();
        } else {
            answerTextarea.value = '';
            updateWordCount();
            updateProgress();
        }
    } else {
        console.error('Answer textarea not found in DOM');
    }
}

// ==================== TIMER MANAGEMENT ====================
/**
 * Start the countdown timer
 */
function startTimer() {
    updateTimerDisplay();

    examState.timerInterval = setInterval(() => {
        examState.timeRemaining--;

        if (examState.timeRemaining < 0) {
            clearInterval(examState.timerInterval);
            submitExam();
            return;
        }

        updateTimerDisplay();
    }, 1000);
}

/**
 * Update timer display with warning indicators
 */
function updateTimerDisplay() {
    const timerElement = document.getElementById('timer');
    const minutes = Math.floor(examState.timeRemaining / 60);
    const seconds = examState.timeRemaining % 60;
    const timeString = `${minutes}:${seconds.toString().padStart(2, '0')}`;

    timerElement.textContent = timeString;

    // Add warning classes
    timerElement.classList.remove('warning', 'critical');
    if (examState.timeRemaining < 60) {
        timerElement.classList.add('critical');
    } else if (examState.timeRemaining < 300) {
        timerElement.classList.add('warning');
    }
}

/**
 * Update elapsed time display
 */
function updateTimeElapsed() {
    const timeElapsedElement = document.getElementById('timeElapsed');
    const elapsed = Date.now() - examState.startTime;
    const seconds = Math.floor(elapsed / 1000);
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;

    timeElapsedElement.textContent = `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
}

// ==================== WORD COUNT & PROGRESS ====================
/**
 * Update word count display
 */
function updateWordCount() {
    const textarea = document.getElementById('answerTextarea');
    const wordCountElement = document.getElementById('wordCount');
    
    if (!textarea || !wordCountElement) {
        console.warn('Word count elements not found');
        return;
    }

    const text = textarea.value.trim();
    const words = text.split(/\s+/).filter(word => word.length > 0).length;

    wordCountElement.textContent = words;
}

/**
 * Update progress percentage
 */
function updateProgress() {
    const textarea = document.getElementById('answerTextarea');
    const progressElement = document.getElementById('progress');
    
    if (!textarea || !progressElement) {
        console.warn('Progress elements not found');
        return;
    }

    const text = textarea.value.trim();
    const words = text.split(/\s+/).filter(word => word.length > 0).length;
    
    // Calculate progress based on typical minimum word count (250 words)
    const targetWords = 250;
    const percentage = Math.min(100, Math.round((words / targetWords) * 100));

    progressElement.textContent = percentage + '%';
}

// ==================== FONT SIZE CONTROL ====================
/**
 * Update font size for textarea
 */
function updateFontSize() {
    const textarea = document.getElementById('answerTextarea');
    const fontSizeDisplay = document.getElementById('fontSizeDisplay');

    if (!textarea || !fontSizeDisplay) {
        console.warn('Font size elements not found');
        return;
    }

    textarea.style.fontSize = currentFontSize + 'px';
    fontSizeDisplay.textContent = currentFontSize;
    console.log('Font size updated to:', currentFontSize);
}

// ==================== NAVIGATION ====================
/**
 * Go to next question
 */
function nextQuestion() {
    console.log('Next question requested. Current index:', examState.currentQuestionIndex, 'Total:', examState.totalQuestions);
    
    // Save current answer
    const textarea = document.getElementById('answerTextarea');
    const currentQuestion = examState.currentExam.questions[examState.currentQuestionIndex];
    
    if (textarea) {
        examState.userAnswers[currentQuestion.id] = textarea.value;
        console.log('Saved answer for question:', currentQuestion.id);
    }

    if (examState.currentQuestionIndex < examState.totalQuestions - 1) {
        console.log('Loading next question:', examState.currentQuestionIndex + 1);
        loadQuestion(examState.currentQuestionIndex + 1);
    } else {
        console.log('Already on last question');
    }
}

/**
 * Go to previous question
 */
function previousQuestion() {
    console.log('Previous question requested. Current index:', examState.currentQuestionIndex);
    
    // Save current answer
    const textarea = document.getElementById('answerTextarea');
    const currentQuestion = examState.currentExam.questions[examState.currentQuestionIndex];
    
    if (textarea) {
        examState.userAnswers[currentQuestion.id] = textarea.value;
        console.log('Saved answer for question:', currentQuestion.id);
    }

    if (examState.currentQuestionIndex > 0) {
        console.log('Loading previous question:', examState.currentQuestionIndex - 1);
        loadQuestion(examState.currentQuestionIndex - 1);
    } else {
        console.log('Already on first question');
    }
}

/**
 * Update question counter display
 */
function updateQuestionCounter() {
    const counter = document.getElementById('questionCounter');
    counter.textContent = `سوال ${examState.currentQuestionIndex + 1} از ${examState.totalQuestions}`;
}

/**
 * Update navigation button states
 */
function updateNavigationButtons() {
    const prevBtn = document.getElementById('previousBtn');
    const nextBtn = document.getElementById('nextBtn');

    if (!prevBtn || !nextBtn) {
        console.error('Navigation buttons not found in DOM');
        return;
    }

    // Disable previous button if on first question
    if (examState.currentQuestionIndex === 0) {
        prevBtn.classList.add('disabled');
        prevBtn.style.pointerEvents = 'none';
        prevBtn.style.opacity = '0.5';
    } else {
        prevBtn.classList.remove('disabled');
        prevBtn.style.pointerEvents = 'auto';
        prevBtn.style.opacity = '1';
    }

    // Disable next button if on last question
    if (examState.currentQuestionIndex === examState.totalQuestions - 1) {
        nextBtn.classList.add('disabled');
        nextBtn.style.pointerEvents = 'none';
        nextBtn.style.opacity = '0.5';
    } else {
        nextBtn.classList.remove('disabled');
        nextBtn.style.pointerEvents = 'auto';
        nextBtn.style.opacity = '1';
    }
}

// ==================== EXAM SUBMISSION ====================
/**
 * Save draft answers
 */
function saveDraft() {
    const textarea = document.getElementById('answerTextarea');
    const currentQuestion = examState.currentExam.questions[examState.currentQuestionIndex];
    examState.userAnswers[currentQuestion.id] = textarea.value;

    // Visual feedback
    const saveBtn = document.getElementById('saveBtn');
    const originalText = saveBtn.textContent;
    saveBtn.textContent = 'ذخیره شد ✓';

    setTimeout(() => {
        saveBtn.textContent = originalText;
    }, 2000);

    console.log('Draft saved:', examState.userAnswers);
}

/**
 * Submit exam
 */
function submitExam() {
    // Show submit confirmation popup
    showSubmitExamPopup(() => {
        // Save current answer
        const textarea = document.getElementById('answerTextarea');
        const currentQuestion = examState.currentExam.questions[examState.currentQuestionIndex];
        examState.userAnswers[currentQuestion.id] = textarea.value;

        // Stop timers
        clearInterval(examState.timerInterval);
        clearInterval(examState.timeElapsedInterval);

        // Prepare submission data
        const submissionData = {
            examId: examState.currentExamId,
            examTitle: examState.currentExam.title,
            totalQuestions: examState.totalQuestions,
            answers: examState.userAnswers,
            submittedAt: new Date().toISOString(),
            timeUsed: Math.floor((Date.now() - examState.startTime) / 1000)
        };

        console.log('Submitting exam:', submissionData);

        // TODO: Send to API
        // fetch('/api/submit-exam', {
        //     method: 'POST',
        //     headers: {
        //         'Content-Type': 'application/json',
        //     },
        //     body: JSON.stringify(submissionData)
        // }).then(response => response.json())
        //   .then(data => {
        //       // Handle response
        //       window.location.href = '/exams/results/';
        //   });

        // Show result popup
        const resultData = {
            score: 8.2,
            totalScore: 10,
            type: examState.currentExam.title,
            message: 'عملکرد خوبی داشتید. برای بهبود بیشتر، نکات ضعیف خود را بررسی کنید.'
        };
        showExamResultPopup(resultData);
    });
}

// ==================== EVENT LISTENERS ====================
/**
 * Attach all event listeners
 */
function attachEventListeners() {
    console.log('Attaching event listeners...');
    
    // Navigation
    const previousBtn = document.getElementById('previousBtn');
    const nextBtn = document.getElementById('nextBtn');
    
    if (previousBtn) {
        previousBtn.addEventListener('click', previousQuestion);
        console.log('Previous button listener attached');
    } else {
        console.error('Previous button not found');
    }
    
    if (nextBtn) {
        nextBtn.addEventListener('click', nextQuestion);
        console.log('Next button listener attached');
    } else {
        console.error('Next button not found');
    }

    // Buttons
    const saveBtn = document.getElementById('saveBtn');
    const submitBtn = document.getElementById('submitBtn');
    
    if (saveBtn) {
        saveBtn.addEventListener('click', saveDraft);
        console.log('Save button listener attached');
    } else {
        console.error('Save button not found');
    }
    
    if (submitBtn) {
        submitBtn.addEventListener('click', () => {
                submitExam();
            
        });
        console.log('Submit button listener attached');
    } else {
        console.error('Submit button not found');
    }

    // Textarea
    const textarea = document.getElementById('answerTextarea');
    if (textarea) {
        textarea.addEventListener('input', () => {
            updateWordCount();
            updateProgress();
        });
        console.log('Textarea listener attached');
    } else {
        console.error('Answer textarea not found');
    }

    // Font size controls
    const decreaseFont = document.getElementById('decreaseFont');
    const increaseFont = document.getElementById('increaseFont');
    
    if (decreaseFont) {
        decreaseFont.addEventListener('click', () => {
            if (currentFontSize > minFontSize) {
                currentFontSize--;
                updateFontSize();
            }
        });
        console.log('Decrease font button listener attached');
    } else {
        console.error('Decrease font button not found');
    }
    
    if (increaseFont) {
        increaseFont.addEventListener('click', () => {
            if (currentFontSize < maxFontSize) {
                currentFontSize++;
                updateFontSize();
            }
        });
        console.log('Increase font button listener attached');
    } else {
        console.error('Increase font button not found');
    }

    // Update elapsed time every second
    examState.timeElapsedInterval = setInterval(updateTimeElapsed, 1000);
    updateTimeElapsed();
    
    console.log('All event listeners attached successfully');
}

// ==================== PAGE INITIALIZATION ====================
/**
 * Initialize exam page on DOM ready
 */
document.addEventListener('DOMContentLoaded', () => {
    // Get exam ID from URL or data attribute
    const urlParams = new URLSearchParams(window.location.search);
    const examId = urlParams.get('exam') || document.body.dataset.examId || 'write-1';
    
    console.log('Exam Template Page Loaded');
    console.log('URL:', window.location.href);
    console.log('Query Parameters:', Object.fromEntries(urlParams));
    console.log('Exam ID:', examId);
    console.log('Available exams:', Object.keys(mockExamData));

    // Initialize exam
    if (examId && mockExamData[examId]) {
        console.log('Initializing exam:', examId);
        initializeExam(examId);
    } else {
        console.error('Invalid exam ID or exam data not found:', examId);
        alert(`خطا: آزمون با شناسه "${examId}" یافت نشد.\n\nآزمون‌های موجود: ${Object.keys(mockExamData).join(', ')}`);
    }
});

// ==================== EXPORT FOR TESTING ====================
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        initializeExam,
        loadQuestion,
        nextQuestion,
        previousQuestion,
        submitExam,
        examState,
        mockExamData
    };
}
