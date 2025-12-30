"""Example scenarios for testing the sales agent system."""

SCENARIOS = {
    "hot_lead": {
        "name": "Hot Lead - Quick Conversion",
        "description": "A qualified prospect ready to buy, minimal negotiation needed",
        "messages": [
            "Hi, I'm the CTO of a 50-person SaaS startup. We need a sales automation solution ASAP. We have budget approved for up to $500/month. What can you offer?",
            "That sounds good! Can we get a 14-day trial to test it out?",
            "Perfect! Let's do it. Sign us up for the PROFESSIONAL plan with the trial."
        ]
    },

    "price_negotiation": {
        "name": "Price Negotiation - Multiple Rounds",
        "description": "Prospect interested but concerned about price, needs negotiation",
        "messages": [
            "Hello, I run a small e-commerce business with 15 employees. I'm looking for a CRM solution but I'm on a tight budget.",
            "That's more than I wanted to spend. I was thinking more like $50-75/month. Do you have anything in that range?",
            "Hmm, still a bit high. What if I commit to a full year upfront? Can you give me a better discount?",
            "Okay, that works for me. Let's go with the annual plan at 20% off."
        ]
    },

    "feature_concerns": {
        "name": "Feature Requirements - Needs Specific Functionality",
        "description": "Prospect has specific feature requirements and needs clarification",
        "messages": [
            "I'm interested in your product, but I need to know - does it integrate with Salesforce? That's a must-have for us.",
            "Good to know. What about custom reporting and analytics? We need very detailed sales metrics.",
            "And one more thing - we're a team of 75 people. Can your system handle that many users?",
            "Excellent! I think the BUSINESS plan would work for us. Let's proceed."
        ]
    },

    "timing_objection": {
        "name": "Timing Objection - Not Ready Now",
        "description": "Prospect interested but wants to wait, needs nurturing",
        "messages": [
            "Hi, I've been researching sales tools and came across your product. Looks interesting.",
            "It looks good, but we're not quite ready to make a decision yet. We're currently in the middle of Q4 planning.",
            "Maybe in January when our new budget kicks in. Can you follow up with me then?",
        ]
    },

    "enterprise_escalation": {
        "name": "Enterprise Deal - Requires Escalation",
        "description": "Large enterprise deal with complex requirements, needs human involvement",
        "messages": [
            "Hello, I represent a 500-person enterprise in the healthcare sector. We're looking for an enterprise-grade sales solution with very specific compliance requirements.",
            "We need HIPAA compliance, SSO integration with Okta, custom SLA agreements, and a dedicated support team. Can your system handle all of that?",
            "We're also looking at a multi-year contract, potentially 3-5 years. What kind of volume discounts can you offer for a deal this size?",
            "This is getting complex. I think we need to involve our procurement team and legal. Do you have someone senior I can speak with about custom enterprise terms?"
        ]
    },

    "competitor_comparison": {
        "name": "Competitor Comparison - Evaluating Options",
        "description": "Prospect comparing with competitors, needs strong value proposition",
        "messages": [
            "I'm currently using [Competitor X] but I'm not fully satisfied. What makes your solution different?",
            "That's interesting, but [Competitor X] is offering me a deal at $250/month for similar features. Why should I switch to you?",
            "Okay, the trial period is longer which is good. If I like it, I might switch. Let's start with the trial.",
        ]
    },

    "unqualified_cold": {
        "name": "Unqualified Cold Lead",
        "description": "Cold lead with no budget or decision authority, should be nurtured",
        "messages": [
            "Hey, just browsing. What do you guys do?",
            "Oh, CRM stuff. Yeah, we might need something like that eventually. How much does it cost?",
            "Whoa, that's way too expensive for us right now. We're just a 3-person team.",
            "Nah, I don't think so. Maybe in the future. Thanks anyway."
        ]
    },

    "decision_maker_check": {
        "name": "Not a Decision Maker - Needs Approval",
        "description": "Prospect is interested but needs manager approval",
        "messages": [
            "Hi, I'm a sales manager at a medium-sized company. I've been tasked with finding a new CRM for our 40-person sales team.",
            "This looks really good! The BUSINESS plan seems perfect for us.",
            "I love it, but I need to get approval from my VP of Sales first. Can you send me some materials I can share with them?",
            "Actually, would it be possible for someone from your team to do a demo for my VP? That might help get approval faster."
        ]
    },

    "multiple_objections": {
        "name": "Multiple Objections - Complex Sale",
        "description": "Prospect has multiple concerns that need to be addressed",
        "messages": [
            "I'm interested, but I have some concerns. First, the price seems high for what we need.",
            "Also, we're already using another tool and migration seems like a pain. How hard is it to switch?",
            "And what about training? Our team isn't super tech-savvy. Do you provide onboarding?",
            "Okay, those are good points. But I still need to think about it. It's a big decision."
        ]
    },

    "rapid_conversion": {
        "name": "Rapid Fire Conversion",
        "description": "Very hot lead, knows exactly what they want, quick close",
        "messages": [
            "I need your ENTERPRISE plan for 200 users, starting immediately. Already did my research, you're the best fit.",
            "Yes, let's do it. What's the next step?",
        ]
    }
}


def list_scenarios():
    """List all available scenarios."""
    print("\n📚 AVAILABLE SCENARIOS:\n")
    for key, scenario in SCENARIOS.items():
        print(f"  {key:25} - {scenario['name']}")
        print(f"  {' '*25}   {scenario['description']}\n")


if __name__ == "__main__":
    list_scenarios()
