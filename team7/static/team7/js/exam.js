/**
 * Language Academy - Exam Page JavaScript
 * Page-specific functionality for exams
 */

// ==================== Mock Data ====================
/**
 * Hardcoded exam data - can be replaced with API calls in future
 */
const examData = {
    speaking: [
        {
            id: 'speak-1',
            title: 'توصیف یک مکان مورد علاقه',
            description: 'در این آزمون باید درباره مکانی که دوست دارید صحبت کنید و دلایل علاقه خود را بیان کنید',
            type: 'گفتاری',
            difficulty: 'آسان',
            duration: '10 دقیقه',
            questions: 3
        },
        {
            id: 'speak-2',
            title: 'بحث درباره فناوری و آموزش',
            description: 'نظرات خود را درباره تأثیر فناوری بر سیستم آموزشی بیان کنید',
            type: 'گفتاری',
            difficulty: 'متوسط',
            duration: '15 دقیقه',
            questions: 3
        },
        {
            id: 'speak-3',
            title: 'معرفی خود و علایق شخصی',
            description: 'خودتان را معرفی کنید و درباره علایق و سرگرمی‌های خود صحبت کنید',
            type: 'گفتاری',
            difficulty: 'آسان',
            duration: '10 دقیقه',
            questions: 2
        },
        {
            id: 'speak-4',
            title: 'بیان نظر درباره یک موضوع اجتماعی',
            description: 'نظرات خود درباره یک موضوع اجتماعی جاری را بیان کنید و دلایل آن را توضیح دهید',
            type: 'گفتاری',
            difficulty: 'سخت',
            duration: '20 دقیقه',
            questions: 4
        }
    ],
    writing: [
        {
            id: 'write-1',
            title: 'نامه رسمی',
            description: 'یک نامه رسمی برای درخواست اطلاعات بنویسید',
            type: 'نوشتاری',
            difficulty: 'آسان',
            duration: '20 دقیقه',
            questions: 1
        },
        {
            id: 'write-2',
            title: 'تحلیل متن آکادمیک',
            description: 'متن آکادمیک داده شده را تحلیل کنید و نظرات خود را بیان کنید',
            type: 'نوشتاری',
            difficulty: 'متوسط',
            duration: '25 دقیقه',
            questions: 1
        },
        {
            id: 'write-3',
            title: 'داستان کوتاه',
            description: 'با توجه به موضوع داده شده یک داستان کوتاه بنویسید',
            type: 'نوشتاری',
            difficulty: 'آسان',
            duration: '25 دقیقه',
            questions: 1
        },
        {
            id: 'write-4',
            title: 'مقاله توصیفی',
            description: 'موضوعی را برگزینید و یک مقاله توصیفی بنویسید',
            type: 'نوشتاری',
            difficulty: 'سخت',
            duration: '40 دقیقه',
            questions: 1
        }
    ]
};

/**
 * Hardcoded history data - can be replaced with API calls in future
 */
const historyData = [
    {
        id: 'hist-1',
        title: 'توصیف مکان',
        type: 'گفتاری',
        score: 8.5,
        duration: '15 دقیقه',
        date: '1403/09/15'
    },
    {
        id: 'hist-2',
        title: 'معرفی خود',
        type: 'گفتاری',
        score: 7.5,
        duration: '20 دقیقه',
        date: '1403/09/12'
    },
    {
        id: 'hist-3',
        title: 'نامه رسمی',
        type: 'نوشتاری',
        score: 8.0,
        duration: '25 دقیقه',
        date: '1403/09/10'
    },
    {
        id: 'hist-4',
        title: 'تحلیل متن آکادمیک',
        type: 'نوشتاری',
        score: 7.0,
        duration: '40 دقیقه',
        date: '1403/09/08'
    },
    {
        id: 'hist-5',
        title: 'فناوری و آموزش',
        type: 'گفتاری',
        score: 7.8,
        duration: '18 دقیقه',
        date: '1403/09/05'
    },
    {
        id: 'hist-6',
        title: 'داستان کوتاه',
        type: 'نوشتاری',
        score: 8.2,
        duration: '30 دقیقه',
        date: '1403/08/28'
    },
    {
        id: 'hist-7',
        title: 'فناوری و آموزش',
        type: 'گفتاری',
        score: 7.8,
        duration: '18 دقیقه',
        date: '1403/09/05'
    },
    {
        id: 'hist-8',
        title: 'فناوری و آموزش',
        type: 'گفتاری',
        score: 7.8,
        duration: '18 دقیقه',
        date: '1403/09/05'
    },
    {
        id: 'hist-9',
        title: 'فناوری و آموزش',
        type: 'گفتاری',
        score: 7.8,
        duration: '18 دقیقه',
        date: '1403/09/05'
    },
    {
        id: 'hist-10',
        title: 'فناوری و آموزش',
        type: 'گفتاری',
        score: 7.8,
        duration: '18 دقیقه',
        date: '1403/09/05'
    },
];

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
            <div><button class="view-button">مشاهده جزئیات</button></div>
            <div><span class="score-badge">${item.score}</span></div>
            <div>${item.duration}</div>
            <div>${item.date}</div>
            <div data-title="${item.title}">${item.title}</div>
        `;
        
        tableBody.appendChild(row);
    });
}

// ==================== Carousel Handlers ====================
/**
 * Initialize carousel functionality
 */
function initializeCarousels() {
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
            examCards.forEach(c => c.classList.remove('active-card'));
            c.classList.add('blur-card');
            
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
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const examTitle = this.closest('.exam-card')?.querySelector('.card-title')?.textContent;
            console.log('Starting exam:', examTitle);
            
            // Add visual feedback
            this.style.transform = 'scale(0.95)';
            setTimeout(() => {
                this.style.transform = '';
            }, 150);
            
            // Navigate to exam (implement actual navigation)
            // window.location.href = `/exams/${examTitle}`;
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
    
    viewButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const row = this.closest('.table-row');
            const examTitle = row.querySelector('[data-title]')?.textContent;
            const score = row.querySelector('.score-badge')?.textContent;
            
            console.log('Viewing details:', examTitle, 'Score:', score);
            
            // Add visual feedback
            this.style.transform = 'scale(0.95)';
            setTimeout(() => {
                this.style.transform = '';
            }, 150);
            
            // Navigate to exam details (implement actual navigation)
            // window.location.href = `/exams/details/${examTitle}`;
        });
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
    const filteredData = getFilteredHistoryData(paginationState.currentType);
    paginationState.totalPages = calculateTotalPages(filteredData);
    paginationState.currentPage = 1;
    
    const paginatedData = getPaginatedItems(filteredData, 1);
    renderHistoryTable(paginatedData);
    generatePaginationButtons(paginationState.totalPages);
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
function initializeExamPage() {
    // Initialize carousels with data
    initializeCarousels();
    
    // Render history table
    renderHistoryTable(historyData);
    
    // Initialize all event handlers
    initializeExamCards();
    initializeExamButtons();
    initializeHistoryTabs();
    initializeViewButtons();
    initializePagination();
    initializeCtaButtons();
    initializeChatIcon();
    initializeAnimations(['.hero-text', '.exam-card', '.history-container']);
}

// Run initialization when DOM is ready
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
