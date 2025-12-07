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

        # 5. Combine custom budget logic with LLM decisions
        combined_decisions = {
            "campaign_budget_actions": budget_actions,  # From custom logic
            "ad_group_bid_actions": llm_decisions.get("ad_group_bid_actions", []),  # From LLM
            "audience_targeting_actions": llm_decisions.get("audience_targeting_actions", []),  # From LLM
            "explanation": llm_decisions.get("explanation", "Hybrid optimization: budget via ranking, bids and audiences via AI analysis")
        }

        # 6. Finalize logger step
        agent_logger.end_step()

        # 7. Return combined recommendations and log history
        return {
            "decisions": combined_decisions,
            "log_history": agent_logger.get_history() # Return the full log history
        }
