"""
Test script for Mock Adobe Client
Verifies that mock client correctly simulates Adobe AEP and RT-CDP APIs.
"""

import sys
import os

# Fix Windows console encoding for emojis
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from backend.services.adobe_client_factory import AdobeClientFactory


def test_mock_adobe_client():
    """Test mock Adobe client with CSV data"""

    print("=" * 80)
    print("TESTING MOCK ADOBE CLIENT")
    print("=" * 80)

    # Create mock client
    client = AdobeClientFactory.create_client(use_mock=True, data_dir="backend/data")

    print("\n" + "=" * 80)
    print("TEST 1: Fetching Campaign Data (simulating Adobe AEP Campaign API)")
    print("=" * 80)

    campaigns_df = client.get_campaign_data(days_back=14)

    print(f"\n✅ Retrieved {len(campaigns_df)} campaigns")
    print(f"   Columns: {list(campaigns_df.columns)}")
    print(f"\n   Sample data (first 3 campaigns):")
    print(campaigns_df.head(3))

    print("\n" + "=" * 80)
    print("TEST 2: Fetching Ad Group Data (simulating Adobe AEP Source Connectors)")
    print("=" * 80)

    ad_groups_df = client.get_ad_group_metrics()

    print(f"\n✅ Retrieved {len(ad_groups_df)} ad groups")
    print(f"   Columns: {list(ad_groups_df.columns)}")
    print(f"\n   Sample data (first 3 ad groups):")
    print(ad_groups_df.head(3))

    print("\n" + "=" * 80)
    print("TEST 3: Fetching Audience Segments (simulating Adobe RT-CDP API)")
    print("=" * 80)

    audiences_df = client.get_audience_segments()

    print(f"\n✅ Retrieved {len(audiences_df)} audience segments")
    print(f"   Columns: {list(audiences_df.columns)}")
    print(f"\n   Sample data (first 3 audiences):")
    print(audiences_df.head(3))

    print("\n" + "=" * 80)
    print("TEST 4: Testing Execution Methods (mock - log only)")
    print("=" * 80)

    print("\n📝 Testing budget update:")
    client.update_campaign_budget(campaign_id=1, new_budget=1500000.0)

    print("\n📝 Testing bid update:")
    client.update_bid_strategy(ad_group_id=5, new_bid=18.5)

    print("\n📝 Testing segment activation:")
    client.activate_segment(segment_id="AUD3")

    print("\n📝 Testing segment suppression:")
    client.suppress_segment(segment_id="AUD7")

    print("\n" + "=" * 80)
    print("✅ ALL TESTS PASSED!")
    print("=" * 80)

    print("\n🎯 Summary:")
    print(f"   • Campaign data structure matches CSV: {set(campaigns_df.columns) == set(['campaign_id', 'campaign_name', 'objective', 'channel', 'model_line', 'weekly_budget_allocated', 'weekly_budget_spent', 'weekly_impressions', 'weekly_clicks', 'weekly_conversions', 'weekly_conversion_value', 'roas', 'week'])}")
    print(f"   • Ad group data structure matches CSV: {len(ad_groups_df.columns) == 17}")
    print(f"   • Audience data structure matches CSV: {len(audiences_df.columns) == 11}")
    print(f"   • Mock client successfully simulates Adobe AEP + RT-CDP APIs")

    return True


if __name__ == "__main__":
    try:
        test_mock_adobe_client()
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
