/**
 * Language Academy - Speaking Exam JavaScript
 * Handles AJAX loading of speaking exam questions and exam flow
 */

// ==================== EXAM STATE MANAGEMENT ====================
const speakingExamState = {
    currentExamId: null,
    currentQuestionIndex: 0,
    totalQuestions: 0,
    currentExam: null,
    recordings: {}, // { questionId: [{ blob, duration, attempt }, ...] }
    selectedRecordings: {}, // { questionId: recordingIndex } - tracks which recording is selected for each question
    startTime: null,
    timeRemaining: 0,
    timerInterval: null,
    timeElapsedInterval: null,
    isRecording: false,
    isPaused: false,
    recordingTime: 0,
    recordingTimer: null,
    currentAttempt: 0,
    maxAttempts: 3,
    mediaRecorder: null,
    audioChunks: [],
};

// ==================== INITIALIZATION ====================
document.addEventListener('DOMContentLoaded', function() {
    console.log('Speaking exam page loaded');
    
    // Get exam ID from URL
    const params = new URLSearchParams(window.location.search);
    const examId = params.get('exam_id');
    
    if (!examId) {
        console.error('No exam_id provided');
        // alert('خطا: شناسه آزمون مشخص نشده است');
        return;
    }
    
    initializeSpeakingExam(examId);
    attachEventListeners();
});

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

// ==================== INITIALIZE EXAM ====================
async function initializeSpeakingExam(examId) {
    console.log('Initializing speaking exam:', examId);
    
    // Load from API
    let exam = await fetchExamFromAPI(examId);
    
    if (!exam) {
        console.error('Failed to load exam from API:', examId);
        alert('خطا: آزمون مورد نظر یافت نشد');
        return;
    }
    
    speakingExamState.currentExamId = examId;
    speakingExamState.currentExam = exam;
    speakingExamState.totalQuestions = exam.totalQuestions || exam.questions.length;
    speakingExamState.currentQuestionIndex = 0;
    speakingExamState.timeRemaining = exam.totalTime;
    
    console.log('Speaking exam initialized:', exam);
    
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
    
    // Update attempts for this question
    const questionId = question.id;
    const questionRecordings = speakingExamState.recordings[questionId] || [];
    const attempts = document.getElementById('attempts');
    if (attempts) {
        attempts.textContent = `${questionRecordings.length}/${speakingExamState.maxAttempts}`;
    }
    
    // Load playback items for this question
    loadPlaybackItems(questionId);
    
    // Reset recording state for new question
    resetRecordingState();
}

// ==================== LOAD PLAYBACK ITEMS ====================
function loadPlaybackItems(questionId) {
    const playbackList = document.getElementById('playbackList');
    if (!playbackList) return;
    
    // Clear existing playback items
    playbackList.innerHTML = '';
    
    // Get recordings for this question
    const questionRecordings = speakingExamState.recordings[questionId];
    if (!questionRecordings || questionRecordings.length === 0) {
        return; // No recordings yet
    }
    
    // Add each recording
    questionRecordings.forEach((recording, index) => {
        const isSelected = !speakingExamState.selectedRecordings || 
                          speakingExamState.selectedRecordings[questionId] === index;
        const playbackHTML = `
            <div class="playback-item" data-question-id="${questionId}" data-recording-index="${index}">
                <div class="playback-item-inner">
                    <!-- Selection Radio Button -->
                    <input type="radio" 
                           name="recording-${questionId}" 
                           value="${index}" 
                           ${isSelected ? 'checked' : ''}
                           onchange="selectRecording('${questionId}', ${index})"
                           style="width: 20px; height: 20px; cursor: pointer; margin-right: 12px;">
                    
                    <!-- Playback Actions -->
                    <div class="playback-actions">
                        <div class="playback-action-btn download-btn" onclick="downloadRecording('${questionId}', ${index})">
                            <svg viewBox="0 0 40 40" fill="none">
                                <rect width="40" height="40" rx="8" fill="white"/>
                                <path d="M20 14V26M20 26L16 22M20 26L24 22" stroke="#0B0754" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                            </svg>
                        </div>
                        <div class="playback-action-btn play-btn" onclick="playRecording('${questionId}', ${index})">
                            <svg viewBox="0 0 40 40" fill="none">
                                <rect x="1" y="1" width="38" height="38" rx="7" fill="white" stroke="#4CAF50" stroke-width="2"/>
                                <path d="M17 14L26 20L17 26V14Z" fill="#4CAF50"/>
                            </svg>
                        </div>
                    </div>

                    <!-- Playback Left -->
                    <div class="playback-left">
                        <div class="playback-info">
                            <p class="playback-name">ضبط ${index + 1} - تلاش ${index + 1}</p>
                            <p class="playback-duration">مدت زمان: ${formatTime(recording.duration)}</p>
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
    });
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
        
        // Add animation classes
        const micButton = document.querySelector('.mic-button');
        const bars = document.querySelectorAll('.sound-wave-icon .bar');
        const pauseBtn = document.getElementById('pauseBtn');
        
        if (micButton) micButton.classList.add('recording');
        bars.forEach(bar => bar.classList.add('recording'));
        if (pauseBtn) pauseBtn.classList.remove('paused');
        
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
    
    const pauseBtn = document.getElementById('pauseBtn');
    const micTitle = document.getElementById('micTitle');
    const micButton = document.querySelector('.mic-button');
    const bars = document.querySelectorAll('.sound-wave-icon .bar');
    
    if (speakingExamState.isPaused) {
        // Paused state
        speakingExamState.mediaRecorder.pause();
        if (micTitle) micTitle.textContent = 'ضبط متوقف شد';
        if (pauseBtn) pauseBtn.classList.add('paused');
        
        // Stop animation
        if (micButton) micButton.classList.remove('recording');
        bars.forEach(bar => bar.classList.remove('recording'));
        
        console.log('Recording paused');
    } else {
        // Recording state
        speakingExamState.mediaRecorder.resume();
        if (micTitle) micTitle.textContent = 'در حال ضبط...';
        if (pauseBtn) pauseBtn.classList.remove('paused');
        
        // Resume animation
        if (micButton) micButton.classList.add('recording');
        bars.forEach(bar => bar.classList.add('recording'));
        
        console.log('Recording resumed');
    }
}

function stopRecording() {
    if (!speakingExamState.isRecording || !speakingExamState.mediaRecorder) return;
    
    // Remove animation classes
    const micButton = document.querySelector('.mic-button');
    const bars = document.querySelectorAll('.sound-wave-icon .bar');
    if (micButton) micButton.classList.remove('recording');
    bars.forEach(bar => bar.classList.remove('recording'));
    
    speakingExamState.mediaRecorder.stop();
    speakingExamState.mediaRecorder.onstop = function() {
        const audioBlob = new Blob(speakingExamState.audioChunks, { type: 'audio/wav' });
        const questionId = speakingExamState.currentExam.questions[speakingExamState.currentQuestionIndex].id;
        
        // Initialize recordings array for this question if it doesn't exist
        if (!speakingExamState.recordings[questionId]) {
            speakingExamState.recordings[questionId] = [];
        }
        
        // Check if max attempts reached BEFORE adding
        if (speakingExamState.recordings[questionId].length >= speakingExamState.maxAttempts) {
            alert(`حداکثر تعداد تلاش‌ها (${speakingExamState.maxAttempts}) برای این سوال به پایان رسیده است.`);
            // Stop all tracks
            speakingExamState.mediaRecorder.stream.getTracks().forEach(track => track.stop());
            resetRecordingState();
            return;
        }
        
        // Store recording with metadata
        speakingExamState.recordings[questionId].push({
            blob: audioBlob,
            duration: speakingExamState.recordingTime,
            attempt: speakingExamState.recordings[questionId].length + 1
        });
        
        // Stop all tracks
        speakingExamState.mediaRecorder.stream.getTracks().forEach(track => track.stop());
        
        // Update attempts counter - NOW show the count of recordings we have
        const attempts = document.getElementById('attempts');
        if (attempts) {
            const currentAttempts = speakingExamState.recordings[questionId].length;
            attempts.textContent = `${currentAttempts}/${speakingExamState.maxAttempts}`;
        }
        
        // Update playback items display
        loadPlaybackItems(questionId);
        
        // Reset recording state
        resetRecordingState();
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
    
    // Reset pause button state
    const pauseBtn = document.getElementById('pauseBtn');
    if (pauseBtn) pauseBtn.classList.remove('paused');
    
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

function playRecording(questionId, recordingIndex) {
    const questionRecordings = speakingExamState.recordings[questionId];
    if (!questionRecordings || !questionRecordings[recordingIndex] || !questionRecordings[recordingIndex].blob) {
        console.error('Recording not found');
        return;
    }
    
    const audioBlob = questionRecordings[recordingIndex].blob;
    const audioUrl = URL.createObjectURL(audioBlob);
    const audio = new Audio(audioUrl);
    audio.play();
}

function downloadRecording(questionId, recordingIndex) {
    const questionRecordings = speakingExamState.recordings[questionId];
    if (!questionRecordings || !questionRecordings[recordingIndex] || !questionRecordings[recordingIndex].blob) {
        console.error('Recording not found');
        return;
    }
    
    const audioBlob = questionRecordings[recordingIndex].blob;
    const audioUrl = URL.createObjectURL(audioBlob);
    const a = document.createElement('a');
    a.href = audioUrl;
    a.download = `recording-${questionId}-${recordingIndex + 1}.wav`;
    a.click();
    URL.revokeObjectURL(audioUrl);
}

function selectRecording(questionId, recordingIndex) {
    // Store which recording is selected for this question
    speakingExamState.selectedRecordings[questionId] = recordingIndex;
    console.log(`Selected recording ${recordingIndex + 1} for question ${questionId}`);
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
