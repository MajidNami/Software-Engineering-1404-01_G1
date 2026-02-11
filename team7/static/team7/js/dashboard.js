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
                    break;
                case 2: // Speaking Test
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
 * Buttons are now inside links and handle navigation directly
 */
function initializeStartExamButtons() {
    const startButtons = document.querySelectorAll('.btn-start');
    
    startButtons.forEach(button => {
        button.addEventListener('click', function(e) {
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
