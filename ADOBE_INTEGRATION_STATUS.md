# Adobe Integration Status Report

**Branch**: `adobe-integration`
**Date**: 2025-12-10
**Status**: ✅ Phase 1 Complete - Mock Infrastructure Ready

---

## What We Built (Step 1)

### 1. Mock Adobe Client Infrastructure

Created a complete mock system that simulates **both** Adobe Experience Platform (AEP) and Real-Time CDP (RT-CDP) APIs using your existing CSV data.

#### Files Created:

| File | Purpose | Lines |
|------|---------|-------|
| `backend/services/__init__.py` | Package marker | 2 |
| **`backend/services/adobe_data_translator.py`** | Converts Adobe JSON ↔ DataFrames | ~150 |
| **`backend/services/mock_adobe_client.py`** | Mock client (uses CSV data) | ~250 |
| **`backend/services/adobe_aep_client.py`** | Real client skeleton (for future) | ~200 |
| **`backend/services/adobe_client_factory.py`** | Factory to switch mock/real | ~60 |
| `backend/config.example.py` | Updated with Adobe config | Updated |
| `requirements.txt` | Added Adobe dependencies | Updated |
| `backend/test_adobe_mock.py` | Test script | ~100 |

---

## Architecture Overview

### Data Sources (Simulated in Mock Mode)

```
┌─────────────────────────────────────────────────────────────┐
│                    ADOBE ECOSYSTEM                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌────────────────────────────────────────────────┐       │
│  │  Adobe Experience Platform (AEP)               │       │
│  ├────────────────────────────────────────────────┤       │
│  │  • Campaign performance data                   │       │
│  │  • Ad group metrics (via Source Connectors)    │       │
│  │  • Budget & spend tracking                     │       │
│  │  • Performance metrics (ROAS, conversions)     │       │
│  │                                                │       │
│  │  APIs:                                         │       │
│  │  - GET /campaign/performance                   │       │
│  │  - GET /data/foundation/query/adgroups         │       │
│  └────────────────────────────────────────────────┘       │
│                                                             │
│  ┌────────────────────────────────────────────────┐       │
│  │  Adobe Real-Time CDP (RT-CDP)                  │       │
│  ├────────────────────────────────────────────────┤       │
│  │  • Audience segments & profiles                │       │
│  │  • Intent scores, fatigue scores               │       │
│  │  • Segment activation/suppression              │       │
│  │  • Customer behavioral data                    │       │
│  │                                                │       │
│  │  APIs:                                         │       │
│  │  - GET /data/core/ups/segment/definitions      │       │
│  │  - POST /data/core/ups/segment/jobs            │       │
│  └────────────────────────────────────────────────┘       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Mock Mode Data Flow

```
┌─────────────────┐
│   CSV Files     │
│  (backend/data) │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────┐
│  MockAdobeClient            │
│  - Reads CSV                │
│  - Converts to Adobe JSON   │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐     ┌────────────────────────┐
│  Adobe JSON Format          │────▶│  AdobeDataTranslator   │
│  (AEP + RT-CDP structure)   │     │  - Parses nested JSON  │
└─────────────────────────────┘     │  - Flattens to DataFrame│
                                    └────────┬───────────────┘
                                             │
                                             ▼
                                    ┌────────────────────────┐
                                    │  pandas DataFrame      │
                                    │  (same as original CSV)│
                                    └────────┬───────────────┘
                                             │
                                             ▼
                                    ┌────────────────────────┐
                                    │  Your Existing Code    │
                                    │  (analytics_enricher)  │
                                    │  (budget_allocator)    │
                                    │  (policy_agent)        │
                                    └────────────────────────┘
```

### Real Mode Data Flow (Future)

```
┌─────────────────────────────┐
│  Adobe AEP/RT-CDP APIs      │
│  (Live production data)     │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│  AdobeAEPClient             │
│  - JWT authentication       │
│  - REST API calls           │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐     ┌────────────────────────┐
│  Adobe JSON Format          │────▶│  AdobeDataTranslator   │
│  (AEP + RT-CDP structure)   │     │  (SAME AS MOCK!)       │
└─────────────────────────────┘     └────────┬───────────────┘
                                             │
                                             ▼
                                    ┌────────────────────────┐
                                    │  pandas DataFrame      │
                                    │  (SAME AS MOCK!)       │
                                    └────────┬───────────────┘
                                             │
                                             ▼
                                    ┌────────────────────────┐
                                    │  Your Existing Code    │
                                    │  (UNCHANGED!)          │
                                    └────────────────────────┘
```

---

## Adobe JSON Structures (What APIs Return)

### 1. Campaign Data (Adobe AEP)

**Source**: Adobe Campaign Standard/Classic API

```json
{
  "campaigns": [
    {
      "campaignId": "1",
      "campaignName": "Suzuki Festive Campaign 1",
      "objective": "Awareness",
      "channel": "Social",
      "customAttributes": {
        "model_line": "Arena"
      },
      "budget": {
        "allocated": 1401135.85,
        "spent": 1435793.54,
        "currency": "INR"
      },
      "performance": {
        "impressions": 6750255,
        "clicks": 121076,
        "conversions": 6530,
        "conversionValue": 65629680.56,
        "roas": 45.71
      },
      "dateRange": {
        "start": "2024-11-27",
        "end": "2024-12-10"
      }
    }
  ]
}
```

### 2. Ad Group Data (Adobe AEP via Source Connectors)

**Source**: Google Ads/Meta APIs → AEP Source Connectors

```json
{
  "adGroups": [
    {
      "adGroupId": "1",
      "campaignId": "1",
      "adGroupName": "AG_1_1",
      "targetingCriteria": {
        "audienceId": "AUD6"
      },
      "channel": "Social",
      "bidding": {
        "strategy": "Manual CPC",
        "averageBid": 17.67,
        "currency": "INR"
      },
      "budget": {
        "allocated": 419353.66,
        "spent": 403121.71
      },
      "performance": {
        "impressions": 2799176,
        "clicks": 45396,
        "conversions": 2607,
        "conversionValue": 22338898.04,
        "ctr": 0.0162,
        "cvr": 0.0574,
        "roas": 55.415
      }
    }
  ]
}
```

### 3. Audience Segments (Adobe RT-CDP)

**Source**: Real-Time CDP Unified Profile Service (UPS)

```json
{
  "segments": [
    {
      "id": "AUD1",
      "name": "Audience Segment 1",
      "segmentType": "Retargeting",
      "customAttributes": {
        "intent_score": 69,
        "fatigue_score": 17.75,
        "frequency": 9.0,
        "recency_last_engagement": 10,
        "model_preference": "Sedan",
        "location_cluster": "Tier 1"
      },
      "performance": {
        "avgCtr": 0.0421,
        "avgCvr": 0.0882,
        "totalProfiles": 156000
      },
      "status": "active",
      "lastEvaluated": "2024-12-10T00:00:00Z"
    }
  ]
}
```

---

## Test Results

```
✅ Campaign data: 50 campaigns retrieved
✅ Ad group data: 125 ad groups retrieved
✅ Audience data: 10 segments retrieved
✅ Data structure matches CSV format
✅ Translator correctly converts Adobe JSON → DataFrames
✅ Execution methods (mock logging) working
```

---

## How to Switch Between Mock and Real

### Option 1: Using Config Flag

```python
# backend/config.py
USE_MOCK_ADOBE = True   # Development mode (CSV data)
# USE_MOCK_ADOBE = False  # Production mode (Adobe APIs)
```

### Option 2: Using Factory Directly

```python
from backend.services.adobe_client_factory import AdobeClientFactory

# Mock mode
client = AdobeClientFactory.create_client(
    use_mock=True,
    data_dir="backend/data"
)

# Real mode (future)
client = AdobeClientFactory.create_client(
    use_mock=False,
    api_key="your-key",
    org_id="your-org",
    technical_account_id="your-account",
    private_key="your-private-key",
    client_secret="your-secret"
)

# Same interface for both!
campaigns = client.get_campaign_data(days_back=14)
ad_groups = client.get_ad_group_metrics()
audiences = client.get_audience_segments()
```

---

## Key Benefits

1. **Zero Changes to Core Logic**: Your existing `analytics_enricher.py`, `budget_allocator.py`, `policy_agent.py` work unchanged
2. **Same Data Structure**: DataFrames from mock and real client are identical
3. **Easy Testing**: Develop without Adobe credentials
4. **One-Line Switch**: Change `USE_MOCK_ADOBE` flag to go live
5. **Realistic Simulation**: Mock client mimics exact Adobe JSON format

---

## Next Steps

### ✅ Phase 1: COMPLETE
- Mock infrastructure created
- Data translator working
- Tests passing

### 🔄 Phase 2: IN PROGRESS (Next)
- Update `main.py` to use Adobe client instead of CSV loading
- Integrate with existing state manager
- Update analytics for 2-week trend analysis (instead of 3-week)

### ⏳ Phase 3: TODO
- Enable execution layer
- Test autonomous decision making
- Update dashboard for daily view

### ⏳ Phase 4: TODO
- Deploy with cron job
- Switch to real Adobe APIs when credentials available

---

## Dependencies Installed

```
PyJWT==2.10.1           # JWT authentication
cryptography==46.0.3    # RSA key handling
requests (already had)  # HTTP client
python-dateutil         # Date parsing
```

---

## Important Notes

### Adobe API Endpoints (For Future Real Integration)

**Authentication**:
- URL: `https://ims-na1.adobelogin.com/ims/exchange/jwt`
- Method: JWT token exchange

**Adobe Experience Platform**:
- Base URL: `https://platform.adobe.io`
- Campaign data: `GET /campaign/performance?start=...&end=...`
- Ad groups: `GET /data/foundation/query/adgroups`

**Adobe Real-Time CDP**:
- Base URL: `https://platform.adobe.io`
- Segments: `GET /data/core/ups/segment/definitions`
- Activation: `POST /data/core/ups/segment/jobs`

---

## File Structure (After Phase 1)

```
marketing-agent/
├── backend/
│   ├── services/              [NEW]
│   │   ├── __init__.py
│   │   ├── adobe_data_translator.py
│   │   ├── mock_adobe_client.py
│   │   ├── adobe_aep_client.py
│   │   └── adobe_client_factory.py
│   ├── test_adobe_mock.py     [NEW]
│   ├── config.example.py      [UPDATED]
│   └── ...
├── requirements.txt           [NEW]
└── ...
```

---

**Status**: Ready for Phase 2 - Main script integration! 🚀
