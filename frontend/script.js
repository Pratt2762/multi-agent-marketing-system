const RESULTS_FILE = 'results.json';
let globalData = null;
let fullData = null; // Store complete data including week 12
let currentWeekIndex = null;
let roasChart = null;
let cvrChart = null;
let demoMode = true; // Start in demo mode (hide week 12 initially)
let agentRunning = false; // Track if agent is running

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
// Currency Formatting Helper
// ===========================================
function formatIndianCurrency(amount) {
    // Convert to thousands, lakhs or crores as appropriate
    if (amount >= 10000000) { // 1 crore or more
        return `₹${(amount / 10000000).toFixed(2)}Cr`;
    } else if (amount >= 100000) { // 1 lakh or more
        return `₹${(amount / 100000).toFixed(2)}L`;
    } else if (amount >= 1000) { // 1 thousand or more
        return `₹${(amount / 1000).toFixed(2)}K`;
    } else {
        return `₹${amount.toFixed(2)}`;
    }
}

// ===========================================
// Implementation Status/Button Helper
// ===========================================
function getImplementationHtml(changeData, actionId, actionType) {
    // changeData is budget_change or bid_change object
    // actionType is 'budget' or 'bid'

    if (!changeData || !changeData.tier) {
        return '';
    }

    const tier = changeData.tier;

    // For high tier (20%), show implementation button
    if (tier === 'high') {
        return `<button class="implement-btn" onclick="handleImplement('${actionId}', '${actionType}', event)">Implement</button>`;
    }

    // For moderate (10%) and low (5%) tiers, show "Implemented" status in italic
    if (tier === 'moderate' || tier === 'low') {
        return `<div class="implemented-status">Implemented</div>`;
    }

    return '';
}

// ===========================================
// Handle Implementation Button Click
// ===========================================
function handleImplement(actionId, actionType, event) {
    // Find the button and replace it with "Implemented" status
    const button = event.target;
    button.outerHTML = `<div class="implemented-status success">Implemented</div>`;

    // Optional: You can also log this action or send to backend
    console.log(`Implemented ${actionType} recommendation for ID: ${actionId}`);
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
            const budgetChangeHtml = action.budget_change ?
                `<span class="budget-amount increase">Increase budget from ${formatIndianCurrency(action.budget_change.current)} to ${formatIndianCurrency(action.budget_change.new)}</span>`
                : '';
            const implementationHtml = getImplementationHtml(action.budget_change, action.campaign_id, 'budget');
            positiveHtml += `
                <li class="recommendation-item">
                    <div class="item-header">
                        <strong>${action.campaign_name}</strong>
                        ${budgetChangeHtml}
                    </div>
                    <div class="item-metrics">
                        <div style="display: flex; gap: 15px;">
                            <span class="metric">ROAS: <strong>${action.roas}</strong></span>
                            <span class="metric">Rank: <strong>#${action.rank}/${budgetActions.length}</strong></span>
                        </div>
                        ${implementationHtml}
                    </div>
                    <div class="item-reason">${action.reason}</div>
                </li>
            `;
        });
        // Add hidden items
        increases.slice(displayCount).forEach(action => {
            const budgetChangeHtml = action.budget_change ?
                `<span class="budget-amount increase">Increase budget from ${formatIndianCurrency(action.budget_change.current)} to ${formatIndianCurrency(action.budget_change.new)}</span>`
                : '';
            const implementationHtml = getImplementationHtml(action.budget_change, action.campaign_id, 'budget');
            positiveHtml += `
                <li class="recommendation-item hidden-item" style="display: none;">
                    <div class="item-header">
                        <strong>${action.campaign_name}</strong>
                        ${budgetChangeHtml}
                    </div>
                    <div class="item-metrics">
                        <div style="display: flex; gap: 15px;">
                            <span class="metric">ROAS: <strong>${action.roas}</strong></span>
                            <span class="metric">Rank: <strong>#${action.rank}/${budgetActions.length}</strong></span>
                        </div>
                        ${implementationHtml}
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
            const budgetChangeHtml = action.budget_change ?
                `<span class="budget-amount decrease">Decrease budget from ${formatIndianCurrency(action.budget_change.current)} to ${formatIndianCurrency(action.budget_change.new)}</span>`
                : '';
            const implementationHtml = getImplementationHtml(action.budget_change, action.campaign_id, 'budget');
            negativeHtml += `
                <li class="recommendation-item">
                    <div class="item-header">
                        <strong>${action.campaign_name}</strong>
                        ${budgetChangeHtml}
                    </div>
                    <div class="item-metrics">
                        <div style="display: flex; gap: 15px;">
                            <span class="metric">ROAS: <strong>${action.roas}</strong></span>
                            <span class="metric">Rank: <strong>#${action.rank}/${budgetActions.length}</strong></span>
                        </div>
                        ${implementationHtml}
                    </div>
                    <div class="item-reason">${action.reason}</div>
                </li>
            `;
        });
        // Add hidden items
        decreases.slice(displayCount).forEach(action => {
            const budgetChangeHtml = action.budget_change ?
                `<span class="budget-amount decrease">Decrease budget from ${formatIndianCurrency(action.budget_change.current)} to ${formatIndianCurrency(action.budget_change.new)}</span>`
                : '';
            const implementationHtml = getImplementationHtml(action.budget_change, action.campaign_id, 'budget');
            negativeHtml += `
                <li class="recommendation-item hidden-item" style="display: none;">
                    <div class="item-header">
                        <strong>${action.campaign_name}</strong>
                        ${budgetChangeHtml}
                    </div>
                    <div class="item-metrics">
                        <div style="display: flex; gap: 15px;">
                            <span class="metric">ROAS: <strong>${action.roas}</strong></span>
                            <span class="metric">Rank: <strong>#${action.rank}/${budgetActions.length}</strong></span>
                        </div>
                        ${implementationHtml}
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
            const bidChangeHtml = action.bid_change ?
                `<span class="bid-amount increase">Raise bid from ${formatIndianCurrency(action.bid_change.current)} to ${formatIndianCurrency(action.bid_change.new)}</span>`
                : '';
            const implementationHtml = getImplementationHtml(action.bid_change, action.ad_group_id, 'bid');
            positiveHtml += `
                <li class="recommendation-item">
                    <div class="item-header">
                        <strong>Ad Group ${action.ad_group_id}</strong>
                        ${bidChangeHtml}
                    </div>
                    ${adGroup ? `
                    <div class="item-metrics">
                        <div style="display: flex; gap: 15px;">
                            <span class="metric">ROAS: <strong>${adGroup.roas.toFixed(2)}</strong></span>
                            <span class="metric">Bid: <strong>$${adGroup.avg_bid.toFixed(2)}</strong></span>
                        </div>
                        ${implementationHtml}
                    </div>
                    ` : ''}
                    <div class="item-reason">${action.reason}</div>
                </li>
            `;
        });
        // Add hidden items
        raises.slice(displayCount).forEach(action => {
            const adGroup = finalState.ad_groups.find(ag => ag.ad_group_id === action.ad_group_id);
            const bidChangeHtml = action.bid_change ?
                `<span class="bid-amount increase">Raise bid from ${formatIndianCurrency(action.bid_change.current)} to ${formatIndianCurrency(action.bid_change.new)}</span>`
                : '';
            const implementationHtml = getImplementationHtml(action.bid_change, action.ad_group_id, 'bid');
            positiveHtml += `
                <li class="recommendation-item hidden-item" style="display: none;">
                    <div class="item-header">
                        <strong>Ad Group ${action.ad_group_id}</strong>
                        ${bidChangeHtml}
                    </div>
                    ${adGroup ? `
                    <div class="item-metrics">
                        <div style="display: flex; gap: 15px;">
                            <span class="metric">ROAS: <strong>${adGroup.roas.toFixed(2)}</strong></span>
                            <span class="metric">Bid: <strong>$${adGroup.avg_bid.toFixed(2)}</strong></span>
                        </div>
                        ${implementationHtml}
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
            const bidChangeHtml = action.bid_change ?
                `<span class="bid-amount decrease">Lower bid from ${formatIndianCurrency(action.bid_change.current)} to ${formatIndianCurrency(action.bid_change.new)}</span>`
                : '';
            const implementationHtml = getImplementationHtml(action.bid_change, action.ad_group_id, 'bid');
            negativeHtml += `
                <li class="recommendation-item">
                    <div class="item-header">
                        <strong>Ad Group ${action.ad_group_id}</strong>
                        ${bidChangeHtml}
                    </div>
                    ${adGroup ? `
                    <div class="item-metrics">
                        <div style="display: flex; gap: 15px;">
                            <span class="metric">ROAS: <strong>${adGroup.roas.toFixed(2)}</strong></span>
                            <span class="metric">Bid: <strong>$${adGroup.avg_bid.toFixed(2)}</strong></span>
                        </div>
                        ${implementationHtml}
                    </div>
                    ` : ''}
                    <div class="item-reason">${action.reason}</div>
                </li>
            `;
        });
        // Add hidden items
        lowers.slice(displayCount).forEach(action => {
            const adGroup = finalState.ad_groups.find(ag => ag.ad_group_id === action.ad_group_id);
            const bidChangeHtml = action.bid_change ?
                `<span class="bid-amount decrease">Lower bid from ${formatIndianCurrency(action.bid_change.current)} to ${formatIndianCurrency(action.bid_change.new)}</span>`
                : '';
            const implementationHtml = getImplementationHtml(action.bid_change, action.ad_group_id, 'bid');
            negativeHtml += `
                <li class="recommendation-item hidden-item" style="display: none;">
                    <div class="item-header">
                        <strong>Ad Group ${action.ad_group_id}</strong>
                        ${bidChangeHtml}
                    </div>
                    ${adGroup ? `
                    <div class="item-metrics">
                        <div style="display: flex; gap: 15px;">
                            <span class="metric">ROAS: <strong>${adGroup.roas.toFixed(2)}</strong></span>
                            <span class="metric">Bid: <strong>$${adGroup.avg_bid.toFixed(2)}</strong></span>
                        </div>
                        ${implementationHtml}
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

// Helper function to generate distinct colors for each campaign
function generateDistinctColors(count) {
    const colors = [];
    const hueStep = 360 / count;

    for (let i = 0; i < count; i++) {
        const hue = i * hueStep;
        // Use varying saturation and lightness for better distinction
        const saturation = 60 + (i % 3) * 15;
        const lightness = 45 + (i % 4) * 10;
        colors.push(`hsl(${hue}, ${saturation}%, ${lightness}%)`);
    }

    return colors;
}

function renderPerformanceCharts() {
    // Defensive checks
    if (!globalData || !globalData.campaign_history || globalData.campaign_history.length === 0) {
        console.error('No campaign history data available');
        return;
    }

    const campaignHistory = globalData.campaign_history;

    // Check if first week has valid data
    if (!campaignHistory[0] || !campaignHistory[0].state_snapshot || !Array.isArray(campaignHistory[0].state_snapshot.campaigns)) {
        console.error('Invalid campaign data structure');
        return;
    }

    // Always use ALL weeks for the charts (static display)
    const weeks = campaignHistory.map(entry => `Week ${entry.week}`);

    // Build a map of campaign_id -> {name, roas_data[], cvr_data[]}
    const campaignMap = {};

    // Initialize campaign map with all campaigns from the first week
    campaignHistory[0].state_snapshot.campaigns.forEach(campaign => {
        campaignMap[campaign.campaign_id] = {
            name: campaign.campaign_name,
            roasData: [],
            cvrData: []
        };
    });

    // Populate data for each campaign across all weeks
    campaignHistory.forEach(entry => {
        entry.state_snapshot.campaigns.forEach(campaign => {
            const campId = campaign.campaign_id;

            // Add ROAS data
            campaignMap[campId].roasData.push(campaign.roas);

            // Add CVR data (conversion rate percentage)
            const conversions = campaign.weekly_conversions || 0;
            const spent = campaign.weekly_budget_spent || 0;
            // Calculate CVR as conversions per dollar spent (scaled to percentage)
            // Or we can use a simple metric: conversions as a rate
            const cvr = spent > 0 ? (conversions / spent) * 100 : 0;
            campaignMap[campId].cvrData.push(cvr);
        });
    });

    // Update week indicators to show full range
    const maxWeek = campaignHistory[campaignHistory.length - 1].week;
    document.getElementById('charts-current-week').textContent = maxWeek;

    // Show the charts section
    document.getElementById('performance-charts').style.display = 'block';

    // Populate single campaign selector for both charts
    populateCampaignSelector(campaignMap);

    // Render both charts with the same selected campaigns (initially show top 5)
    const selectedCampaigns = getSelectedCampaigns();
    renderROASChart(weeks, campaignMap, selectedCampaigns);
    renderCVRChart(weeks, campaignMap, selectedCampaigns);
}

function populateCampaignSelector(campaignMap) {
    const select = document.getElementById('campaign-select');

    // Clear existing options and event listeners
    const newSelect = select.cloneNode(false);
    select.parentNode.replaceChild(newSelect, select);

    // Get campaign IDs sorted by average ROAS (descending)
    const campaignIds = Object.keys(campaignMap).sort((a, b) => {
        const avgRoasA = campaignMap[a].roasData.reduce((sum, val) => sum + val, 0) / campaignMap[a].roasData.length;
        const avgRoasB = campaignMap[b].roasData.reduce((sum, val) => sum + val, 0) / campaignMap[b].roasData.length;
        return avgRoasB - avgRoasA;
    });

    // Default campaigns to select (names ending with 25, 16, 19, 8)
    const defaultCampaignNames = [
        'MSIL Festive Campaign 25',
        'Maruti Launch Campaign 16',
        'MSIL Festive Campaign 19',
        'MSIL Exchange Campaign 8'
    ];

    // Populate selector
    campaignIds.forEach((campaignId) => {
        const campaign = campaignMap[campaignId];
        const option = document.createElement('option');
        option.value = campaignId;
        option.textContent = campaign.name;
        // Select campaigns that match the default names
        option.selected = defaultCampaignNames.includes(campaign.name);

        newSelect.appendChild(option);
    });

    // Add change event listener to update BOTH charts when selection changes
    newSelect.addEventListener('change', () => {
        if (!globalData || !globalData.campaign_history) {
            console.error('Campaign data not available');
            return;
        }

        const campaignHistory = globalData.campaign_history;
        const weeks = campaignHistory.map(entry => `Week ${entry.week}`);
        const selectedCampaigns = getSelectedCampaigns();

        // Update both charts with the same selection
        renderROASChart(weeks, campaignMap, selectedCampaigns);
        renderCVRChart(weeks, campaignMap, selectedCampaigns);
    });
}

function getSelectedCampaigns() {
    const select = document.getElementById('campaign-select');
    const selectedOptions = Array.from(select.selectedOptions);
    return selectedOptions.map(option => option.value);
}

function renderROASChart(weeks, campaignMap, selectedCampaignIds = null) {
    const ctx = document.getElementById('roas-chart').getContext('2d');

    // Destroy existing chart if it exists
    if (roasChart) {
        roasChart.destroy();
    }

    // Filter campaigns based on selection
    const campaignsToShow = selectedCampaignIds && selectedCampaignIds.length > 0
        ? selectedCampaignIds
        : Object.keys(campaignMap);

    // Generate distinct colors for selected campaigns
    const colors = generateDistinctColors(campaignsToShow.length);

    // Create datasets for selected campaigns only
    const datasets = campaignsToShow.map((campaignId, index) => {
        const campaign = campaignMap[campaignId];
        return {
            label: campaign.name,
            data: campaign.roasData,
            borderColor: colors[index],
            backgroundColor: 'transparent',
            borderWidth: 2,
            fill: false,
            tension: 0.4,
            pointRadius: 3,
            pointHoverRadius: 6,
            pointBackgroundColor: colors[index],
            pointBorderColor: '#fff',
            pointBorderWidth: 2
        };
    });

    roasChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: weeks,
            datasets: datasets
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
                            return context.dataset.label + ': ' + context.parsed.y.toFixed(2);
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

function renderCVRChart(weeks, campaignMap, selectedCampaignIds = null) {
    const ctx = document.getElementById('cvr-chart').getContext('2d');

    // Destroy existing chart if it exists
    if (cvrChart) {
        cvrChart.destroy();
    }

    // Filter campaigns based on selection
    const campaignsToShow = selectedCampaignIds && selectedCampaignIds.length > 0
        ? selectedCampaignIds
        : Object.keys(campaignMap);

    // Generate distinct colors for selected campaigns
    const colors = generateDistinctColors(campaignsToShow.length);

    // Create datasets for selected campaigns only
    const datasets = campaignsToShow.map((campaignId, index) => {
        const campaign = campaignMap[campaignId];
        return {
            label: campaign.name,
            data: campaign.cvrData,
            borderColor: colors[index],
            backgroundColor: 'transparent',
            borderWidth: 2,
            fill: false,
            tension: 0.4,
            pointRadius: 3,
            pointHoverRadius: 6,
            pointBackgroundColor: colors[index],
            pointBorderColor: '#fff',
            pointBorderWidth: 2
        };
    });

    cvrChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: weeks,
            datasets: datasets
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
                            return context.dataset.label + ': ' + context.parsed.y.toFixed(2) + '%';
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
                            return value.toFixed(1) + '%';
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
    // If agent is already running, prevent duplicate runs
    if (agentRunning) {
        return;
    }

    // If demo mode is active and we haven't loaded full data yet, trigger the demo run
    if (demoMode && !fullData) {
        // First time load - load everything but only show weeks 1-11
        loadInitialData();
    } else if (demoMode && fullData) {
        // Demo mode active with full data loaded - run the 2-minute simulation
        runDemoAgentSimulation();
    } else {
        // Normal load (not in demo mode)
        loadAllData();
    }
}

function loadInitialData() {
    fetch(RESULTS_FILE)
        .then(response => {
            if (!response.ok) throw new Error('Results file not found');
            return response.json();
        })
        .then(data => {
            console.log('Initial data loaded:', data);

            // Validate data structure
            if (!data || !data.campaign_history || !Array.isArray(data.campaign_history)) {
                throw new Error('Invalid data structure: campaign_history missing or not an array');
            }

            if (data.campaign_history.length === 0) {
                throw new Error('campaign_history is empty');
            }

            if (!data.campaign_history[0].state_snapshot) {
                throw new Error('state_snapshot missing from first week');
            }

            if (!Array.isArray(data.campaign_history[0].state_snapshot.campaigns)) {
                throw new Error('campaigns is not an array: ' + typeof data.campaign_history[0].state_snapshot.campaigns);
            }

            // Store the full data (including week 12)
            fullData = data;

            // Create a copy with only weeks 1-11 (exclude the last week)
            const limitedData = {
                ...data,
                campaign_history: data.campaign_history.slice(0, -1) // Remove last week
            };

            globalData = limitedData;

            // Render static performance charts (with weeks 1-11 only)
            renderPerformanceCharts();

            // Initialize week navigator (weeks 1-11 only)
            initializeWeekNavigator();

            // Display week 11 (the latest available in demo mode)
            updateWeekDisplay(globalData.campaign_history.length - 1);

            document.getElementById('status').innerHTML = '';
        })
        .catch(error => {
            console.error('Load error:', error);
            document.getElementById('status').innerHTML = `<strong>Error:</strong> ${error.message}. Please run the backend first.`;
        });
}

function loadAllData() {
    fetch(RESULTS_FILE)
        .then(response => {
            if (!response.ok) throw new Error('Results file not found');
            return response.json();
        })
        .then(data => {
            console.log('Full data loaded:', data);

            // Validate data structure
            if (!data || !data.campaign_history || !Array.isArray(data.campaign_history)) {
                throw new Error('Invalid data structure: campaign_history missing or not an array');
            }

            if (data.campaign_history.length === 0) {
                throw new Error('campaign_history is empty');
            }

            if (!data.campaign_history[0].state_snapshot) {
                throw new Error('state_snapshot missing from first week');
            }

            if (!Array.isArray(data.campaign_history[0].state_snapshot.campaigns)) {
                throw new Error('campaigns is not an array: ' + typeof data.campaign_history[0].state_snapshot.campaigns);
            }

            globalData = data;
            fullData = data;

            // Render static performance charts (all weeks)
            renderPerformanceCharts();

            // Initialize week navigator
            initializeWeekNavigator();

            // Display the latest week by default
            updateWeekDisplay(globalData.campaign_history.length - 1);

            document.getElementById('status').innerHTML = '';
        })
        .catch(error => {
            console.error('Load error:', error);
            document.getElementById('status').innerHTML = `<strong>Error:</strong> ${error.message}. Please run the backend first.`;
        });
}

function runDemoAgentSimulation() {
    agentRunning = true;

    // Update button to show running state
    const button = document.getElementById('visualize');
    button.disabled = true;
    button.style.opacity = '0.7';
    button.style.cursor = 'not-allowed';

    // Show running status
    const statusDiv = document.getElementById('status');

    statusDiv.innerHTML = `
        <div style="text-align: center; padding: 20px;">
            <div style="font-size: 1.2em; font-weight: 500; font-style: italic; color: #6c757d;">
                AI Agent Running - Analyzing Latest Week Data...
            </div>
        </div>
    `;

    // After 2 minutes, reveal week 12
    setTimeout(() => {
        // Update globalData to include week 12
        globalData = fullData;
        demoMode = false;
        agentRunning = false;

        // Reset button
        button.disabled = false;
        button.style.opacity = '1';
        button.style.cursor = 'pointer';
        button.textContent = 'Analysis Complete ✓';
        button.style.background = 'linear-gradient(135deg, #28a745 0%, #20c997 100%)';

        // Show success message
        statusDiv.innerHTML = `
            <div style="text-align: center; padding: 20px; color: #28a745; font-size: 1.1em; font-weight: 600;">
                ✅ Week 12 Analysis Complete! New recommendations available.
            </div>
        `;

        // Re-render charts with all weeks including week 12
        renderPerformanceCharts();

        // Re-initialize week navigator to include week 12
        initializeWeekNavigator();

        // Display week 12
        updateWeekDisplay(globalData.campaign_history.length - 1);

        // Clear success message after 3 seconds
        setTimeout(() => {
            statusDiv.innerHTML = '';
        }, 3000);
    }, 120000); // 120 seconds = 2 minutes
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
