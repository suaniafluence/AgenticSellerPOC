"""State management for the sales agent system."""
from typing import TypedDict, List, Dict, Any, Optional, Literal
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class LeadType(str, Enum):
    """Lead classification types."""
    HOT = "hot"
    WARM = "warm"
    COLD = "cold"
    QUALIFIED = "qualified"
    UNQUALIFIED = "unqualified"


class LeadSector(str, Enum):
    """Lead sector classification."""
    SAAS = "saas"
    ECOMMERCE = "ecommerce"
    MANUFACTURING = "manufacturing"
    SERVICES = "services"
    HEALTHCARE = "healthcare"
    FINANCE = "finance"
    OTHER = "other"


class CompanySize(str, Enum):
    """Company size classification."""
    STARTUP = "startup"  # 1-10 employees
    SME = "sme"  # 11-50 employees
    MEDIUM = "medium"  # 51-200 employees
    ENTERPRISE = "enterprise"  # 200+ employees


@dataclass
class LeadInfo:
    """Information about the lead/prospect."""
    name: Optional[str] = None
    company: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    sector: Optional[LeadSector] = None
    company_size: Optional[CompanySize] = None
    budget: Optional[float] = None
    decision_maker: bool = False
    pain_points: List[str] = field(default_factory=list)
    interests: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "company": self.company,
            "email": self.email,
            "phone": self.phone,
            "sector": self.sector.value if self.sector else None,
            "company_size": self.company_size.value if self.company_size else None,
            "budget": self.budget,
            "decision_maker": self.decision_maker,
            "pain_points": self.pain_points,
            "interests": self.interests,
        }


@dataclass
class Message:
    """A message in the conversation."""
    role: Literal["user", "assistant", "system"]
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }


@dataclass
class Offer:
    """An offer made to the prospect."""
    product: str
    price: float
    features: List[str]
    discount: float = 0.0
    trial_period: Optional[int] = None  # days
    commitment_period: Optional[int] = None  # months
    conditions: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "product": self.product,
            "price": self.price,
            "features": self.features,
            "discount": self.discount,
            "trial_period": self.trial_period,
            "commitment_period": self.commitment_period,
            "conditions": self.conditions,
        }

    def final_price(self) -> float:
        """Calculate final price after discount."""
        return self.price * (1 - self.discount / 100)


class SalesState(TypedDict):
    """
    Global state for the sales agent system.

    This state is passed through all nodes in the LangGraph workflow.
    """
    # Conversation tracking
    messages: List[Dict[str, Any]]  # Message history
    current_message: str  # Latest user message

    # Lead information
    lead_info: Dict[str, Any]  # LeadInfo as dict
    lead_type: Optional[str]  # LeadType classification
    lead_score: float  # 0-100 score

    # Sales process
    current_agent: str  # Which agent is active
    last_agent: Optional[str]  # Previous agent
    offers_made: List[Dict[str, Any]]  # List of offers
    current_offer: Optional[Dict[str, Any]]  # Current active offer

    # Objections and negotiations
    objections: List[str]  # List of objections raised
    objections_handled: List[str]  # Objections that were addressed
    negotiation_count: int  # Number of negotiation rounds

    # Status flags
    qualified: bool  # Is the lead qualified?
    converted: bool  # Did they accept an offer?
    escalated: bool  # Needs human intervention?
    closed: bool  # Conversation closed

    # Metadata
    session_id: str  # Unique session identifier
    context: str  # Current context/phase
    next_action: Optional[str]  # Next recommended action
    crm_synced: bool  # Has data been synced to CRM?

    # Memory and insights
    key_insights: List[str]  # Important insights from conversation
    sentiment: str  # Overall sentiment (positive, neutral, negative)


def create_initial_state(initial_message: str, session_id: str) -> SalesState:
    """Create initial state for a new sales session."""
    return SalesState(
        messages=[],
        current_message=initial_message,
        lead_info=LeadInfo().to_dict(),
        lead_type=None,
        lead_score=0.0,
        current_agent="start",
        last_agent=None,
        offers_made=[],
        current_offer=None,
        objections=[],
        objections_handled=[],
        negotiation_count=0,
        qualified=False,
        converted=False,
        escalated=False,
        closed=False,
        session_id=session_id,
        context="initial",
        next_action=None,
        crm_synced=False,
        key_insights=[],
        sentiment="neutral",
    )


def add_message(state: SalesState, role: str, content: str, metadata: Optional[Dict] = None) -> None:
    """Add a message to the state."""
    message = Message(role=role, content=content, metadata=metadata or {})
    state["messages"].append(message.to_dict())


def get_conversation_history(state: SalesState, last_n: Optional[int] = None) -> List[Dict[str, Any]]:
    """Get conversation history, optionally limited to last N messages."""
    messages = state["messages"]
    if last_n:
        return messages[-last_n:]
    return messages
