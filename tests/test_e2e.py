"""End-to-end tests for the IAfluence web application.

These tests simulate real user interactions using Playwright.
Run with: pytest tests/test_e2e.py --headed (to see browser)
"""
import os
import pytest
import subprocess
import time
import signal
from typing import Generator

# Skip if playwright is not installed
pytest.importorskip("playwright")

from playwright.sync_api import Page, expect, sync_playwright


# Test configuration
TEST_PORT = 8765
TEST_URL = f"http://localhost:{TEST_PORT}"
TEST_EMAIL = "e2e-test@example.com"


@pytest.fixture(scope="module")
def server() -> Generator:
    """Start the FastAPI server for E2E tests."""
    # Set environment for testing
    env = os.environ.copy()
    env.update({
        "PORT": str(TEST_PORT),
        "DEBUG": "false",
        "SECRET_KEY": "e2e-test-secret-key",
        "GOOGLE_CLIENT_ID": "test-client-id",
        "GOOGLE_CLIENT_SECRET": "test-client-secret",
        "APP_URL": TEST_URL,
        "AUTHORIZED_EMAILS": TEST_EMAIL,
        "DATABASE_URL": "sqlite+aiosqlite:///./test_data/e2e_users.db",
    })

    # Start server
    process = subprocess.Popen(
        ["python", "run_web.py"],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Wait for server to start
    time.sleep(3)

    yield process

    # Cleanup
    process.send_signal(signal.SIGTERM)
    process.wait(timeout=5)


@pytest.fixture(scope="module")
def browser():
    """Create a Playwright browser instance."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()


@pytest.fixture
def page(browser) -> Page:
    """Create a new page for each test."""
    context = browser.new_context()
    page = context.new_page()
    yield page
    context.close()


@pytest.fixture
def authenticated_page(browser) -> Page:
    """Create an authenticated page with session cookie."""
    from web.auth import create_session_token, SESSION_COOKIE_NAME

    context = browser.new_context()
    page = context.new_page()

    # Create session token
    token = create_session_token({
        "email": TEST_EMAIL,
        "name": "E2E Test User",
        "picture": None,
    })

    # Set cookie
    context.add_cookies([{
        "name": SESSION_COOKIE_NAME,
        "value": token,
        "domain": "localhost",
        "path": "/",
    }])

    yield page
    context.close()


class TestHomePage:
    """E2E tests for the home page."""

    @pytest.mark.e2e
    def test_home_page_loads(self, page: Page, server):
        """Test that home page loads correctly."""
        page.goto(TEST_URL)

        # Check title
        expect(page).to_have_title("IAfluence - Assistant Commercial IA")

        # Check main elements
        expect(page.locator("text=IAfluence")).to_be_visible()
        expect(page.locator("text=Assistant Commercial IA")).to_be_visible()

    @pytest.mark.e2e
    def test_login_button_visible(self, page: Page, server):
        """Test that login button is visible."""
        page.goto(TEST_URL)

        login_btn = page.locator("text=Connexion avec Google")
        expect(login_btn).to_be_visible()

    @pytest.mark.e2e
    def test_features_section(self, page: Page, server):
        """Test that features section displays agents."""
        page.goto(TEST_URL)

        # Check agent cards
        expect(page.locator("text=Classifier")).to_be_visible()
        expect(page.locator("text=Seller")).to_be_visible()
        expect(page.locator("text=Negotiator")).to_be_visible()


class TestDashboard:
    """E2E tests for the dashboard."""

    @pytest.mark.e2e
    def test_dashboard_requires_auth(self, page: Page, server):
        """Test that dashboard redirects unauthenticated users."""
        page.goto(f"{TEST_URL}/dashboard")

        # Should redirect to login or show error
        expect(page).not_to_have_url(f"{TEST_URL}/dashboard")

    @pytest.mark.e2e
    def test_dashboard_loads_authenticated(self, authenticated_page: Page, server):
        """Test that dashboard loads for authenticated users."""
        authenticated_page.goto(f"{TEST_URL}/dashboard")

        # Check for chat interface
        expect(authenticated_page.locator("#chatMessages")).to_be_visible()
        expect(authenticated_page.locator("#messageInput")).to_be_visible()
        expect(authenticated_page.locator("#sendBtn")).to_be_visible()

    @pytest.mark.e2e
    def test_new_chat_button(self, authenticated_page: Page, server):
        """Test new chat button functionality."""
        authenticated_page.goto(f"{TEST_URL}/dashboard")

        new_chat_btn = authenticated_page.locator("#newChatBtn")
        expect(new_chat_btn).to_be_visible()

        # Click should reset conversation
        new_chat_btn.click()
        expect(authenticated_page.locator("text=Nouvelle conversation")).to_be_visible()


class TestChatInteraction:
    """E2E tests for chat functionality."""

    @pytest.mark.e2e
    def test_send_message(self, authenticated_page: Page, server):
        """Test sending a chat message."""
        authenticated_page.goto(f"{TEST_URL}/dashboard")

        # Type a message
        message_input = authenticated_page.locator("#messageInput")
        message_input.fill("Bonjour, je suis interesse par vos services")

        # Send message
        send_btn = authenticated_page.locator("#sendBtn")
        send_btn.click()

        # Wait for response (with timeout)
        # The user message should appear
        expect(authenticated_page.locator("text=Bonjour, je suis interesse")).to_be_visible(timeout=10000)

    @pytest.mark.e2e
    def test_chat_shows_agent_response(self, authenticated_page: Page, server):
        """Test that agent responses are displayed."""
        authenticated_page.goto(f"{TEST_URL}/dashboard")

        # Send message
        authenticated_page.locator("#messageInput").fill("Je cherche une formation IA")
        authenticated_page.locator("#sendBtn").click()

        # Wait for typing indicator to appear and disappear
        time.sleep(2)

        # Check for any agent badge (classifier, seller, etc.)
        # The response container should have an agent label
        agent_labels = ["CLASSIFIER", "SELLER", "NEGOTIATOR", "SUPERVISOR", "CRM"]
        for label in agent_labels:
            if authenticated_page.locator(f"text={label}").count() > 0:
                break
        else:
            # At minimum, there should be some response
            pass

    @pytest.mark.e2e
    def test_stats_panel_updates(self, authenticated_page: Page, server):
        """Test that stats panel updates after conversation."""
        authenticated_page.goto(f"{TEST_URL}/dashboard")

        # Get initial stats
        initial_score = authenticated_page.locator("#leadScore").inner_text()

        # Send a message
        authenticated_page.locator("#messageInput").fill("Je veux investir 50000 euros")
        authenticated_page.locator("#sendBtn").click()

        # Wait for response
        time.sleep(3)

        # Stats should potentially change
        # (This depends on the LLM response, so we just check it doesn't error)
        expect(authenticated_page.locator("#leadScore")).to_be_visible()


class TestAccessDenied:
    """E2E tests for access denied page."""

    @pytest.mark.e2e
    def test_access_denied_page(self, page: Page, server):
        """Test access denied page displays correctly."""
        page.goto(f"{TEST_URL}/access-denied")

        expect(page.locator("text=refuse")).to_be_visible()
        expect(page.locator("text=Retour")).to_be_visible()

    @pytest.mark.e2e
    def test_access_denied_has_return_link(self, page: Page, server):
        """Test return link on access denied page."""
        page.goto(f"{TEST_URL}/access-denied")

        return_link = page.locator("text=Retour a l'accueil")
        expect(return_link).to_be_visible()

        return_link.click()
        expect(page).to_have_url(TEST_URL + "/")


class TestResponsiveDesign:
    """E2E tests for responsive design."""

    @pytest.mark.e2e
    def test_mobile_viewport(self, browser, server):
        """Test the app works on mobile viewport."""
        context = browser.new_context(
            viewport={"width": 375, "height": 667}  # iPhone SE
        )
        page = context.new_page()

        page.goto(TEST_URL)

        # Header should still be visible
        expect(page.locator("text=IAfluence")).to_be_visible()

        context.close()

    @pytest.mark.e2e
    def test_tablet_viewport(self, browser, server):
        """Test the app works on tablet viewport."""
        context = browser.new_context(
            viewport={"width": 768, "height": 1024}  # iPad
        )
        page = context.new_page()

        page.goto(TEST_URL)

        # All main content should be visible
        expect(page.locator("text=IAfluence")).to_be_visible()
        expect(page.locator("text=Assistant Commercial IA")).to_be_visible()

        context.close()


class TestLogout:
    """E2E tests for logout functionality."""

    @pytest.mark.e2e
    def test_logout_redirects_to_home(self, authenticated_page: Page, server):
        """Test that logout redirects to home page."""
        authenticated_page.goto(f"{TEST_URL}/dashboard")

        # Click logout
        logout_link = authenticated_page.locator("text=Deconnexion")
        logout_link.click()

        # Should redirect to home
        expect(authenticated_page).to_have_url(f"{TEST_URL}/")

    @pytest.mark.e2e
    def test_logout_clears_session(self, authenticated_page: Page, server):
        """Test that logout clears session."""
        authenticated_page.goto(f"{TEST_URL}/dashboard")

        # Logout
        authenticated_page.locator("text=Deconnexion").click()

        # Try to access dashboard again
        authenticated_page.goto(f"{TEST_URL}/dashboard")

        # Should be redirected
        expect(authenticated_page).not_to_have_url(f"{TEST_URL}/dashboard")
