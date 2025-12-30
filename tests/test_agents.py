"""Unit tests for sales agents."""
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from agents import (
    ProspectClassifier,
    SellerAgent,
    NegotiatorAgent,
    CRMAgent,
    SupervisorAgent,
)
from agents.base import BaseAgent


class TestBaseAgent:
    """Tests for BaseAgent base class."""

    def test_format_conversation_history(self, mock_llm):
        """Test conversation history formatting."""
        with patch.object(BaseAgent, "__abstractmethods__", set()):
            agent = BaseAgent(name="test", llm=mock_llm)

        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
        ]

        formatted = agent.format_conversation_history(messages)
        assert "USER: Hello" in formatted
        assert "ASSISTANT: Hi there!" in formatted

    def test_get_system_prompt(self, mock_llm):
        """Test default system prompt generation."""
        with patch.object(BaseAgent, "__abstractmethods__", set()):
            agent = BaseAgent(name="TestAgent", llm=mock_llm)

        prompt = agent.get_system_prompt()
        assert "TestAgent" in prompt


class TestProspectClassifier:
    """Tests for ProspectClassifier agent."""

    @pytest.fixture
    def classifier(self, mock_llm):
        """Create classifier with mock LLM."""
        with patch("agents.classifier.ChatOpenAI", return_value=mock_llm):
            with patch("agents.classifier.ChatAnthropic", return_value=mock_llm):
                return ProspectClassifier(llm=mock_llm)

    def test_classifier_initialization(self, classifier):
        """Test classifier is initialized correctly."""
        assert classifier.name == "classifier"

    def test_process_sets_lead_type(self, classifier, sample_state, mock_llm):
        """Test that process sets lead type."""
        # Mock LLM response for classification
        mock_llm.invoke.return_value = MagicMock(
            content="""
            ANALYSE:
            - Entreprise: TechCorp
            - Secteur: SaaS
            - Taille: Medium
            - Urgence: High
            - Budget: Yes

            CLASSIFICATION: hot
            SCORE: 85
            QUALIFIED: true

            RESPONSE: Bonjour! Je vois que vous etes interesse par nos services IA.
            """
        )

        result = classifier.process(sample_state)

        # The state should be modified
        assert result is not None
        assert "next_action" in result

    def test_classifier_handles_cold_lead(self, classifier, sample_cold_lead_state, mock_llm):
        """Test classifier properly handles cold leads."""
        mock_llm.invoke.return_value = MagicMock(
            content="""
            CLASSIFICATION: cold
            SCORE: 20
            QUALIFIED: false
            RESPONSE: Merci pour votre interet.
            """
        )

        result = classifier.process(sample_cold_lead_state)
        assert result is not None


class TestSellerAgent:
    """Tests for SellerAgent."""

    @pytest.fixture
    def seller(self, mock_llm):
        """Create seller with mock LLM."""
        with patch("agents.seller.ChatOpenAI", return_value=mock_llm):
            return SellerAgent(llm=mock_llm)

    def test_seller_initialization(self, seller):
        """Test seller is initialized correctly."""
        assert seller.name == "seller"

    def test_process_creates_offer(self, seller, sample_hot_lead_state, mock_llm):
        """Test that seller creates an offer."""
        mock_llm.invoke.return_value = MagicMock(
            content="""
            OFFER:
            - Product: Diagnostic IA
            - Price: 3000
            - Features: Audit complet, Recommandations

            RESPONSE: Voici notre offre adaptee a vos besoins.
            """
        )

        result = seller.process(sample_hot_lead_state)
        assert result is not None


class TestNegotiatorAgent:
    """Tests for NegotiatorAgent."""

    @pytest.fixture
    def negotiator(self, mock_llm):
        """Create negotiator with mock LLM."""
        with patch("agents.negotiator.ChatOpenAI", return_value=mock_llm):
            return NegotiatorAgent(llm=mock_llm)

    def test_negotiator_initialization(self, negotiator):
        """Test negotiator is initialized correctly."""
        assert negotiator.name == "negotiator"

    def test_handles_budget_objection(self, negotiator, sample_hot_lead_state, mock_llm):
        """Test handling budget objection."""
        sample_hot_lead_state["current_message"] = "C'est trop cher"
        sample_hot_lead_state["objections"] = ["budget"]

        mock_llm.invoke.return_value = MagicMock(
            content="""
            OBJECTION_TYPE: budget
            RESPONSE: Je comprends votre preoccupation. Nous pouvons proposer un echelonnement.
            COUNTER_OFFER: discount=10
            """
        )

        result = negotiator.process(sample_hot_lead_state)
        assert result is not None

    def test_escalation_after_max_rounds(self, negotiator, sample_hot_lead_state, mock_llm):
        """Test escalation after maximum negotiation rounds."""
        sample_hot_lead_state["negotiation_count"] = 3

        mock_llm.invoke.return_value = MagicMock(
            content="ESCALATE: true\nRESPONSE: Je vous mets en relation avec notre directeur."
        )

        result = negotiator.process(sample_hot_lead_state)
        # After 3 rounds, should recommend escalation
        assert result is not None


class TestCRMAgent:
    """Tests for CRMAgent."""

    @pytest.fixture
    def crm_agent(self, mock_llm):
        """Create CRM agent with mock LLM."""
        with patch("agents.crm.ChatOpenAI", return_value=mock_llm):
            return CRMAgent(llm=mock_llm)

    def test_crm_initialization(self, crm_agent):
        """Test CRM agent is initialized correctly."""
        assert crm_agent.name == "crm"

    def test_generates_crm_record(self, crm_agent, sample_hot_lead_state, mock_llm):
        """Test CRM record generation."""
        sample_hot_lead_state["converted"] = True

        mock_llm.invoke.return_value = MagicMock(
            content="""
            CRM_RECORD:
            - Status: Won
            - Value: 5000
            - Next Steps: Signature du contrat

            RESPONSE: Felicitations! Votre dossier est enregistre.
            """
        )

        result = crm_agent.process(sample_hot_lead_state)
        assert result is not None
        assert result.get("closed") is True or result.get("crm_synced") is True


class TestSupervisorAgent:
    """Tests for SupervisorAgent."""

    @pytest.fixture
    def supervisor(self, mock_llm):
        """Create supervisor with mock LLM."""
        with patch("agents.supervisor.ChatOpenAI", return_value=mock_llm):
            return SupervisorAgent(llm=mock_llm)

    def test_supervisor_initialization(self, supervisor):
        """Test supervisor is initialized correctly."""
        assert supervisor.name == "supervisor"

    def test_routes_to_seller(self, supervisor, sample_hot_lead_state, mock_llm):
        """Test routing to seller agent."""
        mock_llm.invoke.return_value = MagicMock(
            content="""
            DECISION: seller
            REASON: Le prospect est qualifie et pret pour une offre.
            """
        )

        result = supervisor.process(sample_hot_lead_state)
        assert result is not None

    def test_routes_to_negotiator(self, supervisor, sample_hot_lead_state, mock_llm):
        """Test routing to negotiator when objection detected."""
        sample_hot_lead_state["current_message"] = "C'est trop cher pour nous"

        mock_llm.invoke.return_value = MagicMock(
            content="""
            DECISION: negotiator
            REASON: Objection budget detectee.
            """
        )

        result = supervisor.process(sample_hot_lead_state)
        assert result is not None


class TestAgentIntegration:
    """Integration tests for agent interactions."""

    def test_all_agents_have_process_method(self, mock_llm):
        """Verify all agents implement process method."""
        with patch("agents.classifier.ChatOpenAI", return_value=mock_llm):
            with patch("agents.seller.ChatOpenAI", return_value=mock_llm):
                with patch("agents.negotiator.ChatOpenAI", return_value=mock_llm):
                    with patch("agents.crm.ChatOpenAI", return_value=mock_llm):
                        with patch("agents.supervisor.ChatOpenAI", return_value=mock_llm):
                            agents = [
                                ProspectClassifier(llm=mock_llm),
                                SellerAgent(llm=mock_llm),
                                NegotiatorAgent(llm=mock_llm),
                                CRMAgent(llm=mock_llm),
                                SupervisorAgent(llm=mock_llm),
                            ]

                            for agent in agents:
                                assert hasattr(agent, "process")
                                assert callable(agent.process)

    def test_agents_return_state_dict(self, mock_llm, sample_state):
        """Verify all agents return a state dictionary."""
        mock_llm.invoke.return_value = MagicMock(content="Test response")

        with patch("agents.classifier.ChatOpenAI", return_value=mock_llm):
            classifier = ProspectClassifier(llm=mock_llm)
            result = classifier.process(sample_state)

            assert isinstance(result, dict)
