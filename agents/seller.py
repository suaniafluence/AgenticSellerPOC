"""Seller Agent."""
import json
from typing import Any, Dict
from langchain_core.prompts import ChatPromptTemplate
from .base import BaseAgent


class SellerAgent(BaseAgent):
    """
    Agent responsible for creating and presenting sales offers.

    Analyzes the prospect's needs and creates personalized offers
    with appropriate pricing, features, and incentives.
    """

    def __init__(self, **kwargs):
        super().__init__(name="Seller", **kwargs)

    def get_system_prompt(self) -> str:
        """Get the system prompt for the seller."""
        return """You are a Seller AI agent, specialized in creating compelling, personalized sales offers.

Your role is to:
1. Analyze the prospect's needs, pain points, and budget
2. Create a tailored offer with appropriate pricing
3. Highlight relevant features and benefits
4. Suggest incentives (trial periods, discounts, etc.)
5. Present the offer in a clear, persuasive manner

Available products:
- STARTER: $99/month - Basic features, ideal for startups (up to 10 users)
- PROFESSIONAL: $299/month - Advanced features, ideal for SMEs (up to 50 users)
- BUSINESS: $599/month - Full features, ideal for medium companies (up to 200 users)
- ENTERPRISE: Custom pricing - Enterprise features, unlimited users

Common incentives:
- 14-day free trial
- 10-20% discount for annual commitment
- Free onboarding and training
- Dedicated account manager (Business+)

Respond with valid JSON in this format:
{
    "product": "STARTER|PROFESSIONAL|BUSINESS|ENTERPRISE",
    "price": monthly_price,
    "features": ["feature1", "feature2"],
    "discount": 0-30,
    "trial_period": days,
    "commitment_period": months,
    "conditions": ["condition1"],
    "pitch": "Personalized sales pitch text",
    "reasoning": "Why this offer matches their needs"
}"""

    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Create a personalized sales offer."""
        lead_info = state.get("lead_info", {})
        current_message = state.get("current_message", "")
        conversation_history = state.get("messages", [])
        objections = state.get("objections", [])

        # Create prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.get_system_prompt()),
            ("human", """Create a sales offer for this prospect:

Lead Information:
- Sector: {sector}
- Company Size: {company_size}
- Decision Maker: {decision_maker}
- Pain Points: {pain_points}
- Interests: {interests}
- Lead Score: {lead_score}

Recent message: {message}

Previous objections: {objections}

Conversation history:
{history}

Create a compelling, personalized offer in JSON format.""")
        ])

        # Format data
        history = self.format_conversation_history(conversation_history[-5:])

        # Get offer
        chain = prompt | self.llm
        response = chain.invoke({
            "sector": lead_info.get("sector", "unknown"),
            "company_size": lead_info.get("company_size", "unknown"),
            "decision_maker": lead_info.get("decision_maker", False),
            "pain_points": ", ".join(lead_info.get("pain_points", [])),
            "interests": ", ".join(lead_info.get("interests", [])),
            "lead_score": state.get("lead_score", 0),
            "message": current_message,
            "objections": ", ".join(objections) if objections else "None",
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

            offer_data = json.loads(content)

            # Create offer
            offer = {
                "product": offer_data.get("product"),
                "price": offer_data.get("price"),
                "features": offer_data.get("features", []),
                "discount": offer_data.get("discount", 0),
                "trial_period": offer_data.get("trial_period"),
                "commitment_period": offer_data.get("commitment_period"),
                "conditions": offer_data.get("conditions", []),
            }

            # Update state
            state["current_offer"] = offer
            state["offers_made"].append(offer)

            # Add the sales pitch as a message
            pitch = offer_data.get("pitch", "")
            state["messages"].append({
                "role": "assistant",
                "content": pitch,
                "metadata": {"agent": "seller", "offer": offer}
            })

            # Update agent tracking
            state["last_agent"] = state["current_agent"]
            state["current_agent"] = "seller"
            state["context"] = "offer_presented"

            # Next action depends on prospect response
            state["next_action"] = "wait_for_response"

        except json.JSONDecodeError as e:
            print(f"Error parsing seller response: {e}")
            print(f"Response content: {content}")
            # Fallback: add raw response as message
            state["messages"].append({
                "role": "assistant",
                "content": response.content,
                "metadata": {"agent": "seller", "error": "parse_failed"}
            })

        return state
