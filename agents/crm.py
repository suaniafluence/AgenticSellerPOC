"""CRM Agent."""
import json
from typing import Any, Dict
from datetime import datetime
from .base import BaseAgent


class CRMAgent(BaseAgent):
    """
    Agent responsible for CRM integration and data management.

    Records conversations, tracks deals, updates contact information,
    and creates tasks for human sales team.
    """

    def __init__(self, **kwargs):
        super().__init__(name="CRM_Agent", **kwargs)

    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Sync data to CRM and create tasks."""
        lead_info = state.get("lead_info", {})
        session_id = state.get("session_id", "")
        converted = state.get("converted", False)
        escalated = state.get("escalated", False)

        # Create CRM record
        crm_record = {
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "lead_info": lead_info,
            "lead_type": state.get("lead_type"),
            "lead_score": state.get("lead_score"),
            "qualified": state.get("qualified"),
            "converted": converted,
            "escalated": escalated,
            "offers_made": state.get("offers_made", []),
            "final_offer": state.get("current_offer"),
            "objections": state.get("objections", []),
            "negotiation_rounds": state.get("negotiation_count", 0),
            "key_insights": state.get("key_insights", []),
            "sentiment": state.get("sentiment", "neutral"),
            "conversation_summary": self._create_summary(state),
        }

        # Simulate CRM sync (in production, this would call actual CRM API)
        print("\n" + "="*60)
        print("📊 CRM SYNC")
        print("="*60)
        print(json.dumps(crm_record, indent=2))
        print("="*60 + "\n")

        # Create tasks for sales team
        tasks = self._create_tasks(state)
        if tasks:
            print("📋 TASKS CREATED:")
            for i, task in enumerate(tasks, 1):
                print(f"{i}. {task}")
            print()

        # Update state
        state["crm_synced"] = True
        state["last_agent"] = state["current_agent"]
        state["current_agent"] = "crm"

        # Add CRM sync message
        if converted:
            message = "Great! I've recorded your information and created your account. You'll receive a confirmation email shortly with next steps."
        elif escalated:
            message = "I've recorded our conversation and a senior sales specialist will reach out to you within 24 hours to discuss your specific needs."
        else:
            message = "Thank you for your time. I've saved our conversation and you'll hear from us soon with more information."

        state["messages"].append({
            "role": "assistant",
            "content": message,
            "metadata": {"agent": "crm", "synced": True}
        })

        # Mark as closed
        state["closed"] = True
        state["next_action"] = "end"

        return state

    def _create_summary(self, state: Dict[str, Any]) -> str:
        """Create a summary of the conversation."""
        messages = state.get("messages", [])
        lead_score = state.get("lead_score", 0)
        converted = state.get("converted", False)

        message_count = len(messages)

        if converted:
            status = "✅ CONVERTED"
        elif state.get("escalated"):
            status = "⬆️ ESCALATED"
        elif state.get("qualified"):
            status = "🔥 QUALIFIED"
        else:
            status = "❄️ NOT QUALIFIED"

        return f"{status} | Lead Score: {lead_score} | Messages: {message_count}"

    def _create_tasks(self, state: Dict[str, Any]) -> list:
        """Create tasks for the sales team."""
        tasks = []

        if state.get("converted"):
            tasks.append("Send welcome email and onboarding materials")
            tasks.append("Schedule kickoff call")
            tasks.append("Set up account and provision access")

        elif state.get("escalated"):
            tasks.append("Senior sales rep to follow up within 24 hours")
            tasks.append("Prepare custom proposal addressing specific objections")
            objections = state.get("objections", [])
            if objections:
                tasks.append(f"Review objections: {', '.join(objections[:3])}")

        elif state.get("qualified"):
            tasks.append("Follow up in 3-5 days")
            tasks.append("Send case studies relevant to their sector")

        else:
            tasks.append("Add to nurture campaign")
            tasks.append("Follow up in 30 days")

        return tasks
