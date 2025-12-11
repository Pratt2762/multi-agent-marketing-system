"""
Action Calculator Module - Converts qualitative actions to quantitative changes.

This module takes strategic actions (increase/decrease/no_change) and converts them
to exact dollar/bid amounts using a 3-tier scaling system based on 3-week metrics.
"""

def calculate_budget_change(action_type, current_budget, campaign_metrics):
    """
    Calculates exact budget change based on action type and 3-week performance metrics.

    3-Tier System:
    - HIGH (20%): Strong sustained performance (consistent trend + high momentum)
    - MODERATE (10%): Good performance (improving trend or moderate momentum)
    - LOW (5%): Conservative adjustment (mild signals or volatile performance)

    Args:
        action_type: "increase" / "decrease" / "no_change"
        current_budget: Current weekly budget (float)
        campaign_metrics: Dict with:
            - momentum_2week: 2-week momentum percentage
            - trend_consistency: "consistent_improving" / "consistent_declining" / "volatile"
            - rank: Campaign rank (1 = best)

    Returns:
        {
            "current": 500.00,
            "new": 600.00,
            "change_amount": 100.00,
            "change_percent": 20.0,
            "tier": "high"  # high/moderate/low
        }
    """

    if action_type == "no_change":
        return {
            "current": round(current_budget, 2),
            "new": round(current_budget, 2),
            "change_amount": 0.00,
            "change_percent": 0.0,
            "tier": "none"
        }

    # Extract metrics
    momentum_2week = campaign_metrics.get('momentum_2week', 0)
    trend_consistency = campaign_metrics.get('trend_consistency', 'stable')
    rank = campaign_metrics.get('rank', 50)

    # Determine tier and multiplier
    if action_type == "increase":
        tier, multiplier = _determine_increase_tier(momentum_2week, trend_consistency, rank)
    elif action_type == "decrease":
        tier, multiplier = _determine_decrease_tier(momentum_2week, trend_consistency, rank)
    else:
        # Fallback
        return {
            "current": round(current_budget, 2),
            "new": round(current_budget, 2),
            "change_amount": 0.00,
            "change_percent": 0.0,
            "tier": "none"
        }

    # Calculate new budget
    new_budget = current_budget * multiplier
    change_amount = new_budget - current_budget
    change_percent = (multiplier - 1) * 100

    return {
        "current": round(current_budget, 2),
        "new": round(new_budget, 2),
        "change_amount": round(change_amount, 2),
        "change_percent": round(change_percent, 1),
        "tier": tier
    }


def calculate_bid_change(action_type, current_bid, ad_group_metrics):
    """
    Calculates exact bid change based on action type and 3-week performance metrics.

    3-Tier System (same as budget):
    - HIGH (20%): Strong sustained performance
    - MODERATE (10%): Good performance
    - LOW (5%): Conservative adjustment

    Args:
        action_type: "raise_bid" / "lower_bid" / "no_change"
        current_bid: Current bid amount (float)
        ad_group_metrics: Dict with:
            - momentum_2week: 2-week momentum percentage
            - trend_consistency: "consistent_improving" / "consistent_declining" / "volatile"
            - rank: Ad group rank (1 = best)

    Returns:
        {
            "current": 2.50,
            "new": 3.00,
            "change_amount": 0.50,
            "change_percent": 20.0,
            "tier": "high"
        }
    """

    if action_type == "no_change":
        return {
            "current": round(current_bid, 2),
            "new": round(current_bid, 2),
            "change_amount": 0.00,
            "change_percent": 0.0,
            "tier": "none"
        }

    # Extract metrics
    momentum_2week = ad_group_metrics.get('momentum_2week', 0)
    trend_consistency = ad_group_metrics.get('trend_consistency', 'stable')
    rank = ad_group_metrics.get('rank', 50)

    # Determine tier and multiplier (raise_bid = increase, lower_bid = decrease)
    if action_type == "raise_bid":
        tier, multiplier = _determine_increase_tier(momentum_2week, trend_consistency, rank)
    elif action_type == "lower_bid":
        tier, multiplier = _determine_decrease_tier(momentum_2week, trend_consistency, rank)
    else:
        # Fallback
        return {
            "current": round(current_bid, 2),
            "new": round(current_bid, 2),
            "change_amount": 0.00,
            "change_percent": 0.0,
            "tier": "none"
        }

    # Calculate new bid
    new_bid = current_bid * multiplier
    change_amount = new_bid - current_bid
    change_percent = (multiplier - 1) * 100

    return {
        "current": round(current_bid, 2),
        "new": round(new_bid, 2),
        "change_amount": round(change_amount, 2),
        "change_percent": round(change_percent, 1),
        "tier": tier
    }


def _determine_increase_tier(momentum_2week, trend_consistency, rank):
    """
    Determines the tier (high/moderate/low) for budget/bid increases.

    HIGH (20%): Consistent strong growth
    MODERATE (10%): Good growth or improving trend
    LOW (5%): Mild growth or uncertain signals

    Returns:
        (tier_name, multiplier) e.g., ("high", 1.20)
    """

    # HIGH TIER (20%): Strong consistent improvement
    if trend_consistency == "consistent_improving" and momentum_2week >= 15:
        return ("high", 1.20)

    # HIGH TIER (20%): Top performer with good momentum
    if rank <= 10 and momentum_2week >= 10:
        return ("high", 1.20)

    # MODERATE TIER (10%): Consistent improvement with moderate momentum
    if trend_consistency == "consistent_improving" and momentum_2week >= 5:
        return ("moderate", 1.10)

    # MODERATE TIER (10%): Good momentum even if not perfectly consistent
    if momentum_2week >= 10:
        return ("moderate", 1.10)

    # LOW TIER (5%): Default for any increase action
    # (Mild positive signals, or volatile but improving)
    return ("low", 1.05)


def _determine_decrease_tier(momentum_2week, trend_consistency, rank):
    """
    Determines the tier (high/moderate/low) for budget/bid decreases.

    HIGH (20%): Consistent strong decline
    MODERATE (10%): Notable decline or poor ranking
    LOW (5%): Mild decline or uncertain signals

    Returns:
        (tier_name, multiplier) e.g., ("high", 0.80)
    """

    # HIGH TIER (-20%): Strong consistent decline
    if trend_consistency == "consistent_declining" and momentum_2week <= -15:
        return ("high", 0.80)

    # HIGH TIER (-20%): Bottom performer with negative momentum
    if rank >= 100 and momentum_2week <= -10:
        return ("high", 0.80)

    # MODERATE TIER (-10%): Consistent decline with moderate negative momentum
    if trend_consistency == "consistent_declining" and momentum_2week <= -5:
        return ("moderate", 0.90)

    # MODERATE TIER (-10%): Significant negative momentum
    if momentum_2week <= -10:
        return ("moderate", 0.90)

    # LOW TIER (-5%): Default for any decrease action
    # (Mild negative signals, or volatile but declining)
    return ("low", 0.95)
