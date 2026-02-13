/**
 * Language Academy - Exam Page JavaScript
 * Page-specific functionality for exams
 */

// ==================== Mock Data ====================
/**
 * Carousel data for exam listing page
 * Generated from mockExamData (writing-exam.js) to avoid redundancy
 */
let examData = {
    speaking: [],
    writing: []
};

/**
 * Convert difficulty level (1-5) to difficulty text
 * @param {number} difficultyLevel - Difficulty level (1-5)
 * @returns {string} Difficulty text ('آسان', 'متوسط', 'سخت')
 */
function getDifficultyText(difficultyLevel) {
    if (difficultyLevel <= 2) return 'آسان';
    if (difficultyLevel <= 3) return 'متوسط';
    return 'سخت';
}

/**
 * Fetch exam data from API and generate carousel data
 * This ensures single source of truth - all exam data comes from the API
 */
async function generateExamDataFromAPI() {
    examData.speaking = [];
    examData.writing = [];
    
    try {
        const response = await fetch('/team7/api/exams/', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (!data.exams || data.exams.length === 0) {
        console.warn('No exams returned from API');
        return;
        }
        
        // Convert API exams to carousel format
        data.exams.forEach(exam => {
            const carouselItem = {
                id: exam.id,
                title: exam.title,
                description: exam.title,
                type: exam.type === 'writing' ? 'نوشتاری' : 'گفتاری',
                difficulty: getDifficultyText(exam.difficulty),
                duration: Math.round(exam.totalTime / 60) + ' دقیقه',
                questions: exam.totalQuestions
            };
            
            if (exam.type === 'writing') {
                examData.writing.push(carouselItem);
            } else if (exam.type === 'speaking') {
                examData.speaking.push(carouselItem);
            }
        });
        
        console.log('Loaded exams from API:', examData);
    } catch (error) {
        console.error('Error fetching exams from API:', error);
        // Don't show alert - just log the error and continue
        console.log('Could not load exams from API, carousels may be empty');
    }
}

/**
 * History data - fetched from API
 */
let historyData = [];

// ==================== Data Rendering Functions ====================
/**
 * Render carousel items from data
 */
function renderCarouselItems(containerId, items) {
    const carousel = document.getElementById(containerId);
    if (!carousel) return;

    carousel.innerHTML = '';
    
    items.forEach((item) => {
        const card = document.createElement('div');
        card.className = 'exam-card';
        // Make sure we have a valid ID - use 'id' field from API response
        card.id = item.id || `exam-${Date.now()}-${Math.random()}`;
        // Also store the ID as a data attribute for extra reliability
        card.setAttribute('data-exam-id', item.id);
        
        const difficultyClass = 
            item.difficulty === 'آسان' ? 'green' :
            item.difficulty === 'متوسط' ? 'yellow' :
            'red';
        
        card.innerHTML = `
            <div class="card-header">
                <span class="type-tag">${item.type}</span>
                <span class="difficulty-badge ${difficultyClass}">${item.difficulty}</span>
            </div>
            <h3 class="card-title">${item.title}</h3>
            <p class="card-description">${item.description}</p>
            <div class="card-meta">
                <div class="meta-item">
                    <div class="meta-icon"></div>
                    <span>${item.duration}</span>
                </div>
                <div class="meta-item">
                    <div class="meta-icon"></div>
                    <span>${item.questions} سؤال</span>
                </div>
            </div>
            <button class="card-button">شروع آزمون</button>
        `;
        
        carousel.appendChild(card);
    });
}

/**
 * Render history table rows from data
 */
function renderHistoryTable(items) {
    const tableContainer = document.querySelector('.history-table');
    if (!tableContainer) return;

    // Find or create table body
    let tableBody = tableContainer.querySelector('.table-body');
    if (!tableBody) {
        tableBody = document.createElement('div');
        tableBody.className = 'table-body';
        tableContainer.appendChild(tableBody);
    }

    tableBody.innerHTML = '';
    
    if (items.length === 0) {
        const emptyMessage = document.createElement('div');
        emptyMessage.className = 'empty-message';
        emptyMessage.textContent = 'آزمونی برای این دسته وجود ندارد';
        tableBody.appendChild(emptyMessage);
        return;
    }
    
    items.forEach(item => {
        const row = document.createElement('div');
        row.className = 'table-row';
        
        row.innerHTML = `
            <div data-title="${item.title}">${item.title}</div>
            <div>${item.date}</div>
            <div>${item.duration}</div>
            <div><span class="score-badge">${item.score}</span></div>
            <div><button class="view-button">مشاهده جزئیات</button></div>
        `;
        
        tableBody.appendChild(row);
    });
}

// ==================== Carousel Handlers ====================
/**
 * Initialize carousel functionality (fetch from API)
 */
async function initializeCarousels() {
    // Fetch exam data from API (with fallback to mock)
    await generateExamDataFromAPI();
    
    const speakingCarousel = document.getElementById('speakingCarousel');
    const writingCarousel = document.getElementById('writingCarousel');
    
    if (speakingCarousel) {
        renderCarouselItems('speakingCarousel', examData.speaking);
    }
    
    if (writingCarousel) {
        renderCarouselItems('writingCarousel', examData.writing);
    }
}

// ==================== Exam Card Handlers ====================
/**
 * Initialize exam card click handlers
 */
function initializeExamCards() {
    const examCards = document.querySelectorAll('.exam-card');
    
    examCards.forEach(card => {
        card.addEventListener('click', function(e) {
            // Don't trigger if clicking the button
            if (e.target.closest('.card-button')) return;
            
            // Remove active class from all cards
            examCards.forEach(c => {
                c.classList.remove('active-card');
                c.classList.add('blur-card');
            });
            
            // Add active class to clicked card
            this.classList.add('active-card');
            this.classList.remove('blur-card');
        });
    });
    
    // Initialize with first card active
    if (examCards.length > 0) {
        examCards[0].classList.add('active-card');
    }
}

/**
 * Initialize exam card button handlers
 */
function initializeExamButtons() {
    const examButtons = document.querySelectorAll('.card-button');
    
    examButtons.forEach(button => {
        button.addEventListener('click', async function(e) {
            e.preventDefault();
            const card = this.closest('.exam-card');
            // Try to get ID from data attribute first, then from element ID
            let examId = card?.getAttribute('data-exam-id') || card?.id;
            const examTitle = card?.querySelector('.card-title')?.textContent;
            const examTypeTag = card?.querySelector('.type-tag')?.textContent?.trim();
            
            console.log('Card element:', card);
            console.log('Card ID attribute:', card?.id);
            console.log('Card data-exam-id:', card?.getAttribute('data-exam-id'));
            console.log('Starting exam:', examTitle, 'ID:', examId, 'Type:', examTypeTag);
            
            if (!examId) {
                console.error('Exam ID not found on card element');
                console.error('Card HTML:', card?.outerHTML);
                // Silently return instead of alerting - the card may not be fully initialized yet
                console.warn('Button clicked but exam ID not available, ignoring click');
                return;
            }
            
            // Add visual feedback
            this.style.transform = 'scale(0.95)';
            setTimeout(() => {
                this.style.transform = '';
            }, 150);
            
            try {
                console.log('Fetching exam data for ID:', examId);
                const response = await fetch(`/team7/api/exams/?exam_id=${examId}`, {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                    }
                });
                
                if (!response.ok) {
                    throw new Error(`API error: ${response.status}`);
                }
                
                const data = await response.json();
                console.log('API response:', data);
                
                const examData = data.exams && data.exams.length > 0 ? data.exams[0] : null;
                
                if (!examData) {
                    throw new Error('No exam data found in response');
                }
                
                console.log('Exam data loaded successfully:', examData);
                console.log('Exam type from API:', examData.type, 'Type of:', typeof examData.type);
                
                // Show start exam popup before navigating
                showStartExamPopup(examData, () => {
                    PopupManager.closePopup();
                    // Use the exam type from API response instead of card tag
                    if (examData.type && examData.type.toLowerCase() === 'speaking') {
                        window.location.href = `/team7/speaking-exam/?exam_id=${examId}`;
                    } else {
                        window.location.href = `/team7/writing-exam/?exam_id=${examId}`;
                    }
                });
            } catch (error) {
                console.error('Error fetching exam data:', error);
                alert('خطا در بارگذاری آزمون: ' + error.message);
            }
        });
    });
}

// ==================== History Table Handlers ====================
/**
 * Initialize history table tab switching
 */
function initializeHistoryTabs() {
    const tabButtons = document.querySelectorAll('.tab-button');
    
    tabButtons.forEach((button, index) => {
        button.addEventListener('click', function() {
            // Remove active class from all tabs
            tabButtons.forEach(btn => btn.classList.remove('active'));
            // Add active class to clicked tab
            this.classList.add('active');
            
            const tabType = this.textContent.trim();
            console.log('Switched to:', tabType);
            
            // Update pagination state and reload data
            paginationState.currentType = tabType;
            paginationState.currentPage = 1;
            
            // Re-render table and pagination
            const filteredData = getFilteredHistoryData(tabType);
            paginationState.totalPages = calculateTotalPages(filteredData);
            const paginatedData = getPaginatedItems(filteredData, 1);
            
            renderHistoryTable(paginatedData);
            generatePaginationButtons(paginationState.totalPages);
            initializeViewButtons();
        });
    });
}

/**
 * Switch tab programmatically (backward compatibility)
 */
function switchTab(index) {
    const tabButtons = document.querySelectorAll('.tab-button');
    if (tabButtons[index]) {
        tabButtons[index].click();
    }
}

/**
 * Filter history table based on exam type
 */
function filterHistoryTable(examType) {
    const tableRows = document.querySelectorAll('.table-row');
    
    tableRows.forEach(row => {
        const rowType = row.querySelector('[data-exam-type]')?.getAttribute('data-exam-type');
        if (rowType === examType || examType === 'All') {
            row.style.display = 'grid';
        } else {
            row.style.display = 'none';
        }
    });
}

/**
 * Initialize view details button handlers
 */
function initializeViewButtons() {
    const viewButtons = document.querySelectorAll('.view-button');
    
    viewButtons.forEach((button, buttonIndex) => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const row = this.closest('.table-row');
            const score = row.querySelector('.score-badge')?.textContent;
            
            // Get the current filtered data based on active tab
            const filteredData = getFilteredHistoryData(paginationState.currentType);
            
            // Calculate which item in the filtered data this button represents
            const startIndex = (paginationState.currentPage - 1) * paginationState.itemsPerPage;
            const itemIndexInFiltered = startIndex + Array.from(viewButtons).indexOf(button);
            
            // Get the evaluation data from filtered data
            const evaluationData = filteredData[itemIndexInFiltered];
            
            if (!evaluationData) {
                console.error('Could not find evaluation data for this row');
                return;
            }
            
            // Add visual feedback
            this.style.transform = 'scale(0.95)';
            setTimeout(() => {
                this.style.transform = '';
            }, 150);
            
            // Show detailed popup - pass evaluationData and score only
            showEvaluationDetailsPopup(evaluationData, score);
        });
    });
}

/**
 * Show evaluation details popup with criteria
 * @param {Object} evaluationData - Evaluation data from API
 * @param {Number} score - Overall score
 */
function showEvaluationDetailsPopup(evaluationData, score) {
    // Detect exam type from task_type field in evaluation data
    const taskType = evaluationData.task_type;
    const isSpeaking = taskType === "speaking";
    const examTypePersian = isSpeaking ? 'گفتاری' : 'نوشتاری';
    const badgeText = isSpeaking ? 'TOEFL Speaking Exam' : 'TOEFL Writing Exam';
    
    // Get criteria HTML directly from API response (should be the 3 standard criteria)
    let criteriaHTML = '';
    if (evaluationData.criteria && evaluationData.criteria.length > 0) {
        criteriaHTML = evaluationData.criteria.map(criterion => {
            return `
                <div class="criteria-item">
                    <div class="criteria-header">
                        <span class="criteria-name">${criterion.name}</span>
                        <span class="criteria-score">${criterion.score}</span>
                    </div>
                </div>
            `;
        }).join('');
    }
    
    // Create popup HTML
    const popupHTML = `
        <div class="evaluation-details-popup">
            <div class="popup-header">
                <h2>جزئیات ارزیابی</h2>
                <button class="close-button">&times;</button>
            </div>
            
            <div class="badge-section">
                <span class="exam-badge">${badgeText}</span>
            </div>
            
            <div class="evaluation-overview">
                <div class="overview-item">
                    <span class="overview-label">نوع:</span>
                    <span class="overview-value">${examTypePersian}</span>
                </div>
                <div class="overview-item">
                    <span class="overview-label">نمره کل:</span>
                    <span class="overview-value score-highlight">${score}</span>
                </div>
                <div class="overview-item">
                    <span class="overview-label">تاریخ:</span>
                    <span class="overview-value">${evaluationData.date}</span>
                </div>
            </div>
            
            <div class="criteria-section">
                <h3>معیارهای ارزیابی</h3>
                <div class="criteria-list">
                    ${criteriaHTML || '<p class="no-criteria">معیاری موجود نیست</p>'}
                </div>
            </div>
        </div>
    `;
    
    // Create modal container
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.innerHTML = popupHTML;
    
    // Add styles if not already present
    if (!document.getElementById('evaluation-popup-styles')) {
        const style = document.createElement('style');
        style.id = 'evaluation-popup-styles';
        style.textContent = `
            .modal-overlay {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(0, 0, 0, 0.5);
                display: flex;
                justify-content: center;
                align-items: center;
                z-index: 2000;
                direction: rtl;
            }
            
            .evaluation-details-popup {
                background: white;
                border-radius: 12px;
                padding: 30px;
                max-width: 500px;
                width: 90%;
                max-height: 80vh;
                overflow-y: auto;
                box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
                animation: popupSlideIn 0.3s ease-out;
            }
            
            @keyframes popupSlideIn {
                from {
                    transform: translateY(-20px);
                    opacity: 0;
                }
                to {
                    transform: translateY(0);
                    opacity: 1;
                }
            }
            
            .popup-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 25px;
                border-bottom: 2px solid #f0f0f0;
                padding-bottom: 15px;
            }
            
            .popup-header h2 {
                margin: 0;
                font-size: 20px;
                color: #2c3e50;
                font-weight: 600;
            }
            
            .close-button {
                background: none;
                border: none;
                font-size: 28px;
                color: #95a5a6;
                cursor: pointer;
                padding: 0;
                width: 32px;
                height: 32px;
                display: flex;
                align-items: center;
                justify-content: center;
                border-radius: 50%;
                transition: all 0.2s;
            }
            
            .close-button:hover {
                background: #ecf0f1;
                color: #2c3e50;
            }
            
            .badge-section {
                display: flex;
                justify-content: center;
                margin-bottom: 20px;
            }
            
            .exam-badge {
                display: inline-block;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 8px 16px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            
            .evaluation-overview {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 8px;
                padding: 20px;
                margin-bottom: 25px;
                color: white;
            }
            
            .overview-item {
                display: flex;
                justify-content: space-between;
                margin-bottom: 12px;
                font-size: 14px;
            }
            
            .overview-item:last-child {
                margin-bottom: 0;
            }
            
            .overview-label {
                font-weight: 600;
                opacity: 0.9;
            }
            
            .overview-value {
                font-weight: 500;
            }
            
            .score-highlight {
                font-size: 18px;
                font-weight: 700;
                background: rgba(255, 255, 255, 0.2);
                padding: 4px 12px;
                border-radius: 6px;
            }
            
            .criteria-section h3 {
                font-size: 16px;
                color: #2c3e50;
                margin-bottom: 15px;
                font-weight: 600;
            }
            
            .criteria-list {
                display: flex;
                flex-direction: column;
                gap: 12px;
            }
            
            .criteria-item {
                background: #f8f9fa;
                border-left: 4px solid #667eea;
                padding: 15px;
                border-radius: 6px;
                transition: all 0.2s;
            }
            
            .criteria-item:hover {
                background: #f0f2ff;
                transform: translateX(-4px);
            }
            
            .criteria-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            
            .criteria-name {
                font-size: 14px;
                color: #2c3e50;
                font-weight: 500;
            }
            
            .criteria-score {
                background: #667eea;
                color: white;
                padding: 4px 12px;
                border-radius: 20px;
                font-size: 13px;
                font-weight: 600;
            }
            
            .no-criteria {
                color: #95a5a6;
                font-size: 14px;
                text-align: center;
                padding: 20px;
            }
        `;
        document.head.appendChild(style);
    }
    
    // Add to DOM
    document.body.appendChild(modal);
    
    // Close button handler
    modal.querySelector('.close-button').addEventListener('click', () => {
        modal.remove();
    });
    
    // Click outside to close
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.remove();
        }
    });
}

// ==================== Pagination State ====================
const paginationState = {
    currentPage: 1,
    itemsPerPage: 5,
    currentType: 'گفتاری',
    totalPages: 1
};

// ==================== Pagination Utilities ====================
/**
 * Get filtered data based on current exam type
 */
function getFilteredHistoryData(examType) {
    return historyData.filter(item => item.type === examType);
}

/**
 * Calculate total pages
 */
function calculateTotalPages(filteredData) {
    return Math.ceil(filteredData.length / paginationState.itemsPerPage);
}

/**
 * Get paginated items
 */
function getPaginatedItems(filteredData, page) {
    const startIndex = (page - 1) * paginationState.itemsPerPage;
    const endIndex = startIndex + paginationState.itemsPerPage;
    return filteredData.slice(startIndex, endIndex);
}

/**
 * Generate pagination buttons dynamically
 */
function generatePaginationButtons(totalPages) {
    const paginationContainer = document.querySelector('.pagination');
    if (!paginationContainer) return;
    
    paginationContainer.innerHTML = '';
    
    // Previous button
    const prevButton = document.createElement('button');
    prevButton.className = 'pagination-button';
    prevButton.textContent = 'قبلی';
    prevButton.disabled = paginationState.currentPage === 1;
    prevButton.addEventListener('click', () => goToPreviousPage());
    paginationContainer.appendChild(prevButton);
    
    // Page number buttons
    const maxVisiblePages = 5;
    let startPage = 1;
    let endPage = Math.min(totalPages, maxVisiblePages);
    
    // Adjust start and end if current page is near the end
    if (paginationState.currentPage > maxVisiblePages - 2) {
        startPage = Math.max(1, paginationState.currentPage - 2);
        endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);
    }
    
    // Add dots before if needed
    if (startPage > 1) {
        const dotsSpan = document.createElement('span');
        dotsSpan.className = 'pagination-dots';
        dotsSpan.textContent = '...';
        paginationContainer.appendChild(dotsSpan);
    }
    
    // Add page number buttons
    for (let i = startPage; i <= endPage; i++) {
        const pageButton = document.createElement('button');
        pageButton.className = 'pagination-button';
        pageButton.textContent = i;
        
        if (i === paginationState.currentPage) {
            pageButton.classList.add('active');
        }
        
        pageButton.addEventListener('click', () => goToPage(i));
        paginationContainer.appendChild(pageButton);
    }
    
    // Add dots after if needed
    if (endPage < totalPages) {
        const dotsSpan = document.createElement('span');
        dotsSpan.className = 'pagination-dots';
        dotsSpan.textContent = '...';
        paginationContainer.appendChild(dotsSpan);
    }
    
    // Add last page button if not visible
    if (endPage < totalPages) {
        const lastPageButton = document.createElement('button');
        lastPageButton.className = 'pagination-button';
        lastPageButton.textContent = totalPages;
        lastPageButton.addEventListener('click', () => goToPage(totalPages));
        paginationContainer.appendChild(lastPageButton);
    }
    
    // Next button
    const nextButton = document.createElement('button');
    nextButton.className = 'pagination-button';
    nextButton.textContent = 'بعدی';
    nextButton.disabled = paginationState.currentPage === totalPages;
    nextButton.addEventListener('click', () => goToNextPage());
    paginationContainer.appendChild(nextButton);
}

/**
 * Go to specific page
 */
function goToPage(pageNumber) {
    const filteredData = getFilteredHistoryData(paginationState.currentType);
    const totalPages = calculateTotalPages(filteredData);
    
    if (pageNumber < 1 || pageNumber > totalPages) return;
    
    paginationState.currentPage = pageNumber;
    const paginatedData = getPaginatedItems(filteredData, pageNumber);
    
    renderHistoryTable(paginatedData);
    generatePaginationButtons(totalPages);
    initializeViewButtons();
    
    // Scroll to history section
    document.querySelector('.history-section')?.scrollIntoView({ behavior: 'smooth' });
}

/**
 * Go to next page
 */
function goToNextPage() {
    const filteredData = getFilteredHistoryData(paginationState.currentType);
    const totalPages = calculateTotalPages(filteredData);
    
    if (paginationState.currentPage < totalPages) {
        goToPage(paginationState.currentPage + 1);
    }
}

/**
 * Go to previous page
 */
function goToPreviousPage() {
    if (paginationState.currentPage > 1) {
        goToPage(paginationState.currentPage - 1);
    }
}

/**
 * Initialize pagination on page load
 */
function initializePagination() {
    // Get the first tab's type (should be گفتاری by default)
    const firstTab = document.querySelector('.tab-button');
    if (firstTab) {
        paginationState.currentType = firstTab.textContent.trim();
    }
    
    const filteredData = getFilteredHistoryData(paginationState.currentType);
    paginationState.totalPages = calculateTotalPages(filteredData);
    paginationState.currentPage = 1;
    
    const paginatedData = getPaginatedItems(filteredData, 1);
    renderHistoryTable(paginatedData);
    generatePaginationButtons(paginationState.totalPages);
    initializeViewButtons();  // Initialize view buttons after rendering the initial table
}

// ==================== Start Exam Button Handlers ====================
/**
 * Initialize CTA button handlers
 */
function initializeCtaButtons() {
    const startExamButton = document.querySelector('.start-exam-button');
    const learnMoreButton = document.querySelector('.learn-more-button');
    
    if (startExamButton) {
        startExamButton.addEventListener('click', function() {
            const isAuthenticated = isUserAuthenticated();
            
            if (!isAuthenticated) {
                redirectToLogin();
            } else {
                // Scroll to exams section
                document.querySelector('.exams-section')?.scrollIntoView({ behavior: 'smooth' });
            }
        });
    }
    
    if (learnMoreButton) {
        learnMoreButton.addEventListener('click', function() {
            // Scroll to exams section
            document.querySelector('.exams-section')?.scrollIntoView({ behavior: 'smooth' });
        });
    }
}

// ==================== Chat Icon Handler ====================
/**
 * Initialize chat icon interaction
 */
function initializeChatIcon() {
    const chatIcon = document.querySelector('.chat-icon');
    
    if (chatIcon) {
        chatIcon.addEventListener('click', function() {
            console.log('Chat icon clicked');
            // Implement chat functionality
            // openChat();
        });
    }
}

// ==================== Initialize Exam Page ====================
/**
 * Initialize all exam page specific functionality
 */
async function initializeExamPage() {
    // Wait for auth to be ready
    if (window.authManager && window.authManager.isInitialized && !window.authManager.isInitialized()) {
        await window.authManager.initialize();
    }
    
    // Check authentication and update user profile
    if (window.authManager) {
        const isAuthenticated = await window.authManager.checkAuthStatus();
        const currentUser = window.authManager.getCurrentUser();
        
        if (isAuthenticated && currentUser) {
            // Update user name in header
            const userNameElement = document.querySelector('.user-name');
            if (userNameElement) {
                const fullName = `${currentUser.first_name || ''} ${currentUser.last_name || ''}`.trim();
                userNameElement.textContent = fullName || currentUser.email || 'کاربر';
            }
        }
    }
    
    // Initialize carousels with data - WAIT for this to complete
    await initializeCarousels();
    
    // Fetch history data from API - WAIT for this to complete
    await generateHistoryDataFromAPI();
    
    // Initialize all event handlers AFTER data is loaded
    initializeExamCards();
    initializeExamButtons();
    initializeHistoryTabs();
    
    // Initialize pagination (which renders the table and sets up view buttons)
    initializePagination();
    
    // Initialize other handlers
    initializeCtaButtons();
    initializeChatIcon();
    initializeAnimations(['.hero-text', '.exam-card', '.history-container']);
}
document.addEventListener('DOMContentLoaded', initializeExamPage);

// Export for testing
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        examData,
        historyData,
        renderCarouselItems,
        renderHistoryTable,
        initializeCarousels,
        initializeExamCards,
        initializeExamButtons,
        initializeHistoryTabs,
        filterHistoryTable,
        initializeViewButtons,
        initializePagination,
        initializeCtaButtons,
        initializeChatIcon,
        initializeExamPage
    };
}

/**
 * Fetch history data from API
 * Converts API response to format suitable for display
 */
async function generateHistoryDataFromAPI() {
    try {
        const response = await fetch('/team7/api/history/', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (!data.attempts || data.attempts.length === 0) {
            console.warn('No history data returned from API');
            historyData = [];
            return;
        }
        
        // Convert API history to display format
        const rawHistory = data.attempts.map((attempt) => {
            const date = new Date(attempt.created_at);
            const year = date.getFullYear();
            const month = String(date.getMonth() + 1).padStart(2, '0');
            const day = String(date.getDate()).padStart(2, '0');
            
            return {
                evaluation_id: attempt.evaluation_id,
                exam_id: attempt.exam_id,  // Include exam_id for grouping
                title: attempt.exam_name || `Evaluation`,
                type: attempt.task_type === 'writing' ? 'نوشتاری' : 'گفتاری',
                task_type: attempt.task_type,  // Keep the original task_type (writing or speaking) for detection
                score: attempt.overall_score || 0,
                duration: attempt.exam_name || '—',  // Use exam name instead of duration
                date: `${year}/${month}/${day}`,
                criteria: attempt.criteria || [],
                question_id: attempt.question_id,
                created_at: attempt.created_at
            };
        });
        
        // Group attempts by exam_id and timestamp to group multi-question exams
        const examGroups = {};
        rawHistory.forEach(attempt => {
            const examId = attempt.exam_id;
            const createdTime = new Date(attempt.created_at);
            
            // Create a key combining exam_id and a time window (same minute)
            // This groups all questions from the same exam taken within the same minute
            const timeKey = Math.floor(createdTime.getTime() / 60000); // Round to minute
            const groupKey = `${examId}_${timeKey}`;
            
            if (!examGroups[groupKey]) {
                examGroups[groupKey] = {
                    ...attempt,
                    scores: [attempt.score],
                    allCriteria: attempt.criteria || [],
                    evaluationIds: [attempt.evaluation_id],
                    dates: [attempt.created_at]
                };
            } else {
                // Add to existing group
                examGroups[groupKey].scores.push(attempt.score);
                examGroups[groupKey].evaluationIds.push(attempt.evaluation_id);
                examGroups[groupKey].dates.push(attempt.created_at);
                // Merge criteria
                if (attempt.criteria && attempt.criteria.length > 0) {
                    examGroups[groupKey].allCriteria = attempt.criteria;
                }
            }
        });
        
        // Convert groups back to array and calculate averages
        historyData = Object.values(examGroups).map(group => {
            // Calculate average score
            const averageScore = group.scores.length > 0 
                ? (group.scores.reduce((a, b) => a + b, 0) / group.scores.length)
                : 0;
            
            // Use the most recent date
            const mostRecentDate = group.dates.sort((a, b) => 
                new Date(b) - new Date(a)
            )[0];
            const date = new Date(mostRecentDate);
            const year = date.getFullYear();
            const month = String(date.getMonth() + 1).padStart(2, '0');
            const day = String(date.getDate()).padStart(2, '0');
            
            return {
                evaluation_id: group.evaluationIds[0],  // Use first evaluation ID
                exam_id: group.exam_id,
                title: group.title,
                type: group.type,
                task_type: group.task_type,
                score: parseFloat(averageScore.toFixed(1)),  // Round to 1 decimal
                duration: group.duration,
                date: `${year}/${month}/${day}`,
                criteria: group.allCriteria,
                question_count: group.scores.length,  // Number of questions in exam
                created_at: mostRecentDate
            };
        }).sort((a, b) => new Date(b.created_at) - new Date(a.created_at));  // Sort by most recent first
        
        console.log('Loaded history from API:', historyData);
    } catch (error) {
        console.error('Error fetching history from API:', error);
        console.log('Could not load history from API');
        historyData = [];
    }
}
