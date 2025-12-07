def build_prompt(state):
    """
    Builds the LLM prompt for bid adjustments and audience targeting.
    Note: Budget reallocation is handled by custom logic, not by the LLM.

    The prompt now leverages enriched analytics including trends, rankings,
    momentum, and portfolio-level insights for intelligent decision-making.
    """

    # Extract portfolio summary for context
    portfolio = state.get('portfolio_analytics', {})

    portfolio_summary = f"""
PORTFOLIO OVERVIEW (Week {portfolio.get('week', 'N/A')}):
- Total Campaigns: {portfolio.get('total_campaigns', 0)}
- Average ROAS: {portfolio.get('roas_mean', 0)} (Median: {portfolio.get('roas_median', 0)})
- Campaigns Improving: {portfolio.get('efficiency_improving', 0)}
- Campaigns Declining: {portfolio.get('efficiency_declining', 0)}
- Campaigns Stable: {portfolio.get('efficiency_stable', 0)}

TOP MOVERS THIS WEEK:
{format_movers(portfolio.get('top_movers', []))}

BOTTOM MOVERS THIS WEEK:
{format_movers(portfolio.get('bottom_movers', []))}
"""

    return f"""
You are an autonomous marketing optimization agent for Maruti Suzuki.

Your goals:
1. Automated bid adjustments for ad groups based on performance, trends, and momentum
2. Audience targeting refinement to optimize engagement and reduce fatigue

{portfolio_summary}

=== ENRICHED DATA FIELDS EXPLAINED ===

Each Campaign/Ad Group now includes:
- rank: Relative ranking among all entities (1 = best)
- percentile: Performance percentile (higher = better)
- trend_direction: "improving", "declining", or "stable" (based on 3-week analysis)
- momentum: 1-week percentage change (e.g., +15.5 means 15.5% improvement week-over-week)
- momentum_3week: 3-week percentage change (current vs 3 weeks ago - more stable signal)
- avg_roas_3week: Rolling 3-week average ROAS (smoothed performance indicator)
- trend_consistency: "consistent_improving", "consistent_declining", or "volatile" (direction stability over 3 weeks)
- distance_from_mean: How far above/below average performance
- volatility: Performance stability over last 3 weeks (lower = more consistent)

Each Audience includes:
- composite_health_score: Pre-calculated health metric
- health_rank: Ranking by health (1 = healthiest)
- health_percentile: Percentile by health
- engagement_trend: CTR/CVR trend direction
- fatigue_trend: Fatigue score trend direction
- optimal_action: Suggested action based on relative ranking

=== INTELLIGENT BID ADJUSTMENT GUIDELINES ===

CRITICAL: Don't just look at absolute ROAS thresholds. Consider CONTEXT:

1. MOMENTUM-BASED DECISIONS (Use 3-week momentum for more stable insights):
   - Strong 3-week positive momentum (+10% or more) → Raise bid even if current ROAS is mid-range
   - Strong 3-week negative momentum (-10% or more) → Lower bid even if historical ROAS was good
   - Consistent improving trend (trend_consistency = "consistent_improving") → Be aggressive
   - Volatile performance (trend_consistency = "volatile") → Be cautious, prefer no_change until stable
   - Use 1-week momentum to detect recent inflection points, but prioritize 3-week signals

2. RELATIVE PERFORMANCE:
   - Top 30% by rank → Prioritize for bid increases
   - Bottom 30% by rank → Consider bid decreases
   - Trending up rapidly → Aggressive bid increases to capitalize on momentum
   - Trending down rapidly → Defensive bid decreases to limit losses

3. CONTEXTUAL FACTORS (Use 3-week averages for stability):
   - High avg_roas_3week + consistent_improving → RAISE (scaling winner with sustained performance)
   - High avg_roas_3week + consistent_declining → NO_CHANGE (monitor closely, may be temporary)
   - Low avg_roas_3week + consistent_improving → NO_CHANGE (give time to develop, positive trajectory)
   - Low avg_roas_3week + consistent_declining → LOWER (cut losses, confirmed poor performance)
   - Mid avg_roas_3week + strong 3-week momentum → Follow the trend direction
   - Volatile trend_consistency → Prefer NO_CHANGE until pattern stabilizes over 3+ weeks

4. PORTFOLIO AWARENESS:
   - If most campaigns are improving, be more aggressive with top performers
   - If most campaigns are declining, be more defensive overall
   - Top movers deserve special attention and resource allocation

5. EXPLANATION QUALITY - CRITICAL FOR BID ADJUSTMENTS:
   Your reasons MUST be written as NATURAL, FLUENT SENTENCES that sound like sophisticated AI analysis.
   NEVER output metric names directly (no "avg_roas_3week:", "momentum_3week:", "trend_consistency:").
   Instead, WEAVE the data into coherent, professional narrative.

   ❌ BAD - Metric dump format:
   - "avg_roas_3week 35.16 with momentum_3week 21.18 and consistent_improving trend_consistency; rank 1379, recent uplift; capitalize on momentum with aggressive scaling."
   - "ROAS > 100, raise bid"
   - "rank 1376, elevated volatility, defensive reduction preserves efficiency"

   ❌ BAD - Too simple:
   - "High ROAS, raise bid"
   - "Strong performance, increase"
   - "Low ROAS, decrease"

   ✅ GOOD - Natural, sophisticated narrative that integrates metrics smoothly:
   - "This ad group demonstrates exceptional efficiency with a 3-week average ROAS of 138.2, currently ranking #4 and showing sustained upward momentum of +18.3% over the period. The consistent improving trend justifies aggressive bid scaling to capitalize on this premium performance tier."

   - "Underperforming with a 3-week average ROAS of 31.5 (rank #89), this ad group exhibits persistent decline of -14.2% alongside high volatility. A defensive bid reduction is warranted to preserve capital and limit exposure to continued deterioration."

   - "Positioned in the mid-tier with a 3-week average ROAS of 74.1 (rank #45), this ad group shows promising sustained momentum of +12.8%, improving from 65.3 to 74.1. A moderate bid increase capitalizes on this confirmed uptrend while managing risk appropriately."

   KEY PRINCIPLES:
   - Write in COMPLETE, FLUENT SENTENCES (not fragmented phrases with semicolons)
   - Integrate metrics naturally: "with a 3-week average of X" instead of "avg_roas_3week: X"
   - Describe trends conversationally: "showing sustained momentum of +18%" instead of "momentum_3week: +18"
   - Use professional business language: "demonstrates", "exhibits", "warrants", "justifies"
   - Build logical flow: observation → evidence → conclusion/recommendation
   - Reference 3-week metrics for credibility but write like a human analyst
   - Never use colons, semicolons, or raw metric field names
   - Make it sound like an executive recommendation, not a data readout

=== INTELLIGENT AUDIENCE TARGETING GUIDELINES ===

The system has PRE-CALCULATED optimal_action for each audience based on:
- Composite health score ranking
- Relative performance vs peers
- Statistical distribution (top 30% activate, bottom 30% suppress)

YOUR TASK:
1. USE the optimal_action as your PRIMARY guide
2. REFINE based on trends:
   - If optimal_action = "activate" BUT fatigue_trend = "declining" (worsening) → Consider no_change
   - If optimal_action = "suppress" BUT engagement_trend = "improving" → Consider no_change
   - If optimal_action = "no_change" AND engagement_trend = "improving" → Consider activate
   - If optimal_action = "no_change" AND engagement_trend = "declining" → Consider suppress

3. ALWAYS maintain a DISTRIBUTION:
   - ~30% activate
   - ~40% no_change
   - ~30% suppress

4. EXPLANATION QUALITY FOR AUDIENCES - CRITICAL:
   Your reasons MUST be written as NATURAL, FLUENT SENTENCES like professional audience analysis.
   NEVER reveal distribution rules, thresholds, or use fragmented phrases with semicolons.

   ❌ BAD - Reveals rules or uses metric dump format:
   - "Top 30% by health score - activate"
   - "Bottom 30% performer - suppress"
   - "Composite score > X, activate"
   - "Premium health profile (composite 87.5, rank #2) exhibiting engagement momentum (+8.2% CTR lift); strategic activation maximizes reach"

   ❌ BAD - Too generic or fragmented:
   - "Good health, activate"
   - "High fatigue, suppress"
   - "Average performance, no change"

   ✅ GOOD - Natural, sophisticated narrative integrating multiple dimensions:
   - "This audience segment exhibits a premium health profile with a composite score of 87.5, ranking #2 overall while demonstrating strong engagement momentum with an 8.2% CTR lift and improving conversion trajectory. Despite moderate fatigue levels of 34.1, strategic activation maximizes high-quality reach and capitalizes on the strong positive signals across multiple engagement metrics."

   - "This audience shows deteriorating vitality with a health rank of #8 and a significant 12.4% decline in engagement rates. Fatigue accumulation is accelerating from 41.2 to 48.7, coupled with declining conversion efficiency. Suppression is warranted to prevent inefficient inventory spend and avoid audience burnout that could damage long-term brand perception."

   - "This audience maintains a balanced health position at rank #6 with a composite score of 72.3, sustaining stable engagement levels with a 2.8% CTR and 4.2% CVR. While frequency has escalated from 5.2 to 7.8 exposures, current targeting levels should be maintained with close monitoring for saturation signals that may indicate the need for future adjustment."

   KEY PRINCIPLES FOR AUDIENCES:
   - Write COMPLETE, FLUENT SENTENCES (not fragmented semicolon phrases)
   - Integrate metrics naturally into narrative flow
   - Reference multiple dimensions: health scores, engagement trends, fatigue dynamics, conversion patterns
   - Build logical progression: observation → evidence → strategic recommendation
   - Use professional analytical language: "exhibits", "demonstrates", "warrants", "indicates"
   - Never use semicolons, colons, or raw metric names as labels
   - Make it sound like executive audience analysis, not a data readout

=== CURRENT STATE DATA ===

{state}

=== OUTPUT FORMAT ===

Produce output strictly in this JSON format (valid JSON only, no explanations outside):

CRITICAL: You MUST provide recommendations for EVERY SINGLE ad group and audience in the current state.
- For ad groups: Return exactly one action for EACH ad_group_id in the state (all {len(state.get('ad_groups', []))} ad groups)
- For audiences: Return exactly one action for EACH audience_id in the state (all {len(state.get('audiences', []))} audiences)
- DO NOT skip any entities - even if action is "no_change", you must include it

CRITICAL REQUIREMENTS FOR "reason" FIELDS:
- MUST be written as COMPLETE, NATURAL SENTENCES (like an executive summary)
- NEVER use raw metric names (no "avg_roas_3week:", "momentum_3week:", "trend_consistency:")
- INTEGRATE data naturally: "with a 3-week average ROAS of X" not "avg_roas_3week X"
- Include relevant metrics: 3-week averages, momentum percentages, ranking, trend direction
- Use professional analytical language: "demonstrates", "exhibits", "indicates", "warrants"
- Build coherent narrative: observation → evidence → strategic recommendation
- Length: 20-40 words per reason (one or two complete sentences)

CRITICAL REQUIREMENTS FOR "explanation" FIELD:
- MUST summarize the week's strategic direction
- MUST reference portfolio metrics (how many improving vs declining)
- MUST mention top movers or key insights
- MUST explain the overall optimization philosophy for the week
- Length: 2-3 sentences, analytical and strategic tone

{{
  "ad_group_bid_actions": [
    {{
      "ad_group_id": 0,
      "type": "raise_bid | lower_bid | no_change",
      "reason": "EXAMPLE: This ad group demonstrates strong efficiency with a 3-week average ROAS of 85.3 and sustained upward momentum of +12.4%, currently ranking in the top quartile. The consistent improving trend warrants a moderate bid increase to capitalize on this performance trajectory."
    }}
  ],
  "audience_targeting_actions": [
    {{
      "audience_id": "AUD1",
      "type": "suppress | activate | no_change",
      "reason": "EXAMPLE: This audience exhibits premium engagement vitality with strong CTR performance (rank #3) and improving conversion trends, offsetting moderate frequency levels. Strategic activation maximizes high-quality reach while maintaining audience health."
    }}
  ],
  "explanation": "EXAMPLE: Week 8 reflects a balanced optimization strategy across a portfolio showing moderate improvement, with 12 campaigns trending upward and 8 declining. Bid adjustments capitalize on sustained 3-week momentum patterns while defensive reductions limit exposure to persistent underperformers, emphasizing data-driven capital reallocation toward proven efficiency."
}}
"""


def format_movers(movers_list):
    """Formats top/bottom movers for the prompt."""
    if not movers_list:
        return "  None"

    formatted = []
    for mover in movers_list:
        formatted.append(
            f"  - {mover['campaign_name']} (ID: {mover['campaign_id']}): "
            f"{mover['change']:+.1f}% change, Current ROAS: {mover['current_roas']:.2f}"
        )
    return "\n".join(formatted)