# Phase 4: Execution Layer - DESIGN DOCUMENT

**Status**: Ready for implementation when Adobe credentials available
**Branch**: `adobe-integration`
**Date**: 2025-12-13

---

## 🎯 **What is Phase 4?**

Phase 4 enables your multi-agent system to **write decisions back to Adobe** instead of just generating recommendations. This turns your system from "advisory" to "autonomous."

---

## 📊 **Current State (Phases 1-3)**

```
Adobe APIs → Data → Analytics → Recommendations → JSON file → Dashboard
              ↑                                      ↓
              └──────────── (Read Only) ─────────────┘
```

**Current Behavior**:
- ✅ Reads data from Adobe (mock or real)
- ✅ Analyzes performance (2-week trends)
- ✅ Generates recommendations (budgets, bids, segments)
- ❌ Does NOT execute changes back to Adobe
- ❌ Recommendations stay in JSON (manual review required)

---

## 🚀 **Target State (After Phase 4)**

```
Adobe APIs → Data → Analytics → Decisions → Execute → Adobe APIs
     ↓                                                      ↓
     └────────────── (Read + Write) ──────────────────────┘
```

**New Behavior**:
- ✅ Reads data from Adobe
- ✅ Analyzes performance
- ✅ Generates decisions
- ✅ **EXECUTES** changes to Adobe automatically
- ✅ Updates budgets, bids, segments in production
- ✅ Autonomous daily optimization

---

## 🏗️ **Architecture Changes Required**

### **1. Update Executor Class** (`backend/logic/executor.py`)

**Current**:
```python
class Executor:
    def __init__(self):
        pass  # No Adobe client

    def execute_decisions(self, data, decisions):
        # Only simulates changes locally
        # No actual API calls
        pass
```

**Needed**:
```python
class Executor:
    def __init__(self, adobe_client=None, execute_to_adobe=False):
        self.adobe_client = adobe_client
        self.execute_to_adobe = execute_to_adobe

    def _execute_budget_to_adobe(self, campaign_id, old_budget, new_budget):
        if self.execute_to_adobe:
            result = self.adobe_client.update_campaign_budget(campaign_id, new_budget)
            # Log success/failure
        else:
            # Dry-run mode: only log
            pass

    def _execute_bid_to_adobe(self, ad_group_id, old_bid, new_bid):
        if self.execute_to_adobe:
            result = self.adobe_client.update_bid_strategy(ad_group_id, new_bid)
            # Log success/failure
        else:
            # Dry-run mode: only log
            pass

    def _execute_segment_action_to_adobe(self, audience_id, action_type):
        if self.execute_to_adobe:
            if action_type == "activate":
                result = self.adobe_client.activate_segment(audience_id)
            elif action_type == "suppress":
                result = self.adobe_client.suppress_segment(audience_id)
            # Log success/failure
        else:
            # Dry-run mode: only log
            pass
```

---

### **2. Update Main Script** (`backend/main_adobe.py`)

**Current**:
```python
# Only generates recommendations
agent = PolicyAgent()
results = agent.get_recommendations(current_week_state)

# NO execution happens
```

**Needed**:
```python
# Initialize executor with Adobe client
executor = Executor(
    adobe_client=adobe_client,
    execute_to_adobe=config.ENABLE_ADOBE_EXECUTION  # New flag
)

# Generate recommendations
agent = PolicyAgent()
results = agent.get_recommendations(current_week_state)

# EXECUTE to Adobe (optional based on flag)
if config.ENABLE_ADOBE_EXECUTION:
    execution_results = executor.execute_decisions(data, results["decisions"])
    # Log execution results
else:
    # Dry-run mode: only show what would happen
    pass
```

---

### **3. Add Configuration Flag** (`backend/config.py`)

```python
# Existing flags
USE_MOCK_ADOBE = True  # Mock vs Real client

# NEW - Execution control
ENABLE_ADOBE_EXECUTION = False  # Dry-run vs Write mode
```

**Safety Matrix**:

| USE_MOCK_ADOBE | ENABLE_ADOBE_EXECUTION | Behavior |
|----------------|------------------------|----------|
| True | False | Mock data, no execution (safe testing) |
| True | True | Mock data, mock execution (test execution logic) |
| False | False | Real data, no execution (read-only prod) |
| False | True | Real data, REAL execution (**PRODUCTION**) |

---

## 📝 **Execution Methods Mapping**

### **Budget Updates** → Adobe Campaign API

**Your Decision**:
```json
{
  "campaign_id": 5,
  "type": "increase",
  "current": 500000.0,
  "new": 600000.0,
  "tier": "high"
}
```

**Adobe API Call**:
```http
PATCH https://platform.adobe.io/campaign/5
Authorization: Bearer {access_token}
x-api-key: {api_key}

{
  "budget": {
    "allocated": 600000.0,
    "currency": "INR"
  }
}
```

**Response**:
```json
{
  "status": "success",
  "campaignId": "5",
  "newBudget": 600000.0,
  "effectiveDate": "2025-12-14T00:00:00Z"
}
```

---

### **Bid Updates** → Adobe Destination Connectors

**Your Decision**:
```json
{
  "ad_group_id": 23,
  "type": "raise_bid",
  "current": 15.50,
  "new": 17.05,
  "tier": "moderate"
}
```

**Adobe API Call**:
```http
PATCH https://platform.adobe.io/adGroups/23/bidding
Authorization: Bearer {access_token}
x-api-key: {api_key}

{
  "averageBid": 17.05,
  "currency": "INR"
}
```

**Response**:
```json
{
  "status": "success",
  "adGroupId": "23",
  "newBid": 17.05,
  "platform": "Google Ads"
}
```

---

### **Segment Actions** → Adobe RT-CDP

**Your Decision (Activate)**:
```json
{
  "audience_id": "AUD5",
  "type": "activate",
  "reason": "High intent score + low fatigue"
}
```

**Adobe API Call**:
```http
POST https://platform.adobe.io/data/core/ups/segment/jobs
Authorization: Bearer {access_token}
x-api-key: {api_key}

{
  "segmentId": "AUD5",
  "action": "activate",
  "destinations": ["google-ads", "meta-ads"]
}
```

**Response**:
```json
{
  "status": "success",
  "jobId": "job-12345",
  "segmentId": "AUD5",
  "action": "activate",
  "estimatedProfiles": 125000,
  "destinations": ["google-ads", "meta-ads"]
}
```

---

**Your Decision (Suppress)**:
```json
{
  "audience_id": "AUD3",
  "type": "suppress",
  "reason": "High fatigue score (>80)"
}
```

**Adobe API Call**:
```http
POST https://platform.adobe.io/data/core/ups/segment/jobs
Authorization: Bearer {access_token}
x-api-key: {api_key}

{
  "segmentId": "AUD3",
  "action": "deactivate"
}
```

**Response**:
```json
{
  "status": "success",
  "jobId": "job-12346",
  "segmentId": "AUD3",
  "action": "deactivate"
}
```

---

## 🧪 **Testing Strategy**

### **Stage 1: Mock Client Testing** (Current - Safe)

```python
# config.py
USE_MOCK_ADOBE = True
ENABLE_ADOBE_EXECUTION = True  # Execute to mock (logs only)

# Result: Logs show "[MOCK] Would update campaign 5 budget to ₹600,000"
```

**Benefits**:
- ✅ Test execution logic without Adobe access
- ✅ Verify all decision types are handled
- ✅ Check error handling and logging
- ✅ Safe for development

---

### **Stage 2: Real Client, Read-Only** (When you get credentials)

```python
# config.py
USE_MOCK_ADOBE = False  # Real Adobe APIs
ENABLE_ADOBE_EXECUTION = False  # Read-only mode

# Result: Reads real Maruti data, generates recommendations, but doesn't execute
```

**Benefits**:
- ✅ Verify real data integration
- ✅ Test with production scale
- ✅ Review decisions before enabling execution
- ✅ Build confidence

---

### **Stage 3: Real Client, Limited Execution** (Pilot)

```python
# config.py
USE_MOCK_ADOBE = False
ENABLE_ADOBE_EXECUTION = True

# NEW - Add execution limits
MAX_CAMPAIGNS_TO_UPDATE = 5  # Start with just 5 campaigns
MAX_BUDGET_CHANGE_PERCENT = 10  # Cap at 10% changes
REQUIRE_MANUAL_APPROVAL = True  # Human-in-the-loop
```

**Benefits**:
- ✅ Test real execution with minimal risk
- ✅ Monitor results closely
- ✅ Gradual rollout
- ✅ Easy rollback

---

### **Stage 4: Full Autonomous** (Production)

```python
# config.py
USE_MOCK_ADOBE = False
ENABLE_ADOBE_EXECUTION = True
MAX_CAMPAIGNS_TO_UPDATE = None  # No limit
REQUIRE_MANUAL_APPROVAL = False  # Fully autonomous
```

**Benefits**:
- ✅ Daily autonomous optimization
- ✅ Zero manual intervention
- ✅ Continuous improvement
- ✅ Scalable to 1000s of campaigns

---

## 🔒 **Safety Mechanisms**

### **1. Dry-Run Mode**

Always test with `ENABLE_ADOBE_EXECUTION = False` first:
```python
if config.ENABLE_ADOBE_EXECUTION:
    adobe_client.update_campaign_budget(...)
else:
    logger.info(f"DRY-RUN: Would update campaign {id} budget to {new_budget}")
```

---

### **2. Budget Constraints**

Already implemented in executor:
```python
# Maximum increase cap
max_budget = current_budget * 1.30  # 30% max increase
new_budget = min(new_budget, max_budget)

# Minimum budget floor
min_budget = 100.0  # ₹100 minimum
new_budget = max(new_budget, min_budget)
```

---

### **3. Budget Neutrality**

Total budget never changes:
```python
# Before changes: Total = ₹10,000,000
# After increases/decreases: Total = ₹10,200,000

# Rebalance to maintain neutrality:
scaling_factor = 10000000 / 10200000 = 0.98
all_budgets *= 0.98

# Final total = ₹10,000,000 ✅
```

---

### **4. Error Handling**

```python
try:
    result = adobe_client.update_campaign_budget(campaign_id, new_budget)
    logger.success(f"Updated campaign {campaign_id}")
except AdobeAPIError as e:
    logger.error(f"Failed to update campaign {campaign_id}: {e}")
    # Rollback or alert
    send_alert_to_ops_team(e)
```

---

### **5. Audit Trail**

Every execution logged:
```json
{
  "timestamp": "2025-12-14T02:05:23Z",
  "action": "budget_update",
  "campaign_id": 5,
  "old_budget": 500000.0,
  "new_budget": 600000.0,
  "tier": "high",
  "adobe_response": {
    "status": "success",
    "jobId": "job-789"
  },
  "agent_version": "v1.2-adobe",
  "execution_mode": "PRODUCTION"
}
```

---

## 📋 **Implementation Checklist**

### **Code Changes**:
- [ ] Update `Executor.__init__()` to accept `adobe_client` and `execute_to_adobe`
- [ ] Add `_execute_budget_to_adobe()` method
- [ ] Add `_execute_bid_to_adobe()` method
- [ ] Add `_execute_segment_action_to_adobe()` method
- [ ] Update `_deterministic_budget_reallocation()` to call Adobe
- [ ] Update `_apply_ad_group_bid_actions()` to call Adobe
- [ ] Update `_apply_audience_suppression()` to call Adobe
- [ ] Add `ENABLE_ADOBE_EXECUTION` flag to config
- [ ] Update `main_adobe.py` to initialize executor with client

### **Testing**:
- [ ] Test with mock client, execution enabled (dry-run logs)
- [ ] Test error handling (simulate API failures)
- [ ] Test with real client, execution disabled (read-only)
- [ ] Pilot with real client, limited execution (5 campaigns)
- [ ] Monitor results for 3-5 days
- [ ] Enable full autonomous execution

### **Documentation**:
- [ ] Update `ADOBE_INTEGRATION_STATUS.md` with Phase 4 status
- [ ] Document execution flags and safety modes
- [ ] Create runbook for monitoring/rollback
- [ ] Add execution metrics to dashboard

---

## ⚠️ **Important Notes**

1. **DO NOT enable execution without Adobe credentials** - The real client needs valid API keys

2. **Start with DRY-RUN mode** - Set `ENABLE_ADOBE_EXECUTION = False` initially

3. **Test thoroughly with mock** - Verify all decision types execute correctly

4. **Monitor closely in pilot** - Watch first 5-10 executions carefully

5. **Have rollback plan** - Know how to revert changes if needed

---

## 🎓 **When to Enable Phase 4**

**Enable execution when**:
1. ✅ You have Adobe credentials from Maruti Suzuki
2. ✅ You've tested with mock client successfully
3. ✅ You've reviewed real data in read-only mode
4. ✅ Stakeholders approve autonomous execution
5. ✅ Monitoring dashboards are in place
6. ✅ Rollback procedures documented

**Current blockers**:
- ❌ No Adobe credentials yet (waiting for Maruti)
- ✅ Mock infrastructure ready
- ✅ Execution logic designed
- ✅ Safety mechanisms in place

---

## 🚀 **Summary**

Phase 4 is **architecturally ready** but waiting for:
1. Adobe API credentials from Maruti Suzuki
2. Stakeholder approval for autonomous execution
3. Monitoring infrastructure setup

**Once credentials available**:
1. Enable mock execution → test → verify logs
2. Enable real read-only → review recommendations
3. Enable limited execution → pilot 5 campaigns
4. Enable full autonomous → daily optimization at scale

**Estimated time to implement** (when credentials ready): **2-3 days**

---

**Status**: Design complete, ready for implementation ✅
