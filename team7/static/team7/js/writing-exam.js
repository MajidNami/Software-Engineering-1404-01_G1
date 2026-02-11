/**
 * Language Academy - Exam Template JavaScript
 * Handles AJAX loading of exam questions and exam flow
 */

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

// ==================== API FUNCTIONS ====================
/**
 * Fetch exam data from API
 * @param {string} examId - The exam UUID to fetch
 * @returns {Promise<Object>} Exam data
 */
async function fetchExamFromAPI(examId) {
    try {
        const response = await fetch(`/team7/api/exams/?exam_id=${examId}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        if (!response.ok) {
            console.error(`API error: ${response.status}`);
            return null;
        }
        
        const data = await response.json();
        return data.exams && data.exams.length > 0 ? data.exams[0] : null;
    } catch (error) {
        console.error('Error fetching exam from API:', error);
        return null;
    }
}

// ==================== INITIALIZATION ====================
/**
 * Initialize exam - fetches from API
 * @param {string} examId - The exam ID to load
 */
async function initializeExam(examId) {
    console.log('Initializing exam:', examId);
    
    // Load from API
    let exam = await fetchExamFromAPI(examId);
    
    if (!exam) {
        console.error('Failed to load exam from API:', examId);
        alert('خطا: آزمون مورد نظر یافت نشد');
        return;
    }

    console.log('Setting up exam state for:', examId);
    examState.currentExamId = examId;
    examState.currentExam = exam;
    examState.totalQuestions = exam.totalQuestions || exam.questions.length;
    examState.timeRemaining = exam.totalTime;
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
    // Get exam ID from URL parameters
    const urlParams = new URLSearchParams(window.location.search);
    const examId = urlParams.get('exam_id');
    
    console.log('Writing Exam Page Loaded');
    console.log('URL:', window.location.href);
    console.log('Exam ID:', examId);

    // Initialize exam
    if (!examId) {
        console.error('No exam ID specified in URL');
        // alert('خطا: شناسه آزمون مشخص نشده است');
        return;
    }
    
    console.log('Initializing exam:', examId);
    initializeExam(examId);
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
