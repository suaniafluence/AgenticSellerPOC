"""FastAPI web application for IAfluence Sales Agent."""
import os
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv

from .auth import (
    oauth_login,
    oauth_callback,
    logout,
    get_current_user,
    get_current_user_optional,
    get_session_user,
    get_oauth_configured,
    SESSION_COOKIE_NAME,
)
from .database import (
    init_db,
    UserRepository,
    SyncSessionLocal,
    AuthorizedUser,
)
from orchestrator import SalesOrchestrator
from memory import set_memory_store, InMemoryStore, JSONFileStore

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Initialize database
    init_db()
    # Initialize memory store
    os.makedirs("./data", exist_ok=True)
    set_memory_store(JSONFileStore("./data"))
    yield


# Create FastAPI app
app = FastAPI(
    title="IAfluence Sales Agent",
    description="Assistant commercial IA propulse par LangGraph",
    version="1.0.0",
    lifespan=lifespan,
)

# Add session middleware for OAuth
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

# Setup templates
templates_dir = os.path.join(os.path.dirname(__file__), "templates")
os.makedirs(templates_dir, exist_ok=True)
templates = Jinja2Templates(directory=templates_dir)

# Static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Store orchestrators per session
orchestrators: dict = {}


def get_orchestrator(session_id: str) -> SalesOrchestrator:
    """Get or create an orchestrator for a session."""
    if session_id not in orchestrators:
        orchestrators[session_id] = SalesOrchestrator()
    return orchestrators[session_id]


# =============================================================================
# Public Routes
# =============================================================================

@app.get("/", response_class=HTMLResponse)
async def home(request: Request, user: Optional[dict] = Depends(get_current_user_optional)):
    """Home page."""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "user": user,
        "oauth_configured": get_oauth_configured(),
    })


@app.get("/login")
async def login_page(request: Request):
    """Redirect to Google OAuth login."""
    if not get_oauth_configured():
        return templates.TemplateResponse("error.html", {
            "request": request,
            "error": "Google OAuth non configure",
            "message": "Configurez GOOGLE_CLIENT_ID et GOOGLE_CLIENT_SECRET dans .env",
        })
    return await oauth_login(request)


@app.get("/auth/callback")
async def auth_callback(request: Request):
    """Handle OAuth callback from Google."""
    return await oauth_callback(request)


@app.get("/logout")
async def logout_route(request: Request):
    """Log out the user."""
    return logout(request)


@app.get("/access-denied", response_class=HTMLResponse)
async def access_denied(request: Request):
    """Access denied page for unauthorized users."""
    return templates.TemplateResponse("access_denied.html", {
        "request": request,
    })


# =============================================================================
# Protected Routes (require authentication)
# =============================================================================

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, user: dict = Depends(get_current_user)):
    """Main dashboard - chat interface."""
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": user,
    })


@app.post("/api/chat")
async def chat(
    request: Request,
    user: dict = Depends(get_current_user),
):
    """Handle chat messages."""
    try:
        body = await request.json()
        message = body.get("message", "").strip()
        session_id = body.get("session_id")

        if not message:
            raise HTTPException(status_code=400, detail="Message is required")

        orchestrator = get_orchestrator(user["email"])

        if session_id:
            # Continue existing conversation
            try:
                state = orchestrator.continue_conversation(session_id, message)
            except ValueError:
                # Session not found, start new
                state = orchestrator.run_conversation(message)
        else:
            # Start new conversation
            state = orchestrator.run_conversation(message)

        # Get the last assistant message
        assistant_messages = [
            msg for msg in state.get("messages", [])
            if msg.get("role") == "assistant"
        ]
        last_response = assistant_messages[-1]["content"] if assistant_messages else ""
        agent = assistant_messages[-1].get("metadata", {}).get("agent", "assistant") if assistant_messages else "assistant"

        return JSONResponse({
            "response": last_response,
            "agent": agent,
            "session_id": state.get("session_id"),
            "lead_type": state.get("lead_type"),
            "lead_score": state.get("lead_score", 0),
            "qualified": state.get("qualified", False),
            "converted": state.get("converted", False),
            "closed": state.get("closed", False),
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/session/{session_id}")
async def get_session(
    session_id: str,
    user: dict = Depends(get_current_user),
):
    """Get session details."""
    orchestrator = get_orchestrator(user["email"])
    history = orchestrator.get_conversation_history(session_id)

    if not history:
        raise HTTPException(status_code=404, detail="Session not found")

    return JSONResponse({
        "session_id": session_id,
        "messages": history,
    })


@app.post("/api/session/new")
async def new_session(user: dict = Depends(get_current_user)):
    """Start a new chat session."""
    return JSONResponse({
        "session_id": None,
        "message": "Ready to start a new conversation",
    })


# =============================================================================
# Admin Routes
# =============================================================================

@app.get("/admin/users", response_class=HTMLResponse)
async def admin_users(request: Request, user: dict = Depends(get_current_user)):
    """Admin page to manage authorized users."""
    db = SyncSessionLocal()
    try:
        db_user = UserRepository.get_user_by_email_sync(db, user["email"])
        if not db_user or not db_user.is_admin:
            raise HTTPException(status_code=403, detail="Admin access required")

        users = UserRepository.get_all_users_sync(db)
        env_emails = UserRepository.get_authorized_emails_from_env()

        return templates.TemplateResponse("admin_users.html", {
            "request": request,
            "user": user,
            "users": users,
            "env_emails": env_emails,
        })
    finally:
        db.close()


@app.post("/admin/users/add")
async def add_user(
    request: Request,
    user: dict = Depends(get_current_user),
):
    """Add a new authorized user."""
    db = SyncSessionLocal()
    try:
        db_user = UserRepository.get_user_by_email_sync(db, user["email"])
        if not db_user or not db_user.is_admin:
            raise HTTPException(status_code=403, detail="Admin access required")

        body = await request.json()
        email = body.get("email", "").strip().lower()
        name = body.get("name", "").strip()
        is_admin = body.get("is_admin", False)

        if not email:
            raise HTTPException(status_code=400, detail="Email is required")

        new_user = UserRepository.add_user_sync(db, email, name, is_admin)

        return JSONResponse({
            "success": True,
            "user": {
                "id": new_user.id,
                "email": new_user.email,
                "name": new_user.name,
                "is_admin": new_user.is_admin,
            }
        })
    finally:
        db.close()


@app.delete("/admin/users/{email}")
async def remove_user(
    email: str,
    user: dict = Depends(get_current_user),
):
    """Remove an authorized user."""
    db = SyncSessionLocal()
    try:
        db_user = UserRepository.get_user_by_email_sync(db, user["email"])
        if not db_user or not db_user.is_admin:
            raise HTTPException(status_code=403, detail="Admin access required")

        if email.lower() == user["email"].lower():
            raise HTTPException(status_code=400, detail="Cannot remove yourself")

        success = UserRepository.remove_user_sync(db, email)

        return JSONResponse({
            "success": success,
        })
    finally:
        db.close()


# =============================================================================
# Health Check
# =============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "iafluence-sales-agent"}
