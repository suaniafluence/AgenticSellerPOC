"""Memory management for the sales agent system."""
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from abc import ABC, abstractmethod


class MemoryStore(ABC):
    """Abstract base class for memory storage."""

    @abstractmethod
    def save_session(self, session_id: str, state: Dict[str, Any]) -> None:
        """Save a session state."""
        pass

    @abstractmethod
    def load_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Load a session state."""
        pass

    @abstractmethod
    def save_insight(self, session_id: str, insight: str, metadata: Optional[Dict] = None) -> None:
        """Save an insight from a session."""
        pass

    @abstractmethod
    def get_insights(self, filters: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """Retrieve insights with optional filtering."""
        pass


class InMemoryStore(MemoryStore):
    """Simple in-memory storage for development/testing."""

    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.insights: List[Dict[str, Any]] = []

    def save_session(self, session_id: str, state: Dict[str, Any]) -> None:
        """Save a session state."""
        self.sessions[session_id] = {
            "state": state,
            "updated_at": datetime.now().isoformat(),
        }

    def load_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Load a session state."""
        session = self.sessions.get(session_id)
        return session["state"] if session else None

    def save_insight(self, session_id: str, insight: str, metadata: Optional[Dict] = None) -> None:
        """Save an insight from a session."""
        self.insights.append({
            "session_id": session_id,
            "insight": insight,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat(),
        })

    def get_insights(self, filters: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """Retrieve insights with optional filtering."""
        if not filters:
            return self.insights

        filtered = self.insights
        if "session_id" in filters:
            filtered = [i for i in filtered if i["session_id"] == filters["session_id"]]

        return filtered

    def export_to_file(self, filepath: str) -> None:
        """Export all data to a JSON file."""
        with open(filepath, "w") as f:
            json.dump({
                "sessions": self.sessions,
                "insights": self.insights,
            }, f, indent=2)

    def import_from_file(self, filepath: str) -> None:
        """Import data from a JSON file."""
        with open(filepath, "r") as f:
            data = json.load(f)
            self.sessions = data.get("sessions", {})
            self.insights = data.get("insights", [])


class JSONFileStore(MemoryStore):
    """File-based storage using JSON."""

    def __init__(self, base_path: str = "./data"):
        self.base_path = base_path
        import os
        os.makedirs(base_path, exist_ok=True)
        os.makedirs(f"{base_path}/sessions", exist_ok=True)
        os.makedirs(f"{base_path}/insights", exist_ok=True)

    def save_session(self, session_id: str, state: Dict[str, Any]) -> None:
        """Save a session state."""
        filepath = f"{self.base_path}/sessions/{session_id}.json"
        with open(filepath, "w") as f:
            json.dump({
                "state": state,
                "updated_at": datetime.now().isoformat(),
            }, f, indent=2)

    def load_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Load a session state."""
        filepath = f"{self.base_path}/sessions/{session_id}.json"
        try:
            with open(filepath, "r") as f:
                data = json.load(f)
                return data["state"]
        except FileNotFoundError:
            return None

    def save_insight(self, session_id: str, insight: str, metadata: Optional[Dict] = None) -> None:
        """Save an insight from a session."""
        timestamp = datetime.now().isoformat()
        filepath = f"{self.base_path}/insights/{session_id}_{timestamp.replace(':', '-')}.json"
        with open(filepath, "w") as f:
            json.dump({
                "session_id": session_id,
                "insight": insight,
                "metadata": metadata or {},
                "timestamp": timestamp,
            }, f, indent=2)

    def get_insights(self, filters: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """Retrieve insights with optional filtering."""
        import os
        import glob

        insights = []
        pattern = f"{self.base_path}/insights/*.json"

        for filepath in glob.glob(pattern):
            with open(filepath, "r") as f:
                insight = json.load(f)

                # Apply filters
                if filters:
                    if "session_id" in filters and insight["session_id"] != filters["session_id"]:
                        continue

                insights.append(insight)

        return insights


# Global memory store instance
_memory_store: Optional[MemoryStore] = None


def get_memory_store() -> MemoryStore:
    """Get the global memory store instance."""
    global _memory_store
    if _memory_store is None:
        # Default to in-memory store
        _memory_store = InMemoryStore()
    return _memory_store


def set_memory_store(store: MemoryStore) -> None:
    """Set the global memory store instance."""
    global _memory_store
    _memory_store = store
