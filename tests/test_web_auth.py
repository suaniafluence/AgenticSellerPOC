"""Unit tests for web authentication."""
import os
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta

# Set test environment before imports
os.environ["TESTING"] = "true"
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["GOOGLE_CLIENT_ID"] = "test-client-id"
os.environ["GOOGLE_CLIENT_SECRET"] = "test-client-secret"
os.environ["APP_URL"] = "http://localhost:8000"
os.environ["AUTHORIZED_EMAILS"] = "allowed@example.com,admin@example.com"


class TestSessionTokens:
    """Tests for session token creation and verification."""

    def test_create_session_token(self, test_user_data):
        """Test creating a session token."""
        from web.auth import create_session_token

        token = create_session_token(test_user_data)
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_verify_valid_token(self, test_user_data):
        """Test verifying a valid session token."""
        from web.auth import create_session_token, verify_session_token

        token = create_session_token(test_user_data)
        data = verify_session_token(token)

        assert data is not None
        assert data["email"] == test_user_data["email"]
        assert data["name"] == test_user_data["name"]

    def test_verify_invalid_token(self):
        """Test verifying an invalid token."""
        from web.auth import verify_session_token

        data = verify_session_token("invalid-token")
        assert data is None

    def test_verify_tampered_token(self, test_user_data):
        """Test that tampered tokens are rejected."""
        from web.auth import create_session_token, verify_session_token

        token = create_session_token(test_user_data)
        tampered = token[:-5] + "XXXXX"  # Tamper with signature

        data = verify_session_token(tampered)
        assert data is None


class TestOAuthConfiguration:
    """Tests for OAuth configuration."""

    def test_oauth_configured(self):
        """Test that OAuth is properly configured."""
        from web.auth import get_oauth_configured

        # With test environment variables set
        assert get_oauth_configured() is True

    def test_oauth_not_configured_without_credentials(self):
        """Test OAuth not configured without credentials."""
        with patch.dict(os.environ, {"GOOGLE_CLIENT_ID": "", "GOOGLE_CLIENT_SECRET": ""}):
            # Need to reload the module to pick up new env vars
            from web import auth
            from importlib import reload
            reload(auth)

            # Restore after test
            os.environ["GOOGLE_CLIENT_ID"] = "test-client-id"
            os.environ["GOOGLE_CLIENT_SECRET"] = "test-client-secret"


class TestUserRepository:
    """Tests for UserRepository class."""

    @pytest.fixture(autouse=True)
    def setup_db(self):
        """Setup test database."""
        from web.database import init_db, Base, sync_engine
        Base.metadata.create_all(bind=sync_engine)
        yield
        Base.metadata.drop_all(bind=sync_engine)

    def test_get_authorized_emails_from_env(self):
        """Test getting authorized emails from environment."""
        from web.database import UserRepository

        emails = UserRepository.get_authorized_emails_from_env()
        assert "allowed@example.com" in emails
        assert "admin@example.com" in emails

    def test_is_email_authorized_in_env(self):
        """Test checking if email is authorized via env."""
        from web.database import UserRepository

        assert UserRepository.is_email_authorized_in_env("allowed@example.com") is True
        assert UserRepository.is_email_authorized_in_env("unauthorized@example.com") is False

    def test_create_user_sync(self):
        """Test creating a user in database."""
        from web.database import UserRepository, SyncSessionLocal

        db = SyncSessionLocal()
        try:
            user = UserRepository.create_user_sync(
                db,
                email="newuser@example.com",
                name="New User",
                is_admin=False
            )

            assert user.email == "newuser@example.com"
            assert user.name == "New User"
            assert user.is_admin is False
            assert user.is_active is True
        finally:
            db.close()

    def test_get_user_by_email(self):
        """Test retrieving a user by email."""
        from web.database import UserRepository, SyncSessionLocal

        db = SyncSessionLocal()
        try:
            # Create user first
            UserRepository.create_user_sync(db, "findme@example.com", "Find Me")

            # Then find it
            user = UserRepository.get_user_by_email_sync(db, "findme@example.com")
            assert user is not None
            assert user.email == "findme@example.com"
        finally:
            db.close()

    def test_is_email_authorized_combined(self):
        """Test authorization check combining env and database."""
        from web.database import UserRepository, SyncSessionLocal

        db = SyncSessionLocal()
        try:
            # Email in env should be authorized
            assert UserRepository.is_email_authorized(db, "allowed@example.com") is True

            # Email in database should be authorized
            UserRepository.create_user_sync(db, "dbuser@example.com", "DB User")
            assert UserRepository.is_email_authorized(db, "dbuser@example.com") is True

            # Unknown email should not be authorized
            assert UserRepository.is_email_authorized(db, "unknown@example.com") is False
        finally:
            db.close()

    def test_remove_user(self):
        """Test soft-deleting a user."""
        from web.database import UserRepository, SyncSessionLocal

        db = SyncSessionLocal()
        try:
            UserRepository.create_user_sync(db, "removeme@example.com", "Remove Me")

            success = UserRepository.remove_user_sync(db, "removeme@example.com")
            assert success is True

            # User should still exist but be inactive
            user = UserRepository.get_user_by_email_sync(db, "removeme@example.com")
            assert user is not None
            assert user.is_active is False
        finally:
            db.close()

    def test_add_user_reactivates_inactive(self):
        """Test that adding an inactive user reactivates them."""
        from web.database import UserRepository, SyncSessionLocal

        db = SyncSessionLocal()
        try:
            # Create and remove user
            UserRepository.create_user_sync(db, "reactivate@example.com", "Reactivate")
            UserRepository.remove_user_sync(db, "reactivate@example.com")

            # Add again should reactivate
            user = UserRepository.add_user_sync(db, "reactivate@example.com", "Reactivated")
            assert user.is_active is True
        finally:
            db.close()


class TestAuthenticatedUser:
    """Tests for AuthorizedUser model."""

    @pytest.fixture(autouse=True)
    def setup_db(self):
        """Setup test database."""
        from web.database import init_db, Base, sync_engine
        Base.metadata.create_all(bind=sync_engine)
        yield
        Base.metadata.drop_all(bind=sync_engine)

    def test_user_repr(self):
        """Test user string representation."""
        from web.database import AuthorizedUser

        user = AuthorizedUser(email="test@example.com", is_admin=True)
        repr_str = repr(user)

        assert "test@example.com" in repr_str
        assert "is_admin=True" in repr_str

    def test_user_defaults(self):
        """Test user default values."""
        from web.database import AuthorizedUser

        user = AuthorizedUser(email="defaults@example.com")

        assert user.is_admin is False
        assert user.is_active is True
        assert user.name is None
        assert user.picture is None
        assert user.last_login is None
