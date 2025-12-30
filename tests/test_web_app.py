"""Integration tests for the FastAPI web application."""
import os
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from fastapi.testclient import TestClient

# Set test environment before imports
os.environ["TESTING"] = "true"
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["GOOGLE_CLIENT_ID"] = "test-client-id"
os.environ["GOOGLE_CLIENT_SECRET"] = "test-client-secret"
os.environ["APP_URL"] = "http://localhost:8000"
os.environ["AUTHORIZED_EMAILS"] = "allowed@example.com,admin@example.com"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test_data/test_app.db"


@pytest.fixture
def client():
    """Create a test client."""
    from web.app import app
    from web.database import init_db, Base, sync_engine

    # Initialize database
    os.makedirs("./test_data", exist_ok=True)
    Base.metadata.create_all(bind=sync_engine)

    with TestClient(app) as client:
        yield client

    # Cleanup
    Base.metadata.drop_all(bind=sync_engine)


@pytest.fixture
def authenticated_client(client, test_user_data):
    """Create an authenticated test client."""
    from web.auth import create_session_token, SESSION_COOKIE_NAME

    token = create_session_token(test_user_data)
    client.cookies.set(SESSION_COOKIE_NAME, token)
    return client


class TestPublicRoutes:
    """Tests for public routes."""

    def test_home_page(self, client):
        """Test home page loads."""
        response = client.get("/")
        assert response.status_code == 200
        assert "IAfluence" in response.text

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "iafluence-sales-agent"

    def test_login_redirect(self, client):
        """Test login redirects to Google OAuth."""
        response = client.get("/login", follow_redirects=False)
        # Should redirect to Google
        assert response.status_code in [302, 307]

    def test_access_denied_page(self, client):
        """Test access denied page."""
        response = client.get("/access-denied")
        assert response.status_code == 200
        assert "refuse" in response.text.lower() or "denied" in response.text.lower()


class TestProtectedRoutes:
    """Tests for protected routes."""

    def test_dashboard_requires_auth(self, client):
        """Test that dashboard redirects unauthenticated users."""
        response = client.get("/dashboard", follow_redirects=False)
        assert response.status_code in [302, 307, 401]

    def test_dashboard_with_auth(self, authenticated_client):
        """Test dashboard loads for authenticated users."""
        response = authenticated_client.get("/dashboard")
        assert response.status_code == 200
        assert "Bienvenue" in response.text or "Dashboard" in response.text

    def test_api_chat_requires_auth(self, client):
        """Test that chat API requires authentication."""
        response = client.post("/api/chat", json={"message": "Hello"})
        assert response.status_code == 401

    def test_logout(self, authenticated_client):
        """Test logout clears session."""
        response = authenticated_client.get("/logout", follow_redirects=False)
        assert response.status_code == 302
        # Should redirect to home
        assert response.headers.get("location") == "/"


class TestChatAPI:
    """Tests for chat API endpoints."""

    @patch("web.app.get_orchestrator")
    def test_chat_new_conversation(self, mock_get_orch, authenticated_client):
        """Test starting a new chat conversation."""
        mock_orchestrator = MagicMock()
        mock_orchestrator.run_conversation.return_value = {
            "session_id": "test-session-123",
            "messages": [
                {"role": "user", "content": "Bonjour"},
                {"role": "assistant", "content": "Bonjour!", "metadata": {"agent": "classifier"}},
            ],
            "lead_type": "warm",
            "lead_score": 50,
            "qualified": False,
            "converted": False,
            "closed": False,
        }
        mock_get_orch.return_value = mock_orchestrator

        response = authenticated_client.post(
            "/api/chat",
            json={"message": "Bonjour"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == "test-session-123"
        assert data["response"] == "Bonjour!"
        assert data["agent"] == "classifier"

    @patch("web.app.get_orchestrator")
    def test_chat_continue_conversation(self, mock_get_orch, authenticated_client):
        """Test continuing an existing conversation."""
        mock_orchestrator = MagicMock()
        mock_orchestrator.continue_conversation.return_value = {
            "session_id": "existing-session",
            "messages": [
                {"role": "user", "content": "Previous message"},
                {"role": "assistant", "content": "Previous response", "metadata": {"agent": "classifier"}},
                {"role": "user", "content": "New message"},
                {"role": "assistant", "content": "New response", "metadata": {"agent": "seller"}},
            ],
            "lead_type": "hot",
            "lead_score": 85,
            "qualified": True,
            "converted": False,
            "closed": False,
        }
        mock_get_orch.return_value = mock_orchestrator

        response = authenticated_client.post(
            "/api/chat",
            json={
                "message": "New message",
                "session_id": "existing-session"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == "existing-session"
        assert data["response"] == "New response"
        assert data["agent"] == "seller"

    def test_chat_empty_message(self, authenticated_client):
        """Test that empty messages are rejected."""
        response = authenticated_client.post(
            "/api/chat",
            json={"message": ""}
        )

        assert response.status_code == 400

    def test_new_session_endpoint(self, authenticated_client):
        """Test creating a new session."""
        response = authenticated_client.post("/api/session/new")

        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] is None
        assert "Ready" in data["message"] or "new" in data["message"].lower()


class TestAdminRoutes:
    """Tests for admin routes."""

    @pytest.fixture
    def admin_client(self, client, admin_user_data):
        """Create an admin authenticated client."""
        from web.auth import create_session_token, SESSION_COOKIE_NAME
        from web.database import UserRepository, SyncSessionLocal

        # Create admin user in database
        db = SyncSessionLocal()
        try:
            UserRepository.create_user_sync(
                db,
                email=admin_user_data["email"],
                name=admin_user_data["name"],
                is_admin=True
            )
        finally:
            db.close()

        token = create_session_token(admin_user_data)
        client.cookies.set(SESSION_COOKIE_NAME, token)
        return client

    def test_admin_users_requires_admin(self, authenticated_client):
        """Test that admin page requires admin privileges."""
        response = authenticated_client.get("/admin/users")
        assert response.status_code == 403

    def test_admin_users_page(self, admin_client):
        """Test admin users page loads."""
        response = admin_client.get("/admin/users")
        assert response.status_code == 200
        assert "utilisateurs" in response.text.lower() or "users" in response.text.lower()

    def test_admin_add_user(self, admin_client):
        """Test adding a user via admin API."""
        response = admin_client.post(
            "/admin/users/add",
            json={
                "email": "newuser@example.com",
                "name": "New User",
                "is_admin": False
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["user"]["email"] == "newuser@example.com"

    def test_admin_remove_user(self, admin_client):
        """Test removing a user via admin API."""
        # First add a user
        admin_client.post(
            "/admin/users/add",
            json={"email": "toremove@example.com", "name": "To Remove"}
        )

        # Then remove them
        response = admin_client.delete("/admin/users/toremove@example.com")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_admin_cannot_remove_self(self, admin_client, admin_user_data):
        """Test that admin cannot remove themselves."""
        response = admin_client.delete(f"/admin/users/{admin_user_data['email']}")

        assert response.status_code == 400


class TestSessionManagement:
    """Tests for session management."""

    @patch("web.app.get_orchestrator")
    def test_get_session(self, mock_get_orch, authenticated_client):
        """Test getting session history."""
        mock_orchestrator = MagicMock()
        mock_orchestrator.get_conversation_history.return_value = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
        ]
        mock_get_orch.return_value = mock_orchestrator

        response = authenticated_client.get("/api/session/test-session-id")

        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == "test-session-id"
        assert len(data["messages"]) == 2

    @patch("web.app.get_orchestrator")
    def test_get_nonexistent_session(self, mock_get_orch, authenticated_client):
        """Test getting a session that doesn't exist."""
        mock_orchestrator = MagicMock()
        mock_orchestrator.get_conversation_history.return_value = []
        mock_get_orch.return_value = mock_orchestrator

        response = authenticated_client.get("/api/session/nonexistent")

        assert response.status_code == 404
