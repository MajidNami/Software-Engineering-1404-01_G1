/**
 * Language Academy - Dashboard Charts Module
 * Handles all chart rendering and data visualization
 */

// Chart instances
let scoresChart = null;
let criteriaChart = null;
let grammarChart = null;
let vocabularyChart = null;
let fluencyChart = null;

// Theme colors
const themeColors = {
    primary: '#0b0754',
    accent: '#fa0b67',
    accent2: '#ffb02d',
    blue: '#80caff',
    light: '#a7bccc',
    border: '#d1d9de',
    background: '#f0f3f5'
};

/**
 * Initialize all dashboard charts
 */
async function initializeDashboardCharts() {
    try {
        // Fetch analytics data
        const analyticsData = await fetchAnalyticsData();
        
        if (analyticsData) {
            // Update status cards with real data
            updateStatusCards(analyticsData);
            
            // Initialize score trend chart
            initializeScoresChart(analyticsData);
            
            // Initialize criteria chart
            initializeCriteriaChart(analyticsData);
            
            // Initialize statistics charts
            initializeStatisticsCharts(analyticsData);
        }
    } catch (error) {
        console.error('Error initializing dashboard charts:', error);
    }
}

/**
 * Merge attempts by exam_id and timestamp to group multi-question exams
 * Groups questions from the same exam taken at approximately the same time
 * This ensures multi-question exams are counted as one attempt with average score
 */
function mergeAttemptsByExam(attempts) {
    if (!attempts || attempts.length === 0) return [];
    
    // Sort by created_at first
    const sortedAttempts = [...attempts].sort((a, b) => 
        new Date(a.created_at) - new Date(b.created_at)
    );
    
    const examGroups = {};
    
    sortedAttempts.forEach(attempt => {
        const examId = attempt.exam_id;
        const createdTime = new Date(attempt.created_at);
        
        // Create a key combining exam_id and a time window (same minute)
        // This groups all questions from the same exam taken within the same minute
        const timeKey = Math.floor(createdTime.getTime() / 60000); // Round to minute
        const groupKey = `${examId}_${timeKey}`;
        
        if (!examGroups[groupKey]) {
            examGroups[groupKey] = {
                ...attempt,
                scores: [attempt.overall_score || 0],
                allCriteria: attempt.criteria || [],
                evaluationIds: [attempt.evaluation_id],
                dates: [attempt.created_at],
                taskTypes: [attempt.task_type]  // Preserve task_type
            };
        } else {
            // Add to existing group
            examGroups[groupKey].scores.push(attempt.overall_score || 0);
            examGroups[groupKey].evaluationIds.push(attempt.evaluation_id);
            examGroups[groupKey].dates.push(attempt.created_at);
            examGroups[groupKey].taskTypes.push(attempt.task_type);
            // Merge criteria (keep the latest)
            if (attempt.criteria && attempt.criteria.length > 0) {
                examGroups[groupKey].allCriteria = attempt.criteria;
            }
        }
    });
    
    // Convert groups back to array and calculate averages
    return Object.values(examGroups).map(group => {
        // Calculate average score
        const averageScore = group.scores.length > 0 
            ? (group.scores.reduce((a, b) => a + b, 0) / group.scores.length)
            : 0;
        
        // Use the most recent date
        const mostRecentDate = group.dates.sort((a, b) => 
            new Date(b) - new Date(a)
        )[0];
        
        // Use the most common task_type or the first one if mixed
        const taskType = group.taskTypes[0];
        
        return {
            ...group,
            task_type: taskType,  // Explicitly preserve task_type
            overall_score: parseFloat(averageScore.toFixed(1)),
            question_count: group.scores.length,
            created_at: mostRecentDate
        };
    }).sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
}

/**
 * Fetch analytics data from API
 */
async function fetchAnalyticsData() {
    try {
        const response = await fetch('/team7/api/analytics/', {
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            console.warn('Failed to fetch analytics:', response.status);
            return null;
        }
        
        const data = await response.json();
        console.log('Analytics data fetched:', data);
        
        // Merge attempts by exam_id to group multi-question exams
        if (data.attempts) {
            data.attempts = mergeAttemptsByExam(data.attempts);
        }
        
        return data;
    } catch (error) {
        console.error('Error fetching analytics:', error);
        return null;
    }
}

/**
 * Update status cards with real data
 */
function updateStatusCards(analyticsData) {
    try {
        const attempts = analyticsData.attempts || [];
        
        if (attempts.length === 0) {
            document.getElementById('total-attempts').textContent = '0';
            document.getElementById('best-score').textContent = '--';
            document.getElementById('avg-score').textContent = '--';
            document.getElementById('last-attempt').textContent = 'No exams taken yet';
            document.getElementById('speaking-count').textContent = '0';
            document.getElementById('writing-count').textContent = '0';
            renderLatestExams([]);
            return;
        }
        
        // Total attempts
        document.getElementById('total-attempts').textContent = attempts.length;
        
        // Best score
        const bestScore = Math.max(...attempts.map(a => a.overall_score || 0)).toFixed(1);
        document.getElementById('best-score').textContent = bestScore;
        
        // Average score
        const avgScore = (attempts.reduce((sum, a) => sum + (a.overall_score || 0), 0) / attempts.length).toFixed(1);
        document.getElementById('avg-score').textContent = avgScore;
        
        // Last attempt - show exam name
        if (attempts.length > 0) {
            const lastAttempt = attempts[0];
            const examName = lastAttempt.exam_name || 'Unknown';
            document.getElementById('last-attempt').textContent = examName;
        }
        
        // Count by task type
        const speakingCount = attempts.filter(a => a.task_type === 'speaking').length;
        const writingCount = attempts.filter(a => a.task_type === 'writing').length;
        document.getElementById('speaking-count').textContent = speakingCount;
        document.getElementById('writing-count').textContent = writingCount;
        
        // Render latest exams section
        renderLatestExams(attempts.slice(0, 2)); // Get top 2 most recent
    } catch (error) {
        console.error('Error updating status cards:', error);
    }
}

/**
 * Render the latest exams section with real data from API
 */
function renderLatestExams(attempts) {
    const examsGrid = document.querySelector('.exams-grid');
    if (!examsGrid) return;
    
    examsGrid.innerHTML = '';
    
    if (!attempts || attempts.length === 0) {
        const emptyMessage = document.createElement('div');
        emptyMessage.style.cssText = 'grid-column: 1 / -1; text-align: center; padding: 40px; color: #a7bccc;';
        emptyMessage.innerHTML = '<p>No exams taken yet. Start your first exam!</p>';
        examsGrid.appendChild(emptyMessage);
        return;
    }
    
    attempts.forEach((attempt, index) => {
        const card = document.createElement('div');
        card.className = 'exam-card';
        
        const examType = attempt.task_type === 'speaking' ? 'Speaking' : 'Writing';
        const badgeClass = attempt.task_type === 'speaking' ? 'speaking' : 'writing';
        const badgeText = attempt.task_type === 'speaking' ? 'گفتاری' : 'نوشتاری';
        
        // Format the date
        const createdDate = new Date(attempt.created_at);
        const now = new Date();
        const daysDiff = Math.floor((now - createdDate) / (1000 * 60 * 60 * 24));
        let dateText = '';
        if (daysDiff === 0) {
            dateText = 'امروز';
        } else if (daysDiff === 1) {
            dateText = 'دیروز';
        } else {
            dateText = `${daysDiff} روز پیش`;
        }
        
        const examName = attempt.exam_name || `Exam ${index + 1}`;
        const score = (attempt.overall_score || 0).toFixed(1);
        
        // Determine if this is the best score
        let isBestScore = false;
        if (attempts.length > 0) {
            const maxScore = Math.max(...attempts.map(a => a.overall_score || 0));
            isBestScore = score == maxScore;
        }
        
        card.innerHTML = `
            <div class="exam-badge ${badgeClass}">${badgeText}</div>
            <p class="exam-date">${dateText}</p>
            <p class="exam-title">${examName}</p>
            <div class="exam-score">
                <span class="score-label">Score:</span>
                <span class="score-value">${score}</span>
            </div>
            ${isBestScore ? '<div class="best-badge">بهترین نتیجه</div>' : ''}
        `;
        
        examsGrid.appendChild(card);
    });
}

/**
 * Initialize scores trend chart
 */
function initializeScoresChart(analyticsData) {
    const ctx = document.getElementById('scoresChart');
    if (!ctx) return;
    
    const attempts = analyticsData.attempts || [];
    
    // Create a copy to avoid mutating the original array
    const attemptsForChart = [...attempts].reverse();
    
    // Prepare data - show chronological order (oldest to newest)
    const labels = attemptsForChart.map((attempt, index) => {
        const date = new Date(attempt.created_at);
        return `${date.getDate()}/${date.getMonth() + 1}`;
    }).slice(-10); // Last 10 attempts
    
    const scores = attemptsForChart.slice(-10).map(a => a.overall_score || 0);
    const taskTypes = attemptsForChart.slice(-10).map(a => a.task_type);
    
    // Color each point based on task type
    const pointColors = taskTypes.map(type => 
        type === 'speaking' ? themeColors.accent2 : themeColors.blue
    );
    
    // Destroy previous chart if exists
    if (scoresChart) {
        scoresChart.destroy();
    }
    
    scoresChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'نمره',
                    data: scores,
                    borderColor: themeColors.accent,
                    backgroundColor: `rgba(250, 11, 103, 0.05)`,
                    borderWidth: 3,
                    pointRadius: 6,
                    pointBackgroundColor: pointColors,
                    pointBorderColor: themeColors.primary,
                    pointBorderWidth: 2,
                    pointHoverRadius: 8,
                    tension: 0.4,
                    fill: true,
                    clip: false
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    labels: {
                        color: themeColors.primary,
                        font: {
                            family: "'Noto Sans Arabic', 'Inter', sans-serif",
                            size: 13,
                            weight: '500'
                        },
                        padding: 15,
                        usePointStyle: true,
                        pointStyle: 'circle'
                    }
                },
                tooltip: {
                    enabled: true,
                    backgroundColor: 'rgba(11, 7, 84, 0.9)',
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    borderColor: themeColors.accent,
                    borderWidth: 1,
                    padding: 12,
                    displayColors: true,
                    callbacks: {
                        title: function(context) {
                            return `تاریخ: ${context[0].label}`;
                        },
                        label: function(context) {
                            return `نمره: ${context.parsed.y.toFixed(1)}`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    min: 0,
                    max: 5,
                    ticks: {
                        color: themeColors.light,
                        font: {
                            family: "'Noto Sans Arabic', 'Inter', sans-serif",
                            size: 12
                        },
                        callback: function(value) {
                            return value.toFixed(1);
                        },
                        stepSize: 0.5,
                        padding: 10
                    },
                    grid: {
                        color: 'rgba(209, 217, 222, 0.3)',
                        drawBorder: false
                    }
                },
                x: {
                    ticks: {
                        color: themeColors.light,
                        font: {
                            family: "'Noto Sans Arabic', 'Inter', sans-serif",
                            size: 12
                        },
                        padding: 5
                    },
                    grid: {
                        display: false,
                        drawBorder: false
                    }
                }
            }
        }
    });
}

/**
 * Initialize criteria performance chart
 */
function initializeCriteriaChart(analyticsData) {
    const ctx = document.getElementById('criteriaChart');
    if (!ctx) return;
    
    const attempts = analyticsData.attempts || [];
    
    // Aggregate all criteria scores
    const criteriaMap = {};
    attempts.forEach(attempt => {
        if (attempt.criteria && Array.isArray(attempt.criteria)) {
            attempt.criteria.forEach(criterion => {
                if (!criteriaMap[criterion.name]) {
                    criteriaMap[criterion.name] = [];
                }
                criteriaMap[criterion.name].push(criterion.score || 0);
            });
        }
    });
    
    // Calculate average for each criterion
    const criteria = Object.keys(criteriaMap);
    const averageScores = criteria.map(name => {
        const scores = criteriaMap[name];
        return (scores.reduce((a, b) => a + b, 0) / scores.length).toFixed(2);
    });
    
    // Define colors for criteria
    const colors = [
        themeColors.accent,
        themeColors.accent2,
        themeColors.blue,
        'rgba(88, 124, 230, 0.8)',
        'rgba(160, 190, 255, 0.8)'
    ];
    
    // Destroy previous chart if exists
    if (criteriaChart) {
        criteriaChart.destroy();
    }
    
    if (criteria.length === 0) {
        // Show empty state
        const emptyMessage = document.createElement('div');
        emptyMessage.style.cssText = `
            display: flex;
            align-items: center;
            justify-content: center;
            height: 100%;
            color: ${themeColors.light};
            font-size: 16px;
            font-family: 'Noto Sans Arabic', 'Inter', sans-serif;
        `;
        emptyMessage.textContent = 'هنوز داده‌ای برای نمایش وجود ندارد';
        ctx.parentElement.replaceChild(emptyMessage, ctx);
        return;
    }
    
    criteriaChart = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: criteria,
            datasets: [
                {
                    label: 'میانگین نمرات',
                    data: averageScores,
                    borderColor: themeColors.accent,
                    backgroundColor: `rgba(250, 11, 103, 0.15)`,
                    borderWidth: 2.5,
                    pointBackgroundColor: colors,
                    pointBorderColor: themeColors.primary,
                    pointBorderWidth: 2,
                    pointRadius: 5,
                    pointHoverRadius: 7,
                    fill: true,
                    tension: 0.4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    labels: {
                        color: themeColors.primary,
                        font: {
                            family: "'Noto Sans Arabic', 'Inter', sans-serif",
                            size: 13,
                            weight: '500'
                        },
                        padding: 15,
                        usePointStyle: true
                    }
                },
                tooltip: {
                    enabled: true,
                    backgroundColor: 'rgba(11, 7, 84, 0.9)',
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    borderColor: themeColors.accent,
                    borderWidth: 1,
                    padding: 12,
                    callbacks: {
                        label: function(context) {
                            return `${context.label}: ${context.parsed.r.toFixed(1)}`;
                        }
                    }
                }
            },
            scales: {
                r: {
                    beginAtZero: true,
                    max: 5,
                    ticks: {
                        color: themeColors.light,
                        font: {
                            family: "'Noto Sans Arabic', 'Inter', sans-serif",
                            size: 11
                        },
                        backdropColor: 'transparent',
                        padding: 8,
                        stepSize: 0.5,
                        callback: function(value) {
                            return value.toFixed(1);
                        }
                    },
                    grid: {
                        color: 'rgba(209, 217, 222, 0.3)',
                        drawBorder: false
                    },
                    pointLabels: {
                        color: themeColors.primary,
                        font: {
                            family: "'Noto Sans Arabic', 'Inter', sans-serif",
                            size: 12,
                            weight: '500'
                        },
                        padding: 10
                    }
                }
            }
        }
    });
}

/**
 * Initialize statistics gauge charts (Grammar, Vocabulary, Fluency)
 */
function initializeStatisticsCharts(analyticsData) {
    const attempts = analyticsData.attempts || [];
    
    // Calculate average scores for each criterion across all attempts
    const criteriaScores = {};
    
    attempts.forEach(attempt => {
        if (attempt.criteria && Array.isArray(attempt.criteria)) {
            attempt.criteria.forEach(criterion => {
                if (!criteriaScores[criterion.name]) {
                    criteriaScores[criterion.name] = [];
                }
                criteriaScores[criterion.name].push(criterion.score || 0);
            });
        }
    });
    
    // Calculate averages
    const grammarScore = criteriaScores['Grammar'] 
        ? (criteriaScores['Grammar'].reduce((a, b) => a + b, 0) / criteriaScores['Grammar'].length) * 20
        : 0;
    const vocabularyScore = criteriaScores['Vocabulary'] 
        ? (criteriaScores['Vocabulary'].reduce((a, b) => a + b, 0) / criteriaScores['Vocabulary'].length) * 20
        : 0;
    const fluencyScore = criteriaScores['Language Use'] 
        ? (criteriaScores['Language Use'].reduce((a, b) => a + b, 0) / criteriaScores['Language Use'].length) * 25
        : 0;
    
    // Initialize Grammar Chart
    initializeGaugeChart('grammarChart', grammarScore, 'Grammar', 'grammar-value');
    
    // Initialize Vocabulary Chart
    initializeGaugeChart('vocabularyChart', vocabularyScore, 'Vocabulary', 'vocabulary-value');
    
    // Initialize Fluency Chart
    initializeGaugeChart('fluencyChart', fluencyScore, 'Fluency', 'fluency-value');
}

/**
 * Initialize a gauge chart with given parameters
 */
function initializeGaugeChart(canvasId, percentage, label, valueElementId) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    
    // Clamp percentage between 0 and 100
    const clampedPercentage = Math.max(0, Math.min(100, percentage));
    
    // Destroy previous chart if exists
    if (canvasId === 'grammarChart' && grammarChart) {
        grammarChart.destroy();
    } else if (canvasId === 'vocabularyChart' && vocabularyChart) {
        vocabularyChart.destroy();
    } else if (canvasId === 'fluencyChart' && fluencyChart) {
        fluencyChart.destroy();
    }
    
    // Determine color based on percentage
    let color = themeColors.accent;
    if (clampedPercentage >= 80) {
        color = '#10b981'; // Green
    } else if (clampedPercentage >= 60) {
        color = themeColors.accent2; // Orange
    } else {
        color = '#ef4444'; // Red
    }
    
    // Update the value element
    const valueElement = document.getElementById(valueElementId);
    if (valueElement) {
        valueElement.textContent = `${clampedPercentage.toFixed(0)}%`;
    }
    
    const chart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: [label, 'Remaining'],
            datasets: [
                {
                    data: [clampedPercentage, 100 - clampedPercentage],
                    backgroundColor: [
                        color,
                        'rgba(209, 217, 222, 0.2)'
                    ],
                    borderColor: [
                        color,
                        'rgba(209, 217, 222, 0.4)'
                    ],
                    borderWidth: 2,
                    cutout: '75%'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    enabled: true,
                    backgroundColor: 'rgba(11, 7, 84, 0.9)',
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    borderColor: color,
                    borderWidth: 1,
                    padding: 10,
                    callbacks: {
                        label: function(context) {
                            return `${context.label}: ${context.parsed}%`;
                        }
                    }
                }
            }
        },
        plugins: [
            {
                id: 'textCenter',
                beforeDatasetsDraw(chart) {
                    const { width } = chart;
                    const { height } = chart;
                    const { ctx } = chart;
                    ctx.restore();
                    
                    const fontSize = (height / 200).toFixed(2);
                    ctx.font = `bold ${fontSize}em sans-serif`;
                    ctx.textBaseline = 'middle';
                    ctx.fillStyle = themeColors.primary;
                    
                    const text = `${clampedPercentage.toFixed(0)}%`;
                    const textX = Math.round((width - ctx.measureText(text).width) / 2);
                    const textY = height / 2;
                    
                    ctx.fillText(text, textX, textY);
                    ctx.save();
                }
            }
        ]
    });
    
    // Store reference
    if (canvasId === 'grammarChart') {
        grammarChart = chart;
    } else if (canvasId === 'vocabularyChart') {
        vocabularyChart = chart;
    } else if (canvasId === 'fluencyChart') {
        fluencyChart = chart;
    }
}

// Initialize charts when DOM is ready
document.addEventListener('DOMContentLoaded', initializeDashboardCharts);
