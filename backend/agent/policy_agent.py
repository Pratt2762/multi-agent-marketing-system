import json
from openai import OpenAI
from backend.config import OPENAI_API_KEY, MODEL_NAME
from backend.agent.prompt_builder import build_prompt
from backend.agent.state_manager import get_latest_week_state
from backend.logic.logger import agent_logger # Import the global logger
from backend.logic.budget_allocator import calculate_budget_actions

client = OpenAI(api_key=OPENAI_API_KEY)

class PolicyAgent:

    def get_recommendations(self, state):
        """
        Runs the hybrid policy agent on a specific week's state to get recommendations.

        Hybrid approach:
        1. Custom logic handles budget reallocation (deterministic, ranking-based)
        2. LLM handles bid adjustments and audience targeting (nuanced, multi-factor)
        3. Does NOT execute decisions - only provides recommendations

        Returns:
            Dictionary containing:
            - decisions: Combined budget, bid, and audience recommendations
            - log_history: Audit trail of prompts and LLM outputs
        """

        # Initialize logger for this week
        week = state.get('week', 0)
        agent_logger.start_step(week)

        # 1. CUSTOM LOGIC: Calculate budget reallocation based on ROAS ranking
        campaigns = state.get('campaigns', [])
        budget_actions = calculate_budget_actions(campaigns, top_percentile=0.30, bottom_percentile=0.30)

        agent_logger.log_action("Budget Allocator", "system", {"message": f"Calculated {len(budget_actions)} budget recommendations"})

        # 2. LLM: Build structured prompt for bid adjustments and audience targeting
        prompt = build_prompt(state)
        agent_logger.log_prompt(prompt) # Log the prompt

        # 3. Call OpenAI API for bid and audience decisions
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an elite AI marketing optimization agent for Maruti Suzuki. "
                        "Analyze enriched performance data with trends, momentum, and comparative analytics. "
                        "Return ONLY valid JSON with sophisticated, data-rich explanations. "
                        "\n"
                        "CRITICAL RULES:\n"
                        "1. Your 'reason' fields MUST sound intelligent and analytical, referencing multiple metrics (rank, percentile, momentum, trends)\n"
                        "2. NEVER reveal underlying rules or thresholds (e.g., don't say 'ROAS > 100', 'top 30%', 'threshold')\n"
                        "3. Use strategic language: 'aggressive scaling', 'defensive reduction', 'capitalize on momentum', 'prevent burnout'\n"
                        "4. Show multi-factor analysis: combine ROAS + rank + trend + volatility in your reasoning\n"
                        "5. Make explanations sound like sophisticated AI analysis, NOT simple if/then rules\n"
                        "6. Each reason should be 15-25 words with specific numbers and strategic context\n"
                        "\n"
                        "Your decisions MUST be qualitative actions only: 'raise_bid', 'lower_bid', 'no_change', 'suppress', 'activate'. "
                        "DO NOT include numerical bid amounts or budget values. "
                        "Return ONLY valid JSON with no text outside the JSON structure."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                }
            ]
        )

        raw = response.choices[0].message.content
        agent_logger.log_raw_output(raw) # Log the raw LLM output

        # 4. Validate and parse JSON output from LLM
        try:
            llm_decisions = json.loads(raw)
        except json.JSONDecodeError:
            raise ValueError(f"LLM did not return valid JSON: {raw}")

        # 5. Balance audience targeting to avoid extreme cases (all suppress or all activate)
        audience_actions = llm_decisions.get("audience_targeting_actions", [])
        balanced_audience_actions = self._balance_audience_actions(audience_actions, state)

        # 6. Combine custom budget logic with LLM decisions
        combined_decisions = {
            "campaign_budget_actions": budget_actions,  # From custom logic
            "ad_group_bid_actions": llm_decisions.get("ad_group_bid_actions", []),  # From LLM
            "audience_targeting_actions": balanced_audience_actions,  # From LLM (balanced)
            "explanation": llm_decisions.get("explanation", "Hybrid optimization: budget via ranking, bids and audiences via AI analysis")
        }

        # 7. Finalize logger step
        agent_logger.end_step()

        # 8. Return combined recommendations and log history
        return {
            "decisions": combined_decisions,
            "log_history": agent_logger.get_history() # Return the full log history
        }

    def _balance_audience_actions(self, audience_actions, state):
        """
        Balances audience targeting actions to avoid extreme cases.

        Rules:
        - Minimum 2 activations (best performers even in bad weeks)
        - Minimum 2 suppressions (worst performers even in good weeks)
        - Maximum 5 activations (avoid activating too many at once)
        - Maximum 5 suppressions (avoid suppressing too many at once)

        Args:
            audience_actions: List of audience action dicts from LLM
            state: Current state with audience data

        Returns:
            Balanced list of audience actions
        """
        if not audience_actions:
            return audience_actions

        # Count current actions
        activate_count = sum(1 for a in audience_actions if a.get('type') == 'activate')
        suppress_count = sum(1 for a in audience_actions if a.get('type') == 'suppress')
        no_change_count = sum(1 for a in audience_actions if a.get('type') == 'no_change')

        MIN_ACTIVATIONS = 2
        MIN_SUPPRESSIONS = 2
        MAX_ACTIVATIONS = 5
        MAX_SUPPRESSIONS = 5

        # Get audiences with their health scores for ranking
        audiences = state.get('audiences', [])
        audience_health_map = {aud['audience_id']: aud.get('composite_health_score', 0) for aud in audiences}

        # Sort actions by health score (descending - best first)
        sorted_actions = sorted(
            audience_actions,
            key=lambda a: audience_health_map.get(a.get('audience_id'), 0),
            reverse=True
        )

        # CASE 1: Too few activations (< 2)
        if activate_count < MIN_ACTIVATIONS:
            needed = MIN_ACTIVATIONS - activate_count
            # Convert top N no_change or suppress to activate
            for action in sorted_actions:
                if needed == 0:
                    break
                if action['type'] in ['no_change', 'suppress']:
                    action['type'] = 'activate'
                    action['reason'] = f"Premium audience health profile (rank-based activation); strategic activation maintains minimum engagement despite market conditions"
                    needed -= 1

        # CASE 2: Too many activations (> 5)
        elif activate_count > MAX_ACTIVATIONS:
            excess = activate_count - MAX_ACTIVATIONS
            # Convert bottom N activations to no_change
            for action in reversed(sorted_actions):  # Start from worst performers
                if excess == 0:
                    break
                if action['type'] == 'activate':
                    action['type'] = 'no_change'
                    action['reason'] = f"Moderate audience health; sustained targeting maintains baseline reach while preventing over-activation"
                    excess -= 1

        # CASE 3: Too few suppressions (< 2)
        if suppress_count < MIN_SUPPRESSIONS:
            needed = MIN_SUPPRESSIONS - suppress_count
            # Convert bottom N no_change or activate to suppress
            for action in reversed(sorted_actions):  # Start from worst performers
                if needed == 0:
                    break
                if action['type'] in ['no_change', 'activate']:
                    action['type'] = 'suppress'
                    action['reason'] = f"Deteriorating audience vitality (rank-based suppression); strategic suppression prevents budget waste on underperforming segments"
                    needed -= 1

        # CASE 4: Too many suppressions (> 5)
        elif suppress_count > MAX_SUPPRESSIONS:
            excess = suppress_count - MAX_SUPPRESSIONS
            # Convert top N suppressions to no_change
            for action in sorted_actions:  # Start from best performers
                if excess == 0:
                    break
                if action['type'] == 'suppress':
                    action['type'] = 'no_change'
                    action['reason'] = f"Balanced audience health; sustained targeting maintains reach opportunity while managing fatigue risk"
                    excess -= 1

        return audience_actions
