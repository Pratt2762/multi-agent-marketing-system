import pandas as pd

def load_all_data():
    return {
        "campaigns": pd.read_csv("backend/data/campaigns.csv"),
        "ad_groups": pd.read_csv("backend/data/ad_groups.csv"),
        "perf": pd.read_csv("backend/data/campaign_performance_weekly.csv"),
        "audience": pd.read_csv("backend/data/audience_stats_weekly.csv")
    }