import pandas as pd

def construct_state(data):
    """
    Converts loaded dataframes into a clean JSON state
    suitable for the agent.
    """
    campaigns = data["campaigns"].to_dict(orient="records")
    ad_groups = data["ad_groups"].to_dict(orient="records")
    perf = data["perf"].to_dict(orient="records")
    audience = data["audience"].to_dict(orient="records")

    return {
        "campaigns": campaigns,
        "ad_groups": ad_groups,
        "performance": perf,
        "audience_stats": audience,
    }