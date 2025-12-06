const RESULTS_FILE = 'results.json';
let globalData = null;

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
            icon: '💰',
            title: 'Campaign Budget',
            total: budgetActions.length,
            increase: budgetCounts.increase || 0,
            hold: budgetCounts.no_change || 0,
            decrease: budgetCounts.decrease || 0
        },
        {
            icon: '📈',
            title: 'Ad Group Bids',
            total: bidActions.length,
            increase: bidCounts.raise_bid || 0,
            hold: bidCounts.no_change || 0,
            decrease: bidCounts.lower_bid || 0
        },
        {
            icon: '👥',
            title: 'Audience Targeting',
            total: audienceActions.length,
            increase: audienceCounts.activate || 0,
            hold: audienceCounts.no_change || 0,
            decrease: audienceCounts.suppress || 0
        }
    ];

    let html = '';
    cards.forEach(card => {
        html += `
            <div class="action-summary-card">
                <div class="card-icon">${card.icon}</div>
                <div class="card-header">
                    <h3>${card.title}</h3>
                    <div class="card-total">${card.total} Total</div>
                </div>
                <div class="action-breakdown">
                    <div class="action-item positive">
                        <span class="action-count">${card.increase}</span>
                        <span class="action-label">▲ Increase</span>
                    </div>
                    <div class="action-item neutral">
                        <span class="action-count">${card.hold}</span>
                        <span class="action-label">→ Hold</span>
                    </div>
                    <div class="action-item negative">
                        <span class="action-count">${card.decrease}</span>
                        <span class="action-label">▼ Decrease</span>
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
// NEW: Three-Column Recommendations Layout
// ===========================================
function renderThreeColumnRecommendations(recommendations, finalState) {
    renderBudgetColumn(recommendations.campaign_budget_actions || [], finalState);
    renderBidsColumn(recommendations.ad_group_bid_actions || [], finalState);
    renderAudiencesColumn(recommendations.audience_targeting_actions || [], finalState);
}

function renderBudgetColumn(budgetActions, finalState) {
    // Separate by action type
    const increases = budgetActions.filter(a => a.type === 'increase');
    const decreases = budgetActions.filter(a => a.type === 'decrease');
    const holds = budgetActions.filter(a => a.type === 'no_change');

    let html = '';

    // Top Performers (Increase)
    html += '<div class="recommendation-section">';
    html += '<h4 class="section-title positive">✅ Top Performers (Increase Budget)</h4>';
    if (increases.length > 0) {
        html += '<ul class="recommendation-list">';
        increases.slice(0, 5).forEach(action => {
            html += `
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
        html += '</ul>';
    } else {
        html += '<p class="no-data">No increase recommendations</p>';
    }
    html += '</div>';

    // Bottom Performers (Decrease)
    html += '<div class="recommendation-section">';
    html += '<h4 class="section-title negative">❌ Bottom Performers (Decrease Budget)</h4>';
    if (decreases.length > 0) {
        html += '<ul class="recommendation-list">';
        decreases.slice(0, 5).forEach(action => {
            html += `
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
        html += '</ul>';
    } else {
        html += '<p class="no-data">No decrease recommendations</p>';
    }
    html += '</div>';

    document.getElementById('budget-recommendations').innerHTML = html;
}

function renderBidsColumn(bidActions, finalState) {
    // Separate by action type
    const raises = bidActions.filter(a => a.type === 'raise_bid');
    const lowers = bidActions.filter(a => a.type === 'lower_bid');
    const holds = bidActions.filter(a => a.type === 'no_change');

    let html = '';

    // Top Performers (Raise Bid)
    html += '<div class="recommendation-section">';
    html += '<h4 class="section-title positive">✅ High Performers (Raise Bid)</h4>';
    if (raises.length > 0) {
        html += '<ul class="recommendation-list">';
        raises.slice(0, 5).forEach(action => {
            const adGroup = finalState.ad_groups.find(ag => ag.ad_group_id === action.ad_group_id);
            html += `
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
        html += '</ul>';
    } else {
        html += '<p class="no-data">No raise bid recommendations</p>';
    }
    html += '</div>';

    // Bottom Performers (Lower Bid)
    html += '<div class="recommendation-section">';
    html += '<h4 class="section-title negative">❌ Low Performers (Lower Bid)</h4>';
    if (lowers.length > 0) {
        html += '<ul class="recommendation-list">';
        lowers.slice(0, 5).forEach(action => {
            const adGroup = finalState.ad_groups.find(ag => ag.ad_group_id === action.ad_group_id);
            html += `
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
        html += '</ul>';
    } else {
        html += '<p class="no-data">No lower bid recommendations</p>';
    }
    html += '</div>';

    document.getElementById('bid-recommendations').innerHTML = html;
}

function renderAudiencesColumn(audienceActions, finalState) {
    // Separate by action type
    const activates = audienceActions.filter(a => a.type === 'activate');
    const suppresses = audienceActions.filter(a => a.type === 'suppress');
    const holds = audienceActions.filter(a => a.type === 'no_change');

    let html = '';

    // Best Health (Activate)
    html += '<div class="recommendation-section">';
    html += '<h4 class="section-title positive">✅ Best Health (Activate)</h4>';
    if (activates.length > 0) {
        html += '<ul class="recommendation-list">';
        activates.forEach(action => {
            const audience = finalState.audiences.find(au => au.audience_id === action.audience_id);
            html += `
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
        html += '</ul>';
    } else {
        html += '<p class="no-data">No activate recommendations</p>';
    }
    html += '</div>';

    // Worst Health (Suppress)
    html += '<div class="recommendation-section">';
    html += '<h4 class="section-title negative">❌ Worst Health (Suppress)</h4>';
    if (suppresses.length > 0) {
        html += '<ul class="recommendation-list">';
        suppresses.forEach(action => {
            const audience = finalState.audiences.find(au => au.audience_id === action.audience_id);
            html += `
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
        html += '</ul>';
    } else {
        html += '<p class="no-data">No suppress recommendations</p>';
    }
    html += '</div>';

    document.getElementById('audience-recommendations').innerHTML = html;
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
            const finalState = data.final_state_snapshot;
            const finalRecommendations = data.final_recommendations;
            const latestWeek = data.latest_week;

            // Update week display
            document.getElementById('latest-week').textContent = latestWeek;

            // Render new sections
            renderActionSummaryCards(finalRecommendations);
            renderThreeColumnRecommendations(finalRecommendations, finalState);
            renderAIExplanation(finalRecommendations);

            // Render old sections (in collapsible area)
            renderSummaryCards(finalState);
            renderInitialState(finalState);
            populateCampaignSelector(finalState.campaigns);

            document.getElementById('status').innerHTML = '<strong>✅ Results loaded successfully!</strong>';
        })
        .catch(error => {
            document.getElementById('status').innerHTML = `<strong>Error:</strong> ${error.message}. Please run the backend first.`;
        });
}

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
