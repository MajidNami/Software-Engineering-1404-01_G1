/**
 * Language Academy - Speaking Exam JavaScript
 * Handles AJAX loading of speaking exam questions and exam flow
 */

// ==================== MOCK DATA FOR EXAMS ====================
/**
 * Mock exam questions data - Replace with API calls later
 */
const mockSpeakingExamData = {
    'speak-1': {
        title: 'توصیف تجربه شخصی',
        type: 'گفتاری',
        totalQuestions: 2,
        totalTime: 900, // 15 minutes in seconds
        questions: [
            {
                id: 'q1',
                title: 'Part 1: سوال شخصی',
                type: 'گفتاری',
                badge: 'آزمون گفتاری تافل',
                instruction: 'دستورالعمل: در این بخش باید درباره یک موضوع شخصی صحبت کنید. 45 ثانیه زمان دارید تا آماده شوید و سپس 2 دقیقه برای پاسخ دادن.',
                content: 'درباره یک معلمی که تأثیر مثبتی بر زندگی شما داشته است صحبت کنید. توضیح دهید که این معلم چه کاری انجام داد و چرا این تأثیر برای شما مهم بود.',
                requirements: [
                    'معلم را معرفی کنید',
                    'اقدامات او را توضیح دهید',
                    'تأثیر بر زندگی شما را بیان کنید',
                    'با وضوح و روانی صحبت کنید'
                ],
                tips: [
                    'از زمان آماده‌سازی برای یادداشت نکات کلیدی استفاده کنید',
                    'پاسخ خود را با ساختار منطقی سازماندهی کنید',
                    'از مثال‌های مشخص استفاده کنید',
                    'با آرامش و اعتماد به نفس صحبت کنید'
                ],
                preparationTime: 45,
                speakingTime: 120
            },
            {
                id: 'q2',
                title: 'Part 2: روایت داستان',
                type: 'گفتاری',
                badge: 'آزمون گفتاری تافل',
                instruction: 'دستورالعمل: در این بخش باید یک داستان را روایت کنید. 45 ثانیه زمان دارید تا آماده شوید و سپس 2 دقیقه برای صحبت کردن.',
                content: 'درباره یک سفر خاطره‌انگیز صحبت کنید. توضیح دهید کجا رفتید، چه کسی با شما بود، چه کاری کردید و چرا آن سفر برای شما خاص بود.',
                requirements: [
                    'مقصد سفر را توضیح دهید',
                    'هم‌سفران را معرفی کنید',
                    'فعالیت‌های انجام‌شده را شرح دهید',
                    'احساسات و تأثیرات را بیان کنید'
                ],
                tips: [
                    'ترتیب زمانی را رعایت کنید',
                    'جزئیات جالب و دلچسب را شامل کنید',
                    'از انتقالات صحیح استفاده کنید',
                    'صدای خود را متنوع نگه دارید'
                ],
                preparationTime: 45,
                speakingTime: 120
            }
        ]
    },
    'speak-2': {
        title: 'بحث و بررسی',
        type: 'گفتاری',
        totalQuestions: 2,
        totalTime: 1200, // 20 minutes in seconds
        questions: [
            {
                id: 'q1',
                title: 'Part 1: تحلیل مسئله',
                type: 'گفتاری',
                badge: 'آزمون گفتاری تافل',
                instruction: 'دستورالعمل: یک مسئله اجتماعی معطوف شده است. باید آن را تحلیل کنید و نظرات خود را بیان کنید. 1 دقیقه زمان برای آماده شدن و 3 دقیقه برای صحبت کردن.',
                content: 'بیش‌تر جوانان برای تحصیل و شغل به شهرهای بزرگ مهاجرت می‌کنند. این مسئله را در شهرهای کوچک بحث کنید. مزایا و معایب این مهاجرت را تحلیل کنید.',
                requirements: [
                    'مسئله را واضح تعریف کنید',
                    'مزایا را ذکر کنید',
                    'معایب را بیان کنید',
                    'راه‌حل یا نظر شخصی ارائه دهید'
                ],
                tips: [
                    'موضوع را به خوبی درک کنید',
                    'از مثال‌های واقعی استفاده کنید',
                    'هر دو طرف مسئله را بررسی کنید',
                    'به موضوع اصلی وفادار بمانید'
                ],
                preparationTime: 60,
                speakingTime: 180
            }
        ]
    }
};

// ==================== EXAM STATE MANAGEMENT ====================
const speakingExamState = {
    currentExamId: null,
    currentQuestionIndex: 0,
    totalQuestions: 0,
    currentExam: null,
    recordings: {}, // { questionId: audioBlob }
    startTime: null,
    timeRemaining: 0,
    timerInterval: null,
    timeElapsedInterval: null,
    isRecording: false,
    isPaused: false,
    recordingTime: 0,
    recordingTimer: null,
    currentAttempt: 1,
    maxAttempts: 3,
    mediaRecorder: null,
    audioChunks: [],
};

// ==================== INITIALIZATION ====================
document.addEventListener('DOMContentLoaded', function() {
    console.log('Speaking exam page loaded');
    
    // Get exam ID from URL or default
    const params = new URLSearchParams(window.location.search);
    const examId = params.get('exam_id') || Object.keys(mockSpeakingExamData)[0];
    
    initializeSpeakingExam(examId);
    attachEventListeners();
});

// ==================== INITIALIZE EXAM ====================
function initializeSpeakingExam(examId) {
    if (!mockSpeakingExamData[examId]) {
        console.error(`Exam ${examId} not found`);
        return;
    }
    
    const exam = mockSpeakingExamData[examId];
    speakingExamState.currentExamId = examId;
    speakingExamState.currentExam = exam;
    speakingExamState.totalQuestions = exam.questions.length;
    speakingExamState.currentQuestionIndex = 0;
    speakingExamState.timeRemaining = exam.totalTime;
    
    // Start the exam directly (popup was shown in exam.js)
    loadQuestion(0);
    startExamTimer();
}

// ==================== LOAD QUESTION ====================
function loadQuestion(questionIndex) {
    const exam = speakingExamState.currentExam;
    if (questionIndex < 0 || questionIndex >= exam.questions.length) {
        console.warn('Question index out of bounds');
        return;
    }
    
    speakingExamState.currentQuestionIndex = questionIndex;
    const question = exam.questions[questionIndex];
    
    // Update question counter
    const counter = document.getElementById('questionCounter');
    if (counter) {
        counter.textContent = `سوال ${questionIndex + 1} از ${exam.totalQuestions}`;
    }
    
    // Update question panel
    const questionPanel = document.getElementById('questionPanel');
    if (questionPanel) {
        questionPanel.innerHTML = `
            <div class="question-header">
                <div class="question-type-badge">
                    <div class="question-type-badge-inner">
                        <p>${question.badge}</p>
                    </div>
                </div>
                <p class="question-title">${question.title}</p>
            </div>

            <div class="question-body">
                <!-- Question Instruction -->
                <div class="question-instruction">
                    <p class="instruction-title">دستورالعمل:</p>
                    <p class="instruction-text">${question.instruction}</p>
                </div>

                <!-- Question Content -->
                <div class="question-content">
                    <p>${question.content}</p>
                </div>

                <!-- Question Requirements -->
                <div class="question-requirements">
                    <p class="requirements-title">نکات مهم:</p>
                    ${question.requirements.map(req => `
                        <div class="requirement">
                            <p>${req}</p>
                            <div class="bullet"></div>
                        </div>
                    `).join('')}
                </div>

                <!-- Question Tips -->
                <div class="question-tips">
                    <p class="tips-title">راهنمایی:</p>
                    ${question.tips.map(tip => `
                        <div class="tip">
                            <p>${tip}</p>
                            <div class="tip-icon"></div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }
    
    // Update attempts
    const attempts = document.getElementById('attempts');
    if (attempts) {
        attempts.textContent = `${speakingExamState.currentAttempt}/${speakingExamState.maxAttempts}`;
    }
    
    // Reset recording state for new question
    resetRecordingState();
}

// ==================== TIMER FUNCTIONS ====================
function startExamTimer() {
    if (speakingExamState.timerInterval) {
        clearInterval(speakingExamState.timerInterval);
    }
    
    speakingExamState.timerInterval = setInterval(function() {
        if (speakingExamState.timeRemaining > 0) {
            speakingExamState.timeRemaining--;
            updateTimerDisplay();
        } else {
            clearInterval(speakingExamState.timerInterval);
            handleTimeUp();
        }
    }, 1000);
}

function updateTimerDisplay() {
    const minutes = Math.floor(speakingExamState.timeRemaining / 60);
    const seconds = speakingExamState.timeRemaining % 60;
    const timeString = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
    
    const timerElement = document.getElementById('timer');
    if (timerElement) {
        timerElement.textContent = timeString;
    }
}

function handleTimeUp() {
    alert('زمان آزمون به پایان رسید!');
    // Auto-submit the exam
    submitExam();
}

// ==================== RECORDING FUNCTIONS ====================
function formatTime(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
}

async function startRecording() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        speakingExamState.mediaRecorder = new MediaRecorder(stream);
        speakingExamState.audioChunks = [];
        speakingExamState.isRecording = true;
        speakingExamState.isPaused = false;
        speakingExamState.recordingTime = 0;
        
        speakingExamState.mediaRecorder.ondataavailable = (event) => {
            speakingExamState.audioChunks.push(event.data);
        };
        
        speakingExamState.mediaRecorder.start();
        
        // Update UI
        const micTitle = document.getElementById('micTitle');
        if (micTitle) micTitle.textContent = 'در حال ضبط...';
        const micSubtitle = document.getElementById('micSubtitle');
        if (micSubtitle) micSubtitle.textContent = 'برای توقف ضبط روی دکمه توقف کلیک کنید';
        
        // Start recording timer
        startRecordingTimer();
        console.log('Recording started');
    } catch (error) {
        console.error('Error accessing microphone:', error);
        alert('نمی‌توان به میکروفون دسترسی پیدا کرد. لطفاً مجوزها را بررسی کنید.');
    }
}

function startRecordingTimer() {
    if (speakingExamState.recordingTimer) {
        clearInterval(speakingExamState.recordingTimer);
    }
    
    speakingExamState.recordingTimer = setInterval(function() {
        if (!speakingExamState.isPaused && speakingExamState.isRecording) {
            speakingExamState.recordingTime++;
            updateRecordingTimerDisplay();
        }
    }, 1000);
}

function updateRecordingTimerDisplay() {
    const timeString = formatTime(speakingExamState.recordingTime);
    const recordingTimeElement = document.getElementById('recordingTime');
    if (recordingTimeElement) {
        recordingTimeElement.textContent = timeString;
    }
    const recordingTimerLarge = document.getElementById('recordingTimerLarge');
    if (recordingTimerLarge) {
        recordingTimerLarge.textContent = timeString;
    }
}

function togglePause() {
    if (!speakingExamState.isRecording) return;
    
    speakingExamState.isPaused = !speakingExamState.isPaused;
    
    if (speakingExamState.isPaused) {
        speakingExamState.mediaRecorder.pause();
        const micTitle = document.getElementById('micTitle');
        if (micTitle) micTitle.textContent = 'ضبط متوقف شد';
    } else {
        speakingExamState.mediaRecorder.resume();
        const micTitle = document.getElementById('micTitle');
        if (micTitle) micTitle.textContent = 'در حال ضبط...';
    }
    
    console.log(speakingExamState.isPaused ? 'Recording paused' : 'Recording resumed');
}

function stopRecording() {
    if (!speakingExamState.isRecording || !speakingExamState.mediaRecorder) return;
    
    speakingExamState.mediaRecorder.stop();
    speakingExamState.mediaRecorder.onstop = function() {
        const audioBlob = new Blob(speakingExamState.audioChunks, { type: 'audio/wav' });
        const questionId = speakingExamState.currentExam.questions[speakingExamState.currentQuestionIndex].id;
        speakingExamState.recordings[questionId] = audioBlob;
        
        // Stop all tracks
        speakingExamState.mediaRecorder.stream.getTracks().forEach(track => track.stop());
        
        // Reset recording state
        resetRecordingState();
        
        // Add playback item
        addPlaybackItem(questionId, speakingExamState.recordingTime);
    };
    
    if (speakingExamState.recordingTimer) {
        clearInterval(speakingExamState.recordingTimer);
    }
    
    speakingExamState.isRecording = false;
    speakingExamState.isPaused = false;
    
    console.log('Recording stopped. Duration:', formatTime(speakingExamState.recordingTime));
}

function resetRecordingState() {
    speakingExamState.isRecording = false;
    speakingExamState.isPaused = false;
    speakingExamState.recordingTime = 0;
    
    const micTitle = document.getElementById('micTitle');
    if (micTitle) micTitle.textContent = 'آماده برای ضبط';
    const micSubtitle = document.getElementById('micSubtitle');
    if (micSubtitle) micSubtitle.textContent = 'روی میکروفون کلیک کنید تا ضبط شروع شود';
    
    const recordingTime = document.getElementById('recordingTime');
    if (recordingTime) recordingTime.textContent = '00:00';
    const recordingTimerLarge = document.getElementById('recordingTimerLarge');
    if (recordingTimerLarge) recordingTimerLarge.textContent = '00:00';
    
    if (speakingExamState.recordingTimer) {
        clearInterval(speakingExamState.recordingTimer);
    }
}

function addPlaybackItem(questionId, duration) {
    const playbackList = document.getElementById('playbackList');
    if (!playbackList) return;
    
    const playbackHTML = `
        <div class="playback-item" data-question-id="${questionId}">
            <div class="playback-item-inner">
                <!-- Playback Actions -->
                <div class="playback-actions">
                    <div class="playback-action-btn download-btn" onclick="downloadRecording('${questionId}')">
                        <svg viewBox="0 0 40 40" fill="none">
                            <rect width="40" height="40" rx="8" fill="white"/>
                            <path d="M20 14V26M20 26L16 22M20 26L24 22" stroke="#0B0754" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                    </div>
                    <div class="playback-action-btn play-btn" onclick="playRecording('${questionId}')">
                        <svg viewBox="0 0 40 40" fill="none">
                            <rect x="1" y="1" width="38" height="38" rx="7" fill="white" stroke="#4CAF50" stroke-width="2"/>
                            <path d="M17 14L26 20L17 26V14Z" fill="#4CAF50"/>
                        </svg>
                    </div>
                </div>

                <!-- Playback Left -->
                <div class="playback-left">
                    <div class="playback-info">
                        <p class="playback-name">ضبط ${speakingExamState.currentAttempt} - تلاش ${speakingExamState.currentAttempt}</p>
                        <p class="playback-duration">مدت زمان: ${formatTime(duration)}</p>
                    </div>
                    <div class="playback-sound-wave">
                        <div class="sound-wave-small">
                            <div class="bar-small bar1-small"></div>
                            <div class="bar-small bar2-small"></div>
                            <div class="bar-small bar3-small"></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    playbackList.insertAdjacentHTML('beforeend', playbackHTML);
}

function playRecording(questionId) {
    const audioBlob = speakingExamState.recordings[questionId];
    if (!audioBlob) {
        alert('ضبط یافت نشد');
        return;
    }
    
    const audioUrl = URL.createObjectURL(audioBlob);
    const audio = new Audio(audioUrl);
    audio.play();
}

function downloadRecording(questionId) {
    const audioBlob = speakingExamState.recordings[questionId];
    if (!audioBlob) {
        alert('ضبط یافت نشد');
        return;
    }
    
    const audioUrl = URL.createObjectURL(audioBlob);
    const a = document.createElement('a');
    a.href = audioUrl;
    a.download = `recording-${questionId}.wav`;
    a.click();
    URL.revokeObjectURL(audioUrl);
}

// ==================== NAVIGATION ====================
function previousQuestion() {
    if (speakingExamState.currentQuestionIndex > 0) {
        loadQuestion(speakingExamState.currentQuestionIndex - 1);
    }
}

function nextQuestion() {
    if (speakingExamState.currentQuestionIndex < speakingExamState.totalQuestions - 1) {
        loadQuestion(speakingExamState.currentQuestionIndex + 1);
    }
}

// ==================== SUBMIT EXAM ====================
function submitExam() {
    // Show submit confirmation popup
    showSubmitExamPopup(() => {
        // Stop all timers
        if (speakingExamState.timerInterval) clearInterval(speakingExamState.timerInterval);
        if (speakingExamState.recordingTimer) clearInterval(speakingExamState.recordingTimer);
        if (speakingExamState.isRecording) stopRecording();
        
        // Prepare submission data
        const submissionData = {
            examId: speakingExamState.currentExamId,
            recordings: Object.keys(speakingExamState.recordings).map(qId => ({
                questionId: qId,
                duration: speakingExamState.recordingTime
            })),
            timeElapsed: speakingExamState.currentExam.totalTime - speakingExamState.timeRemaining
        };
        
        console.log('Submitting exam:', submissionData);
        
        // TODO: Send to server via AJAX
        // fetch('/api/v1/evaluate/speaking/', {
        //     method: 'POST',
        //     headers: {
        //         'Content-Type': 'application/json',
        //         'X-CSRFToken': getCookie('csrftoken')
        //     },
        //     body: JSON.stringify(submissionData)
        // })
        // .then(response => response.json())
        // .then(data => {
        //     window.location.href = '/team7/';
        // })
        // .catch(error => console.error('Error:', error));
        
        // Show result popup
        const resultData = {
            score: 7.8,
            answeredQuestions: speakingExamState.totalQuestions,
            totalQuestions: speakingExamState.totalQuestions,
            timeSpent: speakingExamState.currentExam.totalTime - speakingExamState.timeRemaining,
            type: speakingExamState.currentExam.title,
            message: 'عملکرد خوبی در آزمون گفتاری داشتید. برای بهبود تلفظ، تمرین بیشتری انجام دهید.'
        };
        showExamResultPopup(resultData);
    });
}

function saveRecording() {
    console.log('Saving recording...');
    alert('ضبط ذخیره شد.');
}

// ==================== EVENT LISTENERS ====================
function attachEventListeners() {
    // Navigation buttons
    const prevBtn = document.getElementById('previousBtn');
    if (prevBtn) prevBtn.addEventListener('click', previousQuestion);
    
    const nextBtn = document.getElementById('nextBtn');
    if (nextBtn) nextBtn.addEventListener('click', nextQuestion);
    
    // Recording controls
    const micButton = document.getElementById('micButton');
    if (micButton) micButton.addEventListener('click', startRecording);
    
    const recordBtn = document.getElementById('recordBtn');
    if (recordBtn) recordBtn.addEventListener('click', function() {
        if (!speakingExamState.isRecording) {
            startRecording();
        }
    });
    
    const pauseBtn = document.getElementById('pauseBtn');
    if (pauseBtn) pauseBtn.addEventListener('click', togglePause);
    
    const stopBtn = document.getElementById('stopBtn');
    if (stopBtn) stopBtn.addEventListener('click', stopRecording);
    
    // Submit and save buttons
    const submitBtn = document.getElementById('submitBtn');
    if (submitBtn) submitBtn.addEventListener('click', submitExam);
    
    const saveBtn = document.getElementById('saveBtn');
    if (saveBtn) saveBtn.addEventListener('click', saveRecording);
}
