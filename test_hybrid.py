"""
Quick test script to verify the hybrid system works for a single week
"""
import json
import pandas as pd
from backend.agent.policy_agent import PolicyAgent
from backend.agent.state_manager import get_state_for_week

# Load data
campaigns_df = pd.read_csv("backend/data/campaigns.csv")
ad_groups_df = pd.read_csv("backend/data/ad_groups.csv")
audiences_df = pd.read_csv("backend/data/audiences.csv")

data = {
    "campaigns": campaigns_df,
    "ad_groups": ad_groups_df,
    "audiences": audiences_df
}

# Get state for week 1
print("Getting state for Week 1...")
state = get_state_for_week(data, 1)

print(f"State contains {len(state['campaigns'])} campaigns")
print(f"State contains {len(state['ad_groups'])} ad groups")
print(f"State contains {len(state['audiences'])} audiences")

# Run the agent
print("\nRunning hybrid agent...")
agent = PolicyAgent()
results = agent.get_recommendations(state)

# Display results
print("\n=== RESULTS ===")
print(f"\nBudget Actions: {len(results['decisions']['campaign_budget_actions'])}")
for action in results['decisions']['campaign_budget_actions'][:5]:
    print(f"  - Campaign {action['campaign_id']} ({action['campaign_name']}): {action['type']} - {action['reason']}")

print(f"\nBid Actions: {len(results['decisions']['ad_group_bid_actions'])}")
for action in results['decisions']['ad_group_bid_actions'][:5]:
    print(f"  - Ad Group {action['ad_group_id']}: {action['type']} - {action['reason']}")

print(f"\nAudience Actions: {len(results['decisions']['audience_targeting_actions'])}")
for action in results['decisions']['audience_targeting_actions'][:5]:
    print(f"  - Audience {action['audience_id']}: {action['type']} - {action['reason']}")

print(f"\nExplanation: {results['decisions']['explanation']}")

print("\n✅ Test successful!")
