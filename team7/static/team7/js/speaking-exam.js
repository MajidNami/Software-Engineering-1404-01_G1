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
    speakingExamState.startTime = Date.now();
    
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
        
        // Determine the best supported audio codec
        const options = { mimeType: 'audio/webm' };
        if (MediaRecorder.isTypeSupported('audio/webm;codecs=opus')) {
            options.mimeType = 'audio/webm;codecs=opus';
        } else if (MediaRecorder.isTypeSupported('audio/webm')) {
            options.mimeType = 'audio/webm';
        } else if (MediaRecorder.isTypeSupported('audio/mp4')) {
            options.mimeType = 'audio/mp4';
        }
        
        console.log('Recording with mime type:', options.mimeType);
        speakingExamState.mediaRecorder = new MediaRecorder(stream, options);
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
        // Validate we have audio chunks
        if (speakingExamState.audioChunks.length === 0) {
            alert('خطا: هیچ صدایی ثبت نشد. لطفاً دوباره تلاش کنید.');
            resetRecordingState();
            return;
        }
        
        // Create blob with the actual mime type used by mediaRecorder
        const mimeType = speakingExamState.mediaRecorder.mimeType || 'audio/webm';
        const audioBlob = new Blob(speakingExamState.audioChunks, { type: mimeType });
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
    
    const recordingIndex = (speakingExamState.recordings[questionId] || []).length - 1;
    
    const playbackHTML = `
        <div class="playback-item" data-question-id="${questionId}" data-recording-index="${recordingIndex}" onclick="selectRecording('${questionId}', ${recordingIndex})">
            <div class="playback-item-inner">
                <!-- Playback Actions -->
                <div class="playback-actions">
                    <div class="playback-action-btn download-btn" onclick="event.stopPropagation(); downloadRecording('${questionId}', ${recordingIndex})">
                        <svg viewBox="0 0 40 40" fill="none">
                            <rect width="40" height="40" rx="8" fill="white"/>
                            <path d="M20 14V26M20 26L16 22M20 26L24 22" stroke="#0B0754" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                    </div>
                    <div class="playback-action-btn play-btn" onclick="event.stopPropagation(); playRecording('${questionId}', ${recordingIndex})">
                        <svg viewBox="0 0 40 40" fill="none">
                            <rect x="1" y="1" width="38" height="38" rx="7" fill="white" stroke="#4CAF50" stroke-width="2"/>
                            <path d="M17 14L26 20L17 26V14Z" fill="#4CAF50"/>
                        </svg>
                    </div>
                </div>

                <!-- Playback Left -->
                <div class="playback-left">
                    <div class="playback-info">
                        <p class="playback-name">ضبط ${recordingIndex + 1} - تلاش ${recordingIndex + 1}</p>
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
    
    // Update UI to show which recording is selected
    const playbackList = document.getElementById('playbackList');
    if (playbackList) {
        const items = playbackList.querySelectorAll('.playback-item');
        items.forEach((item, index) => {
            if (index === recordingIndex) {
                item.classList.add('selected');
            } else {
                item.classList.remove('selected');
            }
        });
    }
}

/**
 * Validate that all questions have selected recordings
 * @returns {Object} {isValid: boolean, message: string}
 */
function validateAllRecordingsSelected() {
    for (let i = 0; i < speakingExamState.totalQuestions; i++) {
        const question = speakingExamState.currentExam.questions[i];
        const questionId = question.id;
        
        // Check if recording is selected for this question
        if (!(questionId in speakingExamState.selectedRecordings)) {
            return {
                isValid: false,
                message: `سوال ${i + 1}: لطفاً یکی از ضبط‌های خود را انتخاب کنید`
            };
        }
        
        // Check if that recording exists
        const recordingIndex = speakingExamState.selectedRecordings[questionId];
        const recordings = speakingExamState.recordings[questionId];
        
        if (!recordings || !recordings[recordingIndex]) {
            return {
                isValid: false,
                message: `سوال ${i + 1}: ضبط انتخاب شده موجود نیست`
            };
        }
    }
    
    return {
        isValid: true,
        message: 'OK'
    };
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
async function submitExam() {
    // Validate that user has selected a recording for each question
    const validation = validateAllRecordingsSelected();
    if (!validation.isValid) {
        alert(validation.message);
        return;
    }

    // Show submit confirmation popup
    showSubmitExamPopup(async () => {
        // Stop all timers
        if (speakingExamState.timerInterval) clearInterval(speakingExamState.timerInterval);
        if (speakingExamState.recordingTimer) clearInterval(speakingExamState.recordingTimer);
        if (speakingExamState.isRecording) stopRecording();

        // Show loading indicator
        showLoadingPopup();

        try {
            const scores = [];
            const evaluations = [];

            // Get user ID from authManager
            const currentUser = window.authManager?.getCurrentUser();
            if (!currentUser || !currentUser.id) {
                throw new Error('Unable to get current user ID');
            }
            const userId = currentUser.id;

            // Evaluate each selected recording via API
            for (let i = 0; i < speakingExamState.totalQuestions; i++) {
                const question = speakingExamState.currentExam.questions[i];
                const recordingIndex = speakingExamState.selectedRecordings[question.id];

                if (recordingIndex === undefined) {
                    continue; // Should not happen if validation passed
                }

                const recording = speakingExamState.recordings[question.id][recordingIndex];
                if (!recording || !recording.blob) {
                    throw new Error(`No recording found for question ${i + 1}`);
                }

                try {
                    // Convert audio blob to WAV format for compatibility
                    let audioBlob = recording.blob;
                    if (!audioBlob.type.includes('wav')) {
                        console.log(`Converting ${audioBlob.type} to WAV format...`);
                        audioBlob = await convertToWAV(audioBlob);
                    }
                    
                    // Prepare FormData for multipart file upload
                    const formData = new FormData();
                    formData.append('user_id', userId);
                    formData.append('question_id', question.id);
                    formData.append('audio_file', audioBlob, `recording-q${i + 1}.wav`);

                    console.log(`Submitting question ${i + 1}: user_id=${userId}, question_id=${question.id}, blob_size=${recording.blob.size}, type=${recording.blob.type}`);

                    const response = await fetch('/team7/api/submit-speaking/', {
                        method: 'POST',
                        body: formData
                    });

                    if (!response.ok) {
                        const errorText = await response.text();
                        console.error(`API error response: ${errorText}`);
                        throw new Error(`API error: ${response.status} - ${errorText}`);
                    }

                    const result = await response.json();

                    if (result.status === 'success') {
                        scores.push(result.overall_score);
                        evaluations.push({
                            questionIndex: i + 1,
                            score: result.overall_score,
                            feedback: result.feedback,
                            transcript: result.transcript,
                            criteria: result.criteria
                        });
                        console.log(`Question ${i + 1} evaluated: ${result.overall_score}`);
                    } else {
                        throw new Error(result.error || 'Evaluation failed');
                    }
                } catch (error) {
                    console.error(`Error evaluating question ${i + 1}:`, error);
                    // On first error, close popup and show error message
                    if (i === 0) {
                        PopupManager.closePopup();
                        alert(error.message || 'خطا در ارزیابی آزمون. لطفاً دوباره تلاش کنید.');
                        return;
                    }
                    // Continue with other questions even if one fails
                    evaluations.push({
                        questionIndex: i + 1,
                        score: 0,
                        feedback: error.message || 'خطا در ارزیابی این سوال',
                        transcript: '',
                        criteria: []
                    });
                }
            }

            // Calculate average score
            const averageScore = scores.length > 0
                ? (scores.reduce((a, b) => a + b, 0) / scores.length).toFixed(1)
                : 0;

            // Prepare result data
            const timeUsed = Math.floor((Date.now() - speakingExamState.startTime) / 1000);
            const resultData = {
                score: parseFloat(averageScore),
                totalScore: 4.0,
                answeredQuestions: speakingExamState.totalQuestions,
                totalQuestions: speakingExamState.totalQuestions,
                timeSpent: timeUsed,
                type: speakingExamState.currentExam.title,
                message: 'از تلاش شما سپاسگزاریم. نتایج تفصیلی هر سوال را در زیر مشاهده کنید.',
                evaluations: evaluations // Add per-question details
            };

            console.log('Result data:', resultData);

            // Close loading popup and show result
            PopupManager.closePopup();
            setTimeout(() => {
                showExamResultPopupWithDetails(resultData);
            }, 300);

        } catch (error) {
            console.error('Error during exam submission:', error);
            PopupManager.closePopup();
            alert('خطا در ارسال آزمون. لطفاً دوباره تلاش کنید.');
        }
    });
}

// ==================== AUDIO CONVERSION ====================
/**
 * Convert audio blob to WAV format
 * Since we're recording in WebM/MP4, we need to convert to WAV for the API
 * @param {Blob} inputBlob - The audio blob to convert
 * @returns {Promise<Blob>} WAV format blob
 */
async function convertToWAV(inputBlob) {
    try {
        // For now, we'll just wrap the blob with a WAV header
        // This is a simple conversion that works for most browsers
        
        // Read the blob as ArrayBuffer
        const arrayBuffer = await inputBlob.arrayBuffer();
        
        // Create WAV header
        const sampleRate = 16000; // Standard sample rate for speech
        const channels = 1; // Mono for speech
        const bitsPerSample = 16;
        
        // WAV header structure
        const wavHeader = new ArrayBuffer(44);
        const view = new DataView(wavHeader);
        
        // RIFF identifier "RIFF"
        view.setUint8(0, 0x52);
        view.setUint8(1, 0x49);
        view.setUint8(2, 0x46);
        view.setUint8(3, 0x46);
        
        // File length - 8
        view.setUint32(4, arrayBuffer.byteLength + 36, true);
        
        // RIFF type "WAVE"
        view.setUint8(8, 0x57);
        view.setUint8(9, 0x41);
        view.setUint8(10, 0x56);
        view.setUint8(11, 0x45);
        
        // Format chunk identifier "fmt "
        view.setUint8(12, 0x66);
        view.setUint8(13, 0x6D);
        view.setUint8(14, 0x74);
        view.setUint8(15, 0x20);
        
        // Format chunk length
        view.setUint32(16, 16, true);
        
        // Audio format (1 = PCM)
        view.setUint16(20, 1, true);
        
        // Number of channels
        view.setUint16(22, channels, true);
        
        // Sample rate
        view.setUint32(24, sampleRate, true);
        
        // Byte rate
        view.setUint32(28, sampleRate * channels * bitsPerSample / 8, true);
        
        // Block align
        view.setUint16(32, channels * bitsPerSample / 8, true);
        
        // Bits per sample
        view.setUint16(34, bitsPerSample, true);
        
        // Data chunk identifier "data"
        view.setUint8(36, 0x64);
        view.setUint8(37, 0x61);
        view.setUint8(38, 0x74);
        view.setUint8(39, 0x61);
        
        // Data chunk length
        view.setUint32(40, arrayBuffer.byteLength, true);
        
        // Combine header and audio data
        const wavBlob = new Blob([wavHeader, arrayBuffer], { type: 'audio/wav' });
        console.log(`Converted audio to WAV: original=${inputBlob.size} bytes, converted=${wavBlob.size} bytes`);
        
        return wavBlob;
    } catch (error) {
        console.error('Error converting to WAV:', error);
        // If conversion fails, return original blob and let server handle it
        return inputBlob;
    }
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
    
    // Submit button
    const submitBtn = document.getElementById('submitBtn');
    if (submitBtn) submitBtn.addEventListener('click', submitExam);
}
