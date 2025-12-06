import json
from openai import OpenAI
from backend.config import OPENAI_API_KEY, MODEL_NAME
from backend.agent.prompt_builder import build_prompt
from backend.agent.state_manager import get_latest_week_state
from backend.logic.logger import agent_logger # Import the global logger

client = OpenAI(api_key=OPENAI_API_KEY)

class PolicyAgent:

    def get_recommendations(self, state):
        """
        Runs the LLM-based policy agent on a specific week's state to get recommendations.
        1. Gets qualitative decisions (recommendations) from LLM based on the 'state'.
        2. Does NOT execute decisions.
        3. Returns the raw decisions and the log history.
        """

        # 1. The state is already constructed for the current week
        # state = get_latest_week_state(data) # No longer needed here

        # 2. Build structured prompt containing:
        #    - goals
        #    - constraints
        #    - expected JSON schema (qualitative decisions only)
        #    - state snapshot
        prompt = build_prompt(state)
        agent_logger.log_prompt(prompt) # Log the prompt

        # 3. Call the latest OpenAI chat API (GPT-5.x / 4.1)
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an autonomous marketing optimization agent. "
                        "You analyze campaign, bid, and audience data and return ONLY valid JSON. "
                        "Your decisions MUST be qualitative (e.g., 'raise_bid', 'lower_bid', 'suppress'). "
                        "For bid adjustments, strictly follow this rule: Raise bid for Ad Groups with ROAS > 100, Lower bid for Ad Groups with ROAS < 50. "
                        "DO NOT include any numerical values for budgets or bids. "
                        "No explanations. No text outside JSON."
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

        # 4. Strictly validate and parse JSON output (qualitative decisions)
        try:
            decisions = json.loads(raw)
        except json.JSONDecodeError:
            raise ValueError(f"LLM did not return valid JSON: {raw}")
        
        # 5. Return the raw decisions (recommendations) and log history
        # Budget reallocation decisions are kept as they are now part of the recommendation
        return {
            "decisions": decisions,
            "log_history": agent_logger.get_history() # Return the full log history
        }
