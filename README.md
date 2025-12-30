# 🤖 Agentic Seller POC - Multi-Channel Adaptive Sales Agent

An advanced Proof of Concept for an autonomous multi-agent sales system powered by **LangGraph** and LLMs. This system simulates intelligent sales conversations with adaptive behavior, handling lead qualification, offer creation, negotiation, and CRM integration.

## 🎯 Overview

This POC demonstrates a **Multi-Agent Control Plane (MCP)** architecture where specialized AI agents collaborate to:

- ✅ **Qualify leads** - Classify prospects as hot/warm/cold with scoring
- 💼 **Create personalized offers** - Tailored pricing and features based on needs
- 🤝 **Negotiate intelligently** - Handle objections and adjust offers dynamically
- 📊 **Sync with CRM** - Record conversations and create tasks for sales team
- 👨‍💼 **Supervise flow** - Oversee the process and escalate when needed

## 🏗️ Architecture

### Multi-Agent System

The system consists of 5 specialized agents orchestrated by LangGraph:

```
┌─────────────────────────────────────────────────────────┐
│                    MCP Decision Node                     │
│              (Multi-Agent Control Plane)                 │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  Classifier  │ │    Seller    │ │  Negotiator  │
│              │ │              │ │              │
│ - Qualify    │ │ - Create     │ │ - Handle     │
│ - Score      │ │   offers     │ │   objections │
│ - Categorize │ │ - Pitch      │ │ - Adjust     │
└──────────────┘ └──────────────┘ └──────────────┘
        │            │            │
        └────────────┼────────────┘
                     ▼
        ┌────────────────────────┐
        │      Supervisor        │
        │ - Analyze state        │
        │ - Route decisions      │
        │ - Check conversion     │
        └────────────┬───────────┘
                     ▼
        ┌────────────────────────┐
        │       CRM Agent        │
        │ - Sync data            │
        │ - Create tasks         │
        │ - Generate insights    │
        └────────────────────────┘
```

### Agents Description

| Agent | Role | Capabilities |
|-------|------|-------------|
| **Prospect_Classifier** | Lead Qualification | Detects lead type (hot/warm/cold), sector, company size, pain points, decision-maker status. Scores 0-100. |
| **Seller** | Offer Creation | Creates personalized offers with pricing, features, trials, discounts based on prospect profile. |
| **Negotiator** | Objection Handling | Identifies objection categories (price, features, timing, etc.), adjusts offers, finds win-win solutions. |
| **Supervisor** | Process Oversight | Analyzes conversation state, routes to appropriate agents, detects conversion, triggers escalation. |
| **CRM_Agent** | Data Management | Syncs to CRM, creates follow-up tasks, generates conversation summaries and insights. |

## 🚀 Quick Start

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd AgenticSellerPOC
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment**
```bash
cp .env.example .env
# Edit .env and add your API keys
```

Required API keys:
- `OPENAI_API_KEY` - For GPT-4 (recommended)
- `ANTHROPIC_API_KEY` - For Claude (alternative)

### Usage

#### Interactive Demo

Run an interactive conversation as a prospect:

```bash
python main.py demo
```

This launches an interactive session where you can chat with the AI sales agents.

#### Pre-built Scenarios

Run one of the example scenarios:

```bash
python main.py scenario hot_lead
python main.py scenario price_negotiation
python main.py scenario enterprise_escalation
```

Available scenarios:
- `hot_lead` - Quick conversion with minimal negotiation
- `price_negotiation` - Multiple rounds of price discussion
- `feature_concerns` - Specific feature requirements
- `timing_objection` - Prospect wants to wait
- `enterprise_escalation` - Complex deal requiring human involvement
- `competitor_comparison` - Evaluating against competitors
- `unqualified_cold` - Low-quality lead for nurturing
- `decision_maker_check` - Needs manager approval
- `multiple_objections` - Complex sale with several concerns
- `rapid_conversion` - Very hot lead, instant close

List all scenarios:
```bash
python examples.py
```

## 📊 Example Conversation Flow

```
👤 PROSPECT: Hi, I'm the CTO of a 50-person SaaS startup. We need a sales
             automation solution ASAP. Budget approved for $500/month.

🔍 CLASSIFIER: [Analyzes → HOT lead, SAAS sector, SME size, Score: 85/100]

💼 SELLER: Great to meet you! Based on your needs, I recommend our
          PROFESSIONAL plan at $299/month with:
          - Advanced automation features
          - Up to 50 users (perfect for your team)
          - 14-day free trial
          - 15% discount for annual commitment

👤 PROSPECT: That sounds good! Can we get a 14-day trial to test it?

👨‍💼 SUPERVISOR: [Analyzes → Positive sentiment, likely conversion]

💼 SELLER: Absolutely! The 14-day trial is included with no credit card
          required. You'll have full access to all features.

👤 PROSPECT: Perfect! Let's do it. Sign us up for the PROFESSIONAL plan.

👨‍💼 SUPERVISOR: [Detects → CONVERTED]

📊 CRM: Great! I've created your account and you'll receive a confirmation
        email shortly with next steps.

✅ RESULT: Converted | Lead Score: 85/100 | 4 messages
```

## 🧠 MCP (Multi-Agent Control Plane) Logic

The MCP is the brain of the system, implementing adaptive workflow control:

### State Management

The system maintains a comprehensive state including:
- Conversation history
- Lead information and classification
- Offers made and current offer
- Objections raised and handled
- Negotiation count
- Status flags (qualified, converted, escalated, closed)
- Sentiment and insights

### Routing Logic

```python
START → MCP Decision
  ├─ No lead_type? → Classifier → MCP
  ├─ Qualified & no offer? → Seller → MCP
  ├─ Objection detected? → Negotiator → MCP
  ├─ Need decision? → Supervisor → MCP
  ├─ Converted/Escalated? → CRM → END
  └─ Unknown state? → Supervisor → MCP
```

### Adaptive Behavior

- **First interaction**: Always classify the lead
- **After classification**: Route to Seller if qualified, otherwise nurture
- **After offer**: Wait for response, route to Negotiator if objection
- **After negotiation**: Re-offer or escalate after 3 rounds
- **Conversion detection**: Keyword analysis + sentiment
- **Escalation triggers**: Complex requirements, large deals, too many negotiations

## 🔧 Configuration

### Products & Pricing

Default product catalog (configurable in `agents/seller.py`):

| Product | Price/Month | Users | Target |
|---------|-------------|-------|--------|
| STARTER | $99 | Up to 10 | Startups |
| PROFESSIONAL | $299 | Up to 50 | SMEs |
| BUSINESS | $599 | Up to 200 | Medium companies |
| ENTERPRISE | Custom | Unlimited | Large enterprises |

### Negotiation Limits

Configurable in `agents/negotiator.py`:
- Maximum discount: 30% (enterprise only)
- Trial period: Up to 30 days
- Auto-escalation: After 3 negotiation rounds

## 💾 Memory & Persistence

The system supports two memory backends:

### In-Memory Store (Default)
Fast, for testing and demos. Data lost on restart.

### JSON File Store
Persistent storage to disk.

```python
from memory import set_memory_store, JSONFileStore

set_memory_store(JSONFileStore("./data"))
```

### Vector Database (Future)
For semantic search and advanced insights (Qdrant/Weaviate).

## 📈 Insights & Analytics

The CRM agent automatically captures:

- **Lead Classification**: Type, sector, size, score
- **Conversion Metrics**: Conversion rate, time to convert
- **Objection Patterns**: Common objections by sector/size
- **Negotiation Analysis**: Average rounds, discount patterns
- **Sentiment Tracking**: Positive/neutral/negative trends

## 🔌 CRM Integration

Currently supports mock CRM output. Easy to extend to:

- **HubSpot**: Via HubSpot API
- **Salesforce**: Via Salesforce API
- **Custom CRM**: Implement your own adapter

See `agents/crm.py` for integration points.

## 🛠️ Development

### Project Structure

```
AgenticSellerPOC/
├── agents/              # Specialized agent implementations
│   ├── __init__.py
│   ├── base.py         # Base agent class
│   ├── classifier.py   # Prospect classifier
│   ├── seller.py       # Offer creator
│   ├── negotiator.py   # Objection handler
│   ├── crm.py          # CRM integration
│   └── supervisor.py   # Process supervisor
├── config.py           # Configuration management
├── state.py            # State definitions and management
├── memory.py           # Memory storage backends
├── orchestrator.py     # LangGraph MCP orchestrator
├── main.py             # Main entry point
├── examples.py         # Example scenarios
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

### Adding a New Agent

1. Create a new file in `agents/`
2. Inherit from `BaseAgent`
3. Implement the `process(state)` method
4. Add to `orchestrator.py` graph
5. Update routing logic in MCP

### Extending State

Add new fields to `SalesState` in `state.py`:

```python
class SalesState(TypedDict):
    # ... existing fields ...
    your_new_field: YourType
```

## 🧪 Testing

Run different scenarios to test agent behavior:

```bash
# Test lead qualification
python main.py scenario hot_lead

# Test negotiation logic
python main.py scenario price_negotiation

# Test escalation
python main.py scenario enterprise_escalation
```

## 📝 Future Enhancements

- [ ] Vector database integration for semantic memory
- [ ] Multi-language support
- [ ] Voice/audio input handling
- [ ] Real-time CRM webhooks
- [ ] A/B testing framework for offers
- [ ] Sentiment analysis with dedicated model
- [ ] Team collaboration features
- [ ] Analytics dashboard
- [ ] Email/SMS integration
- [ ] Calendar integration for meetings

## 🤝 Contributing

This is a POC for demonstration purposes. Feel free to extend and adapt for your use case.

## 📄 License

MIT License - feel free to use and modify.

## 🙏 Acknowledgments

Built with:
- [LangGraph](https://github.com/langchain-ai/langgraph) - Multi-agent orchestration
- [LangChain](https://github.com/langchain-ai/langchain) - LLM framework
- [OpenAI GPT-4](https://openai.com) - Language model
- [Anthropic Claude](https://anthropic.com) - Alternative LLM

---

**Note**: This is a Proof of Concept for demonstration and educational purposes. For production use, add proper error handling, security measures, rate limiting, and human oversight.