import json
import pandas as pd
import os
import numpy as np # Import numpy for type checking
from backend.agent.policy_agent import PolicyAgent
from backend.logic.logger import agent_logger
from backend.agent.state_manager import get_latest_week_state, get_state_for_week

# --- Configuration ---
DATA_FILES = {
    "campaigns": "backend/data/campaigns.csv",
    "ad_groups": "backend/data/ad_groups.csv",
    "audiences": "backend/data/audiences.csv"
}
OUTPUT_FILE = "frontend/results.json"

def load_data():
    """Loads all CSV data into a dictionary of DataFrames."""
    data = {}
    for key, path in DATA_FILES.items():
        try:
            # Read all data, not just the latest week, as agent.run() handles filtering
            data[key] = pd.read_csv(path)
        except FileNotFoundError:
            print(f"Error: Data file not found at {path}")
            data[key] = pd.DataFrame()
    return data

class NumpyEncoder(json.JSONEncoder):
    """Custom encoder for numpy data types."""
    def default(self, obj):
        if isinstance(obj, (np.integer, np.floating, np.bool_)):
            return obj.item()
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NumpyEncoder, self).default(obj)

def run_agent_and_save_results():
    """Runs the agent and saves the structured output to a JSON file."""
    print("--- Starting Agent Run for Visualization ---")
    
    # 1. Load data
    data = load_data()
    
    # 2. Run the 12-week simulation
    agent = PolicyAgent()
    try:
        max_week = data["campaigns"]["week"].max()
        campaign_history = []
        
        # The initial state is the performance data for week 1
        # The loop runs from week 1 up to the max_week (12)
        for week in range(1, max_week + 1):
            # a. Get the performance state for the current week
            current_week_state = get_state_for_week(data, week)
            
            # b. Run the agent's single step logic to get recommendations
            # We pass None for data_for_execution as no execution is performed
            results = agent.get_recommendations(current_week_state)
            
            # c. Collect the historical snapshot of the state and recommendations
            history_entry = {
                "week": week,
                "state_snapshot": current_week_state,
                "recommendations": results["decisions"],
                "log_history": results["log_history"]
            }
            campaign_history.append(history_entry)
            
            # d. IMPORTANT: Do NOT update the main dataframes with optimized data.
            # The simulation is now recommendation-only.

        # 3. Get the final state for context (the last week's performance)
        final_week_state = get_state_for_week(data, max_week)
        
        # The final recommendations are the ones generated in the last loop iteration
        final_recommendations = results["decisions"]

        # 4. Prepare final output structure
        final_output = {
            "latest_week": max_week,
            "campaign_history": campaign_history,
            "final_state_snapshot": final_week_state,
            "final_recommendations": final_recommendations,
        }

        # 5. Save to JSON file for frontend visualization
        try:
            os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
            with open(OUTPUT_FILE, 'w') as f:
                # Use the custom encoder to handle numpy/pandas types
                json.dump(final_output, f, indent=4, cls=NumpyEncoder)
            print(f"--- Agent Run Complete. Recommendations saved to {OUTPUT_FILE} ---")
        except Exception as e:
            print(f"Error saving results to JSON: {e}")
            
    except Exception as e:
        import traceback
        print(f"An error occurred during agent run: {e}")
        print("Full traceback:")
        traceback.print_exc()
        return

if __name__ == "__main__":
    run_agent_and_save_results()
