"""
Analytics Enrichment Module - Adds comparative and contextual analytics
to state data to enable intelligent, dynamic AI decision-making.
"""

import pandas as pd
import numpy as np


def enrich_state_with_analytics(state, all_weeks_data, current_week):
    """
    Enriches the current week's state with comparative analytics.

    Args:
        state: Current week's state dictionary
        all_weeks_data: Dictionary of all DataFrames (campaigns, ad_groups, audiences)
        current_week: Current week number

    Returns:
        Enriched state with analytics fields added
    """

    # Enrich campaigns
    state['campaigns'] = enrich_campaigns(
        state['campaigns'],
        all_weeks_data['campaigns'],
        current_week
    )

    # Enrich ad groups
    state['ad_groups'] = enrich_ad_groups(
        state['ad_groups'],
        all_weeks_data['ad_groups'],
        current_week
    )

    # Enrich audiences
    state['audiences'] = enrich_audiences(
        state['audiences'],
        all_weeks_data['audiences'],
        current_week
    )

    # Add portfolio-level analytics summary
    state['portfolio_analytics'] = generate_portfolio_summary(
        state['campaigns'],
        all_weeks_data['campaigns'],
        current_week
    )

    return state


def enrich_campaigns(campaigns, campaigns_df, current_week):
    """Enriches campaign data with comparative analytics."""

    # Get current week data
    current_week_df = campaigns_df[campaigns_df['week'] == current_week].copy()

    # Calculate rankings and percentiles
    current_week_df = current_week_df.sort_values('roas', ascending=False)
    total_campaigns = len(current_week_df)

    # Create enrichment map
    enrichment_map = {}

    # Reset index to get sequential ranking
    current_week_df = current_week_df.reset_index(drop=True)

    for idx, row in current_week_df.iterrows():
        campaign_id = row['campaign_id']
        rank = idx + 1
        percentile = int((1 - (rank - 1) / total_campaigns) * 100)

        # Calculate trend (if previous weeks exist)
        trend_data = calculate_trend(
            campaigns_df,
            campaign_id,
            current_week,
            metric='roas'
        )

        # Calculate distance from mean
        mean_roas = current_week_df['roas'].mean()
        distance_from_mean = row['roas'] - mean_roas

        # Calculate category rank (by channel + model_line)
        category_df = current_week_df[
            (current_week_df['channel'] == row['channel']) &
            (current_week_df['model_line'] == row['model_line'])
        ].sort_values('roas', ascending=False)
        category_rank = (category_df['campaign_id'] == campaign_id).idxmax() + 1 if len(category_df) > 0 else 1

        # Calculate weeks above median
        historical_data = campaigns_df[campaigns_df['campaign_id'] == campaign_id]
        median_roas = campaigns_df[campaigns_df['week'] == current_week]['roas'].median()
        weeks_above_median = len(historical_data[historical_data['roas'] > median_roas])

        enrichment_map[campaign_id] = {
            'rank': rank,
            'percentile': percentile,
            'trend_direction': trend_data['direction'],
            'momentum': trend_data['momentum'],  # 1-week momentum
            'momentum_3week': trend_data['momentum_3week'],  # 3-week momentum
            'avg_roas_3week': trend_data['avg_3week'],  # 3-week rolling average
            'trend_consistency': trend_data['trend_consistency'],  # Trend stability
            'weeks_above_median': weeks_above_median,
            'distance_from_mean': round(distance_from_mean, 2),
            'category_rank': category_rank,
            'volatility': trend_data['volatility']
        }

    # Apply enrichment to campaigns list
    enriched_campaigns = []
    for campaign in campaigns:
        campaign_id = campaign['campaign_id']
        if campaign_id in enrichment_map:
            campaign.update(enrichment_map[campaign_id])
        enriched_campaigns.append(campaign)

    return enriched_campaigns


def enrich_ad_groups(ad_groups, ad_groups_df, current_week):
    """Enriches ad group data with comparative analytics."""

    # Get current week data
    current_week_df = ad_groups_df[ad_groups_df['week'] == current_week].copy()

    # Calculate rankings by ROAS
    current_week_df = current_week_df.sort_values('roas', ascending=False).reset_index(drop=True)
    total_ad_groups = len(current_week_df)

    enrichment_map = {}

    for idx, row in current_week_df.iterrows():
        ad_group_id = row['ad_group_id']
        rank = idx + 1
        percentile = int((1 - (rank - 1) / total_ad_groups) * 100)

        # Calculate trend
        trend_data = calculate_trend(
            ad_groups_df,
            ad_group_id,
            current_week,
            metric='roas',
            id_column='ad_group_id'
        )

        # Distance from mean
        mean_roas = current_week_df['roas'].mean()
        distance_from_mean = row['roas'] - mean_roas

        enrichment_map[ad_group_id] = {
            'rank': rank,
            'percentile': percentile,
            'trend_direction': trend_data['direction'],
            'momentum': trend_data['momentum'],  # 1-week momentum
            'momentum_3week': trend_data['momentum_3week'],  # 3-week momentum
            'avg_roas_3week': trend_data['avg_3week'],  # 3-week rolling average
            'trend_consistency': trend_data['trend_consistency'],  # Trend stability
            'distance_from_mean': round(distance_from_mean, 2),
            'volatility': trend_data['volatility']
        }

    # Apply enrichment
    enriched_ad_groups = []
    for ad_group in ad_groups:
        ad_group_id = ad_group['ad_group_id']
        if ad_group_id in enrichment_map:
            ad_group.update(enrichment_map[ad_group_id])
        enriched_ad_groups.append(ad_group)

    return enriched_ad_groups


def enrich_audiences(audiences, audiences_df, current_week):
    """Enriches audience data with composite health scores and rankings."""

    # Get current week data
    current_week_df = audiences_df[audiences_df['week'] == current_week].copy()

    # Calculate composite health score for each audience
    current_week_df['composite_health_score'] = (
        (current_week_df['intent_score'] * 2) +
        (current_week_df['avg_ctr'] * 1000) +
        (current_week_df['avg_cvr'] * 500) -
        (current_week_df['fatigue_score'] * 1.5) -
        (current_week_df['frequency'] * 2)
    )

    # Sort by health score
    current_week_df = current_week_df.sort_values('composite_health_score', ascending=False).reset_index(drop=True)
    total_audiences = len(current_week_df)

    enrichment_map = {}

    for idx, row in current_week_df.iterrows():
        audience_id = row['audience_id']
        rank = idx + 1
        percentile = int((1 - (rank - 1) / total_audiences) * 100)

        # Calculate CTR/CVR trends
        ctr_trend = calculate_trend(
            audiences_df,
            audience_id,
            current_week,
            metric='avg_ctr',
            id_column='audience_id'
        )

        fatigue_trend = calculate_trend(
            audiences_df,
            audience_id,
            current_week,
            metric='fatigue_score',
            id_column='audience_id'
        )

        # Determine optimal action based on relative ranking
        if rank <= total_audiences * 0.30:
            optimal_action = 'activate'
        elif rank >= total_audiences * 0.70:
            optimal_action = 'suppress'
        else:
            optimal_action = 'no_change'

        enrichment_map[audience_id] = {
            'composite_health_score': round(row['composite_health_score'], 2),
            'health_rank': rank,
            'health_percentile': percentile,
            'engagement_trend': ctr_trend['direction'],
            'fatigue_trend': fatigue_trend['direction'],
            'optimal_action': optimal_action
        }

    # Apply enrichment
    enriched_audiences = []
    for audience in audiences:
        audience_id = audience['audience_id']
        if audience_id in enrichment_map:
            audience.update(enrichment_map[audience_id])
        enriched_audiences.append(audience)

    return enriched_audiences


def calculate_trend(df, entity_id, current_week, metric='roas', id_column='campaign_id'):
    """
    Calculates trend direction and momentum for a given entity.
    Now includes both 1-week and 3-week analysis for more stable insights.

    Returns:
        Dictionary with 'direction', 'momentum', 'momentum_3week', 'avg_3week',
        'volatility', and 'trend_consistency'
    """

    # Get historical data up to current week
    entity_data = df[
        (df[id_column] == entity_id) &
        (df['week'] <= current_week)
    ].sort_values('week')

    if len(entity_data) < 2:
        return {
            'direction': 'stable',
            'momentum': 0.0,
            'momentum_3week': 0.0,
            'avg_3week': entity_data[metric].iloc[0] if len(entity_data) == 1 else 0.0,
            'volatility': 0.0,
            'trend_consistency': 'insufficient_data'
        }

    # 1-WEEK MOMENTUM: Compare current week vs previous week
    recent_values = entity_data[metric].tail(2).values
    momentum_1week = 0.0

    if len(recent_values) == 2 and recent_values[0] != 0:
        momentum_1week = ((recent_values[1] - recent_values[0]) / abs(recent_values[0])) * 100

    # 3-WEEK MOMENTUM: Compare current week vs 3 weeks ago (if available)
    momentum_3week = 0.0
    avg_3week = 0.0
    trend_consistency = 'stable'

    if len(entity_data) >= 3:
        # Get last 3 weeks of data
        last_3_weeks = entity_data[metric].tail(3).values
        avg_3week = np.mean(last_3_weeks)

        # 3-week momentum: current vs 3 weeks ago
        if last_3_weeks[0] != 0:
            momentum_3week = ((last_3_weeks[2] - last_3_weeks[0]) / abs(last_3_weeks[0])) * 100

        # Trend consistency: Are all 3 weeks moving in the same direction?
        week1_to_2 = last_3_weeks[1] - last_3_weeks[0]
        week2_to_3 = last_3_weeks[2] - last_3_weeks[1]

        if week1_to_2 > 0 and week2_to_3 > 0:
            trend_consistency = 'consistent_improving'
        elif week1_to_2 < 0 and week2_to_3 < 0:
            trend_consistency = 'consistent_declining'
        else:
            trend_consistency = 'volatile'
    elif len(entity_data) == 2:
        # Only 2 weeks available - use those 2 for average
        avg_3week = np.mean(entity_data[metric].tail(2).values)
        momentum_3week = momentum_1week  # Fallback to 1-week
        trend_consistency = 'limited_data'
    else:
        avg_3week = entity_data[metric].iloc[0]
        trend_consistency = 'insufficient_data'

    # Determine overall direction based on 3-week momentum (more stable)
    if len(entity_data) >= 3:
        # Use 3-week momentum for direction if we have enough data
        if momentum_3week > 5:
            direction = 'improving'
        elif momentum_3week < -5:
            direction = 'declining'
        else:
            direction = 'stable'
    else:
        # Fallback to 1-week momentum
        if momentum_1week > 5:
            direction = 'improving'
        elif momentum_1week < -5:
            direction = 'declining'
        else:
            direction = 'stable'

    # Calculate volatility (standard deviation of last 3 weeks if available)
    if len(entity_data) >= 3:
        volatility = np.std(entity_data[metric].tail(3).values)
    else:
        volatility = entity_data[metric].std() if len(entity_data) >= 2 else 0.0

    return {
        'direction': direction,
        'momentum': round(momentum_1week, 2),  # 1-week momentum
        'momentum_3week': round(momentum_3week, 2),  # 3-week momentum
        'avg_3week': round(avg_3week, 2),  # Rolling 3-week average
        'volatility': round(volatility, 2),
        'trend_consistency': trend_consistency
    }


def generate_portfolio_summary(campaigns, campaigns_df, current_week):
    """
    Generates portfolio-level analytics summary.

    Args:
        campaigns: Enriched campaigns list for current week
        campaigns_df: Full campaigns DataFrame
        current_week: Current week number

    Returns:
        Dictionary with portfolio analytics
    """

    # Current week statistics
    current_week_df = campaigns_df[campaigns_df['week'] == current_week]

    roas_values = current_week_df['roas'].values
    mean_roas = np.mean(roas_values)
    median_roas = np.median(roas_values)
    std_roas = np.std(roas_values)

    # Find top and bottom movers
    movers = []
    for campaign in campaigns:
        if campaign.get('momentum', 0) != 0:
            movers.append({
                'campaign_id': campaign['campaign_id'],
                'campaign_name': campaign['campaign_name'],
                'change': campaign['momentum'],
                'current_roas': campaign['roas']
            })

    # Sort by absolute momentum
    movers.sort(key=lambda x: abs(x['change']), reverse=True)

    top_movers = [m for m in movers if m['change'] > 0][:3]
    bottom_movers = [m for m in movers if m['change'] < 0][:3]

    # Count improving vs declining
    improving_count = sum(1 for c in campaigns if c.get('trend_direction') == 'improving')
    declining_count = sum(1 for c in campaigns if c.get('trend_direction') == 'declining')
    stable_count = sum(1 for c in campaigns if c.get('trend_direction') == 'stable')

    return {
        'total_campaigns': len(campaigns),
        'week': current_week,
        'roas_mean': round(mean_roas, 2),
        'roas_median': round(median_roas, 2),
        'roas_std': round(std_roas, 2),
        'top_movers': top_movers,
        'bottom_movers': bottom_movers,
        'efficiency_improving': improving_count,
        'efficiency_declining': declining_count,
        'efficiency_stable': stable_count
    }
