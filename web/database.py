"""Database configuration and models for user management."""
import os
from datetime import datetime
from typing import Optional, List
from sqlalchemy import create_engine, Column, String, Boolean, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker as async_sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./data/users.db")

# Async engine for FastAPI
async_engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)

# Sync engine for migrations and CLI
sync_database_url = DATABASE_URL.replace("+aiosqlite", "")
sync_engine = create_engine(sync_database_url, echo=False)
SyncSessionLocal = sessionmaker(bind=sync_engine)

Base = declarative_base()


class AuthorizedUser(Base):
    """Model for authorized users who can access the application."""

    __tablename__ = "authorized_users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=True)
    picture = Column(String(512), nullable=True)
    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<AuthorizedUser(email='{self.email}', is_admin={self.is_admin})>"


class UserSession(Base):
    """Model for tracking user sessions."""

    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_email = Column(String(255), nullable=False, index=True)
    session_id = Column(String(255), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)


def init_db():
    """Initialize the database and create tables."""
    import os
    os.makedirs("./data", exist_ok=True)
    Base.metadata.create_all(bind=sync_engine)


async def get_db() -> AsyncSession:
    """Dependency to get database session."""
    async with AsyncSessionLocal() as session:
        yield session


def get_sync_db() -> Session:
    """Get synchronous database session."""
    db = SyncSessionLocal()
    try:
        yield db
    finally:
        db.close()


class UserRepository:
    """Repository for user management operations."""

    @staticmethod
    def get_authorized_emails_from_env() -> List[str]:
        """Get authorized emails from environment variable."""
        emails_str = os.getenv("AUTHORIZED_EMAILS", "")
        if not emails_str:
            return []
        return [email.strip().lower() for email in emails_str.split(",") if email.strip()]

    @staticmethod
    def is_email_authorized_in_env(email: str) -> bool:
        """Check if email is in the environment variable list."""
        authorized = UserRepository.get_authorized_emails_from_env()
        return email.lower() in authorized

    @staticmethod
    def get_user_by_email_sync(db: Session, email: str) -> Optional[AuthorizedUser]:
        """Get user by email (sync version)."""
        return db.query(AuthorizedUser).filter(
            AuthorizedUser.email == email.lower()
        ).first()

    @staticmethod
    def create_user_sync(
        db: Session,
        email: str,
        name: Optional[str] = None,
        picture: Optional[str] = None,
        is_admin: bool = False
    ) -> AuthorizedUser:
        """Create a new authorized user (sync version)."""
        user = AuthorizedUser(
            email=email.lower(),
            name=name,
            picture=picture,
            is_admin=is_admin,
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def update_last_login_sync(db: Session, email: str) -> None:
        """Update user's last login time."""
        user = UserRepository.get_user_by_email_sync(db, email)
        if user:
            user.last_login = datetime.utcnow()
            db.commit()

    @staticmethod
    def is_email_authorized(db: Session, email: str) -> bool:
        """
        Check if an email is authorized to access the application.
        Checks both environment variable and database.
        """
        # First check env variable
        if UserRepository.is_email_authorized_in_env(email):
            return True

        # Then check database
        user = UserRepository.get_user_by_email_sync(db, email)
        return user is not None and user.is_active

    @staticmethod
    def get_all_users_sync(db: Session) -> List[AuthorizedUser]:
        """Get all authorized users."""
        return db.query(AuthorizedUser).all()

    @staticmethod
    def add_user_sync(
        db: Session,
        email: str,
        name: Optional[str] = None,
        is_admin: bool = False
    ) -> AuthorizedUser:
        """Add a new authorized user to the database."""
        existing = UserRepository.get_user_by_email_sync(db, email)
        if existing:
            existing.is_active = True
            existing.name = name or existing.name
            existing.is_admin = is_admin
            db.commit()
            return existing
        return UserRepository.create_user_sync(db, email, name, is_admin=is_admin)

    @staticmethod
    def remove_user_sync(db: Session, email: str) -> bool:
        """Deactivate a user (soft delete)."""
        user = UserRepository.get_user_by_email_sync(db, email)
        if user:
            user.is_active = False
            db.commit()
            return True
        return False


# Initialize database on import
init_db()
