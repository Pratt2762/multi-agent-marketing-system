const RESULTS_FILE = 'results.json';
function runAgent() {
    document.getElementById('status').innerHTML = '<strong>Please run the Python script:</strong> <code>python backend/main.py</code> in your terminal to generate the results file.';
}
function renderTable(data, columns) {
    if (!data || data.length === 0) return '<p>No data available.</p>';
    let html = '<table><thead><tr>';
    
    // Create table headers
    columns.forEach(col => {
        html += `<th>${col.header}</th>`;
    });
    html += '</tr></thead><tbody>';
    // Create table rows
    data.forEach(row => {
        html += '<tr>';
        columns.forEach(col => {
            const value = row[col.field] !== undefined ? row[col.field] : 'N/A';
            // Pass the entire row to the formatter for complex lookups
            html += `<td>${col.formatter ? col.formatter(row) : value}</td>`;
        });
        html += '</tr>';
    });
    
    html += '</tbody></table>';
    return html;
}
function renderSummaryCards(finalState) {
    const finalCampaigns = finalState.campaigns;
    const initialTotalBudget = finalCampaigns.reduce((sum, c) => sum + c.weekly_budget_allocated, 0);
    const initialTotalSpent = finalCampaigns.reduce((sum, c) => sum + c.weekly_budget_spent, 0);
    const initialTotalROAS = finalCampaigns.reduce((sum, c) => sum + c.roas, 0) / finalCampaigns.length;
    const cards = [
        {
            title: 'Total Current Budget',
            value: `$${initialTotalBudget.toFixed(2)}`,
            subtitle: `Total Spent: $${initialTotalSpent.toFixed(2)}`,
            type: 'budget'
        },
        {
            title: 'Average Campaign ROAS',
            value: initialTotalROAS.toFixed(2),
            subtitle: `Total Campaigns: ${finalCampaigns.length}`,
            type: 'increase'
        },
        {
            title: 'Agent Mode',
            value: 'Recommendation Only',
            subtitle: 'No changes applied to data',
            type: 'neutral'
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
    
    // Sort campaigns by ROAS (descending)
    const sortedCampaigns = [...campaigns].sort((a, b) => b.roas - a.roas);
    const topCampaigns = sortedCampaigns.slice(0, 3);
    const bottomCampaigns = sortedCampaigns.slice(-3);
    
    // Sort ad groups by ROAS (descending)
    const sortedAdGroups = [...ad_groups].sort((a, b) => b.roas - a.roas);
    const topAdGroups = sortedAdGroups.slice(0, 3);
    const bottomAdGroups = sortedAdGroups.slice(-3);
    const campaignColumns = [
        { header: 'ID', field: 'campaign_id' },
        { header: 'Name', field: 'campaign_name' },
        { header: 'Current Budget', field: 'weekly_budget_allocated', formatter: r => `$${r.weekly_budget_allocated.toFixed(2)}` },
        { header: 'ROAS', field: 'roas', formatter: r => r.roas.toFixed(2) }
    ];
    
    const adGroupColumns = [
        { header: 'ID', field: 'ad_group_id' },
        { header: 'Campaign ID', field: 'campaign_id' },
        { header: 'Current Bid', field: 'avg_bid', formatter: r => `$${r.avg_bid.toFixed(2)}` },
        { header: 'ROAS', field: 'roas', formatter: r => r.roas.toFixed(2) }
    ];
    let html = '<h4>Top 3 Campaigns (By ROAS)</h4>';
    html += renderTable(topCampaigns, campaignColumns);
    html += '<h4>Bottom 3 Campaigns (By ROAS)</h4>';
    html += renderTable(bottomCampaigns, campaignColumns);
    html += '<h4>Top 3 Ad Groups (By ROAS)</h4>';
    html += renderTable(topAdGroups, adGroupColumns);
    html += '<h4>Bottom 3 Ad Groups (By ROAS)</h4>';
    html += renderTable(bottomAdGroups, adGroupColumns);
    document.getElementById('initial-state-content').innerHTML = html;
}
function getCampaignName(campaignId) {
    if (!globalData || !globalData.final_state_snapshot) return `Campaign ${campaignId}`;
    const campaign = globalData.final_state_snapshot.campaigns.find(c => c.campaign_id === campaignId);
    return campaign ? campaign.campaign_name : `Campaign ${campaignId}`;
}
function getAdGroupName(adGroupId) {
    if (!globalData || !globalData.final_state_snapshot) return `Ad Group ${adGroupId}`;
    const adGroup = globalData.final_state_snapshot.ad_groups.find(a => a.ad_group_id === adGroupId);
    return adGroup ? adGroup.ad_group_name : `Ad Group ${adGroupId}`;
}
function getAudienceName(audienceId) {
    if (!globalData || !globalData.final_state_snapshot) return `Audience ${audienceId}`;
    const audience = globalData.final_state_snapshot.audiences.find(a => a.audience_id === audienceId);
    return audience ? audience.audience_name : `Audience ${audienceId}`;
}
function updateAdGroupTable(campaignId) {
    const container = document.getElementById('ad-group-table-content');
    if (!campaignId || !globalData || !globalData.campaign_history) {
        container.innerHTML = '<p>Please select a campaign to view weekly ad-group details.</p>';
        return;
    }
    const history = globalData.campaign_history;
    const campaignName = getCampaignName(parseInt(campaignId));
    let html = `<h5>${campaignName} - Weekly Ad-Group Performance & Recommendations</h5>`;
    // Group all ad-group data and recommendations by week
    const weeklyData = history.map(weekData => {
        const week = weekData.week;
        const adGroups = weekData.state_snapshot.ad_groups.filter(ag => ag.campaign_id === parseInt(campaignId));
        const audiences = weekData.state_snapshot.audiences;
        
        // Filter recommendations for this campaign's ad groups/audiences
        const bidActions = weekData.recommendations.ad_group_bid_actions || [];
        const audienceActions = weekData.recommendations.audience_targeting_actions || [];
        const actions = [...bidActions, ...audienceActions].filter(a =>
            adGroups.some(ag => ag.ad_group_id === a.ad_group_id) ||
            audiences.some(au => au.audience_id === a.audience_id)
        );
        return { week, adGroups, audiences, actions };
    });
    // Prepare table data
    const tableData = [];
    weeklyData.forEach(wData => {
        wData.adGroups.forEach(ag => {
            const bidAction = wData.actions.find(a => a.ad_group_id === ag.ad_group_id && a.type.includes('bid'));
            const audienceAction = wData.actions.find(a => a.audience_id === ag.audience_id && (a.type === 'suppress' || a.type === 'activate'));
            
            tableData.push({
                week: wData.week,
                ad_group_id: ag.ad_group_id,
                ad_group_name: ag.ad_group_name,
                roas: ag.roas,
                conversion_value: ag.conversion_value,
                conversions: ag.conversions,
                avg_cvr: wData.audiences.find(a => a.audience_id === ag.audience_id)?.avg_cvr || 0,
                fatigue_score: wData.audiences.find(a => a.audience_id === ag.audience_id)?.fatigue_score || 0,
                intent_score: wData.audiences.find(a => a.audience_id === ag.audience_id)?.intent_score || 0,
                avg_bid: ag.avg_bid,
                bid_recommendation: bidAction ? bidAction.type : 'no_change',
                audience_recommendation: audienceAction ? audienceAction.type : 'no_change',
                recommendation_reason: (bidAction || audienceAction) ? (bidAction || audienceAction).reason || 'N/A' : 'N/A'
            });
        });
    });
    const adGroupColumns = [
        { header: 'Week', field: 'week' },
        { header: 'Ad Group', field: 'ad_group_name' },
        { header: 'ROAS', field: 'roas', formatter: r => r.roas.toFixed(2) },
        { header: 'Conv. Value', field: 'conversion_value', formatter: r => `$${r.conversion_value.toFixed(2)}` },
        { header: 'Conversions', field: 'conversions' },
        { header: 'CVR', field: 'avg_cvr', formatter: r => (r.avg_cvr * 100).toFixed(2) + '%' },
        { header: 'Fatigue Score', field: 'fatigue_score', formatter: r => r.fatigue_score.toFixed(2) },
        { header: 'Intent Score', field: 'intent_score' },
        { header: 'Current Bid', field: 'avg_bid', formatter: r => `$${r.avg_bid.toFixed(2)}` },
        { header: 'Bid Rec.', field: 'bid_recommendation', formatter: r => {
            let color = 'inherit';
            if (r.bid_recommendation.includes('raise')) color = '#28a745';
            if (r.bid_recommendation.includes('lower')) color = '#dc3545';
            return `<strong style="color: ${color};">${r.bid_recommendation.toUpperCase().replace('_', ' ')}</strong>`;
        }},
        { header: 'Audience Rec.', field: 'audience_recommendation', formatter: r => {
            let color = 'inherit';
            if (r.audience_recommendation.includes('activate')) color = '#28a745';
            if (r.audience_recommendation.includes('suppress')) color = '#dc3545';
            return `<strong style="color: ${color};">${r.audience_recommendation.toUpperCase().replace('_', ' ')}</strong>`;
        }},
        { header: 'Reason', field: 'recommendation_reason' }
    ];
    html += renderTable(tableData, adGroupColumns);
    container.innerHTML = html;
}
function renderRecommendations(recommendations, history) {
    // Recommendations section shows the LLM's raw JSON recommendations for the latest week
    const latestWeekData = history[history.length - 1];
    const latestWeek = latestWeekData.week;
    const budgetActions = recommendations.campaign_budget_actions || [];
    const bidActions = recommendations.ad_group_bid_actions || [];
    const audienceActions = recommendations.audience_targeting_actions || [];
    let html = `<h4>Agent Recommendations for Next Week (Week ${latestWeek + 1})</h4>`;
    // Budget Actions
    html += '<h5>Campaign Budget Reallocation Recommendations</h5>';
    if (budgetActions.length > 0) {
        html += '<ul>';
        budgetActions.forEach(a => {
            const type = a.type.replace('_', ' ').toUpperCase();
            const color = a.type.includes('increase') ? '#28a745' : '#dc3545';
            html += `<li>Campaign ${a.campaign_id}: <strong style="color: ${color};">${type}</strong> - Reason: ${a.reason || 'N/A'}</li>`;
        });
        html += '</ul>';
    } else {
        html += '<p>No budget reallocation recommendations this week.</p>';
    }
    // Bid Actions
    html += '<h5>Ad Group Bid Adjustment Recommendations</h5>';
    if (bidActions.length > 0) {
        html += '<ul>';
        bidActions.forEach(a => {
            const type = a.type.replace('_', ' ').toUpperCase();
            const color = a.type.includes('raise') ? '#28a745' : '#dc3545';
            html += `<li>Ad Group ${a.ad_group_id}: <strong style="color: ${color};">${type}</strong> - Reason: ${a.reason || 'N/A'}</li>`;
        });
        html += '</ul>';
    } else {
        html += '<p>No bid adjustment recommendations this week.</p>';
    }
    // Audience Actions
    html += '<h5>Audience Targeting Recommendations</h5>';
    if (audienceActions.length > 0) {
        html += '<ul>';
        audienceActions.forEach(a => {
            const type = a.type.toUpperCase();
            const color = a.type.includes('activate') ? '#28a745' : '#dc3545';
            html += `<li>Audience ${a.audience_id}: <strong style="color: ${color};">${type}</strong> - Reason: ${a.reason || 'N/A'}</li>`;
        });
        html += '</ul>';
    } else {
        html += '<p>No audience targeting recommendations this week.</p>';
    }
    // LLM Explanation
    html += '<h5>LLM Explanation</h5>';
    html += `<p>${recommendations.explanation || 'No explanation provided.'}</p>`;
    document.getElementById('decisions-content').innerHTML = html;
}
async function loadResults() {
    document.getElementById('status').textContent = 'Loading results...';
    try {
        const response = await fetch(RESULTS_FILE);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        globalData = data; // Store data globally for drill-down
        document.getElementById('latest-week').textContent = data.latest_week;
        document.getElementById('status').textContent = `Results loaded for Week ${data.latest_week}.`;
        renderSummaryCards(data.final_state_snapshot);
        renderInitialState(data.final_state_snapshot);
        renderRecommendations(data.final_recommendations, data.campaign_history);
    } catch (e) {
        document.getElementById('status').innerHTML = `<strong style="color: red;">Error loading results:</strong> ${e.message}. <br>Please run <code>python backend/main.py</code> first.`;
        console.error("Error loading results:", e);
    }
}
// Initial load attempt
loadResults();