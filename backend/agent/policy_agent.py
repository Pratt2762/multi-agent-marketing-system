import json
from openai import OpenAI
from backend.config import OPENAI_API_KEY, MODEL_NAME
from backend.agent.prompt_builder import build_prompt
from backend.agent.state_manager import get_latest_week_state
from backend.logic.executor import Executor # Import the new Executor

client = OpenAI(api_key=OPENAI_API_KEY)
executor = Executor() # Instantiate the executor

class PolicyAgent:

    def run(self, data):
        """
        Runs the LLM-based policy agent on the current system state.
        1. Gets qualitative decisions from LLM.
        2. Executes decisions deterministically via Python logic.
        3. Returns the new dataframes for the next week.
        """

        # 1. Construct full world-state (campaigns, ad groups, audiences)
        state = get_latest_week_state(data)

        # 2. Build structured prompt containing:
        #    - goals
        #    - constraints
        #    - expected JSON schema (qualitative decisions only)
        #    - state snapshot
        prompt = build_prompt(state)

        # 3. Call the latest OpenAI chat API (GPT-5.x / 4.1)
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an autonomous marketing optimization agent. "
                        "You analyze campaign, bid, and audience data and return ONLY valid JSON. "
                        "Your decisions MUST be qualitative (e.g., 'increase_budget', 'lower_bid'). "
                        "DO NOT include any numerical values for budgets or bids. "
                        "No explanations. No text outside JSON."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            temperature=0.0
        )

        raw = response.choices[0].message.content

        # 4. Strictly validate and parse JSON output (qualitative decisions)
        try:
            decisions = json.loads(raw)
        except json.JSONDecodeError:
            raise ValueError(f"LLM did not return valid JSON: {raw}")
        
        # 5. Execute qualitative decisions to get the next week's state (deterministic, numeric)
        next_week_data = executor.execute_decisions(data, decisions)
        
        # Return the new dataframes and the LLM's reasoning
        return {
            "decisions": decisions,
            "next_week_data": next_week_data
        }
