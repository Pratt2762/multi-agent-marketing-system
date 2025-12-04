import json
from openai import OpenAI
from config import OPENAI_API_KEY, MODEL_NAME
from agent.prompt_builder import build_prompt
from agent.state_manager import construct_state

client = OpenAI(api_key=OPENAI_API_KEY)

class PolicyAgent:

    def run(self, data):
        state = construct_state(data)
        prompt = build_prompt(state)

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0
        )

        raw = response.choices[0].message["content"]

        try:
            return json.loads(raw)
        except:
            return {"error": "LLM did not return valid JSON", "raw": raw}