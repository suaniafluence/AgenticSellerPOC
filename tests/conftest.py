"""Pytest configuration and shared fixtures."""
import os
import sys
import pytest
from unittest.mock import MagicMock, patch
from typing import Dict, Any

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set test environment
os.environ["TESTING"] = "true"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test_data/test_users.db"
os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only"


@pytest.fixture
def mock_llm():
    """Mock LLM for testing without API calls."""
    mock = MagicMock()
    mock.invoke.return_value = MagicMock(content="Test response from LLM")
    # Agents build chains with `prompt | self.llm`, and LangChain coerces a
    # callable into a RunnableLambda, so the chain calls the mock directly
    # instead of going through .invoke(). Route those calls to the same
    # response, resolved lazily so per-test overrides are picked up.
    mock.side_effect = lambda *args, **kwargs: mock.invoke.return_value
    return mock


@pytest.fixture
def sample_state() -> Dict[str, Any]:
    """Create a sample sales state for testing."""
    from state import create_initial_state
    return create_initial_state(
        initial_message="Bonjour, je suis interesse par vos services IA",
        session_id="test-session-123"
    )


@pytest.fixture
def sample_hot_lead_state(sample_state) -> Dict[str, Any]:
    """Create a hot lead state for testing."""
    sample_state["lead_type"] = "hot"
    sample_state["lead_score"] = 85.0
    sample_state["qualified"] = True
    sample_state["lead_info"] = {
        "company": "TechCorp",
        "sector": "saas",
        "company_size": "medium",
        "budget": 50000,
        "decision_maker": True,
        "pain_points": ["Shadow IA", "Gouvernance IA"],
        "interests": ["Formation", "Strategie IA"],
    }
    return sample_state


@pytest.fixture
def sample_cold_lead_state(sample_state) -> Dict[str, Any]:
    """Create a cold lead state for testing."""
    sample_state["lead_type"] = "cold"
    sample_state["lead_score"] = 25.0
    sample_state["qualified"] = False
    return sample_state


@pytest.fixture
def mock_memory_store():
    """Mock memory store for testing."""
    from memory import InMemoryStore
    return InMemoryStore()


@pytest.fixture
def mock_config():
    """Mock configuration for testing."""
    with patch("config.config") as mock:
        mock.openai_api_key = "test-api-key"
        mock.anthropic_api_key = "test-anthropic-key"
        mock.default_llm_model = "gpt-4-turbo-preview"
        mock.temperature = 0.7
        mock.max_iterations = 10
        mock.hubspot_api_key = "test-hubspot-key"
        mock.salesforce_api_key = "test-salesforce-key"
        yield mock


@pytest.fixture
def test_user_data() -> Dict[str, Any]:
    """Sample user data for authentication tests."""
    return {
        "email": "test@example.com",
        "name": "Test User",
        "picture": "https://example.com/photo.jpg",
    }


@pytest.fixture
def admin_user_data() -> Dict[str, Any]:
    """Sample admin user data."""
    return {
        "email": "admin@example.com",
        "name": "Admin User",
        "picture": "https://example.com/admin.jpg",
    }


@pytest.fixture(scope="session", autouse=True)
def setup_test_dirs():
    """Setup and cleanup test directories.

    Session-scoped on purpose: web.database builds its engines once at import
    and keeps the SQLite connections pooled, so wiping this directory between
    tests would leave them holding a deleted file and every later write would
    fail with "attempt to write a readonly database".
    """
    import shutil
    test_data_dir = "./test_data"
    os.makedirs(test_data_dir, exist_ok=True)
    yield
    # Cleanup once the whole session is done
    if os.path.exists(test_data_dir):
        shutil.rmtree(test_data_dir)
