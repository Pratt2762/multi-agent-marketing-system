import pandas as pd

def get_latest_week_state(data):
    # Sanity check for data presence
    if data["campaigns"].empty or data["ad_groups"].empty or data["audiences"].empty:
        raise ValueError("One or more datasets are empty. Cannot construct state.")

    latest_week = data["campaigns"]["week"].max()

    # Filter data to latest week
    campaigns_df = data["campaigns"][data["campaigns"]["week"] == latest_week]
    ad_groups_df = data["ad_groups"][data["ad_groups"]["week"] == latest_week]
    audiences_df = data["audiences"][data["audiences"]["week"] == latest_week]

    if campaigns_df.empty or ad_groups_df.empty or audiences_df.empty:
        raise ValueError(f"No data found for the latest week: {latest_week}. Cannot construct state.")

    # ---- 1. COMPACT CAMPAIGN SUMMARY ----
    campaigns = campaigns_df[[
        "campaign_id",
        "campaign_name",
        "objective",
        "channel",
        "model_line",
        "weekly_budget_allocated",
        "weekly_budget_spent",
        "weekly_conversions",
        "weekly_conversion_value",
        "roas"
    ]].to_dict(orient="records")

    # ---- 2. COMPACT AD-GROUP SUMMARY ----
    ad_groups = ad_groups_df[[
        "ad_group_id",
        "campaign_id",
        "ad_group_name",
        "audience_id",
        "bid_strategy",
        "avg_bid",
        "weekly_budget_allocated", # Added for executor's budget shift logic
        "weekly_budget_spent",
        "conversions",
        "conversion_value",
        "roas"
    ]].to_dict(orient="records")

    # ---- 3. COMPACT AUDIENCE SUMMARY ----
    audiences = audiences_df[[
        "audience_id",
        "audience_name",
        "segment_type",
        "intent_score",
        "fatigue_score",
        "frequency",
        "recency_last_engagement",
        "avg_ctr",
        "avg_cvr"
    ]].to_dict(orient="records")

    return {
        "latest_week": int(latest_week), # Ensure it's a standard type for JSON
        "campaigns": campaigns,
        "ad_groups": ad_groups,
        "audiences": audiences
    }
