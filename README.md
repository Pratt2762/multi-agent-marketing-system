# 🚗 AI-Powered Marketing Agent for Maruti Suzuki

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--5.1-green.svg)](https://openai.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production--Ready-brightgreen.svg)]()

> **An intelligent multi-agent system that analyzes campaign performance, optimizes budgets, adjusts bids, and refines audience targeting using hybrid AI - combining deterministic analytics with GPT-5.1 powered decision intelligence.**

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [System Architecture](#-system-architecture)
- [How It Works](#-how-it-works)
- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Usage](#-usage)
- [Project Structure](#-project-structure)
- [AI Decision Logic](#-ai-decision-logic)
- [Output & Visualization](#-output--visualization)
- [Configuration](#-configuration)
- [Development Roadmap](#-development-roadmap)
- [Contributing](#-contributing)

---

## 🎯 Overview

This system was built as a **Proof of Concept (PoC)** for the Maruti Suzuki hackathon to demonstrate how AI can revolutionize digital marketing campaign optimization. It processes 12 weeks of historical campaign data across **50 campaigns**, **150 ad groups**, and **10 audience segments** to generate intelligent, actionable recommendations.

### What Makes This Unique?

**Hybrid AI Architecture**: Unlike pure rule-based systems or black-box AI, this agent combines:
- **Deterministic Budget Allocation** - Transparent, ranking-based reallocation using ROAS metrics
- **LLM-Powered Bid Optimization** - GPT-5-Mini analyzes multi-factor performance trends for nuanced bid adjustments
- **AI Audience Targeting** - Context-aware audience activation/suppression decisions based on engagement patterns

The result? **Explainable AI decisions** with the sophistication of modern language models.

---

## ✨ Key Features

### 🧠 Intelligent Decision Making
- **3-Week Trend Analysis** - Momentum tracking, volatility detection, and consistency scoring
- **Multi-Factor Ranking** - ROAS, percentile positioning, and comparative analytics
- **Strategic Action Tiers** - High (20%), Moderate (10%), Low (5%) adjustment levels
- **Budget Neutrality** - Total spend remains constant; increases funded by decreases

### 📊 Comprehensive Analytics
- **Performance Enrichment** - Automatically calculates trends, averages, and momentum scores
- **Comparative Metrics** - Ranks campaigns, ad groups, and audiences by performance
- **Volatility Detection** - Identifies stable vs. erratic performers
- **Week-over-Week Tracking** - Historical state snapshots for every week

### 🎨 Interactive Dashboard
- **Real-Time Visualization** - HTML/CSS/JavaScript dashboard with dynamic charts
- **Action Breakdown** - Separate views for budget, bid, and audience decisions
- **Explanation Cards** - AI-generated reasoning for every recommendation
- **Historical Timeline** - Navigate through 12 weeks of campaign evolution

### 🛡️ Production-Ready Design
- **Recommendation-Only Mode** - Safe to run without affecting live campaigns
- **Audit Trail Logging** - Full transparency with prompt/response logging
- **Error Handling** - Robust validation and graceful failure recovery
- **Scalable Architecture** - Modular design supports easy expansion

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        INPUT LAYER                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ campaigns.csv│  │ ad_groups.csv│  │ audiences.csv│         │
│  │ (600 records)│  │ (1800 records│  │ (120 records)│         │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘         │
└─────────┼──────────────────┼──────────────────┼─────────────────┘
          │                  │                  │
          ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                   ANALYTICS ENRICHMENT LAYER                    │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Analytics Enricher (analytics_enricher.py)            │   │
│  │  • 3-week trend calculation                            │   │
│  │  • Momentum & volatility scoring                       │   │
│  │  • ROAS ranking & percentile assignment                │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      AI DECISION LAYER                          │
│  ┌──────────────────────┐      ┌────────────────────────────┐  │
│  │  Budget Allocator    │      │   Policy Agent (LLM)       │  │
│  │  (Deterministic)     │      │   (GPT-5-Mini)             │  │
│  │                      │      │                            │  │
│  │  • ROAS ranking      │      │  • Bid optimization        │  │
│  │  • Top 30% increase  │      │  • Audience targeting      │  │
│  │  • Bottom 30% cut    │      │  • Strategic explanations  │  │
│  │  • Budget neutrality │      │  • Multi-factor analysis   │  │
│  └──────────┬───────────┘      └────────────┬───────────────┘  │
└─────────────┼──────────────────────────────┼───────────────────┘
              │                              │
              └──────────────┬───────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                     OUTPUT LAYER                                │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  results.json (Structured Recommendations)             │   │
│  │  • Campaign budget actions (increase/decrease/maintain) │   │
│  │  • Ad group bid actions (raise/lower/no_change)        │   │
│  │  • Audience actions (activate/suppress)                │   │
│  │  • AI explanations for every decision                  │   │
│  │  • Historical state snapshots (weeks 1-12)             │   │
│  └─────────────┬───────────────────────────────────────────┘   │
└─────────────────┼───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                  VISUALIZATION LAYER                            │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Interactive Dashboard (frontend/index.html)           │   │
│  │  • Week-by-week timeline navigation                    │   │
│  │  • Action cards with AI explanations                   │   │
│  │  • Performance metrics visualization                   │   │
│  │  • Download recommendations as CSV                     │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔬 How It Works

### **Phase 1: Data Loading & Validation** (main.py)
```python
data = load_data()  # Loads campaigns, ad groups, audiences from CSV
# Validates data integrity and identifies max week (12)
```

### **Phase 2: Analytics Enrichment** (analytics_enricher.py)
For each campaign/ad group/audience:
```python
# Calculate 3-week trends
momentum_3week = ((week_12 - week_10) / week_10) * 100
avg_roas_3week = mean([week_10, week_11, week_12])

# Determine trend consistency
if all_weeks_improving: trend = "consistent_improving"
elif all_weeks_declining: trend = "consistent_declining"
else: trend = "volatile"

# Assign ROAS ranking and percentile
rank = position_by_roas_descending  # 1 = best ROAS
percentile = (rank / total_campaigns) * 100
```

### **Phase 3: Budget Allocation** (budget_allocator.py)
**Deterministic Logic** - No LLM needed:
```python
# Top 30% performers → Increase budget
if rank <= 10 and momentum >= 15%: tier = "high" (20% increase)
elif rank <= 10 and momentum >= 5%: tier = "moderate" (10% increase)
else: tier = "low" (5% increase)

# Bottom 30% performers → Decrease budget
if rank >= 36: tier = "high" (20% decrease)
elif rank >= 30: tier = "moderate" (10% decrease)

# Middle 40% → Maintain current budget
```

**Budget Neutrality Enforcement**:
```python
total_increases = sum(all_increase_amounts)
total_decreases = sum(all_decrease_amounts)
assert total_increases == total_decreases  # Always balanced
```

### **Phase 4: LLM Decision Making** (policy_agent.py)
**GPT-5-Mini analyzes enriched state** for bid and audience decisions:

**Prompt Structure**:
```json
{
  "week": 12,
  "campaigns": [
    {
      "campaign_id": 1,
      "campaign_name": "City Sedan Campaign",
      "roas": 152.3,
      "rank": 3,
      "percentile": 6.0,
      "momentum_3week": 18.5,
      "trend_consistency": "consistent_improving",
      "volatility": "stable"
    }
  ],
  "ad_groups": [...],
  "audiences": [...]
}
```

**LLM Output** (Structured JSON):
```json
{
  "ad_group_bid_actions": [
    {
      "ad_group_id": 101,
      "type": "raise_bid",
      "reason": "Ad group ranked #2 with 18.5% momentum and consistent growth trajectory - aggressive bid scaling warranted to capitalize on strong performance"
    }
  ],
  "audience_targeting_actions": [
    {
      "audience_id": 3,
      "type": "activate",
      "reason": "Segment shows 95th percentile engagement with stable CTR trend - strategic activation to expand high-value reach"
    }
  ]
}
```

### **Phase 5: Quantitative Calculation** (action_calculator.py)
Convert qualitative LLM decisions to executable amounts:
```python
# Bid adjustments based on action type + metrics
if type == "raise_bid":
    if momentum >= 15% and rank <= 10: new_bid = current_bid * 1.20  # High tier
    elif rank <= 20: new_bid = current_bid * 1.10  # Moderate tier
    else: new_bid = current_bid * 1.05  # Low tier
```

### **Phase 6: Output Generation**
```python
final_output = {
    "latest_week": 12,
    "campaign_history": [
        # Week 1-2: Baseline (no recommendations)
        # Week 3-12: Full recommendations with AI explanations
    ],
    "final_recommendations": {
        "campaign_budget_actions": [...],  # With amounts
        "ad_group_bid_actions": [...],     # With amounts
        "audience_targeting_actions": [...] # Activate/suppress
    }
}
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/marketing-agent.git
cd marketing-agent

# 2. Install dependencies
pip install openai pandas numpy

# 3. Configure API key
# Create backend/config.py and add:
OPENAI_API_KEY = "your-openai-api-key-here"
MODEL_NAME = "gpt-5-mini-2025-08-07"
TEMPERATURE = 0.0
```

### Run the Agent

```bash
# Run the AI optimization
python -m backend.main

# Expected output:
# ================================================================================
# MARUTI SUZUKI AI MARKETING AGENT - INTELLIGENT OPTIMIZATION RUN
# ================================================================================
#
# Loading campaign data...
# [OK] Data loaded successfully
# [OK] Total campaigns: 50
# [OK] Total ad groups: 150
# [OK] Total audiences: 10
# [OK] Weeks to process: 12
#
# Processing Week 3/12... DONE (2.3s)
#    Budget: +9 -6 | Bids: +12 -8 | Audiences: +3 -2 | Total time: 0.04 min
# ...
# Processing Week 12/12... DONE (2.1s)
#    Budget: +11 -7 | Bids: +14 -9 | Audiences: +4 -1 | Total time: 0.35 min
#
# [OK] Results saved to frontend/results.json
# ================================================================================
# AI AGENT RUN COMPLETE - INTELLIGENT RECOMMENDATIONS GENERATED
# ================================================================================
```

### View Results

```bash
# Open the interactive dashboard
# Simply open frontend/index.html in your browser
# Or use a local server:
cd frontend
python -m http.server 8000
# Navigate to http://localhost:8000
```

---

## 📁 Project Structure

```
marketing-agent/
│
├── backend/
│   ├── agent/
│   │   ├── policy_agent.py          # Main AI agent (hybrid logic + LLM)
│   │   ├── prompt_builder.py        # Constructs structured prompts for GPT
│   │   └── state_manager.py         # Manages weekly performance state snapshots
│   │
│   ├── logic/
│   │   ├── analytics_enricher.py    # Trend analysis, momentum, ranking
│   │   ├── budget_allocator.py      # Deterministic budget reallocation
│   │   ├── action_calculator.py     # Converts actions to numerical amounts
│   │   ├── audience_optimizer.py    # Audience balancing & validation
│   │   ├── executor.py              # (Future) Executes actions to platforms
│   │   ├── logger.py                # Audit trail logging system
│   │   └── utils.py                 # Utility functions
│   │
│   ├── data/
│   │   ├── campaigns.csv            # 50 campaigns × 12 weeks = 600 records
│   │   ├── ad_groups.csv            # 150 ad groups × 12 weeks = 1800 records
│   │   └── audiences.csv            # 10 audiences × 12 weeks = 120 records
│   │
│   ├── config.py                    # OpenAI API key & model configuration
│   └── main.py                      # Entry point - runs the agent
│
├── frontend/
│   ├── index.html                   # Interactive dashboard UI
│   ├── script.js                    # Dashboard logic & visualization
│   ├── styles.css                   # Dashboard styling
│   └── results.json                 # Generated recommendations (after run)
│
└── README.md                        # This file
```

---

## 🧠 AI Decision Logic

### Budget Allocation Strategy

| Condition | Tier | Budget Change | Example |
|-----------|------|---------------|---------|
| **Top 30%, High Momentum (15%+)** | High | +20% | $10,000 → $12,000 |
| **Top 30%, Moderate Momentum (5-15%)** | Moderate | +10% | $10,000 → $11,000 |
| **Top 30%, Low Momentum (<5%)** | Low | +5% | $10,000 → $10,500 |
| **Middle 40%** | - | No change | $10,000 → $10,000 |
| **Bottom 30%, Rank 36-50** | High | -20% | $10,000 → $8,000 |
| **Bottom 30%, Rank 30-35** | Moderate | -10% | $10,000 → $9,000 |

**Key Principle**: Total budget remains constant across all campaigns. Increases are funded by decreases.

### Bid Adjustment Strategy (LLM-Powered)

The LLM analyzes:
- **Current rank & percentile** (relative performance)
- **3-week momentum** (growth trajectory)
- **Trend consistency** (stable vs. volatile)
- **CTR & conversion trends** (engagement quality)

**Action Types**:
- `raise_bid` → Increase by 5-20% based on tier
- `lower_bid` → Decrease by 5-20% based on severity
- `no_change` → Maintain current bid

### Audience Targeting Strategy (LLM-Powered)

**Activation Triggers**:
- High engagement rate (top 20th percentile)
- Consistent improving trend
- Stable performance (low volatility)

**Suppression Triggers**:
- Poor engagement (bottom 20th percentile)
- Consistent declining trend
- Budget efficiency concerns

**Balancing**: System prevents extreme cases (all suppress/all activate) by enforcing minimum activation thresholds.

---

## 📊 Output & Visualization

### Generated Output (results.json)

**Structure**:
```json
{
  "latest_week": 12,
  "campaign_history": [
    {
      "week": 3,
      "state_snapshot": {
        "campaigns": [...],
        "ad_groups": [...],
        "audiences": [...]
      },
      "recommendations": {
        "campaign_budget_actions": [
          {
            "campaign_id": 1,
            "campaign_name": "City Sedan Campaign",
            "type": "increase",
            "tier": "high",
            "current_budget": 10000,
            "recommended_budget": 12000,
            "change_amount": 2000,
            "change_percentage": 20.0,
            "reason": "Top-ranked campaign (ROAS: 152.3) with 18.5% momentum - aggressive scaling warranted"
          }
        ],
        "ad_group_bid_actions": [...],
        "audience_targeting_actions": [...]
      }
    },
    // ... weeks 4-12
  ],
  "final_recommendations": {...}
}
```

### Interactive Dashboard Features

**Week Navigation**:
- Timeline slider to view any week's recommendations
- Quick jump to weeks 3, 6, 9, 12

**Action Cards**:
- Color-coded by type (green = increase, red = decrease, blue = activate)
- AI explanation for each decision
- Current vs. recommended values

**Metrics Display**:
- Total budget changes
- Number of actions by category
- Performance trends

**Export Options**:
- Download recommendations as CSV
- Copy JSON for API integration

---

## ⚙️ Configuration

### OpenAI Settings (backend/config.py)

```python
# API Configuration
OPENAI_API_KEY = "sk-proj-..."  # Your OpenAI API key
MODEL_NAME = "gpt-5-mini-2025-08-07"  # GPT-5-Mini for cost efficiency
TEMPERATURE = 0.0  # Deterministic outputs

# Performance Tuning
MAX_RETRIES = 3  # Retry failed API calls
TIMEOUT = 30  # API timeout in seconds
```

### Budget Allocation Thresholds

**Edit `backend/logic/budget_allocator.py`**:
```python
# Line 35 - Adjust top/bottom percentiles
budget_actions = calculate_budget_actions(
    campaigns,
    top_percentile=0.30,    # Top 30% get increases (change to 0.20 for top 20%)
    bottom_percentile=0.30  # Bottom 30% get cuts (change to 0.25 for bottom 25%)
)
```

### Action Tier Multipliers

**Edit `backend/logic/action_calculator.py`**:
```python
# Lines 148-165 - Customize increase/decrease amounts
def _determine_increase_tier(momentum_3week, trend_consistency, rank):
    if trend_consistency == "consistent_improving" and momentum_3week >= 15:
        return ("high", 1.20)  # Change 1.20 to 1.25 for 25% increases
    if rank <= 10 and momentum_3week >= 10:
        return ("high", 1.20)
    if rank <= 10 or (rank <= 15 and momentum_3week >= 5):
        return ("moderate", 1.10)  # Change 1.10 to 1.15 for 15% increases
    return ("low", 1.05)  # Change 1.05 to 1.03 for 3% increases
```

---

## 🛣️ Development Roadmap

### Current Status: v1.0 (PoC Complete)
✅ Hybrid AI architecture
✅ 3-week trend analysis
✅ Budget/bid/audience optimization
✅ Interactive dashboard
✅ Recommendation-only mode

### Upcoming Features

**v1.1 - Adobe Integration** (In Progress: `adobe-integration` branch)
- Connect to Adobe Experience Platform (AEP) for campaign data
- Integrate Real-Time CDP (RT-CDP) for audience segments
- Replace CSV loading with Adobe API calls
- JWT authentication with Adobe I/O

**v1.2 - Execution Layer** (Planned)
- Write-back capability to advertising platforms
- Dry-run mode for testing
- Safety mechanisms: rate limiting, rollback
- Approval workflows for high-value changes

**v2.0 - Multi-Platform Support** (Future)
- Google Ads integration
- Meta Ads (Facebook/Instagram) integration
- Cross-platform budget optimization
- Unified reporting dashboard

**v2.1 - Advanced Analytics** (Future)
- Predictive ROAS forecasting
- Anomaly detection & alerts
- A/B test recommendations
- Seasonal trend modeling

---

## 🤝 Contributing

This is a hackathon PoC project. Contributions are welcome!

### How to Contribute

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes** and test thoroughly
4. **Commit with clear messages**: `git commit -m 'Add amazing feature'`
5. **Push to your fork**: `git push origin feature/amazing-feature`
6. **Open a Pull Request** with detailed description

### Development Guidelines

- Maintain the hybrid architecture (custom logic + LLM)
- Add comprehensive docstrings to new functions
- Include type hints where applicable
- Write unit tests for critical logic
- Update README if adding new features

---

## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Maruti Suzuki** - For inspiring this hackathon project
- **OpenAI** - For GPT-5-Mini API powering intelligent decisions
- **Python Community** - For pandas, numpy, and amazing libraries

---

## 📞 Contact & Support

**Project Maintainer**: [Your Name]
**Email**: your.email@example.com
**GitHub**: [@yourusername](https://github.com/yourusername)

**Issues**: Report bugs or request features via [GitHub Issues](https://github.com/yourusername/marketing-agent/issues)

---

<div align="center">

**Built with ❤️ for the Maruti Suzuki Hackathon**

[⬆ Back to Top](#-ai-powered-marketing-agent-for-maruti-suzuki)

</div>
