const RESULTS_FILE = 'results.json';
let globalData = null;
let currentWeekIndex = null;
let roasChart = null;
let ctrChart = null;

function runAgent() {
    document.getElementById('status').innerHTML = '<strong>Please run:</strong> <code>py -m backend.main</code> in your terminal to generate results.json';
}

function toggleSection(sectionId) {
    const section = document.getElementById(sectionId);
    const icon = event.target.querySelector('.toggle-icon');
    if (section.style.display === 'none') {
        section.style.display = 'block';
        icon.textContent = '▲';
    } else {
        section.style.display = 'none';
        icon.textContent = '▼';
    }
}

// ===========================================
// NEW: Executive Dashboard with Action Counts
// ===========================================
function renderActionSummaryCards(recommendations) {
    const budgetActions = recommendations.campaign_budget_actions || [];
    const bidActions = recommendations.ad_group_bid_actions || [];
    const audienceActions = recommendations.audience_targeting_actions || [];

    // Count actions by type
    const budgetCounts = countActionTypes(budgetActions);
    const bidCounts = countActionTypes(bidActions);
    const audienceCounts = countActionTypes(audienceActions);

    const cards = [
        {
            icon: '',
            title: 'Campaign Budget',
            cssClass: 'budget-card',
            total: budgetActions.length,
            totalLabel: 'Campaigns',
            increase: budgetCounts.increase || 0,
            hold: budgetCounts.no_change || 0,
            decrease: budgetCounts.decrease || 0
        },
        {
            icon: '',
            title: 'Ad Group Bids',
            cssClass: 'bids-card',
            total: bidActions.length,
            totalLabel: 'Ad Groups',
            increase: bidCounts.raise_bid || 0,
            hold: bidCounts.no_change || 0,
            decrease: bidCounts.lower_bid || 0
        },
        {
            icon: '',
            title: 'Audience Targeting',
            cssClass: 'audience-card',
            total: audienceActions.length,
            totalLabel: 'Audiences',
            increase: audienceCounts.activate || 0,
            hold: audienceCounts.no_change || 0,
            decrease: audienceCounts.suppress || 0
        }
    ];

    let html = '';
    cards.forEach(card => {
        html += `
            <div class="action-summary-card ${card.cssClass}">
                <div class="card-icon">${card.icon}</div>
                <div class="card-header">
                    <h3>${card.title}</h3>
                    <div class="card-total">${card.total} ${card.totalLabel}</div>
                </div>
                <div class="action-breakdown">
                    <div class="action-item positive">
                        <span class="action-count">${card.increase}</span>
                        <span class="action-label">Increase</span>
                    </div>
                    <div class="action-item neutral">
                        <span class="action-count">${card.hold}</span>
                        <span class="action-label">Hold</span>
                    </div>
                    <div class="action-item negative">
                        <span class="action-count">${card.decrease}</span>
                        <span class="action-label">Decrease</span>
                    </div>
                </div>
            </div>
        `;
    });

    document.getElementById('action-summary-cards').innerHTML = html;
}

function countActionTypes(actions) {
    const counts = {};
    actions.forEach(action => {
        const type = action.type;
        counts[type] = (counts[type] || 0) + 1;
    });
    return counts;
}

// ===========================================
// NEW: Stacked Recommendations Layout
// ===========================================
function renderThreeColumnRecommendations(recommendations, finalState) {
    renderBudgetSection(recommendations.campaign_budget_actions || [], finalState);
    renderBidsSection(recommendations.ad_group_bid_actions || [], finalState);
    renderAudiencesSection(recommendations.audience_targeting_actions || [], finalState);
}

function renderBudgetSection(budgetActions, finalState) {
    // Separate by action type
    const increases = budgetActions.filter(a => a.type === 'increase');
    const decreases = budgetActions.filter(a => a.type === 'decrease');

    // Render positive column (increases)
    let positiveHtml = '<h4 class="section-title positive">Top Performers (Increase Budget)</h4>';
    if (increases.length > 0) {
        const displayCount = Math.min(3, increases.length);
        positiveHtml += `<ul class="recommendation-list" data-total="${increases.length}" data-visible="${displayCount}">`;
        increases.slice(0, displayCount).forEach(action => {
            positiveHtml += `
                <li class="recommendation-item">
                    <div class="item-header">
                        <strong>${action.campaign_name}</strong>
                        <span class="item-badge positive">+${action.rank}</span>
                    </div>
                    <div class="item-metrics">
                        <span class="metric">ROAS: <strong>${action.roas}</strong></span>
                        <span class="metric">Rank: <strong>#${action.rank}/${budgetActions.length}</strong></span>
                    </div>
                    <div class="item-reason">${action.reason}</div>
                </li>
            `;
        });
        // Add hidden items
        increases.slice(displayCount).forEach(action => {
            positiveHtml += `
                <li class="recommendation-item hidden-item" style="display: none;">
                    <div class="item-header">
                        <strong>${action.campaign_name}</strong>
                        <span class="item-badge positive">+${action.rank}</span>
                    </div>
                    <div class="item-metrics">
                        <span class="metric">ROAS: <strong>${action.roas}</strong></span>
                        <span class="metric">Rank: <strong>#${action.rank}/${budgetActions.length}</strong></span>
                    </div>
                    <div class="item-reason">${action.reason}</div>
                </li>
            `;
        });
        positiveHtml += '</ul>';
        if (increases.length > 3) {
            positiveHtml += `<button class="view-all-btn" onclick="toggleViewAll(this)">View All (${increases.length})</button>`;
        }
    } else {
        positiveHtml += '<p class="no-data">No increase recommendations</p>';
    }

    // Render negative column (decreases)
    let negativeHtml = '<h4 class="section-title negative">Bottom Performers (Decrease Budget)</h4>';
    if (decreases.length > 0) {
        const displayCount = Math.min(3, decreases.length);
        negativeHtml += `<ul class="recommendation-list" data-total="${decreases.length}" data-visible="${displayCount}">`;
        decreases.slice(0, displayCount).forEach(action => {
            negativeHtml += `
                <li class="recommendation-item">
                    <div class="item-header">
                        <strong>${action.campaign_name}</strong>
                        <span class="item-badge negative">-${action.rank}</span>
                    </div>
                    <div class="item-metrics">
                        <span class="metric">ROAS: <strong>${action.roas}</strong></span>
                        <span class="metric">Rank: <strong>#${action.rank}/${budgetActions.length}</strong></span>
                    </div>
                    <div class="item-reason">${action.reason}</div>
                </li>
            `;
        });
        // Add hidden items
        decreases.slice(displayCount).forEach(action => {
            negativeHtml += `
                <li class="recommendation-item hidden-item" style="display: none;">
                    <div class="item-header">
                        <strong>${action.campaign_name}</strong>
                        <span class="item-badge negative">-${action.rank}</span>
                    </div>
                    <div class="item-metrics">
                        <span class="metric">ROAS: <strong>${action.roas}</strong></span>
                        <span class="metric">Rank: <strong>#${action.rank}/${budgetActions.length}</strong></span>
                    </div>
                    <div class="item-reason">${action.reason}</div>
                </li>
            `;
        });
        negativeHtml += '</ul>';
        if (decreases.length > 3) {
            negativeHtml += `<button class="view-all-btn" onclick="toggleViewAll(this)">View All (${decreases.length})</button>`;
        }
    } else {
        negativeHtml += '<p class="no-data">No decrease recommendations</p>';
    }

    document.getElementById('budget-recommendations-positive').innerHTML = positiveHtml;
    document.getElementById('budget-recommendations-negative').innerHTML = negativeHtml;
}

function renderBidsSection(bidActions, finalState) {
    // Separate by action type
    const raises = bidActions.filter(a => a.type === 'raise_bid');
    const lowers = bidActions.filter(a => a.type === 'lower_bid');

    // Render positive column (raises)
    let positiveHtml = '<h4 class="section-title positive">High Performers (Raise Bid)</h4>';
    if (raises.length > 0) {
        const displayCount = Math.min(3, raises.length);
        positiveHtml += `<ul class="recommendation-list" data-total="${raises.length}" data-visible="${displayCount}">`;
        raises.slice(0, displayCount).forEach(action => {
            const adGroup = finalState.ad_groups.find(ag => ag.ad_group_id === action.ad_group_id);
            positiveHtml += `
                <li class="recommendation-item">
                    <div class="item-header">
                        <strong>Ad Group ${action.ad_group_id}</strong>
                        ${adGroup ? `<span class="item-detail">${adGroup.ad_group_name}</span>` : ''}
                    </div>
                    ${adGroup ? `
                    <div class="item-metrics">
                        <span class="metric">ROAS: <strong>${adGroup.roas.toFixed(2)}</strong></span>
                        <span class="metric">Bid: <strong>$${adGroup.avg_bid.toFixed(2)}</strong></span>
                    </div>
                    ` : ''}
                    <div class="item-reason">${action.reason}</div>
                </li>
            `;
        });
        // Add hidden items
        raises.slice(displayCount).forEach(action => {
            const adGroup = finalState.ad_groups.find(ag => ag.ad_group_id === action.ad_group_id);
            positiveHtml += `
                <li class="recommendation-item hidden-item" style="display: none;">
                    <div class="item-header">
                        <strong>Ad Group ${action.ad_group_id}</strong>
                        ${adGroup ? `<span class="item-detail">${adGroup.ad_group_name}</span>` : ''}
                    </div>
                    ${adGroup ? `
                    <div class="item-metrics">
                        <span class="metric">ROAS: <strong>${adGroup.roas.toFixed(2)}</strong></span>
                        <span class="metric">Bid: <strong>$${adGroup.avg_bid.toFixed(2)}</strong></span>
                    </div>
                    ` : ''}
                    <div class="item-reason">${action.reason}</div>
                </li>
            `;
        });
        positiveHtml += '</ul>';
        if (raises.length > 3) {
            positiveHtml += `<button class="view-all-btn" onclick="toggleViewAll(this)">View All (${raises.length})</button>`;
        }
    } else {
        positiveHtml += '<p class="no-data">No raise bid recommendations</p>';
    }

    // Render negative column (lowers)
    let negativeHtml = '<h4 class="section-title negative">Low Performers (Lower Bid)</h4>';
    if (lowers.length > 0) {
        const displayCount = Math.min(3, lowers.length);
        negativeHtml += `<ul class="recommendation-list" data-total="${lowers.length}" data-visible="${displayCount}">`;
        lowers.slice(0, displayCount).forEach(action => {
            const adGroup = finalState.ad_groups.find(ag => ag.ad_group_id === action.ad_group_id);
            negativeHtml += `
                <li class="recommendation-item">
                    <div class="item-header">
                        <strong>Ad Group ${action.ad_group_id}</strong>
                        ${adGroup ? `<span class="item-detail">${adGroup.ad_group_name}</span>` : ''}
                    </div>
                    ${adGroup ? `
                    <div class="item-metrics">
                        <span class="metric">ROAS: <strong>${adGroup.roas.toFixed(2)}</strong></span>
                        <span class="metric">Bid: <strong>$${adGroup.avg_bid.toFixed(2)}</strong></span>
                    </div>
                    ` : ''}
                    <div class="item-reason">${action.reason}</div>
                </li>
            `;
        });
        // Add hidden items
        lowers.slice(displayCount).forEach(action => {
            const adGroup = finalState.ad_groups.find(ag => ag.ad_group_id === action.ad_group_id);
            negativeHtml += `
                <li class="recommendation-item hidden-item" style="display: none;">
                    <div class="item-header">
                        <strong>Ad Group ${action.ad_group_id}</strong>
                        ${adGroup ? `<span class="item-detail">${adGroup.ad_group_name}</span>` : ''}
                    </div>
                    ${adGroup ? `
                    <div class="item-metrics">
                        <span class="metric">ROAS: <strong>${adGroup.roas.toFixed(2)}</strong></span>
                        <span class="metric">Bid: <strong>$${adGroup.avg_bid.toFixed(2)}</strong></span>
                    </div>
                    ` : ''}
                    <div class="item-reason">${action.reason}</div>
                </li>
            `;
        });
        negativeHtml += '</ul>';
        if (lowers.length > 3) {
            negativeHtml += `<button class="view-all-btn" onclick="toggleViewAll(this)">View All (${lowers.length})</button>`;
        }
    } else {
        negativeHtml += '<p class="no-data">No lower bid recommendations</p>';
    }

    document.getElementById('bid-recommendations-positive').innerHTML = positiveHtml;
    document.getElementById('bid-recommendations-negative').innerHTML = negativeHtml;
}

function renderAudiencesSection(audienceActions, finalState) {
    // Separate by action type
    const activates = audienceActions.filter(a => a.type === 'activate');
    const suppresses = audienceActions.filter(a => a.type === 'suppress');

    // Render positive column (activates)
    let positiveHtml = '<h4 class="section-title positive">Best Health (Activate)</h4>';
    if (activates.length > 0) {
        const displayCount = Math.min(3, activates.length);
        positiveHtml += `<ul class="recommendation-list" data-total="${activates.length}" data-visible="${displayCount}">`;
        activates.slice(0, displayCount).forEach(action => {
            const audience = finalState.audiences.find(au => au.audience_id === action.audience_id);
            positiveHtml += `
                <li class="recommendation-item">
                    <div class="item-header">
                        <strong>${action.audience_id}</strong>
                        ${audience ? `<span class="item-detail">${audience.audience_name}</span>` : ''}
                    </div>
                    ${audience ? `
                    <div class="item-metrics">
                        <span class="metric">Intent: <strong>${audience.intent_score}</strong></span>
                        <span class="metric">Fatigue: <strong>${audience.fatigue_score.toFixed(1)}</strong></span>
                        <span class="metric">CTR: <strong>${(audience.avg_ctr * 100).toFixed(2)}%</strong></span>
                    </div>
                    ` : ''}
                    <div class="item-reason">${action.reason}</div>
                </li>
            `;
        });
        // Add hidden items
        activates.slice(displayCount).forEach(action => {
            const audience = finalState.audiences.find(au => au.audience_id === action.audience_id);
            positiveHtml += `
                <li class="recommendation-item hidden-item" style="display: none;">
                    <div class="item-header">
                        <strong>${action.audience_id}</strong>
                        ${audience ? `<span class="item-detail">${audience.audience_name}</span>` : ''}
                    </div>
                    ${audience ? `
                    <div class="item-metrics">
                        <span class="metric">Intent: <strong>${audience.intent_score}</strong></span>
                        <span class="metric">Fatigue: <strong>${audience.fatigue_score.toFixed(1)}</strong></span>
                        <span class="metric">CTR: <strong>${(audience.avg_ctr * 100).toFixed(2)}%</strong></span>
                    </div>
                    ` : ''}
                    <div class="item-reason">${action.reason}</div>
                </li>
            `;
        });
        positiveHtml += '</ul>';
        if (activates.length > 3) {
            positiveHtml += `<button class="view-all-btn" onclick="toggleViewAll(this)">View All (${activates.length})</button>`;
        }
    } else {
        positiveHtml += '<p class="no-data">No activate recommendations</p>';
    }

    // Render negative column (suppresses)
    let negativeHtml = '<h4 class="section-title negative">Worst Health (Suppress)</h4>';
    if (suppresses.length > 0) {
        const displayCount = Math.min(3, suppresses.length);
        negativeHtml += `<ul class="recommendation-list" data-total="${suppresses.length}" data-visible="${displayCount}">`;
        suppresses.slice(0, displayCount).forEach(action => {
            const audience = finalState.audiences.find(au => au.audience_id === action.audience_id);
            negativeHtml += `
                <li class="recommendation-item">
                    <div class="item-header">
                        <strong>${action.audience_id}</strong>
                        ${audience ? `<span class="item-detail">${audience.audience_name}</span>` : ''}
                    </div>
                    ${audience ? `
                    <div class="item-metrics">
                        <span class="metric">Intent: <strong>${audience.intent_score}</strong></span>
                        <span class="metric">Fatigue: <strong>${audience.fatigue_score.toFixed(1)}</strong></span>
                        <span class="metric">CTR: <strong>${(audience.avg_ctr * 100).toFixed(2)}%</strong></span>
                    </div>
                    ` : ''}
                    <div class="item-reason">${action.reason}</div>
                </li>
            `;
        });
        // Add hidden items
        suppresses.slice(displayCount).forEach(action => {
            const audience = finalState.audiences.find(au => au.audience_id === action.audience_id);
            negativeHtml += `
                <li class="recommendation-item hidden-item" style="display: none;">
                    <div class="item-header">
                        <strong>${action.audience_id}</strong>
                        ${audience ? `<span class="item-detail">${audience.audience_name}</span>` : ''}
                    </div>
                    ${audience ? `
                    <div class="item-metrics">
                        <span class="metric">Intent: <strong>${audience.intent_score}</strong></span>
                        <span class="metric">Fatigue: <strong>${audience.fatigue_score.toFixed(1)}</strong></span>
                        <span class="metric">CTR: <strong>${(audience.avg_ctr * 100).toFixed(2)}%</strong></span>
                    </div>
                    ` : ''}
                    <div class="item-reason">${action.reason}</div>
                </li>
            `;
        });
        negativeHtml += '</ul>';
        if (suppresses.length > 3) {
            negativeHtml += `<button class="view-all-btn" onclick="toggleViewAll(this)">View All (${suppresses.length})</button>`;
        }
    } else {
        negativeHtml += '<p class="no-data">No suppress recommendations</p>';
    }

    document.getElementById('audience-recommendations-positive').innerHTML = positiveHtml;
    document.getElementById('audience-recommendations-negative').innerHTML = negativeHtml;
}

// ===========================================
// View All Toggle Function
// ===========================================
function toggleViewAll(button) {
    const column = button.closest('.recommendations-column');
    const hiddenItems = column.querySelectorAll('.hidden-item');
    const isExpanded = button.classList.contains('expanded');

    if (isExpanded) {
        // Collapse
        hiddenItems.forEach(item => {
            item.style.display = 'none';
        });
        const list = column.querySelector('.recommendation-list');
        const totalCount = list.dataset.total;
        button.textContent = `View All (${totalCount})`;
        button.classList.remove('expanded');
    } else {
        // Expand
        hiddenItems.forEach(item => {
            item.style.display = 'block';
        });
        button.textContent = 'Show Less';
        button.classList.add('expanded');
    }
}

// ===========================================
// NEW: AI Explanation Panel
// ===========================================
function renderAIExplanation(recommendations) {
    const explanation = recommendations.explanation || 'No explanation provided';

    let html = `
        <div class="explanation-text">
            <p>${explanation}</p>
        </div>
    `;

    document.getElementById('ai-explanation-content').innerHTML = html;
}

// ===========================================
// Performance Charts Functions
// ===========================================
function renderPerformanceCharts() {
    const campaignHistory = globalData.campaign_history;

    // Always use ALL weeks for the charts (static display)
    const weeks = campaignHistory.map(entry => `Week ${entry.week}`);

    // Calculate average ROAS and CTR per week across all campaigns
    const avgROASPerWeek = campaignHistory.map(entry => {
        const campaigns = entry.state_snapshot.campaigns;
        const totalROAS = campaigns.reduce((sum, c) => sum + c.roas, 0);
        return (totalROAS / campaigns.length).toFixed(2);
    });

    const avgCTRPerWeek = campaignHistory.map(entry => {
        const campaigns = entry.state_snapshot.campaigns;
        // Calculate weighted average CTR based on impressions
        const totalClicks = campaigns.reduce((sum, c) => sum + (c.weekly_clicks || 0), 0);
        const totalImpressions = campaigns.reduce((sum, c) => sum + (c.weekly_impressions || 0), 0);
        const avgCTR = totalImpressions > 0 ? (totalClicks / totalImpressions) * 100 : 0;
        return avgCTR.toFixed(2);
    });

    // Update week indicators to show full range
    const maxWeek = campaignHistory[campaignHistory.length - 1].week;
    document.getElementById('roas-current-week').textContent = maxWeek;
    document.getElementById('ctr-current-week').textContent = maxWeek;

    // Show the charts section
    document.getElementById('performance-charts').style.display = 'block';

    // Render ROAS Chart
    renderROASChart(weeks, avgROASPerWeek);

    // Render CTR Chart
    renderCTRChart(weeks, avgCTRPerWeek);
}

function renderROASChart(weeks, data) {
    const ctx = document.getElementById('roas-chart').getContext('2d');

    // Destroy existing chart if it exists
    if (roasChart) {
        roasChart.destroy();
    }

    roasChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: weeks,
            datasets: [{
                label: 'Average ROAS',
                data: data,
                borderColor: '#667eea',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointRadius: 5,
                pointHoverRadius: 7,
                pointBackgroundColor: '#667eea',
                pointBorderColor: '#fff',
                pointBorderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(44, 62, 80, 0.9)',
                    padding: 12,
                    titleFont: {
                        size: 14,
                        weight: 'bold'
                    },
                    bodyFont: {
                        size: 13
                    },
                    callbacks: {
                        label: function(context) {
                            return 'ROAS: ' + context.parsed.y;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    },
                    ticks: {
                        font: {
                            size: 12
                        }
                    }
                },
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        font: {
                            size: 12
                        }
                    }
                }
            }
        }
    });
}

function renderCTRChart(weeks, data) {
    const ctx = document.getElementById('ctr-chart').getContext('2d');

    // Destroy existing chart if it exists
    if (ctrChart) {
        ctrChart.destroy();
    }

    ctrChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: weeks,
            datasets: [{
                label: 'Average CTR (%)',
                data: data,
                borderColor: '#764ba2',
                backgroundColor: 'rgba(118, 75, 162, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointRadius: 5,
                pointHoverRadius: 7,
                pointBackgroundColor: '#764ba2',
                pointBorderColor: '#fff',
                pointBorderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(44, 62, 80, 0.9)',
                    padding: 12,
                    titleFont: {
                        size: 14,
                        weight: 'bold'
                    },
                    bodyFont: {
                        size: 13
                    },
                    callbacks: {
                        label: function(context) {
                            return 'CTR: ' + context.parsed.y + '%';
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    },
                    ticks: {
                        font: {
                            size: 12
                        },
                        callback: function(value) {
                            return value + '%';
                        }
                    }
                },
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        font: {
                            size: 12
                        }
                    }
                }
            }
        }
    });
}

// ===========================================
// Week Navigator Functions
// ===========================================
function initializeWeekNavigator() {
    const campaignHistory = globalData.campaign_history;

    // Set to latest week by default
    currentWeekIndex = campaignHistory.length - 1;

    // Show the navigator
    document.getElementById('week-navigator').style.display = 'flex';

    // Update display and button states
    updateNavigatorState();
}

function navigateWeek(direction) {
    const newIndex = currentWeekIndex + direction;
    const maxIndex = globalData.campaign_history.length - 1;

    // Validate bounds
    if (newIndex < 0 || newIndex > maxIndex) {
        return;
    }

    // Update index and display
    currentWeekIndex = newIndex;
    updateWeekDisplay(currentWeekIndex);
    updateNavigatorState();
}

function updateNavigatorState() {
    const maxIndex = globalData.campaign_history.length - 1;
    const weekNumber = globalData.campaign_history[currentWeekIndex].week;

    // Update week display text
    document.getElementById('current-week-display').textContent = `Week ${weekNumber}`;

    // Enable/disable navigation buttons
    document.getElementById('prev-week').disabled = (currentWeekIndex === 0);
    document.getElementById('next-week').disabled = (currentWeekIndex === maxIndex);
}

function updateWeekDisplay(weekIndex) {
    currentWeekIndex = parseInt(weekIndex);
    const weekData = globalData.campaign_history[currentWeekIndex];

    const weekNumber = weekData.week;
    const state = weekData.state_snapshot;
    const recommendations = weekData.recommendations;

    // Update week display
    document.getElementById('latest-week').textContent = weekNumber;

    // Render sections with selected week's data
    renderActionSummaryCards(recommendations);
    renderThreeColumnRecommendations(recommendations, state);
}

// ===========================================
// Main Load Function
// ===========================================
function loadResults() {
    fetch(RESULTS_FILE)
        .then(response => {
            if (!response.ok) throw new Error('Results file not found');
            return response.json();
        })
        .then(data => {
            globalData = data;

            // Render static performance charts (once, with all weeks)
            renderPerformanceCharts();

            // Initialize week navigator
            initializeWeekNavigator();

            // Display the latest week by default
            updateWeekDisplay(globalData.campaign_history.length - 1);

            document.getElementById('status').innerHTML = '';
        })
        .catch(error => {
            document.getElementById('status').innerHTML = `<strong>Error:</strong> ${error.message}. Please run the backend first.`;
        });
}

// Auto-load results when page loads
window.addEventListener('DOMContentLoaded', function() {
    loadResults();
});

// ===========================================
// Legacy Functions (for detailed data section)
// ===========================================
function renderSummaryCards(finalState) {
    const finalCampaigns = finalState.campaigns;
    const initialTotalBudget = finalCampaigns.reduce((sum, c) => sum + c.weekly_budget_allocated, 0);
    const initialTotalSpent = finalCampaigns.reduce((sum, c) => sum + c.weekly_budget_spent, 0);
    const initialTotalROAS = finalCampaigns.reduce((sum, c) => sum + c.roas, 0) / finalCampaigns.length;

    const cards = [
        {
            title: 'Total Budget',
            value: `$${initialTotalBudget.toFixed(2)}`,
            subtitle: `Spent: $${initialTotalSpent.toFixed(2)}`,
            type: 'budget'
        },
        {
            title: 'Average ROAS',
            value: initialTotalROAS.toFixed(2),
            subtitle: `${finalCampaigns.length} campaigns`,
            type: 'increase'
        }
    ];

    let html = '';
    cards.forEach(card => {
        html += `
            <div class="summary-card ${card.type}">
                <div class="card-title">${card.title}</div>
                <div class="card-value">${card.value}</div>
                <div class="card-subtitle">${card.subtitle}</div>
            </div>
        `;
    });
    document.getElementById('summary-cards').innerHTML = html;
}

function renderInitialState(finalState) {
    const campaigns = finalState.campaigns;
    const ad_groups = finalState.ad_groups;

    const sortedCampaigns = [...campaigns].sort((a, b) => b.roas - a.roas);
    const topCampaigns = sortedCampaigns.slice(0, 3);
    const bottomCampaigns = sortedCampaigns.slice(-3);

    const sortedAdGroups = [...ad_groups].sort((a, b) => b.roas - a.roas);
    const topAdGroups = sortedAdGroups.slice(0, 3);
    const bottomAdGroups = sortedAdGroups.slice(-3);

    const campaignColumns = [
        { header: 'ID', field: 'campaign_id' },
        { header: 'Name', field: 'campaign_name' },
        { header: 'Budget', field: 'weekly_budget_allocated', formatter: r => `$${r.weekly_budget_allocated.toFixed(2)}` },
        { header: 'ROAS', field: 'roas', formatter: r => r.roas.toFixed(2) }
    ];

    const adGroupColumns = [
        { header: 'ID', field: 'ad_group_id' },
        { header: 'Name', field: 'ad_group_name' },
        { header: 'Bid', field: 'avg_bid', formatter: r => `$${r.avg_bid.toFixed(2)}` },
        { header: 'ROAS', field: 'roas', formatter: r => r.roas.toFixed(2) }
    ];

    let html = '<h4>Top 3 Campaigns</h4>';
    html += renderTable(topCampaigns, campaignColumns);
    html += '<h4>Bottom 3 Campaigns</h4>';
    html += renderTable(bottomCampaigns, campaignColumns);
    html += '<h4>Top 3 Ad Groups</h4>';
    html += renderTable(topAdGroups, adGroupColumns);
    html += '<h4>Bottom 3 Ad Groups</h4>';
    html += renderTable(bottomAdGroups, adGroupColumns);

    document.getElementById('initial-state-content').innerHTML = html;
}

function renderTable(data, columns) {
    if (!data || data.length === 0) return '<p>No data available.</p>';
    let html = '<table><thead><tr>';

    columns.forEach(col => {
        html += `<th>${col.header}</th>`;
    });
    html += '</tr></thead><tbody>';

    data.forEach(row => {
        html += '<tr>';
        columns.forEach(col => {
            const value = row[col.field] !== undefined ? row[col.field] : 'N/A';
            html += `<td>${col.formatter ? col.formatter(row) : value}</td>`;
        });
        html += '</tr>';
    });

    html += '</tbody></table>';
    return html;
}

function populateCampaignSelector(campaigns) {
    const select = document.getElementById('campaign-select');
    select.innerHTML = '<option value="">-- Select a campaign --</option>';
    campaigns.forEach(campaign => {
        const option = document.createElement('option');
        option.value = campaign.campaign_id;
        option.textContent = `${campaign.campaign_id}: ${campaign.campaign_name}`;
        select.appendChild(option);
    });
}

function updateAdGroupTable(campaignId) {
    const container = document.getElementById('ad-group-table-content');
    if (!campaignId || !globalData) {
        container.innerHTML = '<p>Please select a campaign.</p>';
        return;
    }

    const history = globalData.campaign_history;
    const campaignName = globalData.final_state_snapshot.campaigns.find(c => c.campaign_id === parseInt(campaignId))?.campaign_name || `Campaign ${campaignId}`;

    let html = `<h5>${campaignName} - Weekly Performance</h5>`;
    html += '<table><thead><tr><th>Week</th><th>Ad Group</th><th>Budget</th><th>Spend</th><th>ROAS</th></tr></thead><tbody>';

    history.forEach(weekData => {
        const adGroups = weekData.state_snapshot.ad_groups.filter(ag => ag.campaign_id === parseInt(campaignId));
        adGroups.forEach(ag => {
            html += `<tr>
                <td>${weekData.week}</td>
                <td>${ag.ad_group_name}</td>
                <td>$${ag.weekly_budget_allocated.toFixed(2)}</td>
                <td>$${ag.weekly_budget_spent.toFixed(2)}</td>
                <td>${ag.roas.toFixed(2)}</td>
            </tr>`;
        });
    });

    html += '</tbody></table>';
    container.innerHTML = html;
}
