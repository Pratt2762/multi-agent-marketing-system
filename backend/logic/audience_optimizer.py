"""
Audience Targeting Logic - Deterministic audience optimization
based on relative fatigue and intent scores.
"""

def calculate_audience_actions(audiences, suppress_percentile=0.30, activate_percentile=0.30):
    """
    Calculates audience targeting recommendations based on relative performance.

    Strategy:
    - High fatigue + low engagement → suppress (top 30% most fatigued)
    - High intent + low fatigue + good engagement → activate (top 30% best performers)
    - Middle tier → no_change

    Args:
        audiences: List of audience dictionaries with 'audience_id', 'fatigue_score', 'intent_score', etc.
        suppress_percentile: Percentage of worst performers to suppress (default 30%)
        activate_percentile: Percentage of best performers to activate (default 30%)

    Returns:
        List of audience action dictionaries with audience_id, type, and reason
    """

    if not audiences or len(audiences) == 0:
        return []

    # Calculate composite health score for each audience
    # Higher score = healthier audience
    # Score = (intent_score * 2) - fatigue_score + (avg_ctr * 1000) + (avg_cvr * 1000)
    for audience in audiences:
        intent = audience.get('intent_score', 0)
        fatigue = audience.get('fatigue_score', 0)
        ctr = audience.get('avg_ctr', 0)
        cvr = audience.get('avg_cvr', 0)

        # Composite health score (higher is better)
        health_score = (intent * 2) - fatigue + (ctr * 1000) + (cvr * 1000)
        audience['health_score'] = health_score

    # Sort by health score (descending - healthiest first)
    audiences_sorted = sorted(audiences, key=lambda x: x.get('health_score', 0), reverse=True)

    total_audiences = len(audiences_sorted)
    activate_threshold_index = int(total_audiences * activate_percentile)
    suppress_threshold_index = int(total_audiences * (1 - suppress_percentile))

    audience_actions = []

    for i, audience in enumerate(audiences_sorted):
        audience_id = audience.get('audience_id')
        audience_name = audience.get('audience_name', 'Unknown')
        fatigue = audience.get('fatigue_score', 0)
        intent = audience.get('intent_score', 0)
        ctr = audience.get('avg_ctr', 0)
        cvr = audience.get('avg_cvr', 0)
        health_score = audience.get('health_score', 0)
        rank = i + 1

        # Determine action based on health ranking
        if i < activate_threshold_index:
            # Top performers - healthy audiences
            action_type = "activate"
            reason = f"High health score ({health_score:.1f}): Intent {intent}, Fatigue {fatigue:.1f}, CTR {ctr:.2%} - Top {int(activate_percentile*100)}% performer"
        elif i >= suppress_threshold_index:
            # Bottom performers - unhealthy audiences
            action_type = "suppress"
            reason = f"Low health score ({health_score:.1f}): Intent {intent}, Fatigue {fatigue:.1f}, CTR {ctr:.2%} - Bottom {int(suppress_percentile*100)}% performer"
        else:
            # Middle tier
            action_type = "no_change"
            reason = f"Moderate health score ({health_score:.1f}): Intent {intent}, Fatigue {fatigue:.1f} - Average performer"

        audience_actions.append({
            "audience_id": audience_id,
            "audience_name": audience_name,
            "type": action_type,
            "reason": reason,
            "health_score": round(health_score, 2),
            "rank": rank
        })

    return audience_actions


def get_audience_summary(audience_actions):
    """
    Generates a summary of audience targeting decisions.

    Args:
        audience_actions: List of audience action dictionaries

    Returns:
        Dictionary with summary statistics
    """
    activate_count = sum(1 for action in audience_actions if action['type'] == 'activate')
    suppress_count = sum(1 for action in audience_actions if action['type'] == 'suppress')
    no_change_count = sum(1 for action in audience_actions if action['type'] == 'no_change')

    return {
        "total_audiences": len(audience_actions),
        "activate_count": activate_count,
        "suppress_count": suppress_count,
        "no_change_count": no_change_count
    }
