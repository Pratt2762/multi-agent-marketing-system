"""
Budget Allocation Logic - Intelligent campaign budget reallocation
based on ROAS performance, trends, momentum, and relative ranking.
"""

def calculate_budget_actions(campaigns, top_percentile=0.30, bottom_percentile=0.30):
    """
    Calculates budget reallocation recommendations using intelligent trend-based logic.

    Now considers:
    - Absolute ROAS performance
    - Trend direction (improving/declining/stable)
    - Momentum (percentage change)
    - Relative ranking and percentile
    - Volatility (performance stability)

    Args:
        campaigns: List of enriched campaign dictionaries with analytics fields
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
    budget_actions = []

    for i, campaign in enumerate(campaigns_sorted):
        campaign_id = campaign.get('campaign_id')
        campaign_name = campaign.get('campaign_name', 'Unknown')
        roas = campaign.get('roas', 0)
        rank = campaign.get('rank', i + 1)
        percentile = campaign.get('percentile', 0)
        trend_direction = campaign.get('trend_direction', 'stable')
        momentum = campaign.get('momentum', 0.0)
        distance_from_mean = campaign.get('distance_from_mean', 0)

        # INTELLIGENT DECISION LOGIC - Context-aware budget allocation
        action_type, reason = determine_budget_action(
            rank=rank,
            total_campaigns=total_campaigns,
            roas=roas,
            trend_direction=trend_direction,
            momentum=momentum,
            percentile=percentile,
            distance_from_mean=distance_from_mean,
            campaign_name=campaign_name,
            top_percentile=top_percentile,
            bottom_percentile=bottom_percentile
        )

        budget_actions.append({
            "campaign_id": campaign_id,
            "campaign_name": campaign_name,
            "type": action_type,
            "reason": reason,
            "roas": round(roas, 2),
            "rank": rank,
            "trend_direction": trend_direction,
            "momentum": round(momentum, 2)
        })

    return budget_actions


def determine_budget_action(rank, total_campaigns, roas, trend_direction, momentum,
                            percentile, distance_from_mean, campaign_name,
                            top_percentile, bottom_percentile):
    """
    Determines the budget action using intelligent, context-aware logic.

    Priority Rules:
    1. Strong momentum overrides static ranking
    2. Improving trends in mid-tier campaigns get opportunities
    3. Declining trends in top-tier campaigns get cautious treatment
    4. Extreme performers get adjusted based on sustainability
    """

    top_threshold = int(total_campaigns * top_percentile)
    bottom_threshold = int(total_campaigns * (1 - bottom_percentile))

    # CASE 1: STRONG POSITIVE MOMENTUM (>15%) - Capitalize on rising stars
    if momentum > 15:
        return "increase", (
            f"Exceptional momentum (+{momentum:.1f}%) accelerating performance; "
            f"ROAS {roas:.2f} now ranking #{rank} ({percentile}th percentile) warrants aggressive scaling to capitalize on growth trajectory"
        )

    # CASE 2: STRONG NEGATIVE MOMENTUM (<-15%) - Cut losses quickly
    if momentum < -15:
        return "decrease", (
            f"Sharp decline ({momentum:.1f}%) deteriorating rank #{rank} performance; "
            f"ROAS {roas:.2f} trending downward necessitates defensive budget reduction to limit exposure"
        )

    # CASE 3: TOP TIER PERFORMERS (top 30% by rank)
    if rank <= top_threshold:
        if trend_direction == 'improving':
            return "increase", (
                f"Elite performer ascending to rank #{rank} ({percentile}th percentile) with improving momentum (+{momentum:.1f}%); "
                f"ROAS {roas:.2f} demonstrates sustainable growth trajectory justifying scaled investment"
            )
        elif trend_direction == 'declining':
            return "no_change", (
                f"Premium rank #{rank} position offset by declining momentum ({momentum:.1f}%); "
                f"ROAS {roas:.2f} requires stability verification before additional capital allocation"
            )
        else:
            return "increase", (
                f"Consistent top-tier performance at rank #{rank} ({percentile}th percentile) with stable ROAS {roas:.2f}; "
                f"reliable efficiency profile supports continued growth investment"
            )

    # CASE 4: BOTTOM TIER PERFORMERS (bottom 30% by rank)
    if rank >= bottom_threshold:
        if trend_direction == 'improving' and momentum > 5:
            return "no_change", (
                f"Lower-tier rank #{rank} showing recovery momentum (+{momentum:.1f}%) with ROAS {roas:.2f}; "
                f"emerging positive trend warrants observation period before budget reallocation"
            )
        elif trend_direction == 'declining' or momentum < -5:
            return "decrease", (
                f"Underperforming rank #{rank} with deteriorating trend ({momentum:.1f}%); "
                f"ROAS {roas:.2f} below threshold necessitates budget reduction to reallocate capital to efficient campaigns"
            )
        else:
            return "decrease", (
                f"Persistent bottom-tier performance at rank #{rank} (ROAS {roas:.2f}) with stagnant trajectory; "
                f"strategic reallocation to higher-performing campaigns optimizes portfolio efficiency"
            )

    # CASE 5: MIDDLE TIER (40% in the middle)
    # More dynamic - use trends to make decisions
    if trend_direction == 'improving' and momentum > 10:
        return "increase", (
            f"Emerging mid-tier opportunity at rank #{rank} with robust momentum (+{momentum:.1f}%); "
            f"ROAS {roas:.2f} acceleration signals potential tier-elevation, justifying proactive investment"
        )
    elif trend_direction == 'improving' and momentum > 5:
        return "no_change", (
            f"Mid-tier rank #{rank} exhibiting positive momentum (+{momentum:.1f}%) with ROAS {roas:.2f}; "
            f"constructive trend development warrants sustained allocation while monitoring progression"
        )
    elif trend_direction == 'declining' and momentum < -10:
        return "decrease", (
            f"Mid-tier rank #{rank} experiencing sharp efficiency decline ({momentum:.1f}%); "
            f"ROAS {roas:.2f} deterioration requires defensive budget reduction to preserve capital"
        )
    elif distance_from_mean > 10:
        return "no_change", (
            f"Mid-tier rank #{rank} performing {distance_from_mean:+.1f} points above portfolio average; "
            f"ROAS {roas:.2f} stability supports current allocation strategy"
        )
    else:
        return "no_change", (
            f"Balanced mid-tier performance at rank #{rank} with stable ROAS {roas:.2f}; "
            f"equilibrium efficiency profile maintains current budget allocation pending performance inflection"
        )


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
