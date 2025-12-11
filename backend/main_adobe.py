import json
import pandas as pd
import os
import numpy as np # Import numpy for type checking
import time
from backend.agent.policy_agent import PolicyAgent
from backend.logic.logger import agent_logger
from backend.agent.state_manager import get_latest_week_state, get_state_for_week
from backend.services.adobe_client_factory import AdobeClientFactory
from backend import config

# --- Configuration ---
OUTPUT_FILE = "frontend/results.json"

def load_data_from_adobe(adobe_client):
    """
    Loads data from Adobe AEP/RT-CDP (mock or real).

    Returns data in the same format as CSV loading for compatibility with existing code.
    """
    print("Fetching data from Adobe Experience Platform...")

    # Fetch from Adobe (mock or real)
    # Use days_back=999 to get ALL historical data for hackathon demo
    campaigns_df = adobe_client.get_campaign_data(days_back=999)
    ad_groups_df = adobe_client.get_ad_group_metrics(all_weeks=True)
    audiences_df = adobe_client.get_audience_segments(all_weeks=True)

    print(f"[OK] Retrieved {len(campaigns_df)} campaign records")
    print(f"[OK] Retrieved {len(ad_groups_df)} ad group records")
    print(f"[OK] Retrieved {len(audiences_df)} audience segments")

    return {
        "campaigns": campaigns_df,
        "ad_groups": ad_groups_df,
        "audiences": audiences_df
    }

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
    print("MARUTI SUZUKI AI MARKETING AGENT - ADOBE INTEGRATION MODE")
    print("=" * 80)

    # 1. Initialize Adobe client (mock or real based on config)
    print(f"\nInitializing Adobe client (USE_MOCK_ADOBE = {config.USE_MOCK_ADOBE})...")

    if config.USE_MOCK_ADOBE:
        # Mock mode - uses CSV data
        adobe_client = AdobeClientFactory.create_client(
            use_mock=True,
            data_dir=config.DATA_DIR
        )
    else:
        # Real mode - uses Adobe APIs
        adobe_client = AdobeClientFactory.create_client(
            use_mock=False,
            api_key=config.ADOBE_API_KEY,
            org_id=config.ADOBE_ORG_ID,
            technical_account_id=config.ADOBE_TECHNICAL_ACCOUNT_ID,
            private_key=config.ADOBE_PRIVATE_KEY,
            client_secret=config.ADOBE_CLIENT_SECRET
        )

    # 2. Load data from Adobe
    print("\nLoading campaign data from Adobe...")
    data = load_data_from_adobe(adobe_client)
    max_week = data["campaigns"]["week"].max()
    print(f"[OK] Data loaded successfully from Adobe")
    print(f"[OK] Total campaigns: {len(data['campaigns']['campaign_id'].unique())}")
    print(f"[OK] Total ad groups: {len(data['ad_groups']['ad_group_id'].unique())}")
    print(f"[OK] Total audiences: {len(data['audiences']['audience_id'].unique())}")
    print(f"[OK] Weeks to process: {max_week}")

    # 3. Run the simulation starting from week 2 (2-week trend analysis)
    START_WEEK = 2  # Start from week 2 to have 2 weeks of historical data
    print(f"\nStarting AI-powered analysis for weeks {START_WEEK}-{max_week}...")
    print(f"[INFO] Skipping week 1 (insufficient historical data for 2-week trend analysis)")
    print("-" * 80)

    agent = PolicyAgent()
    try:
        campaign_history = []
        total_start_time = time.time()

        # Store week 1 state snapshot without recommendations
        print(f"\nCollecting baseline data for week 1...")
        baseline_state = get_state_for_week(data, 1)
        history_entry = {
            "week": 1,
            "state_snapshot": baseline_state,
            "recommendations": {
                "campaign_budget_actions": [],
                "ad_group_bid_actions": [],
                "audience_targeting_actions": [],
                "explanation": f"Week 1: Baseline data collection - insufficient historical data for 2-week trend analysis. Recommendations start from week {START_WEEK}."
            },
            "log_history": []
        }
        campaign_history.append(history_entry)
        print(f"   Week 1: Baseline collected (no recommendations)")

        # The loop runs from week 2 up to the max_week
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
            print(f"   - Week 1: Baseline data collection only (no recommendations)")
            print(f"   - Analyzed {len(data['campaigns']['campaign_id'].unique())} campaigns")
            print(f"   - Optimized {len(data['ad_groups']['ad_group_id'].unique())} ad groups")
            print(f"   - Evaluated {len(data['audiences']['audience_id'].unique())} audience segments")
            print(f"   - Total execution time: {total_time/60:.2f} minutes")
            print(f"   - Data source: {'Adobe Mock (CSV simulation)' if config.USE_MOCK_ADOBE else 'Adobe AEP/RT-CDP (Live APIs)'}")
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
