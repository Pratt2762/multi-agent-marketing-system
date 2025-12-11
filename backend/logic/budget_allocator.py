"""
Budget Allocation Logic - Intelligent campaign budget reallocation
based on ROAS performance, trends, momentum, and relative ranking.
"""

from backend.logic.action_calculator import calculate_budget_change

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

        # Calculate quantitative budget change using 3-tier system
        current_budget = campaign.get('weekly_budget_spent', 0)
        budget_change = calculate_budget_change(
            action_type,
            current_budget,
            {
                'momentum_2week': campaign.get('momentum_2week', 0),
                'trend_consistency': campaign.get('trend_consistency', 'stable'),
                'rank': rank
            }
        )

        budget_actions.append({
            "campaign_id": campaign_id,
            "campaign_name": campaign_name,
            "type": action_type,
            "reason": reason,
            "roas": round(roas, 2),
            "rank": rank,
            "trend_direction": trend_direction,
            "momentum": round(momentum, 2),
            "budget_change": budget_change  # Add quantitative change details
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
            f"This campaign demonstrates exceptional momentum with {momentum:.1f}% performance acceleration, "
            f"currently ranking #{rank} ({percentile}th percentile) with a ROAS of {roas:.2f}. "
            f"The strong growth trajectory warrants aggressive budget scaling to capitalize on this sustained upward trend."
        )

    # CASE 2: STRONG NEGATIVE MOMENTUM (<-15%) - Cut losses quickly
    if momentum < -15:
        return "decrease", (
            f"This campaign exhibits a sharp performance decline of {momentum:.1f}%, deteriorating to rank #{rank} with a ROAS of {roas:.2f}. "
            f"The persistent downward trend necessitates a defensive budget reduction to limit capital exposure and reallocate resources to higher-performing campaigns."
        )

    # CASE 3: TOP TIER PERFORMERS (top 30% by rank)
    if rank <= top_threshold:
        if trend_direction == 'improving':
            return "increase", (
                f"As an elite performer ascending to rank #{rank} ({percentile}th percentile), this campaign shows improving momentum of +{momentum:.1f}% with a ROAS of {roas:.2f}. "
                f"The sustainable growth trajectory demonstrates consistent efficiency gains, justifying scaled investment to maximize returns from this top-tier asset."
            )
        elif trend_direction == 'declining':
            return "no_change", (
                f"While maintaining a premium rank #{rank} position, this campaign exhibits declining momentum of {momentum:.1f}% with a ROAS of {roas:.2f}. "
                f"Stability verification is required before additional capital allocation to ensure the decline is temporary rather than systemic."
            )
        else:
            return "increase", (
                f"This campaign maintains consistent top-tier performance at rank #{rank} ({percentile}th percentile) with a stable ROAS of {roas:.2f}. "
                f"The reliable efficiency profile and proven track record support continued growth investment to compound strong returns."
            )

    # CASE 4: BOTTOM TIER PERFORMERS (bottom 30% by rank)
    if rank >= bottom_threshold:
        if trend_direction == 'improving' and momentum > 5:
            return "no_change", (
                f"Despite lower-tier positioning at rank #{rank}, this campaign shows promising recovery momentum of +{momentum:.1f}% with a ROAS of {roas:.2f}. "
                f"The emerging positive trend warrants an observation period to confirm sustainability before committing additional budget or implementing reductions."
            )
        elif trend_direction == 'declining' or momentum < -5:
            return "decrease", (
                f"This underperforming campaign ranks #{rank} with a deteriorating trend of {momentum:.1f}% and a ROAS of {roas:.2f}. "
                f"Budget reduction is necessary to limit inefficient spend and reallocate capital toward campaigns demonstrating stronger efficiency and growth potential."
            )
        else:
            return "decrease", (
                f"This campaign exhibits persistent bottom-tier performance at rank #{rank} with a ROAS of {roas:.2f} and stagnant trajectory. "
                f"Strategic budget reallocation to higher-performing campaigns will optimize overall portfolio efficiency and maximize return on advertising spend."
            )

    # CASE 5: MIDDLE TIER (40% in the middle)
    # More dynamic - use trends to make decisions
    if trend_direction == 'improving' and momentum > 10:
        return "increase", (
            f"This campaign represents an emerging mid-tier opportunity at rank #{rank}, displaying robust momentum of +{momentum:.1f}% with a ROAS of {roas:.2f}. "
            f"The performance acceleration signals potential for tier elevation, justifying proactive investment to capitalize on this upward trajectory before market saturation."
        )
    elif trend_direction == 'improving' and momentum > 5:
        return "no_change", (
            f"Positioned at mid-tier rank #{rank}, this campaign exhibits positive momentum of +{momentum:.1f}% with a ROAS of {roas:.2f}. "
            f"The constructive trend development warrants sustained budget allocation while monitoring progression to determine if the improvement solidifies into a sustained uptrend."
        )
    elif trend_direction == 'declining' and momentum < -10:
        return "decrease", (
            f"This mid-tier campaign at rank #{rank} is experiencing a sharp efficiency decline of {momentum:.1f}% with a ROAS of {roas:.2f}. "
            f"The performance deterioration requires a defensive budget reduction to preserve capital and prevent further erosion of returns."
        )
    elif distance_from_mean > 10:
        return "no_change", (
            f"This mid-tier campaign ranks #{rank} and performs {distance_from_mean:+.1f} points above the portfolio average with a ROAS of {roas:.2f}. "
            f"The above-average stability and consistent performance support maintaining current budget allocation to preserve this advantageous market position."
        )
    else:
        return "no_change", (
            f"This campaign maintains balanced mid-tier performance at rank #{rank} with a stable ROAS of {roas:.2f}. "
            f"The equilibrium efficiency profile supports current budget allocation while monitoring for performance inflection points that may warrant strategic adjustment."
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
