/**
 * Language Academy - Home Page JavaScript
 * Page-specific functionality and interactions
 */

// ==================== Initialize Home Page ====================
/**
 * Initialize all home page specific functionality
 */
async function initializeHomePage() {
    // Wait for auth to be ready
    if (window.authManager && window.authManager.isInitialized && !window.authManager.isInitialized()) {
        await window.authManager.initialize();
    }
    
    initializeAnimations(['.feature-card', '.step-card', '.ai-content', '.ai-image-wrapper']);
    initializeHomeButtons();
}

// ==================== Button Handlers ====================
/**
 * Initialize all button click handlers on home page
 */
function initializeHomeButtons() {
    // Handle all protected links (requiring authentication)
    document.querySelectorAll('.protected-link').forEach(link => {
        link.addEventListener('click', async (e) => {
            e.preventDefault();
            const redirectUrl = link.getAttribute('data-redirect');
            
            if (window.authManager) {
                const isAuthenticated = await window.authManager.checkAuthStatus();
                if (isAuthenticated) {
                    window.location.href = redirectUrl;
                } else {
                    sessionStorage.setItem('redirectAfterLogin', redirectUrl);
                    window.location.href = '/auth/';
                }
            } else {
                sessionStorage.setItem('redirectAfterLogin', redirectUrl);
                window.location.href = '/auth/';
            }
        });
    });

    // Primary CTA - Start Free Test (in hero section)
    const primaryCTA = document.querySelector('.btn-primary-cta:not(.protected-link)');
    if (primaryCTA) {
        primaryCTA.addEventListener('click', async (e) => {
            e.preventDefault();
            if (window.authManager) {
                await window.authManager.navigateToProtectedPage('/team7/exams/');
            } else {
                sessionStorage.setItem('redirectAfterLogin', '/team7/exams/');
                window.location.href = '/auth/';
            }
        });
    }

    // Secondary CTA - View Sample Test
    const secondaryCTA = document.querySelector('.btn-secondary-cta:not(.protected-link)');
    if (secondaryCTA) {
        secondaryCTA.addEventListener('click', (e) => {
            e.preventDefault();
            // Scroll to tests section or show demo
            const testsSection = document.getElementById('tests');
            if (testsSection) {
                testsSection.scrollIntoView({ behavior: 'smooth' });
            } else {
                // If no tests section, show demo
                showTestDemo();
            }
        });
    }

    // AI Section CTA button
    const aiCTA = document.querySelector('.btn-ai-cta:not(.protected-link)');
    if (aiCTA) {
        aiCTA.addEventListener('click', async (e) => {
            e.preventDefault();
            if (window.authManager) {
                await window.authManager.navigateToProtectedPage('/team7/exams/');
            } else {
                sessionStorage.setItem('redirectAfterLogin', '/team7/exams/');
                window.location.href = '/auth/';
            }
        });
    }

    // Main CTA section button at bottom
    const mainCTA = document.querySelector('.btn-cta:not(.protected-link)');
    if (mainCTA) {
        mainCTA.addEventListener('click', async (e) => {
            e.preventDefault();
            if (window.authManager) {
                await window.authManager.navigateToProtectedPage('/team7/exams/');
            } else {
                sessionStorage.setItem('redirectAfterLogin', '/team7/exams/');
                window.location.href = '/auth/';
            }
        });
    }

    // Test Cards - Navigate to specific test types
    document.querySelectorAll('.test-card').forEach(card => {
        card.addEventListener('click', async (e) => {
            e.preventDefault();
            const testType = card.dataset.testType || 'writing';
            if (window.authManager) {
                await window.authManager.navigateToProtectedPage(`/team7/exams/?test=${testType}`);
            } else {
                sessionStorage.setItem('redirectAfterLogin', `/team7/exams/?test=${testType}`);
                window.location.href = '/auth/';
            }
        });
    });

    // Quick action buttons
    document.querySelectorAll('.quick-action-btn').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            e.preventDefault();
            const action = btn.dataset.action;
            if (action === 'writing') {
                if (window.authManager) {
                    await window.authManager.navigateToProtectedPage('/team7/exams/?test=writing');
                } else {
                    sessionStorage.setItem('redirectAfterLogin', '/team7/exams/?test=writing');
                    window.location.href = '/auth/';
                }
            } else if (action === 'speaking') {
                if (window.authManager) {
                    await window.authManager.navigateToProtectedPage('/team7/exams/?test=speaking');
                } else {
                    sessionStorage.setItem('redirectAfterLogin', '/team7/exams/?test=speaking');
                    window.location.href = '/auth/';
                }
            }
        });
    });
}

/**
 * Show a demo of how tests work
 */
function showTestDemo() {
    // Create modal overlay
    const modal = document.createElement('div');
    modal.className = 'demo-modal';
    modal.innerHTML = `
        <div class="demo-modal-content">
            <button class="demo-modal-close">&times;</button>
            <h2>نمونه آزمون TOEFL</h2>
            <p>در این پلتفرم، شما می‌توانید:</p>
            <ul style="text-align: right; margin: 20px; line-height: 2;">
                <li>✓ آزمون‌های نوشتاری (Writing) را انجام دهید</li>
                <li>✓ آزمون‌های گفتاری (Speaking) را ضبط کنید</li>
                <li>✓ بازخورد آنی از هوش مصنوعی دریافت کنید</li>
                <li>✓ پیشرفت خود را در داشبورد مشاهده کنید</li>
            </ul>
            <button class="btn-primary-cta" onclick="window.location.href='/auth/'">ثبت نام و شروع رایگان</button>
        </div>
    `;
    
    // Add styles
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0,0,0,0.7);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 10000;
    `;
    
    const content = modal.querySelector('.demo-modal-content');
    content.style.cssText = `
        background: white;
        padding: 40px;
        border-radius: 12px;
        max-width: 500px;
        position: relative;
        text-align: center;
    `;
    
    const closeBtn = modal.querySelector('.demo-modal-close');
    closeBtn.style.cssText = `
        position: absolute;
        top: 10px;
        right: 10px;
        background: none;
        border: none;
        font-size: 30px;
        cursor: pointer;
        color: #666;
    `;
    
    closeBtn.addEventListener('click', () => modal.remove());
    modal.addEventListener('click', (e) => {
        if (e.target === modal) modal.remove();
    });
    
    document.body.appendChild(modal);
}

// Run initialization when DOM is ready
document.addEventListener('DOMContentLoaded', initializeHomePage);
