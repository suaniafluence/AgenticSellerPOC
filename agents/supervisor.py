"""Supervisor Agent."""
import json
from typing import Any, Dict
from langchain_core.prompts import ChatPromptTemplate
from .base import BaseAgent


class SupervisorAgent(BaseAgent):
    """
    Agent responsible for supervising the overall sales process.

    Analyzes the conversation state and decides:
    - Whether the goal is achieved
    - Which agent should handle the next step
    - When to escalate to humans
    - When to close the conversation
    """

    def __init__(self, **kwargs):
        super().__init__(name="Supervisor", **kwargs)

    def get_system_prompt(self) -> str:
        """Get the system prompt for the supervisor."""
        return """You are a Supervisor AI agent, overseeing the entire sales process.

Your role is to:
1. Analyze the current state of the conversation
2. Determine if the goal is achieved (conversion or qualification)
3. Decide which agent should handle the next step
4. Identify when human escalation is needed
5. Recognize when the conversation should end

Decision criteria:

CONVERTED (Goal achieved):
- Prospect explicitly accepted the offer
- Clear commitment to purchase or start trial
- Action: Route to CRM_Agent

NEEDS_NEGOTIATION:
- Prospect raised objections or price concerns
- Wants modifications to the offer
- Action: Route to Negotiator

NEEDS_NEW_OFFER:
- Current offer not suitable
- Prospect's needs changed
- Action: Route to Seller

ESCALATE:
- Complex custom requirements
- Very large deal requiring approval
- Too many negotiation rounds (3+)
- Prospect explicitly asks for human contact
- Action: Route to CRM_Agent with escalation flag

CLOSE:
- Prospect clearly not interested
- Unqualified lead with no potential
- Conversation reached natural conclusion
- Action: Route to CRM_Agent

CONTINUE:
- Need more information
- Prospect engaged but undecided
- Action: Wait for more input

Respond with valid JSON:
{
    "analysis": "Brief analysis of current situation",
    "prospect_sentiment": "positive|neutral|negative",
    "goal_achieved": true|false,
    "conversion_probability": 0-100,
    "next_agent": "classifier|seller|negotiator|crm|none",
    "should_escalate": true|false,
    "should_close": true|false,
    "reasoning": "Explanation of decision",
    "recommended_action": "What should happen next"
}"""

    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Supervise the sales process and route to next agent."""
        current_message = state.get("current_message", "")
        conversation_history = state.get("messages", [])
        current_agent = state.get("current_agent", "")

        # Create context summary
        context = {
            "lead_type": state.get("lead_type"),
            "lead_score": state.get("lead_score", 0),
            "qualified": state.get("qualified", False),
            "offers_made_count": len(state.get("offers_made", [])),
            "objections_count": len(state.get("objections", [])),
            "negotiation_count": state.get("negotiation_count", 0),
            "converted": state.get("converted", False),
            "escalated": state.get("escalated", False),
        }

        # Create prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.get_system_prompt()),
            ("human", """Analyze this sales conversation and decide next steps:

Current message from prospect: {message}

Context:
- Lead Type: {lead_type}
- Lead Score: {lead_score}
- Qualified: {qualified}
- Offers Made: {offers_count}
- Objections: {objections_count}
- Negotiation Rounds: {negotiation_count}
- Converted: {converted}
- Escalated: {escalated}
- Last Agent: {last_agent}

Recent conversation:
{history}

Provide your analysis and routing decision in JSON format.""")
        ])

        # Format data
        history = self.format_conversation_history(conversation_history[-5:])

        # Get analysis
        chain = prompt | self.llm
        response = chain.invoke({
            "message": current_message,
            "lead_type": context["lead_type"] or "unknown",
            "lead_score": context["lead_score"],
            "qualified": context["qualified"],
            "offers_count": context["offers_made_count"],
            "objections_count": context["objections_count"],
            "negotiation_count": context["negotiation_count"],
            "converted": context["converted"],
            "escalated": context["escalated"],
            "last_agent": current_agent,
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

            analysis = json.loads(content)

            # Update state based on analysis
            state["sentiment"] = analysis.get("prospect_sentiment", "neutral")

            # Add insight
            state["key_insights"].append(
                f"Supervisor: {analysis.get('analysis', 'Analysis unavailable')}"
            )

            # Update agent tracking
            state["last_agent"] = state["current_agent"]
            state["current_agent"] = "supervisor"

            # Determine next action
            if analysis.get("goal_achieved") or analysis.get("should_close"):
                state["next_action"] = "crm"
                if analysis.get("should_escalate"):
                    state["escalated"] = True

            else:
                next_agent = analysis.get("next_agent", "none")
                if next_agent != "none":
                    state["next_action"] = next_agent
                else:
                    state["next_action"] = "wait_for_response"

        except json.JSONDecodeError as e:
            print(f"Error parsing supervisor response: {e}")
            print(f"Response content: {content}")
            # Default: continue conversation
            state["next_action"] = "wait_for_response"

        return state
