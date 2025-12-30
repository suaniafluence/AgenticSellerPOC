"""Prospect Classifier Agent."""
import json
from typing import Any, Dict
from langchain_core.prompts import ChatPromptTemplate
from .base import BaseAgent
from state import LeadType, LeadSector, CompanySize


class ProspectClassifier(BaseAgent):
    """
    Agent responsible for classifying and qualifying leads.

    Analyzes prospect messages to determine:
    - Lead type (hot/warm/cold)
    - Industry sector
    - Company size
    - Pain points and interests
    - Decision-making authority
    """

    def __init__(self, **kwargs):
        super().__init__(name="Prospect_Classifier", **kwargs)

    def get_system_prompt(self) -> str:
        """Get the system prompt for the classifier."""
        return """You are a Prospect Classifier AI agent, specialized in analyzing potential customers.

Your role is to:
1. Classify leads as HOT, WARM, or COLD based on their message
2. Identify the industry sector (SAAS, ECOMMERCE, MANUFACTURING, SERVICES, HEALTHCARE, FINANCE, OTHER)
3. Estimate company size (STARTUP, SME, MEDIUM, ENTERPRISE)
4. Extract pain points and interests
5. Determine if they are a decision-maker
6. Calculate a lead score (0-100)

Classification criteria:
- HOT: Immediate need, budget available, decision-maker, specific requirements
- WARM: Interested but not urgent, exploring options, may need approval
- COLD: General inquiry, no immediate need, unclear budget

Respond ONLY with valid JSON in this exact format:
{
    "lead_type": "hot|warm|cold",
    "sector": "saas|ecommerce|manufacturing|services|healthcare|finance|other",
    "company_size": "startup|sme|medium|enterprise",
    "decision_maker": true|false,
    "pain_points": ["point1", "point2"],
    "interests": ["interest1", "interest2"],
    "lead_score": 0-100,
    "reasoning": "Brief explanation of classification",
    "key_insights": ["insight1", "insight2"]
}"""

    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Classify the prospect based on their message."""
        current_message = state.get("current_message", "")
        conversation_history = state.get("messages", [])

        # Create prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.get_system_prompt()),
            ("human", """Analyze this prospect:

Recent message: {message}

Conversation history:
{history}

Provide your classification in JSON format.""")
        ])

        # Format history
        history = self.format_conversation_history(conversation_history[-5:])

        # Get classification
        chain = prompt | self.llm
        response = chain.invoke({
            "message": current_message,
            "history": history or "No previous conversation"
        })

        # Parse response
        try:
            # Extract JSON from response
            content = response.content
            # Remove markdown code blocks if present
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            classification = json.loads(content)

            # Update state
            lead_info = state.get("lead_info", {})
            lead_info["sector"] = classification.get("sector")
            lead_info["company_size"] = classification.get("company_size")
            lead_info["decision_maker"] = classification.get("decision_maker", False)
            lead_info["pain_points"] = classification.get("pain_points", [])
            lead_info["interests"] = classification.get("interests", [])

            state["lead_info"] = lead_info
            state["lead_type"] = classification.get("lead_type")
            state["lead_score"] = classification.get("lead_score", 0)
            state["qualified"] = classification.get("lead_score", 0) >= 50

            # Add insights
            insights = classification.get("key_insights", [])
            state["key_insights"].extend(insights)

            # Update current agent
            state["last_agent"] = state["current_agent"]
            state["current_agent"] = "classifier"

            # Determine next action based on qualification
            if state["qualified"]:
                state["next_action"] = "seller"
                state["context"] = "qualified_lead"
            else:
                state["next_action"] = "nurture"
                state["context"] = "unqualified_lead"

        except json.JSONDecodeError as e:
            print(f"Error parsing classifier response: {e}")
            print(f"Response content: {content}")
            # Set defaults if parsing fails
            state["qualified"] = False
            state["lead_score"] = 0
            state["next_action"] = "seller"  # Try seller anyway

        return state
