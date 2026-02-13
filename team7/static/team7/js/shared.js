/**
 * Language Academy - Shared JavaScript
 * Common functionality for all pages
 */

// ==================== Header Scroll Effect ====================
/**
 * Updates header style based on scroll position
 */
function initializeHeaderScroll() {
    const header = document.querySelector('.header');
    if (!header) return;

    const SCROLL_THRESHOLD = 100;

    function updateHeaderOnScroll() {
        const isScrolled = window.pageYOffset > SCROLL_THRESHOLD;
        
        if (isScrolled) {
            header.style.boxShadow = '0px 4px 12px rgba(0, 0, 0, 0.15)';
        } else {
            header.style.boxShadow = '0px 2px 8px rgba(0, 0, 0, 0.1)';
        }
    }

    window.addEventListener('scroll', updateHeaderOnScroll, { passive: true });
}

// ==================== Navigation Menu Toggle ====================
/**
 * Initialize mobile navigation menu toggle
 */
function initializeMobileMenu() {
    const menuToggle = document.querySelector('.menu-toggle');
    const navigationMenu = document.querySelector('.navigation-menu');
    
    if (!menuToggle || !navigationMenu) return;

    menuToggle.addEventListener('click', () => {
        navigationMenu.classList.toggle('active');
    });

    // Close menu when a link is clicked
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', () => {
            navigationMenu.classList.remove('active');
        });
    });
}

// ==================== Smooth Scroll Navigation ====================
/**
 * Initialize smooth scrolling for navigation links
 */
function initializeSmoothScroll() {
    const navigationLinks = document.querySelectorAll('.nav-link');
    
    navigationLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            const href = link.getAttribute('href');
            
            // Only prevent default for hash links
            if (href.startsWith('#')) {
                e.preventDefault();
                const targetId = href.substring(1);
                const targetElement = document.getElementById(targetId);
                
                if (targetElement) {
                    targetElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    updateActiveNavLink(link);
                }
            }
        });
    });
}

// ==================== Navigation Active Link ====================
/**
 * Updates the active nav link indicator
 */
function updateActiveNavLink(currentLink) {
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    currentLink.classList.add('active');
}

// ==================== Button Interactions ====================
/**
 * Add visual feedback to button clicks
 */
function initializeButtonFeedback() {
    document.querySelectorAll('button').forEach(button => {
        button.addEventListener('click', (e) => {
            const btn = e.target;
            
            // Add visual feedback
            btn.style.transform = 'scale(0.98)';
            setTimeout(() => {
                btn.style.transform = '';
            }, 150);
        });
    });
}

// ==================== Intersection Observer ====================
/**
 * Initialize intersection observer for fade-in animations
 */
function initializeAnimations(selectors = ['.feature-card', '.step-card', '.ai-content', '.ai-image-wrapper']) {
    const elements = document.querySelectorAll(selectors.join(', '));
    
    if (elements.length === 0) return;

    const ANIMATION_OPTIONS = {
        threshold: 0.15,
        rootMargin: '0px 0px -50px 0px'
    };

    const observerCallback = (entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in-up');
            }
        });
    };

    const observer = new IntersectionObserver(observerCallback, ANIMATION_OPTIONS);
    elements.forEach(el => {
        observer.observe(el);
    });
}

// ==================== Initialize All ====================
/**
 * Initialize all shared functionality
 */
function initializeSharedFunctionality() {
    initializeHeaderScroll();
    initializeMobileMenu();
    initializeSmoothScroll();
    initializeButtonFeedback();
}

// Run initialization when DOM is ready
document.addEventListener('DOMContentLoaded', initializeSharedFunctionality);