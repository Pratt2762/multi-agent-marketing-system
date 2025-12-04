from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.agent.policy_agent import PolicyAgent
from backend.logic.utils import load_all_data, append_next_week_data

app = FastAPI()

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instantiate agent + load data once on startup
agent = PolicyAgent()

# IMPORTANT:
# load_all_data() must now load ONLY:
#   campaigns.csv
#   ad_groups.csv
#   audiences.csv
data_cache = load_all_data()


@app.get("/run-agent")
def run_agent():
    """
    Executes the agent on the current datasets.
    The output includes:
        - budget reallocations
        - bid adjustments
        - audience suppression/expansion
        - agentic reasoning trace
    """
    global data_cache

    try:
        # 1. Run agent to get qualitative decisions and next week's dataframes
        agent_output = agent.run(data_cache)
        
        # 2. Append new dataframes to CSVs
        next_week = append_next_week_data(agent_output["next_week_data"])
        
        # 3. Reload data cache to include the new week for the next run
        data_cache = load_all_data()

        return {
            "status": "success",
            "message": f"Agent executed successfully. Data updated for Week {next_week}",
            "decisions": agent_output["decisions"],
            "next_week": next_week
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
