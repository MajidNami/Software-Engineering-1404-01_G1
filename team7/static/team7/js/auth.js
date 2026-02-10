/**
 * Language Academy - Authentication & User Management
 * Handles user authentication state and UI updates
 */

// ==================== API Configuration ====================
const API_BASE = window.location.origin;
const CORE_AUTH_API = `${API_BASE}/api/auth`;

// ==================== Authentication State Management ====================
let currentUser = null;
let authInitialized = false;

/**
 * Check if user is authenticated by calling the core /api/auth/me endpoint
 */
async function checkAuthStatus() {
    try {
        const response = await fetch(`${CORE_AUTH_API}/me/`, {
            method: 'GET',
            credentials: 'include',  // Include cookies
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (response.ok) {
            const data = await response.json();
            // The API returns { ok: true, user: { id, email, first_name, last_name, age } }
            currentUser = data.user;
            console.log('User authenticated:', currentUser);
            
            // Validate that we have the required fields
            if (!currentUser || !currentUser.id || !currentUser.email) {
                console.error('❌ User data is incomplete:', currentUser);
                console.error('API Response:', data);
                currentUser = null;
                return false;
            }
            
            return true;
        }
        
        console.log('Authentication check failed:', response.status);
        currentUser = null;
        return false;
    } catch (error) {
        console.error('Auth check failed:', error);
        currentUser = null;
        return false;
    }
}

/**
 * Update UI based on authentication status
 */
async function updateAuthUI() {
    const isAuthenticated = await checkAuthStatus();
    
    const loginBtn = document.querySelector('.btn-login');
    const signupBtn = document.querySelector('.btn-signup');
    const headerButtons = document.querySelector('.header-buttons');
    const userName = document.querySelector('.user-name');
    const userProfile = document.querySelector('.user-profile');

    if (isAuthenticated && currentUser) {
        // User is logged in - show user info
        if (loginBtn) loginBtn.style.display = 'none';
        if (signupBtn) signupBtn.style.display = 'none';
        
        // Create user menu if it doesn't exist
        if (headerButtons && !document.querySelector('.user-menu')) {
            const userMenu = document.createElement('div');
            userMenu.className = 'user-menu';
            // Safely get user display name with fallback
            const userDisplayName = currentUser.first_name || currentUser.email || 'کاربر';
            userMenu.innerHTML = `
                <div class="user-info">
                    <span class="user-greeting">سلام، ${userDisplayName}</span>
                    <button class="btn-logout" title="خروج">
                        <svg width="16" height="16" viewBox="0 0 16 16" fill="none" style="margin-left: 4px; vertical-align: middle;">
                            <path d="M6 14H3.33333C2.97971 14 2.64057 13.8595 2.39052 13.6095C2.14048 13.3594 2 13.0203 2 12.6667V3.33333C2 2.97971 2.14048 2.64057 2.39052 2.39052C2.64057 2.14048 2.97971 2 3.33333 2H6" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                            <path d="M10.6667 11.3333L14 8L10.6667 4.66667" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                            <path d="M14 8H6" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                        خروج
                    </button>
                </div>
            `;
            headerButtons.appendChild(userMenu);
            
            // Add CSS styles for the logout button
            const style = document.createElement('style');
            style.textContent = `
                .btn-logout {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 8px;
                    cursor: pointer;
                    font-size: 14px;
                    font-weight: 500;
                    transition: all 0.3s ease;
                    display: inline-flex;
                    align-items: center;
                    box-shadow: 0 2px 8px rgba(102, 126, 234, 0.25);
                }
                .btn-logout:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
                    background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
                }
                .btn-logout:active {
                    transform: translateY(0);
                    box-shadow: 0 2px 6px rgba(102, 126, 234, 0.3);
                }
                .user-greeting {
                    margin-left: 12px;
                    font-weight: 500;
                    color: #1f2937;
                }
                .user-info {
                    display: flex;
                    align-items: center;
                    gap: 8px;
                }
            `;
            document.head.appendChild(style);
            headerButtons.appendChild(userMenu);
            
            // Add logout handler
            const logoutBtn = userMenu.querySelector('.btn-logout');
            if (logoutBtn) {
                logoutBtn.addEventListener('click', handleLogout);
            }
        }

        // Update dashboard user name if it exists
        if (userName) {
            const fullName = `${currentUser.first_name || ''} ${currentUser.last_name || ''}`.trim();
            userName.textContent = fullName || currentUser.email || 'کاربر';
        }
    } else {
        // User is not logged in - show login/signup buttons
        if (loginBtn) {
            loginBtn.style.display = 'block';
            loginBtn.addEventListener('click', () => {
                window.location.href = '/auth/';
            });
        }
        
        if (signupBtn) {
            signupBtn.style.display = 'block';
            signupBtn.addEventListener('click', () => {
                window.location.href = '/auth/signup/';
            });
        }

        // Remove user menu if it exists
        const existingUserMenu = document.querySelector('.user-menu');
        if (existingUserMenu) {
            existingUserMenu.remove();
        }
    }
}

/**
 * Handle user logout
 */
async function handleLogout() {
    try {
        const response = await fetch(`${CORE_AUTH_API}/logout/`, {
            method: 'POST',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (response.ok) {
            currentUser = null;
            window.location.href = '/';  // Redirect to home
        }
    } catch (error) {
        console.error('Logout failed:', error);
        alert('خروج ناموفق بود. لطفاً دوباره تلاش کنید.');
    }
}

/**
 * Check if user is authenticated before performing an action
 * Redirects to login if not authenticated
 */
function requireAuth(callback) {
    return async function(...args) {
        const isAuthenticated = await checkAuthStatus();
        
        if (!isAuthenticated) {
            // Store the intended destination
            sessionStorage.setItem('redirectAfterLogin', window.location.pathname);
            window.location.href = '/auth/';
            return;
        }
        
        return callback.apply(this, args);
    };
}

/**
 * Navigate to a protected page (requires authentication)
 */
async function navigateToProtectedPage(url) {
    const isAuthenticated = await checkAuthStatus();
    
    if (!isAuthenticated) {
        sessionStorage.setItem('redirectAfterLogin', url);
        window.location.href = '/auth/';
        return;
    }
    
    window.location.href = url;
}

// ==================== Initialize Authentication ====================
async function initializeAuth() {
    if (authInitialized) return;
    authInitialized = true;
    
    await updateAuthUI();
    
    // Check for redirect after login
    const redirectUrl = sessionStorage.getItem('redirectAfterLogin');
    if (redirectUrl) {
        sessionStorage.removeItem('redirectAfterLogin');
        window.location.href = redirectUrl;
    }
}

// ==================== Export for use in other scripts ====================
// Create authManager immediately so it's available to other scripts
window.authManager = {
    checkAuthStatus,
    updateAuthUI,
    requireAuth,
    navigateToProtectedPage,
    getCurrentUser: () => currentUser,
    isInitialized: () => authInitialized,
    initialize: initializeAuth,
    // Force a fresh check of user authentication status
    refreshUser: async () => {
        console.log('Forcing user data refresh...');
        return await checkAuthStatus();
    }
};

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeAuth);
} else {
    initializeAuth();
}
