import json
import pandas as pd
import os
import numpy as np # Import numpy for type checking
import time
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
    print("=" * 80)
    print("MARUTI SUZUKI AI MARKETING AGENT - INTELLIGENT OPTIMIZATION RUN")
    print("=" * 80)

    # 1. Load data
    print("\nLoading campaign data...")
    data = load_data()
    max_week = data["campaigns"]["week"].max()
    print(f"[OK] Data loaded successfully")
    print(f"[OK] Total campaigns: {len(data['campaigns']['campaign_id'].unique())}")
    print(f"[OK] Total ad groups: {len(data['ad_groups']['ad_group_id'].unique())}")
    print(f"[OK] Total audiences: {len(data['audiences']['audience_id'].unique())}")
    print(f"[OK] Weeks to process: {max_week}")

    # 2. Run the simulation starting from week 3 (requires 3 weeks of data for trend analysis)
    START_WEEK = 3  # Start from week 3 to have 3 weeks of historical data
    print(f"\nStarting AI-powered analysis for weeks {START_WEEK}-{max_week}...")
    print(f"[INFO] Skipping weeks 1-2 (insufficient historical data for 3-week trend analysis)")
    print("-" * 80)

    agent = PolicyAgent()
    try:
        campaign_history = []
        total_start_time = time.time()

        # Store weeks 1-2 state snapshots without recommendations
        print(f"\nCollecting baseline data for weeks 1-2...")
        for week in range(1, START_WEEK):
            baseline_state = get_state_for_week(data, week)
            history_entry = {
                "week": week,
                "state_snapshot": baseline_state,
                "recommendations": {
                    "campaign_budget_actions": [],
                    "ad_group_bid_actions": [],
                    "audience_targeting_actions": [],
                    "explanation": f"Week {week}: Baseline data collection - insufficient historical data for 3-week trend analysis. Recommendations start from week {START_WEEK}."
                },
                "log_history": []
            }
            campaign_history.append(history_entry)
            print(f"   Week {week}: Baseline collected (no recommendations)")

        # The loop runs from week 3 up to the max_week (12)
        for week in range(START_WEEK, max_week + 1):
            week_start_time = time.time()
            print(f"\nProcessing Week {week}/{max_week}...", end=" ", flush=True)

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

            # d. Show completion with summary
            budget_actions = results["decisions"].get("campaign_budget_actions", [])
            bid_actions = results["decisions"].get("ad_group_bid_actions", [])
            audience_actions = results["decisions"].get("audience_targeting_actions", [])

            budget_increase = sum(1 for a in budget_actions if a.get('type') == 'increase')
            budget_decrease = sum(1 for a in budget_actions if a.get('type') == 'decrease')
            bid_raise = sum(1 for a in bid_actions if a.get('type') == 'raise_bid')
            bid_lower = sum(1 for a in bid_actions if a.get('type') == 'lower_bid')
            aud_activate = sum(1 for a in audience_actions if a.get('type') == 'activate')
            aud_suppress = sum(1 for a in audience_actions if a.get('type') == 'suppress')

            week_elapsed = time.time() - week_start_time
            total_elapsed = time.time() - total_start_time

            print(f"DONE ({week_elapsed:.1f}s)")
            print(f"   Budget: +{budget_increase} -{budget_decrease} | "
                  f"Bids: +{bid_raise} -{bid_lower} | "
                  f"Audiences: +{aud_activate} -{aud_suppress} | "
                  f"Total time: {total_elapsed/60:.2f} min")

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
        print("\n" + "-" * 80)
        print("Saving results to JSON...")
        try:
            os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
            with open(OUTPUT_FILE, 'w') as f:
                # Use the custom encoder to handle numpy/pandas types
                json.dump(final_output, f, indent=4, cls=NumpyEncoder)

            file_size = os.path.getsize(OUTPUT_FILE) / 1024  # Size in KB
            total_time = time.time() - total_start_time

            print(f"[OK] Results saved to {OUTPUT_FILE}")
            print(f"[OK] File size: {file_size:.1f} KB")
            print("\n" + "=" * 80)
            print("AI AGENT RUN COMPLETE - INTELLIGENT RECOMMENDATIONS GENERATED")
            print("=" * 80)
            print(f"\nSummary:")
            print(f"   - Processed {max_week} weeks of campaign data")
            print(f"   - Generated {max_week - START_WEEK + 1} sets of intelligent recommendations (weeks {START_WEEK}-{max_week})")
            print(f"   - Weeks 1-2: Baseline data collection only (no recommendations)")
            print(f"   - Analyzed {len(data['campaigns']['campaign_id'].unique())} campaigns")
            print(f"   - Optimized {len(data['ad_groups']['ad_group_id'].unique())} ad groups")
            print(f"   - Evaluated {len(data['audiences']['audience_id'].unique())} audience segments")
            print(f"   - Total execution time: {total_time/60:.2f} minutes")
            print(f"\nNext step: Open frontend/index.html to view the interactive dashboard")
            print("=" * 80 + "\n")
        except Exception as e:
            print(f"[ERROR] Error saving results to JSON: {e}")
            
    except Exception as e:
        import traceback
        print("\n" + "=" * 80)
        print("[ERROR] ERROR DURING AGENT RUN")
        print("=" * 80)
        print(f"\nError: {e}")
        print("\nFull traceback:")
        traceback.print_exc()
        print("\n" + "=" * 80 + "\n")
        return

if __name__ == "__main__":
    run_agent_and_save_results()
