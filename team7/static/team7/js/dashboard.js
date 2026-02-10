/**
 * Language Academy - Dashboard Page JavaScript
 * Dashboard-specific functionality and interactions
 */

// ==================== State Management ====================
let userHistory = [];
let availableQuestions = [];

// ==================== Initialize Dashboard ====================
/**
 * Initialize dashboard on page load
 */
async function initializeDashboard() {
    // Wait for auth to be ready
    if (window.authManager && window.authManager.isInitialized && !window.authManager.isInitialized()) {
        await window.authManager.initialize();
    }
    
    // Check authentication
    if (!window.authManager) {
        console.error('AuthManager not available');
        window.location.href = '/auth/';
        return;
    }
    
    const isAuthenticated = await window.authManager.checkAuthStatus();
    if (!isAuthenticated) {
        sessionStorage.setItem('redirectAfterLogin', window.location.pathname + window.location.search);
        window.location.href = '/auth/';
        return;
    }

    // Update user info in header
    updateUserInfo();
    
    // Initialize UI components
    initializeSidebarMenu();
    initializeStartExamButtons();
    initializeCardHoverEffects();
    initializeDashboardAnimations();
    initializeExamCardHandlers();
    initializeStatCardHandlers();
    
    // Load user data
    await loadUserHistory();
    
    // Check URL params for specific test to launch
    const urlParams = new URLSearchParams(window.location.search);
    const testType = urlParams.get('test');
    if (testType === 'writing') {
        launchWritingTest();
    } else if (testType === 'speaking') {
        launchSpeakingTest();
    }
}

/**
 * Update user information in the dashboard header
 */
function updateUserInfo() {
    const currentUser = window.authManager.getCurrentUser();
    if (currentUser) {
        const userNameElement = document.querySelector('.user-name');
        if (userNameElement) {
            const fullName = `${currentUser.first_name || ''} ${currentUser.last_name || ''}`.trim();
            userNameElement.textContent = fullName || currentUser.email || 'کاربر';
        }
    }
}

// ==================== Sidebar Menu Handlers ====================
/**
 * Initialize sidebar menu item click handlers
 */
function initializeSidebarMenu() {
    const menuItems = document.querySelectorAll('.menu-item');
    
    menuItems.forEach((item, index) => {
        item.addEventListener('click', function() {
            // Remove active class from all items
            menuItems.forEach(i => i.classList.remove('active'));
            // Add active class to clicked item
            this.classList.add('active');
            
            const menuText = this.querySelector('span')?.textContent || '';
            
            // Handle navigation based on menu item
            switch(index) {
                case 0: // Dashboard
                    // Already on dashboard
                    break;
                case 1: // Writing Test
                    launchWritingTest();
                    break;
                case 2: // Speaking Test
                    launchSpeakingTest();
                    break;
                case 3: // Reports
                    showReports();
                    break;
                case 4: // Settings
                    showSettings();
                    break;
            }
        });
    });
}

// ==================== Start Exam Button Handlers ====================
/**
 * Initialize start exam button handlers
 */
function initializeStartExamButtons() {
    const startButtons = document.querySelectorAll('.btn-start');
    
    startButtons.forEach(button => {
        button.addEventListener('click', function() {
            const card = this.closest('.access-card');
            const examTitle = card?.querySelector('.access-title')?.textContent || '';
            
            // Determine test type from title
            if (examTitle.includes('نوشتاری') || examTitle.includes('Writing')) {
                launchWritingTest();
            } else if (examTitle.includes('گفتاری') || examTitle.includes('Speaking')) {
                launchSpeakingTest();
            }
            
            // Add visual feedback
            this.style.transform = 'scale(0.95)';
            setTimeout(() => {
                this.style.transform = '';
            }, 150);
        });
    });
}

// ==================== Card Hover Effects ====================
/**
 * Initialize hover effects for dashboard cards
 */
function initializeCardHoverEffects() {
    const cards = document.querySelectorAll('.status-card, .chart-card, .exam-card, .stat-card');
    
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-4px)';
            this.style.transition = 'transform 0.3s ease';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
}

// ==================== Intersection Observer ====================
/**
 * Initialize intersection observer for dashboard sections
 */
function initializeDashboardAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observerCallback = (entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    };

    const observer = new IntersectionObserver(observerCallback, observerOptions);

    // Observe sections for animation
    const sections = document.querySelectorAll(
        '.status-section, .charts-section, .exams-section, .access-section, .statistics-section'
    );
    
    sections.forEach(section => {
        section.style.opacity = '0';
        section.style.transform = 'translateY(20px)';
        section.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(section);
    });
}

// ==================== Exam Card Click Handlers ====================
/**
 * Initialize exam card click handlers
 */
function initializeExamCardHandlers() {
    const examCards = document.querySelectorAll('.exam-card');
    
    examCards.forEach(card => {
        card.addEventListener('click', function() {
            const examTitle = this.querySelector('.exam-title')?.textContent;
            const examScore = this.querySelector('.score-value')?.textContent;
            console.log('Viewing exam:', examTitle, 'Score:', examScore);
            
            // Add visual effect
            this.style.outline = '2px solid #587ce6';
            setTimeout(() => {
                this.style.outline = '';
            }, 500);
        });
    });
}

// ==================== Stat Card Click Handlers ====================
/**
 * Initialize stat card click handlers
 */
function initializeStatCardHandlers() {
    const statCards = document.querySelectorAll('.stat-card');
    
    statCards.forEach(card => {
        card.addEventListener('click', function() {
            const statTitle = this.querySelector('.stat-title')?.textContent;
            const statValue = this.querySelector('.stat-value')?.textContent;
            console.log('Viewing stat:', statTitle, 'Value:', statValue);
        });
    });
}

// ==================== Initialize Dashboard ====================
/**
 * Initialize all dashboard page specific functionality
 */
async function initializeDashboardPage() {
    // First initialize auth and check authentication
    await initializeDashboard();
}

// Run initialization when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeDashboardPage);
} else {
    initializeDashboardPage();
}

// ==================== Data Loading ====================
async function loadUserHistory() {
    try {
        // Force a fresh auth check to ensure we have latest user data
        const isAuthenticated = await window.authManager.checkAuthStatus();
        if (!isAuthenticated) {
            console.error('User not authenticated when loading history');
            return;
        }
        
        const currentUser = window.authManager.getCurrentUser();
        if (!currentUser || !currentUser.id) {
            console.error('User ID not available:', currentUser);
            return;
        }

        const response = await fetch(`/team7/api/v1/history/${currentUser.id}/`, {
            credentials: 'include'
        });

        if (response.ok) {
            const data = await response.json();
            userHistory = data.evaluations || [];
        }
    } catch (error) {
        console.error('Failed to load user history:', error);
    }
}

// ==================== Test Launching ====================
function launchWritingTest() {
    showTestModal('writing');
}

function launchSpeakingTest() {
    showTestModal('speaking');
}

async function showTestModal(testType) {
    const placeholderQuestion = {
        question_id: 'placeholder',
        prompt_text: testType === 'writing' 
            ? 'Do you agree or disagree with the following statement? Technology has made the world a better place to live. Use specific reasons and examples to support your answer.'
            : 'Describe your favorite place to study.'
    };

    if (testType === 'writing') {
        showWritingTestModal(placeholderQuestion);
    } else {
        showSpeakingTestModal(placeholderQuestion);
    }
}

function showWritingTestModal(question) {
    const modal = createTestModal('نوشتاری', `
        <div class="test-content">
            <div class="question-section" style="background: #f9fafb; padding: 20px; border-radius: 8px; margin-bottom: 24px;">
                <h3>سوال:</h3>
                <p>${question.prompt_text}</p>
            </div>
            <div class="answer-section">
                <label for="essay-text">پاسخ شما:</label>
                <textarea id="essay-text" rows="15" maxlength="5000" placeholder="متن مقاله خود را اینجا بنویسید... (حداقل 50 کلمه، حداکثر 1000 کلمه یا 5000 کاراکتر)" style="width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 8px; font-family: inherit;"></textarea>
                <div class="counters" style="display: flex; justify-content: space-between; margin-top: 8px; padding: 0 4px;">
                    <div class="word-count" style="text-align: right; color: #666;">
                        تعداد کلمات: <span id="word-count" style="font-weight: 600; color: #6366f1;">0</span> / 1000
                    </div>
                    <div class="char-count" style="text-align: left; color: #666;">
                        تعداد کاراکتر: <span id="char-count" style="font-weight: 600; color: #6366f1;">0</span> / 5000
                    </div>
                </div>
                <div id="validation-message" style="margin-top: 8px; font-size: 13px; min-height: 20px;"></div>
            </div>
            <div class="test-actions" style="display: flex; gap: 12px; justify-content: flex-end; margin-top: 20px;">
                <button class="btn-cancel" onclick="this.closest('.test-modal').remove()" style="background: #e5e7eb; color: #374151; padding: 10px 24px; border: none; border-radius: 8px; cursor: pointer;">انصراف</button>
                <button class="btn-submit-test" style="background: #6366f1; color: white; padding: 10px 24px; border: none; border-radius: 8px; cursor: pointer; font-weight: 500;">ارسال</button>
            </div>
        </div>
    `, question);

    const textarea = modal.querySelector('#essay-text');
    const wordCountSpan = modal.querySelector('#word-count');
    const charCountSpan = modal.querySelector('#char-count');
    const validationMessage = modal.querySelector('#validation-message');
    const submitBtn = modal.querySelector('.btn-submit-test');

    // Real-time validation
    textarea.addEventListener('input', () => {
        const text = textarea.value;
        const charCount = text.length;
        const words = text.trim().split(/\s+/).filter(w => w.length > 0);
        const wordCount = words.length;
        
        wordCountSpan.textContent = wordCount;
        charCountSpan.textContent = charCount;
        
        // Color coding
        if (wordCount < 50) {
            wordCountSpan.style.color = '#ef4444';
            validationMessage.innerHTML = '<span style="color: #ef4444;">⚠ حداقل 50 کلمه مورد نیاز است</span>';
            submitBtn.disabled = true;
            submitBtn.style.opacity = '0.5';
            submitBtn.style.cursor = 'not-allowed';
        } else if (wordCount > 1000) {
            wordCountSpan.style.color = '#ef4444';
            validationMessage.innerHTML = '<span style="color: #ef4444;">⚠ حداکثر 1000 کلمه مجاز است</span>';
            submitBtn.disabled = true;
            submitBtn.style.opacity = '0.5';
            submitBtn.style.cursor = 'not-allowed';
        } else if (charCount > 5000) {
            charCountSpan.style.color = '#ef4444';
            validationMessage.innerHTML = '<span style="color: #ef4444;">⚠ حداکثر 5000 کاراکتر مجاز است</span>';
            submitBtn.disabled = true;
            submitBtn.style.opacity = '0.5';
            submitBtn.style.cursor = 'not-allowed';
        } else {
            wordCountSpan.style.color = '#10b981';
            charCountSpan.style.color = '#10b981';
            validationMessage.innerHTML = '<span style="color: #10b981;">✓ متن شما آماده ارسال است</span>';
            submitBtn.disabled = false;
            submitBtn.style.opacity = '1';
            submitBtn.style.cursor = 'pointer';
        }
    });

    submitBtn.addEventListener('click', () => submitWritingTest(question, textarea.value, modal));

    document.body.appendChild(modal);
}

function showSpeakingTestModal(question) {
    const modal = createTestModal('گفتاری', `
        <div class="test-content">
            <div class="question-section"style="background: #f9fafb; padding: 20px; border-radius: 8px; margin-bottom: 24px;">
                <h3>سوال:</h3>
                <p>${question.prompt_text}</p>
            </div>
            <div class="recording-section" style="text-align: center; padding: 40px 20px;">
                <div class="recording-indicator" style="width: 100px; height: 100px; border-radius: 50%; background: #f0f0f0; margin: 0 auto 20px; display: flex; align-items: center; justify-content: center; font-size: 40px;">🎤</div>
                <p class="recording-status">آماده ضبط</p>
            </div>
            <div class="test-actions" style="display: flex; gap: 12px; justify-content: center; margin-top: 20px;">
                <button class="btn-cancel" onclick="this.closest('.test-modal').remove()">انصراف</button>
                <button class="btn-record" style="background: #ef4444; color: white; padding: 10px 24px; border: none; border-radius: 8px; cursor: pointer;">● شروع ضبط</button>
            </div>
        </div>
    `, question);

    const recordBtn = modal.querySelector('.btn-record');
    recordBtn.addEventListener('click', () => {
        alert('قابلیت ضبط صدا در اسپرینت 2 پیاده‌سازی خواهد شد.');
    });

    document.body.appendChild(modal);
}

function createTestModal(testTitle, content, question) {
    const modal = document.createElement('div');
    modal.className = 'test-modal';
    modal.innerHTML = `
        <div class="test-modal-overlay"></div>
        <div class="test-modal-content">
            <div class="test-modal-header">
                <h2>آزمون ${testTitle}</h2>
                <button class="test-modal-close">&times;</button>
            </div>
            <div class="test-modal-body">${content}</div>
        </div>
    `;

    modal.style.cssText = 'position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: 10000; display: flex; align-items: center; justify-content: center;';
    modal.querySelector('.test-modal-overlay').style.cssText = 'position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0, 0, 0, 0.7);';
    modal.querySelector('.test-modal-content').style.cssText = 'position: relative; background: white; border-radius: 12px; max-width: 800px; width: 90%; max-height: 90vh; overflow-y: auto; z-index: 1;';
    modal.querySelector('.test-modal-header').style.cssText = 'display: flex; justify-content: space-between; align-items: center; padding: 20px 24px; border-bottom: 1px solid #e5e7eb;';
    modal.querySelector('.test-modal-body').style.cssText = 'padding: 24px;';
    
    const closeBtn = modal.querySelector('.test-modal-close');
    closeBtn.style.cssText = 'background: none; border: none; font-size: 30px; cursor: pointer; color: #666;';
    closeBtn.addEventListener('click', () => modal.remove());
    modal.querySelector('.test-modal-overlay').addEventListener('click', () => modal.remove());

    return modal;
}

async function submitWritingTest(question, text, modal) {
    // Force a fresh auth check before submission
    const isAuthenticated = await window.authManager.checkAuthStatus();
    if (!isAuthenticated) {
        showErrorNotification('لطفاً ابتدا وارد شوید.');
        // Redirect to login
        sessionStorage.setItem('redirectAfterLogin', window.location.pathname + window.location.search);
        setTimeout(() => window.location.href = '/auth/', 1500);
        return;
    }
    
    const currentUser = window.authManager.getCurrentUser();
    if (!currentUser || !currentUser.id) {
        console.error('User data incomplete after auth check:', currentUser);
        showErrorNotification('خطا: اطلاعات کاربر ناقص است. لطفاً از کش مرورگر پاک کنید و دوباره وارد شوید.');
        // Try to logout and redirect
        setTimeout(async () => {
            await fetch(`${window.location.origin}/api/auth/logout/`, {
                method: 'POST',
                credentials: 'include'
            });
            window.location.href = '/auth/';
        }, 2000);
        return;
    }

    // Validate text
    const trimmedText = text.trim();
    if (!trimmedText) {
        showErrorNotification('لطفاً متن خود را وارد کنید.');
        return;
    }

    // Character limit check (5000 chars max to prevent LLM context overflow)
    const MAX_CHARS = 5000;
    if (trimmedText.length > MAX_CHARS) {
        showErrorNotification(`متن شما خیلی طولانی است! حداکثر ${MAX_CHARS} کاراکتر مجاز است. (کاراکترهای فعلی: ${trimmedText.length})`);
        return;
    }

    // Word count check
    const words = trimmedText.split(/\s+/).filter(w => w.length > 0);
    if (words.length < 50) {
        showErrorNotification(`متن شما باید حداقل 50 کلمه باشد. تعداد کلمات فعلی: ${words.length}`);
        return;
    }

    if (words.length > 1000) {
        showErrorNotification(`متن شما خیلی طولانی است! حداکثر 1000 کلمه مجاز است. (کلمات فعلی: ${words.length}`);
        return;
    }

    const submitBtn = modal.querySelector('.btn-submit-test');
    submitBtn.disabled = true;
    submitBtn.textContent = '⏳ در حال ارزیابی...';

    try {
        const payload = {
            user_id: currentUser.id,
            question_id: question.question_id,
            text: trimmedText
        };

        console.log('Submitting writing test:', payload);

        const response = await fetch('/team7/api/v1/evaluate/writing/', {
            method: 'POST',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (response.ok) {
            const result = await response.json();
            modal.remove();
            showResultModal(result);
            showSuccessNotification('ارزیابی با موفقیت انجام شد!');
            await loadUserHistory();
        } else {
            const error = await response.json();
            const errorMessage = error.message || error.error || 'خطای نامشخص در ارزیابی';
            console.error('API Error:', error);
            showErrorNotification(`خطا: ${errorMessage}`);
            submitBtn.disabled = false;
            submitBtn.textContent = 'ارسال';
        }
    } catch (error) {
        console.error('Submit error:', error);
        showErrorNotification('خطا در ارسال. لطفاً اتصال اینترنت خود را بررسی کنید و دوباره تلاش کنید.');
        submitBtn.disabled = false;
        submitBtn.textContent = 'ارسال';
    }
}

function showResultModal(result) {
    let detailedScoresHTML = '';
    if (result.detailed_scores && result.detailed_scores.length > 0) {
        detailedScoresHTML = '<div class="detailed-scores"><h3>امتیازات جزئی:</h3><ul style="list-style: none; padding: 0;">';
        result.detailed_scores.forEach(score => {
            detailedScoresHTML += `<li style="margin: 12px 0; padding: 16px; background: #f9fafb; border-radius: 8px;">
                <strong>${score.criterion}: ${score.score_value}/5.0</strong>
                ${score.comment ? `<br><small>${score.comment}</small>` : ''}
            </li>`;
        });
        detailedScoresHTML += '</ul></div>';
    }

    const modal = document.createElement('div');
    modal.innerHTML = `
        <div class="result-modal-overlay"></div>
        <div class="result-modal-content" style="background: white; padding: 40px; border-radius: 12px; max-width: 700px; position: relative; z-index: 1;">
            <h2 style="text-align: center; color: #6366f1;">نتیجه آزمون</h2>
            <div class="result-score" style="text-align: center; font-size: 60px; font-weight: bold; color: #10b981; margin: 30px 0;">${result.overall_score || result.score || 0}/5.0</div>
            <div class="result-feedback" style="background: #f0fdf4; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h3>بازخورد:</h3>
                <p>${result.ai_feedback || result.feedback || 'بدون بازخورد'}</p>
            </div>
            ${detailedScoresHTML}
            <div style="text-align: center; margin-top: 30px;">
                <button class="btn-close-result" style="background: #6366f1; color: white; padding: 12px 32px; border: none; border-radius: 8px; cursor: pointer;">بستن</button>
            </div>
        </div>
    `;

    modal.style.cssText = 'position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: 10001; display: flex; align-items: center; justify-content: center;';
    modal.querySelector('.result-modal-overlay').style.cssText = 'position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0, 0, 0, 0.7);';
    modal.querySelector('.btn-close-result').addEventListener('click', () => modal.remove());
    modal.querySelector('.result-modal-overlay').addEventListener('click', () => modal.remove());

    document.body.appendChild(modal);
}

function showReports() {
    alert('صفحه گزارشات در حال توسعه است (Sprint 3).');
}

function showSettings() {
    alert('صفحه تنظیمات در حال توسعه است.');
}

// ==================== Notification System ====================
/**
 * Show error notification
 */
function showErrorNotification(message) {
    showNotification(message, 'error');
}

/**
 * Show success notification
 */
function showSuccessNotification(message) {
    showNotification(message, 'success');
}

/**
 * Show notification with custom styling
 */
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    
    const colors = {
        error: { bg: '#fee', border: '#ef4444', text: '#991b1b', icon: '⚠️' },
        success: { bg: '#f0fdf4', border: '#10b981', text: '#065f46', icon: '✓' },
        info: { bg: '#eff6ff', border: '#3b82f6', text: '#1e40af', icon: 'ℹ️' }
    };
    
    const color = colors[type] || colors.info;
    
    notification.innerHTML = `
        <div style="display: flex; align-items: start; gap: 12px;">
            <span style="font-size: 24px;">${color.icon}</span>
            <div style="flex: 1;">
                <p style="margin: 0; line-height: 1.5;">${message}</p>
            </div>
            <button class="notification-close" style="background: none; border: none; font-size: 20px; cursor: pointer; color: #6b7280; padding: 0; line-height: 1;">&times;</button>
        </div>
    `;
    
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${color.bg};
        border: 2px solid ${color.border};
        border-radius: 12px;
        padding: 16px 20px;
        color: ${color.text};
        font-size: 14px;
        font-weight: 500;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
        z-index: 100000;
        min-width: 300px;
        max-width: 500px;
        animation: slideInRight 0.3s ease-out;
    `;
    
    // Add animation
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideInRight {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        @keyframes slideOutRight {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(100%);
                opacity: 0;
            }
        }
    `;
    if (!document.querySelector('#notification-styles')) {
        style.id = 'notification-styles';
        document.head.appendChild(style);
    }
    
    document.body.appendChild(notification);
    
    // Close button handler
    const closeBtn = notification.querySelector('.notification-close');
    closeBtn.addEventListener('click', () => {
        notification.style.animation = 'slideOutRight 0.3s ease-out';
        setTimeout(() => notification.remove(), 300);
    });
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.style.animation = 'slideOutRight 0.3s ease-out';
            setTimeout(() => notification.remove(), 300);
        }
    }, 5000);
}
