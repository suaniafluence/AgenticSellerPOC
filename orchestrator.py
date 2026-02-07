"""LangGraph orchestrator with MCP (Multi-Agent Control Plane) logic."""
import re
from typing import Literal
from langgraph.graph import StateGraph, END
from state import SalesState, create_initial_state, add_message
from agents import (
    ProspectClassifier,
    SellerAgent,
    NegotiatorAgent,
    CRMAgent,
    SupervisorAgent,
)
from memory import get_memory_store
import uuid


class SalesOrchestrator:
    """
    Multi-Agent Control Plane (MCP) for the sales system.

    Orchestrates the flow between different specialized agents
    based on the conversation state and business logic.
    """

    def __init__(self):
        """Initialize the orchestrator with all agents."""
        # Initialize agents
        self.classifier = ProspectClassifier()
        self.seller = SellerAgent()
        self.negotiator = NegotiatorAgent()
        self.crm = CRMAgent()
        self.supervisor = SupervisorAgent()

        # Initialize memory
        self.memory = get_memory_store()

        # Build the graph
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow."""
        # Create the graph
        workflow = StateGraph(SalesState)

        # Add nodes for each agent
        workflow.add_node("mcp_decision", self._mcp_decision_node)
        workflow.add_node("classifier", self._classifier_node)
        workflow.add_node("seller", self._seller_node)
        workflow.add_node("negotiator", self._negotiator_node)
        workflow.add_node("supervisor", self._supervisor_node)
        workflow.add_node("crm", self._crm_node)

        # Set entry point
        workflow.set_entry_point("mcp_decision")

        # Add conditional edges from MCP decision node
        workflow.add_conditional_edges(
            "mcp_decision",
            self._route_from_mcp,
            {
                "classifier": "classifier",
                "seller": "seller",
                "negotiator": "negotiator",
                "supervisor": "supervisor",
                "crm": "crm",
                "end": END,
            }
        )

        # All agents route back to MCP for next decision
        for node in ["classifier", "seller", "negotiator", "supervisor"]:
            workflow.add_edge(node, "mcp_decision")

        # CRM is terminal - goes to END
        workflow.add_edge("crm", END)

        return workflow.compile()

    def _mcp_decision_node(self, state: SalesState) -> SalesState:
        """
        Multi-Agent Control Plane decision node.

        This is the central control logic that decides which agent
        should handle the next step based on the current state.
        """
        # First interaction - always classify
        if not state.get("lead_type"):
            state["next_action"] = "classifier"
            state["context"] = "initial_classification"
            return state

        # Check if conversation is closed
        if state.get("closed", False):
            state["next_action"] = "end"
            return state

        # Check if already routed to CRM
        if state.get("next_action") == "crm" or state.get("next_action") == "end":
            return state

        # Check for explicit conversion (only after an offer has been made)
        if state.get("offers_made") and self._check_for_conversion(state):
            state["converted"] = True
            state["next_action"] = "crm"
            return state

        # Check for escalation
        if state.get("escalated", False):
            state["next_action"] = "crm"
            return state

        # Follow the next_action set by previous agent
        next_action = state.get("next_action")

        # If no next action is set, use supervisor to decide
        if not next_action or next_action == "wait_for_response":
            state["next_action"] = "supervisor"

        return state

    def _route_from_mcp(self, state: SalesState) -> Literal["classifier", "seller", "negotiator", "supervisor", "crm", "end"]:
        """Route from MCP to the appropriate agent."""
        next_action = state.get("next_action", "end")

        if next_action == "classifier":
            return "classifier"
        elif next_action == "seller":
            return "seller"
        elif next_action == "negotiator":
            return "negotiator"
        elif next_action == "supervisor":
            return "supervisor"
        elif next_action == "crm":
            return "crm"
        else:
            return "end"

    def _classifier_node(self, state: SalesState) -> SalesState:
        """Prospect Classifier node."""
        return self.classifier.process(state)

    def _seller_node(self, state: SalesState) -> SalesState:
        """Seller node."""
        return self.seller.process(state)

    def _negotiator_node(self, state: SalesState) -> SalesState:
        """Negotiator node."""
        return self.negotiator.process(state)

    def _supervisor_node(self, state: SalesState) -> SalesState:
        """Supervisor node."""
        return self.supervisor.process(state)

    def _crm_node(self, state: SalesState) -> SalesState:
        """CRM node."""
        state = self.crm.process(state)

        # Save to memory
        session_id = state.get("session_id", "")
        self.memory.save_session(session_id, state)

        # Save insights
        for insight in state.get("key_insights", []):
            self.memory.save_insight(session_id, insight)

        return state

    def _check_for_conversion(self, state: SalesState) -> bool:
        """Check if the prospect has converted based on their message."""
        current_message = state.get("current_message", "").lower()

        # Positive conversion signals - use word boundary matching to avoid
        # false positives (e.g. "ok" matching inside "TikTok")
        conversion_keywords = [
            "yes", "sure", r"\bok\b", "okay", "let's do it", "let's go",
            "sign me up", "i'll take it", "sounds good", "deal",
            "agreed", "accept", "i'm in", "let's start", "proceed",
            "d'accord", "je suis intéressé", "allons-y", "banco",
            "on y va", "je prends", "je signe", "c'est bon",
            "ça marche", "parfait", "je valide", "on fonce",
        ]

        return any(re.search(keyword, current_message) for keyword in conversion_keywords)

    def run_conversation(self, initial_message: str, session_id: str = None, lead_info: dict = None) -> dict:
        """
        Run a complete sales conversation.

        Args:
            initial_message: The first message from the prospect
            session_id: Optional session ID (generates one if not provided)
            lead_info: Optional lead info dict with prospect contact data

        Returns:
            Final state of the conversation
        """
        # Generate session ID if not provided
        if not session_id:
            session_id = str(uuid.uuid4())

        # Create initial state
        state = create_initial_state(initial_message, session_id)

        # Pre-populate lead_info with contact data from prospect form
        if lead_info:
            existing = state.get("lead_info", {})
            existing.update({k: v for k, v in lead_info.items() if v is not None})
            state["lead_info"] = existing

        # Add initial message to history
        add_message(state, "user", initial_message)

        # Run the graph
        final_state = self.graph.invoke(state)

        return final_state

    def continue_conversation(self, session_id: str, new_message: str) -> dict:
        """
        Continue an existing conversation.

        Args:
            session_id: Session ID of the conversation
            new_message: New message from the prospect

        Returns:
            Updated state of the conversation
        """
        # Load existing state
        state = self.memory.load_session(session_id)

        if not state:
            raise ValueError(f"No session found with ID: {session_id}")

        # Update with new message
        state["current_message"] = new_message
        add_message(state, "user", new_message)

        # Reset next_action to let MCP decide
        state["next_action"] = None

        # Continue the graph
        final_state = self.graph.invoke(state)

        return final_state

    def get_conversation_history(self, session_id: str) -> list:
        """Get the conversation history for a session."""
        state = self.memory.load_session(session_id)
        if not state:
            return []

        return state.get("messages", [])

    def export_graph_visualization(self, filepath: str = "sales_graph.png"):
        """Export a visualization of the graph (requires pygraphviz)."""
        try:
            from IPython.display import Image, display
            display(Image(self.graph.get_graph().draw_mermaid_png()))
        except ImportError:
            print("Graph visualization requires pygraphviz and IPython")
            print("Install with: pip install pygraphviz ipython")
