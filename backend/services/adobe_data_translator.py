"""
Adobe Data Translator
Converts Adobe AEP/RT-CDP JSON responses into pandas DataFrames matching CSV structure.
Works with both mock and real Adobe clients - ensures zero changes to core analytics logic.
"""

import pandas as pd
from datetime import datetime


class AdobeDataTranslator:
    """
    Translates Adobe AEP/RT-CDP JSON responses into pandas DataFrames
    matching your current CSV structure.

    This allows ZERO changes to your existing analytics code.
    """

    @staticmethod
    def translate_campaigns(adobe_campaigns_json):
        """
        Convert Adobe AEP campaign JSON to campaigns.csv structure.

        Source: Adobe Experience Platform (Campaign Standard/Classic API)
        Format: Nested JSON with budget, performance, dateRange objects
        """
        records = []

        for campaign in adobe_campaigns_json.get('campaigns', []):
            record = {
                'campaign_id': int(campaign['campaignId']),
                'campaign_name': campaign['campaignName'],
                'objective': campaign['objective'],
                'channel': campaign['channel'],
                'model_line': campaign.get('customAttributes', {}).get('model_line', 'Unknown'),
                'weekly_budget_allocated': campaign['budget']['allocated'],
                'weekly_budget_spent': campaign['budget']['spent'],
                'weekly_impressions': campaign['performance']['impressions'],
                'weekly_clicks': campaign['performance']['clicks'],
                'weekly_conversions': campaign['performance']['conversions'],
                'weekly_conversion_value': campaign['performance']['conversionValue'],
                'roas': campaign['performance']['roas'],
                'week': AdobeDataTranslator._date_to_week(campaign['dateRange']['end'])
            }
            records.append(record)

        # Return pandas DataFrame with exact same structure as CSV
        return pd.DataFrame(records)

    @staticmethod
    def translate_ad_groups(adobe_ad_groups_json):
        """
        Convert Adobe AEP ad group JSON to ad_groups.csv structure.

        Source: Adobe Experience Platform (via Google Ads/Meta Source Connectors)
        Format: Nested JSON with bidding, budget, targeting, performance objects
        """
        records = []

        for ag in adobe_ad_groups_json.get('adGroups', []):
            record = {
                'ad_group_id': int(ag['adGroupId']),
                'campaign_id': int(ag['campaignId']),
                'ad_group_name': ag['adGroupName'],
                'audience_id': ag['targetingCriteria']['audienceId'],
                'channel': ag['channel'],
                'bid_strategy': ag['bidding']['strategy'],
                'avg_bid': ag['bidding']['averageBid'],
                'weekly_budget_allocated': ag['budget']['allocated'],
                'weekly_budget_spent': ag['budget']['spent'],
                'impressions': ag['performance']['impressions'],
                'clicks': ag['performance']['clicks'],
                'conversions': ag['performance']['conversions'],
                'conversion_value': ag['performance']['conversionValue'],
                'ctr': ag['performance']['ctr'],
                'cvr': ag['performance']['cvr'],
                'roas': ag['performance']['roas'],
                'week': AdobeDataTranslator._date_to_week(ag.get('dateRange', {}).get('end', ''))
            }
            records.append(record)

        return pd.DataFrame(records)

    @staticmethod
    def translate_audiences(adobe_segments_json):
        """
        Convert Adobe RT-CDP segment JSON to audiences.csv structure.

        Source: Adobe Real-Time CDP (Unified Profile Service API)
        Format: Nested JSON with customAttributes, performance, status objects
        """
        records = []

        for segment in adobe_segments_json.get('segments', []):
            attrs = segment.get('customAttributes', {})
            perf = segment.get('performance', {})

            record = {
                'audience_id': segment['id'],
                'audience_name': segment['name'],
                'segment_type': segment['segmentType'],
                'intent_score': attrs.get('intent_score', 50),
                'fatigue_score': attrs.get('fatigue_score', 0),
                'frequency': attrs.get('frequency', 1.0),
                'recency_last_engagement': attrs.get('recency_last_engagement', 0),
                'avg_ctr': perf.get('avgCtr', 0.0),
                'avg_cvr': perf.get('avgCvr', 0.0),
                'model_preference': attrs.get('model_preference', 'Unknown'),
                'location_cluster': attrs.get('location_cluster', 'Unknown'),
                'week': AdobeDataTranslator._current_week()
            }
            records.append(record)

        return pd.DataFrame(records)

    @staticmethod
    def _date_to_week(date_string):
        """Convert ISO date string to week number (matching your existing convention)"""
        if not date_string:
            return AdobeDataTranslator._current_week()

        try:
            # Handle ISO format with or without timezone
            date = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
            # Return week of year (1-52)
            return date.isocalendar()[1]
        except:
            return AdobeDataTranslator._current_week()

    @staticmethod
    def _current_week():
        """Get current week number"""
        return datetime.now().isocalendar()[1]
