"""Negotiator Agent."""
import json
from typing import Any, Dict
from langchain_core.prompts import ChatPromptTemplate
from .base import BaseAgent


class NegotiatorAgent(BaseAgent):
    """
    Agent responsible for handling objections and negotiating terms.

    Analyzes objections, adjusts offers, and tries to find mutually
    beneficial solutions to close the deal.
    """

    def __init__(self, **kwargs):
        super().__init__(name="Negotiator", **kwargs)

    def get_system_prompt(self) -> str:
        """Get the system prompt for the negotiator."""
        return """You are a Negotiator AI agent, specialized in handling objections and finding win-win solutions.

Your role is to:
1. Identify and categorize objections (price, features, timing, authority, etc.)
2. Address objections with empathy and evidence
3. Adjust offers when appropriate (within limits)
4. Find creative solutions that satisfy both parties
5. Know when to escalate to human sales team

Negotiation guidelines:
- Maximum discount: 30% (only for enterprise deals with long commitments)
- Can extend trial period up to 30 days
- Can add features from higher tiers for medium/enterprise
- Always require commitment for larger discounts
- Budget objections: offer payment plans, phased implementation
- Feature objections: explain value or suggest alternatives
- Timing objections: create urgency with limited-time offers

Objection categories:
- PRICE: "Too expensive", "Over budget", "Need cheaper option"
- FEATURES: "Missing X feature", "Need more/less functionality"
- TIMING: "Not right now", "Need to wait", "Next quarter"
- AUTHORITY: "Need to ask boss", "Requires approval"
- COMPETITION: "Competitor offers more", "Already using X"
- TRUST: "Not sure if it works", "Need proof", "What about support"

Respond with valid JSON:
{
    "objection_category": "PRICE|FEATURES|TIMING|AUTHORITY|COMPETITION|TRUST",
    "objection_summary": "Brief summary of the objection",
    "response_strategy": "How you will address it",
    "adjusted_offer": {
        "product": "same or different product",
        "price": adjusted_price,
        "discount": 0-30,
        "trial_period": days,
        "commitment_period": months,
        "conditions": ["new conditions"],
        "features": ["feature list"]
    },
    "response": "Your response to the prospect",
    "should_escalate": true|false,
    "escalation_reason": "Why escalation is needed (if applicable)"
}"""

    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Handle objections and negotiate."""
        current_message = state.get("current_message", "")
        current_offer = state.get("current_offer", {})
        objections = state.get("objections", [])
        negotiation_count = state.get("negotiation_count", 0)
        lead_info = state.get("lead_info", {})
        conversation_history = state.get("messages", [])

        # Check if we've negotiated too many times
        if negotiation_count >= 3:
            state["escalated"] = True
            state["next_action"] = "escalate"
            state["messages"].append({
                "role": "assistant",
                "content": "I appreciate your interest and want to ensure we find the perfect solution for you. Let me connect you with our senior sales specialist who can discuss custom options tailored to your specific needs.",
                "metadata": {"agent": "negotiator", "action": "escalate"}
            })
            return state

        # Create prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.get_system_prompt()),
            ("human", """Handle this negotiation:

Prospect's message: {message}

Current offer:
- Product: {product}
- Price: ${price}/month
- Discount: {discount}%
- Trial: {trial_period} days
- Features: {features}

Previous objections: {previous_objections}
Negotiation round: {negotiation_round}

Lead context:
- Sector: {sector}
- Company size: {company_size}
- Lead score: {lead_score}

Conversation history:
{history}

Provide your negotiation response in JSON format.""")
        ])

        # Format data
        history = self.format_conversation_history(conversation_history[-5:])

        # Get negotiation response
        chain = prompt | self.llm
        response = chain.invoke({
            "message": current_message,
            "product": current_offer.get("product", "N/A"),
            "price": current_offer.get("price", 0),
            "discount": current_offer.get("discount", 0),
            "trial_period": current_offer.get("trial_period", 0),
            "features": ", ".join(current_offer.get("features", [])),
            "previous_objections": ", ".join(objections[-3:]) if objections else "None",
            "negotiation_round": negotiation_count + 1,
            "sector": lead_info.get("sector", "unknown"),
            "company_size": lead_info.get("company_size", "unknown"),
            "lead_score": state.get("lead_score", 0),
            "history": history or "No previous conversation"
        })

        # Parse response
        try:
            content = response.content
            # Remove markdown code blocks if present
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            negotiation = json.loads(content)

            # Track objection
            objection_summary = negotiation.get("objection_summary", current_message)
            state["objections"].append(objection_summary)

            # Update offer if adjusted
            if "adjusted_offer" in negotiation:
                adjusted_offer = negotiation["adjusted_offer"]
                state["current_offer"] = adjusted_offer
                state["offers_made"].append(adjusted_offer)

            # Add response to conversation
            response_text = negotiation.get("response", "")
            state["messages"].append({
                "role": "assistant",
                "content": response_text,
                "metadata": {
                    "agent": "negotiator",
                    "objection_category": negotiation.get("objection_category"),
                    "negotiation_round": negotiation_count + 1
                }
            })

            # Update state
            state["negotiation_count"] = negotiation_count + 1
            state["last_agent"] = state["current_agent"]
            state["current_agent"] = "negotiator"
            state["context"] = "negotiating"

            # Check for escalation
            if negotiation.get("should_escalate", False):
                state["escalated"] = True
                state["next_action"] = "escalate"
                state["key_insights"].append(
                    f"Escalation needed: {negotiation.get('escalation_reason', 'Unknown')}"
                )
            else:
                state["next_action"] = "wait_for_response"

        except json.JSONDecodeError as e:
            print(f"Error parsing negotiator response: {e}")
            print(f"Response content: {content}")
            # Fallback: add raw response
            state["messages"].append({
                "role": "assistant",
                "content": response.content,
                "metadata": {"agent": "negotiator", "error": "parse_failed"}
            })

        return state
