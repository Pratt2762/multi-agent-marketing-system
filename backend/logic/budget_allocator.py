"""
Budget Allocation Logic - Deterministic campaign budget reallocation
based on relative ROAS performance.
"""

def calculate_budget_actions(campaigns, top_percentile=0.30, bottom_percentile=0.30):
    """
    Calculates budget reallocation recommendations based on relative ROAS ranking.

    Args:
        campaigns: List of campaign dictionaries with 'campaign_id', 'campaign_name', 'roas'
        top_percentile: Percentage of top performers to increase (default 30%)
        bottom_percentile: Percentage of bottom performers to decrease (default 30%)

    Returns:
        List of budget action dictionaries with campaign_id, type, and reason
    """

    if not campaigns or len(campaigns) == 0:
        return []

    # Sort campaigns by ROAS (descending - highest first)
    campaigns_sorted = sorted(campaigns, key=lambda x: x.get('roas', 0), reverse=True)

    total_campaigns = len(campaigns_sorted)
    top_threshold_index = int(total_campaigns * top_percentile)
    bottom_threshold_index = int(total_campaigns * (1 - bottom_percentile))

    budget_actions = []

    for i, campaign in enumerate(campaigns_sorted):
        campaign_id = campaign.get('campaign_id')
        campaign_name = campaign.get('campaign_name', 'Unknown')
        roas = campaign.get('roas', 0)
        rank = i + 1

        # Determine action based on rank
        if i < top_threshold_index:
            # Top performers
            action_type = "increase"
            reason = f"ROAS {roas:.2f} ranks #{rank}/{total_campaigns} (top {int(top_percentile*100)}% performer)"
        elif i >= bottom_threshold_index:
            # Bottom performers
            action_type = "decrease"
            reason = f"ROAS {roas:.2f} ranks #{rank}/{total_campaigns} (bottom {int(bottom_percentile*100)}% performer)"
        else:
            # Middle tier
            action_type = "no_change"
            reason = f"ROAS {roas:.2f} ranks #{rank}/{total_campaigns} (average performer)"

        budget_actions.append({
            "campaign_id": campaign_id,
            "campaign_name": campaign_name,
            "type": action_type,
            "reason": reason,
            "roas": round(roas, 2),
            "rank": rank
        })

    return budget_actions


def get_budget_summary(budget_actions):
    """
    Generates a summary of budget allocation decisions.

    Args:
        budget_actions: List of budget action dictionaries

    Returns:
        Dictionary with summary statistics
    """
    increase_count = sum(1 for action in budget_actions if action['type'] == 'increase')
    decrease_count = sum(1 for action in budget_actions if action['type'] == 'decrease')
    no_change_count = sum(1 for action in budget_actions if action['type'] == 'no_change')

    return {
        "total_campaigns": len(budget_actions),
        "increase_count": increase_count,
        "decrease_count": decrease_count,
        "no_change_count": no_change_count
    }
