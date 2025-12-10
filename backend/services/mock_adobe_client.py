"""
Mock Adobe Client
Simulates Adobe AEP and RT-CDP API responses using CSV data.
Mimics the exact JSON structure that real Adobe APIs would return.

Data Sources (Simulated):
- Adobe AEP: Campaign & Ad Group performance data
- Adobe RT-CDP: Audience segments and targeting data
"""

import pandas as pd
import os
from datetime import datetime, timedelta
from backend.services.adobe_data_translator import AdobeDataTranslator


class MockAdobeClient:
    """
    Mock client that reads CSV files and returns Adobe-formatted JSON.

    Architecture:
    1. Reads CSV data (simulating AEP/RT-CDP databases)
    2. Converts to Adobe JSON format (simulating API responses)
    3. Uses same translator as real client (same downstream code)

    This allows development/testing without Adobe credentials.
    """

    def __init__(self, data_dir="data"):
        """
        Initialize mock client with path to CSV data directory.

        Args:
            data_dir: Directory containing campaigns.csv, ad_groups.csv, audiences.csv
        """
        self.data_dir = data_dir
        self.base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

        # Load CSV data (simulating Adobe's data lake)
        self.campaigns_csv = pd.read_csv(os.path.join(self.base_path, data_dir, 'campaigns.csv'))
        self.ad_groups_csv = pd.read_csv(os.path.join(self.base_path, data_dir, 'ad_groups.csv'))
        self.audiences_csv = pd.read_csv(os.path.join(self.base_path, data_dir, 'audiences.csv'))

        print(f"📦 Mock Adobe Client initialized (using CSV data from {data_dir}/)")
        print(f"   Simulating Adobe AEP + RT-CDP APIs")

    def get_campaign_data(self, days_back=14):
        """
        Simulate Adobe Experience Platform Campaign API.

        Real endpoint: GET /campaign/performance?start=...&end=...
        Returns: pandas DataFrame (via translator)

        Args:
            days_back: Number of days to fetch (simulates date range query)
        """
        # Simulate date filtering (last N days = last N/7 weeks in CSV)
        weeks_back = max(1, days_back // 7)
        max_week = self.campaigns_csv['week'].max()
        min_week = max_week - weeks_back + 1

        # Filter to recent weeks (simulating AEP date range query)
        recent_campaigns = self.campaigns_csv[self.campaigns_csv['week'] >= min_week]

        # Convert CSV to Adobe AEP JSON format
        adobe_json = self._csv_to_adobe_campaign_json(recent_campaigns)

        # Translate back to DataFrame (same as real client)
        return AdobeDataTranslator.translate_campaigns(adobe_json)

    def get_ad_group_metrics(self):
        """
        Simulate Adobe Experience Platform Ad Group API (via Source Connectors).

        Real endpoint: GET /data/foundation/query/adgroups
        Returns: pandas DataFrame (via translator)
        """
        # Get latest week data (simulating current state)
        max_week = self.ad_groups_csv['week'].max()
        recent_ad_groups = self.ad_groups_csv[self.ad_groups_csv['week'] == max_week]

        # Convert CSV to Adobe AEP JSON format
        adobe_json = self._csv_to_adobe_adgroup_json(recent_ad_groups)

        # Translate back to DataFrame (same as real client)
        return AdobeDataTranslator.translate_ad_groups(adobe_json)

    def get_audience_segments(self):
        """
        Simulate Adobe Real-Time CDP Segment API.

        Real endpoint: GET /data/core/ups/segment/definitions
        Returns: pandas DataFrame (via translator)
        """
        # Get latest week data (simulating current segment state)
        max_week = self.audiences_csv['week'].max()
        current_audiences = self.audiences_csv[self.audiences_csv['week'] == max_week]

        # Convert CSV to Adobe RT-CDP JSON format
        adobe_json = self._csv_to_adobe_segment_json(current_audiences)

        # Translate back to DataFrame (same as real client)
        return AdobeDataTranslator.translate_audiences(adobe_json)

    # ========== EXECUTION METHODS (Mock - Log Only) ==========

    def update_campaign_budget(self, campaign_id, new_budget):
        """Mock: Log budget update (would call Adobe Campaign API in real client)"""
        print(f"   [MOCK] Would update campaign {campaign_id} budget to ₹{new_budget:,.2f}")
        return {"status": "success", "campaignId": campaign_id, "newBudget": new_budget}

    def update_bid_strategy(self, ad_group_id, new_bid):
        """Mock: Log bid update (would call Adobe Destination Connector in real client)"""
        print(f"   [MOCK] Would update ad group {ad_group_id} bid to ₹{new_bid:.2f}")
        return {"status": "success", "adGroupId": ad_group_id, "newBid": new_bid}

    def activate_segment(self, segment_id):
        """Mock: Log segment activation (would call Adobe RT-CDP in real client)"""
        print(f"   [MOCK] Would activate RT-CDP segment: {segment_id}")
        return {"status": "success", "segmentId": segment_id, "action": "activated"}

    def suppress_segment(self, segment_id):
        """Mock: Log segment suppression (would call Adobe RT-CDP in real client)"""
        print(f"   [MOCK] Would suppress RT-CDP segment: {segment_id}")
        return {"status": "success", "segmentId": segment_id, "action": "suppressed"}

    # ========== CSV TO ADOBE JSON CONVERTERS ==========

    def _csv_to_adobe_campaign_json(self, campaigns_df):
        """Convert campaigns CSV to Adobe AEP JSON structure"""
        campaigns = []

        for _, row in campaigns_df.iterrows():
            campaign = {
                "campaignId": str(int(row['campaign_id'])),
                "campaignName": row['campaign_name'],
                "objective": row['objective'],
                "channel": row['channel'],
                "customAttributes": {
                    "model_line": row['model_line']
                },
                "budget": {
                    "allocated": float(row['weekly_budget_allocated']),
                    "spent": float(row['weekly_budget_spent']),
                    "currency": "INR"
                },
                "performance": {
                    "impressions": int(row['weekly_impressions']),
                    "clicks": int(row['weekly_clicks']),
                    "conversions": int(row['weekly_conversions']),
                    "conversionValue": float(row['weekly_conversion_value']),
                    "roas": float(row['roas'])
                },
                "dateRange": {
                    "start": self._week_to_date(int(row['week']), offset_days=-13),
                    "end": self._week_to_date(int(row['week']))
                }
            }
            campaigns.append(campaign)

        return {"campaigns": campaigns}

    def _csv_to_adobe_adgroup_json(self, ad_groups_df):
        """Convert ad_groups CSV to Adobe AEP JSON structure"""
        ad_groups = []

        for _, row in ad_groups_df.iterrows():
            ad_group = {
                "adGroupId": str(int(row['ad_group_id'])),
                "campaignId": str(int(row['campaign_id'])),
                "adGroupName": row['ad_group_name'],
                "targetingCriteria": {
                    "audienceId": row['audience_id']
                },
                "channel": row['channel'],
                "bidding": {
                    "strategy": row['bid_strategy'],
                    "averageBid": float(row['avg_bid']),
                    "currency": "INR"
                },
                "budget": {
                    "allocated": float(row['weekly_budget_allocated']),
                    "spent": float(row['weekly_budget_spent'])
                },
                "performance": {
                    "impressions": int(row['impressions']),
                    "clicks": int(row['clicks']),
                    "conversions": int(row['conversions']),
                    "conversionValue": float(row['conversion_value']),
                    "ctr": float(row['ctr']),
                    "cvr": float(row['cvr']),
                    "roas": float(row['roas'])
                },
                "dateRange": {
                    "end": self._week_to_date(int(row['week']))
                }
            }
            ad_groups.append(ad_group)

        return {"adGroups": ad_groups}

    def _csv_to_adobe_segment_json(self, audiences_df):
        """Convert audiences CSV to Adobe RT-CDP JSON structure"""
        segments = []

        for _, row in audiences_df.iterrows():
            segment = {
                "id": row['audience_id'],
                "name": row['audience_name'],
                "segmentType": row['segment_type'],
                "customAttributes": {
                    "intent_score": int(row['intent_score']),
                    "fatigue_score": float(row['fatigue_score']),
                    "frequency": float(row['frequency']),
                    "recency_last_engagement": int(row['recency_last_engagement']),
                    "model_preference": row['model_preference'],
                    "location_cluster": row['location_cluster']
                },
                "performance": {
                    "avgCtr": float(row['avg_ctr']),
                    "avgCvr": float(row['avg_cvr']),
                    "totalProfiles": 150000  # Mock value
                },
                "status": "active",
                "lastEvaluated": datetime.now().isoformat() + "Z"
            }
            segments.append(segment)

        return {"segments": segments}

    def _week_to_date(self, week_number, offset_days=0):
        """Convert week number to ISO date string"""
        # Approximate: assume week 1 = Jan 1st
        year = datetime.now().year
        base_date = datetime(year, 1, 1)
        target_date = base_date + timedelta(weeks=week_number-1, days=offset_days)
        return target_date.isoformat()
