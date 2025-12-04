from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from agent.policy_agent import PolicyAgent
from logic.utils import load_all_data

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

agent = PolicyAgent()
data_cache = load_all_data()

@app.get("/run-agent")
def run_agent():
    """
    Executes the agent on current dataset.
    """
    global data_cache

    result = agent.run(data_cache)

    return result