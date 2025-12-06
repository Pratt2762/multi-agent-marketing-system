def build_prompt(state):
    # The Executor now enforces budget neutrality, so we remove the calculation and strict constraint from the prompt.
    
    return f"""
You are an autonomous marketing optimization agent for Maruti Suzuki.

Your goals:
1. Dynamic budget reallocation (Handled deterministically by Executor based on ROAS ranking)
2. Automated bid adjustments (Raise bid for Ad Groups with ROAS > 100, Lower bid for Ad Groups with ROAS < 50)
3. Audience targeting refinement

Inputs:
- Campaign performance (ROAS, CPC, conversions, cost, reach)
- Audience stats (CTR, fatigue score, engagement)
- Current budget + bids
- Constraints: No single campaign can exceed ±30% change unless ROAS < 0.8 or > 3.0. For bid adjustments, strictly follow the ROAS thresholds in the goal above.

State (JSON):
{state}

Produce output strictly in this JSON format:

{{
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