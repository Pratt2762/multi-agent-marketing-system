def build_prompt(state):
    return f"""
You are an autonomous marketing optimization agent for Maruti Suzuki.

Your goals:
1. Dynamic budget reallocation
2. Automated bid adjustments
3. Audience targeting refinement

Inputs:
- Campaign performance (ROAS, CPC, conversions, cost, reach)
- Audience stats (CTR, fatigue score, engagement)
- Current budget + bids
- Constraints: keep total budget constant; no campaign can exceed ±30% change unless ROAS < 0.8 or > 3.0.

State (JSON):
{state}

Produce output strictly in this JSON format:

{{
  "campaign_budget_actions": [
    {{
      "campaign_id": 0,
      "type": "increase_budget | decrease_budget | no_change",
      "confidence": 0.0,
      "reason": "Short explanation for the action"
    }}
  ],
  "ad_group_bid_actions": [
    {{
      "ad_group_id": 0,
      "type": "raise_bid | lower_bid | no_change",
      "reason": "Short explanation for the action"
    }}
  ],
  "audience_targeting_actions": [
    {{
      "audience_id": 0,
      "type": "suppress | activate | no_change",
      "reason": "Short explanation for the action"
    }}
  ],
  "explanation": "Short human-readable explanation of the overall strategy"
}}
"""