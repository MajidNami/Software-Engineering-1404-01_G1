/**
 * Authentication Debugging Utilities
 * Use these functions in browser console to diagnose auth issues
 */

// Export debug utilities to window
window.authDebug = {
    /**
     * Check current authentication status
     */
    async checkAuth() {
        console.log('🔍 Checking authentication status...\n');
        
        // Check if authManager exists
        if (!window.authManager) {
            console.error('❌ AuthManager not found!');
            return;
        }
        console.log('✅ AuthManager is available');
        
        // Check if initialized
        const initialized = window.authManager.isInitialized();
        console.log(`${initialized ? '✅' : '❌'} AuthManager initialized: ${initialized}`);
        
        // Get current user
        const currentUser = window.authManager.getCurrentUser();
        console.log('\n📋 Current User Object:');
        console.log(currentUser);
        
        // Validate user data
        if (!currentUser) {
            console.warn('⚠️ No user data - user not logged in');
            return;
        }
        
        console.log('\n🔎 Validating user data...');
        const requiredFields = ['id', 'email'];
        const missingFields = requiredFields.filter(field => !currentUser[field]);
        
        if (missingFields.length > 0) {
            console.error(`❌ Missing required fields: ${missingFields.join(', ')}`);
            console.error('This will cause submission errors!');
        } else {
            console.log('✅ All required fields present');
        }
        
        // Check optional fields
        const optionalFields = ['first_name', 'last_name', 'age'];
        optionalFields.forEach(field => {
            if (currentUser[field]) {
                console.log(`✅ ${field}: ${currentUser[field]}`);
            } else {
                console.log(`ℹ️ ${field}: (not set)`);
            }
        });
        
        return currentUser;
    },
    
    /**
     * Force refresh user data from backend
     */
    async refresh() {
        console.log('🔄 Forcing user data refresh from backend...\n');
        
        if (!window.authManager) {
            console.error('❌ AuthManager not found!');
            return;
        }
        
        const success = await window.authManager.refreshUser();
        
        if (success) {
            console.log('✅ User data refreshed successfully');
            const user = window.authManager.getCurrentUser();
            console.log('Updated user data:', user);
            return user;
        } else {
            console.error('❌ Failed to refresh user data');
            console.log('You may need to login again');
            return null;
        }
    },
    
    /**
     * Test API call to /api/auth/me/
     */
    async testAuthAPI() {
        console.log('🧪 Testing /api/auth/me/ endpoint...\n');
        
        try {
            const response = await fetch('/api/auth/me/', {
                method: 'GET',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            console.log(`Status: ${response.status} ${response.statusText}`);
            
            if (response.ok) {
                const data = await response.json();
                console.log('✅ API Response:');
                console.log(data);
                return data;
            } else {
                const error = await response.text();
                console.error('❌ API Error:');
                console.error(error);
                return null;
            }
        } catch (error) {
            console.error('❌ Network Error:');
            console.error(error);
            return null;
        }
    },
    
    /**
     * Check cookies
     */
    checkCookies() {
        console.log('🍪 Checking authentication cookies...\n');
        
        const cookies = document.cookie.split(';').map(c => c.trim());
        const authCookies = cookies.filter(c => 
            c.startsWith('access_token=') || 
            c.startsWith('refresh_token=') ||
            c.startsWith('sessionid=')
        );
        
        if (authCookies.length === 0) {
            console.warn('⚠️ No authentication cookies found!');
            console.log('You may need to login again.');
        } else {
            console.log(`✅ Found ${authCookies.length} auth cookie(s):`);
            authCookies.forEach(cookie => {
                const [name] = cookie.split('=');
                console.log(`  - ${name}`);
            });
        }
        
        return authCookies;
    },
    
    /**
     * Full diagnostic report
     */
    async fullReport() {
        console.log('═══════════════════════════════════════════════');
        console.log('   TEAM 7 AUTHENTICATION DIAGNOSTIC REPORT   ');
        console.log('═══════════════════════════════════════════════\n');
        
        // Check environment
        console.log('🌍 Environment:');
        console.log(`  URL: ${window.location.href}`);
        console.log(`  Origin: ${window.location.origin}\n`);
        
        // Check cookies
        this.checkCookies();
        console.log();
        
        // Test API
        await this.testAuthAPI();
        console.log();
        
        // Check auth status
        await this.checkAuth();
        
        console.log('\n═══════════════════════════════════════════════');
        console.log('End of diagnostic report');
        console.log('═══════════════════════════════════════════════');
    },
    
    /**
     * Quick fix: Clear cache and redirect to login
     */
    clearAndLogin() {
        console.log('🧹 Clearing session storage and redirecting to login...');
        sessionStorage.clear();
        localStorage.clear();
        window.location.href = '/auth/';
    },
    
    /**
     * Show help
     */
    help() {
        console.log('═══════════════════════════════════════════════');
        console.log('   AUTH DEBUG UTILITIES - HELP               ');
        console.log('═══════════════════════════════════════════════\n');
        console.log('Available commands:');
        console.log('');
        console.log('  authDebug.checkAuth()     - Check current auth status');
        console.log('  authDebug.refresh()       - Force refresh user data');
        console.log('  authDebug.testAuthAPI()   - Test /api/auth/me/ endpoint');
        console.log('  authDebug.checkCookies()  - Check authentication cookies');
        console.log('  authDebug.fullReport()    - Generate full diagnostic report');
        console.log('  authDebug.clearAndLogin() - Clear cache and go to login');
        console.log('  authDebug.help()          - Show this help message');
        console.log('\n═══════════════════════════════════════════════');
        console.log('Quick start: Run authDebug.fullReport()');
        console.log('═══════════════════════════════════════════════');
    }
};

// Show help on load in development
if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    console.log('🛠️ Auth Debug Utilities loaded. Type authDebug.help() for commands.');
}
