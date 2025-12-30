"""Unit tests for state management."""
import pytest
from datetime import datetime
from state import (
    SalesState,
    LeadType,
    LeadSector,
    CompanySize,
    LeadInfo,
    Message,
    Offer,
    create_initial_state,
    add_message,
    get_conversation_history,
)


class TestLeadInfo:
    """Tests for LeadInfo dataclass."""

    def test_default_values(self):
        """Test default values of LeadInfo."""
        lead = LeadInfo()
        assert lead.name is None
        assert lead.company is None
        assert lead.email is None
        assert lead.phone is None
        assert lead.sector is None
        assert lead.company_size is None
        assert lead.budget is None
        assert lead.decision_maker is False
        assert lead.pain_points == []
        assert lead.interests == []

    def test_to_dict(self):
        """Test conversion to dictionary."""
        lead = LeadInfo(
            name="Jean Dupont",
            company="TechCorp",
            email="jean@techcorp.fr",
            sector=LeadSector.SAAS,
            company_size=CompanySize.MEDIUM,
            budget=50000,
            decision_maker=True,
            pain_points=["Shadow IA", "Formation"],
            interests=["Strategie IA"],
        )
        data = lead.to_dict()

        assert data["name"] == "Jean Dupont"
        assert data["company"] == "TechCorp"
        assert data["sector"] == "saas"
        assert data["company_size"] == "medium"
        assert data["budget"] == 50000
        assert data["decision_maker"] is True
        assert "Shadow IA" in data["pain_points"]


class TestMessage:
    """Tests for Message dataclass."""

    def test_message_creation(self):
        """Test message creation with defaults."""
        msg = Message(role="user", content="Hello")
        assert msg.role == "user"
        assert msg.content == "Hello"
        assert isinstance(msg.timestamp, datetime)
        assert msg.metadata == {}

    def test_message_to_dict(self):
        """Test message conversion to dictionary."""
        msg = Message(
            role="assistant",
            content="Bonjour!",
            metadata={"agent": "classifier"}
        )
        data = msg.to_dict()

        assert data["role"] == "assistant"
        assert data["content"] == "Bonjour!"
        assert data["metadata"]["agent"] == "classifier"
        assert "timestamp" in data


class TestOffer:
    """Tests for Offer dataclass."""

    def test_offer_creation(self):
        """Test offer creation."""
        offer = Offer(
            product="Diagnostic IA",
            price=3000,
            features=["Audit", "Recommandations"],
            discount=10.0,
        )
        assert offer.product == "Diagnostic IA"
        assert offer.price == 3000
        assert offer.discount == 10.0

    def test_final_price_calculation(self):
        """Test final price with discount."""
        offer = Offer(
            product="Formation",
            price=5000,
            features=["3 jours"],
            discount=20.0,
        )
        assert offer.final_price() == 4000  # 5000 * 0.8

    def test_final_price_no_discount(self):
        """Test final price without discount."""
        offer = Offer(
            product="POC",
            price=10000,
            features=["POC complet"],
        )
        assert offer.final_price() == 10000


class TestCreateInitialState:
    """Tests for create_initial_state function."""

    def test_creates_valid_state(self):
        """Test initial state creation."""
        state = create_initial_state(
            initial_message="Bonjour",
            session_id="test-123"
        )

        assert state["current_message"] == "Bonjour"
        assert state["session_id"] == "test-123"
        assert state["messages"] == []
        assert state["lead_type"] is None
        assert state["lead_score"] == 0.0
        assert state["qualified"] is False
        assert state["converted"] is False
        assert state["escalated"] is False
        assert state["closed"] is False
        assert state["context"] == "initial"

    def test_has_all_required_fields(self):
        """Test that all required fields are present."""
        state = create_initial_state("Test", "test-id")

        required_fields = [
            "messages", "current_message", "lead_info", "lead_type",
            "lead_score", "current_agent", "offers_made", "objections",
            "qualified", "converted", "escalated", "closed",
            "session_id", "context", "next_action", "key_insights",
        ]

        for field in required_fields:
            assert field in state, f"Missing field: {field}"


class TestAddMessage:
    """Tests for add_message function."""

    def test_adds_user_message(self, sample_state):
        """Test adding a user message."""
        add_message(sample_state, "user", "Test message")

        assert len(sample_state["messages"]) == 1
        assert sample_state["messages"][0]["role"] == "user"
        assert sample_state["messages"][0]["content"] == "Test message"

    def test_adds_assistant_message_with_metadata(self, sample_state):
        """Test adding an assistant message with metadata."""
        add_message(
            sample_state,
            "assistant",
            "Response",
            metadata={"agent": "classifier"}
        )

        assert len(sample_state["messages"]) == 1
        msg = sample_state["messages"][0]
        assert msg["role"] == "assistant"
        assert msg["metadata"]["agent"] == "classifier"

    def test_multiple_messages(self, sample_state):
        """Test adding multiple messages."""
        add_message(sample_state, "user", "Message 1")
        add_message(sample_state, "assistant", "Response 1")
        add_message(sample_state, "user", "Message 2")

        assert len(sample_state["messages"]) == 3


class TestGetConversationHistory:
    """Tests for get_conversation_history function."""

    def test_returns_all_messages(self, sample_state):
        """Test getting all messages."""
        add_message(sample_state, "user", "Msg 1")
        add_message(sample_state, "assistant", "Msg 2")
        add_message(sample_state, "user", "Msg 3")

        history = get_conversation_history(sample_state)
        assert len(history) == 3

    def test_returns_last_n_messages(self, sample_state):
        """Test getting last N messages."""
        for i in range(5):
            add_message(sample_state, "user", f"Message {i}")

        history = get_conversation_history(sample_state, last_n=2)
        assert len(history) == 2
        assert history[0]["content"] == "Message 3"
        assert history[1]["content"] == "Message 4"

    def test_empty_history(self, sample_state):
        """Test with empty message history."""
        history = get_conversation_history(sample_state)
        assert history == []


class TestLeadEnums:
    """Tests for lead classification enums."""

    def test_lead_type_values(self):
        """Test LeadType enum values."""
        assert LeadType.HOT.value == "hot"
        assert LeadType.WARM.value == "warm"
        assert LeadType.COLD.value == "cold"
        assert LeadType.QUALIFIED.value == "qualified"

    def test_lead_sector_values(self):
        """Test LeadSector enum values."""
        assert LeadSector.SAAS.value == "saas"
        assert LeadSector.ECOMMERCE.value == "ecommerce"
        assert LeadSector.MANUFACTURING.value == "manufacturing"

    def test_company_size_values(self):
        """Test CompanySize enum values."""
        assert CompanySize.STARTUP.value == "startup"
        assert CompanySize.SME.value == "sme"
        assert CompanySize.MEDIUM.value == "medium"
        assert CompanySize.ENTERPRISE.value == "enterprise"
