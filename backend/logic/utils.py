import pandas as pd
from pathlib import Path

def load_all_data():
    """
    Loads the 3 final datasets used by the agent.
    """
    base = Path("backend/data")

    campaigns = pd.read_csv(base / "campaigns.csv")
    ad_groups = pd.read_csv(base / "ad_groups.csv")
    audiences = pd.read_csv(base / "audiences.csv")

    return {
        "campaigns": campaigns,
        "ad_groups": ad_groups,
        "audiences": audiences
    }

def append_next_week_data(next_week_data):
    """
    Appends the next week's dataframes to the respective CSV files.
    """
    base = Path("backend/data")
    
    next_week_data["campaigns"].to_csv(
        base / "campaigns.csv", mode='a', header=False, index=False
    )
    next_week_data["ad_groups"].to_csv(
        base / "ad_groups.csv", mode='a', header=False, index=False
    )
    next_week_data["audiences"].to_csv(
        base / "audiences.csv", mode='a', header=False, index=False
    )
    
    return next_week_data["next_week"]
