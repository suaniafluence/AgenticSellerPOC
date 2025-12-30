"""Google OAuth authentication for the web application."""
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from functools import wraps

from fastapi import HTTPException, Request, Depends
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from dotenv import load_dotenv

from .database import (
    UserRepository,
    SyncSessionLocal,
    AuthorizedUser,
)

load_dotenv()

# OAuth Configuration
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")
APP_URL = os.getenv("APP_URL", "http://localhost:8000")

# Session configuration
SESSION_COOKIE_NAME = "iafluence_session"
SESSION_EXPIRY_HOURS = 24

# Initialize OAuth
oauth = OAuth()

if GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET:
    oauth.register(
        name="google",
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={
            "scope": "openid email profile",
            "prompt": "select_account",
        },
    )

# Session serializer
serializer = URLSafeTimedSerializer(SECRET_KEY)


class AuthError(Exception):
    """Authentication error."""
    pass


def create_session_token(user_data: Dict[str, Any]) -> str:
    """Create a signed session token."""
    session_data = {
        "email": user_data.get("email"),
        "name": user_data.get("name"),
        "picture": user_data.get("picture"),
        "created_at": datetime.utcnow().isoformat(),
    }
    return serializer.dumps(session_data)


def verify_session_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify and decode a session token."""
    try:
        # Token expires after SESSION_EXPIRY_HOURS
        max_age = SESSION_EXPIRY_HOURS * 3600
        data = serializer.loads(token, max_age=max_age)
        return data
    except (BadSignature, SignatureExpired):
        return None


def get_session_user(request: Request) -> Optional[Dict[str, Any]]:
    """Get the current user from session cookie."""
    token = request.cookies.get(SESSION_COOKIE_NAME)
    if not token:
        return None
    return verify_session_token(token)


def require_auth(func):
    """Decorator to require authentication for a route."""
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        user = get_session_user(request)
        if not user:
            return RedirectResponse(url="/login", status_code=302)
        request.state.user = user
        return await func(request, *args, **kwargs)
    return wrapper


async def get_current_user(request: Request) -> Dict[str, Any]:
    """Dependency to get current authenticated user."""
    user = get_session_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user


async def get_current_user_optional(request: Request) -> Optional[Dict[str, Any]]:
    """Dependency to get current user if authenticated, None otherwise."""
    return get_session_user(request)


async def oauth_login(request: Request):
    """Initiate Google OAuth login."""
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        raise HTTPException(
            status_code=500,
            detail="Google OAuth not configured. Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET."
        )

    redirect_uri = f"{APP_URL}/auth/callback"
    return await oauth.google.authorize_redirect(request, redirect_uri)


async def oauth_callback(request: Request):
    """Handle Google OAuth callback."""
    try:
        token = await oauth.google.authorize_access_token(request)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"OAuth error: {str(e)}")

    # Get user info from token
    user_info = token.get("userinfo")
    if not user_info:
        raise HTTPException(status_code=400, detail="Could not get user info from Google")

    email = user_info.get("email", "").lower()
    name = user_info.get("name", "")
    picture = user_info.get("picture", "")

    # Check if user is authorized
    db = next(SyncSessionLocal().__enter__() for _ in [1])
    try:
        is_authorized = UserRepository.is_email_authorized(db, email)

        if not is_authorized:
            # User not authorized - redirect to access denied page
            return RedirectResponse(url="/access-denied", status_code=302)

        # Update or create user in database
        existing_user = UserRepository.get_user_by_email_sync(db, email)
        if existing_user:
            existing_user.name = name
            existing_user.picture = picture
            existing_user.last_login = datetime.utcnow()
            db.commit()
        else:
            # User authorized via env but not in DB - create them
            UserRepository.create_user_sync(db, email, name, picture, is_admin=False)

    finally:
        db.close()

    # Create session token
    session_token = create_session_token({
        "email": email,
        "name": name,
        "picture": picture,
    })

    # Redirect to dashboard with session cookie
    response = RedirectResponse(url="/dashboard", status_code=302)
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=session_token,
        httponly=True,
        secure=APP_URL.startswith("https"),
        samesite="lax",
        max_age=SESSION_EXPIRY_HOURS * 3600,
    )

    return response


def logout(request: Request):
    """Log out the current user."""
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie(SESSION_COOKIE_NAME)
    return response


def get_oauth_configured() -> bool:
    """Check if OAuth is properly configured."""
    return bool(GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET)
