"""Unit tests for memory management."""
import os
import json
import pytest
from datetime import datetime
from memory import (
    MemoryStore,
    InMemoryStore,
    JSONFileStore,
    get_memory_store,
    set_memory_store,
)


class TestInMemoryStore:
    """Tests for InMemoryStore class."""

    @pytest.fixture
    def store(self):
        """Create a fresh InMemoryStore for each test."""
        return InMemoryStore()

    def test_save_and_load_session(self, store, sample_state):
        """Test saving and loading a session."""
        store.save_session("test-session", sample_state)
        loaded = store.load_session("test-session")

        assert loaded is not None
        assert loaded["session_id"] == sample_state["session_id"]
        assert loaded["current_message"] == sample_state["current_message"]

    def test_load_nonexistent_session(self, store):
        """Test loading a session that doesn't exist."""
        loaded = store.load_session("nonexistent")
        assert loaded is None

    def test_overwrite_session(self, store, sample_state):
        """Test that saving overwrites existing session."""
        store.save_session("test-session", sample_state)

        # Modify and save again
        sample_state["lead_score"] = 99.0
        store.save_session("test-session", sample_state)

        loaded = store.load_session("test-session")
        assert loaded["lead_score"] == 99.0

    def test_save_insight(self, store):
        """Test saving an insight."""
        store.save_insight("session-1", "Customer interested in AI training")

        insights = store.get_insights()
        assert len(insights) == 1
        assert insights[0]["session_id"] == "session-1"
        assert insights[0]["insight"] == "Customer interested in AI training"

    def test_save_insight_with_metadata(self, store):
        """Test saving an insight with metadata."""
        store.save_insight(
            "session-1",
            "High budget prospect",
            metadata={"priority": "high", "budget": 100000}
        )

        insights = store.get_insights()
        assert insights[0]["metadata"]["priority"] == "high"
        assert insights[0]["metadata"]["budget"] == 100000

    def test_get_insights_filtered_by_session(self, store):
        """Test filtering insights by session ID."""
        store.save_insight("session-1", "Insight 1")
        store.save_insight("session-2", "Insight 2")
        store.save_insight("session-1", "Insight 3")

        filtered = store.get_insights({"session_id": "session-1"})
        assert len(filtered) == 2
        assert all(i["session_id"] == "session-1" for i in filtered)

    def test_export_and_import(self, store, sample_state, tmp_path):
        """Test exporting and importing data."""
        store.save_session("session-1", sample_state)
        store.save_insight("session-1", "Test insight")

        filepath = str(tmp_path / "export.json")
        store.export_to_file(filepath)

        # Create new store and import
        new_store = InMemoryStore()
        new_store.import_from_file(filepath)

        loaded = new_store.load_session("session-1")
        assert loaded is not None

        insights = new_store.get_insights()
        assert len(insights) == 1


class TestJSONFileStore:
    """Tests for JSONFileStore class."""

    @pytest.fixture
    def store(self, tmp_path):
        """Create a JSONFileStore with temporary directory."""
        return JSONFileStore(str(tmp_path / "data"))

    def test_creates_directories(self, tmp_path):
        """Test that required directories are created."""
        base_path = str(tmp_path / "json_store")
        store = JSONFileStore(base_path)

        assert os.path.exists(base_path)
        assert os.path.exists(f"{base_path}/sessions")
        assert os.path.exists(f"{base_path}/insights")

    def test_save_and_load_session(self, store, sample_state):
        """Test saving and loading a session."""
        store.save_session("file-session", sample_state)
        loaded = store.load_session("file-session")

        assert loaded is not None
        assert loaded["session_id"] == sample_state["session_id"]

    def test_load_nonexistent_session(self, store):
        """Test loading a session that doesn't exist."""
        loaded = store.load_session("nonexistent")
        assert loaded is None

    def test_session_persists_to_file(self, store, sample_state, tmp_path):
        """Test that session is actually written to file."""
        store.save_session("persist-test", sample_state)

        # Check file exists
        filepath = f"{store.base_path}/sessions/persist-test.json"
        assert os.path.exists(filepath)

        # Verify content
        with open(filepath) as f:
            data = json.load(f)
            assert data["state"]["session_id"] == sample_state["session_id"]

    def test_save_insight(self, store):
        """Test saving an insight to file."""
        store.save_insight("session-1", "File-based insight")

        insights = store.get_insights()
        assert len(insights) == 1
        assert insights[0]["insight"] == "File-based insight"


class TestGlobalMemoryStore:
    """Tests for global memory store functions."""

    def test_get_default_store(self):
        """Test that default store is InMemoryStore."""
        # Reset global store
        import memory
        memory._memory_store = None

        store = get_memory_store()
        assert isinstance(store, InMemoryStore)

    def test_set_memory_store(self):
        """Test setting a custom memory store."""
        custom_store = InMemoryStore()
        set_memory_store(custom_store)

        store = get_memory_store()
        assert store is custom_store

    def test_set_json_file_store(self, tmp_path):
        """Test setting JSONFileStore as global store."""
        json_store = JSONFileStore(str(tmp_path / "global_store"))
        set_memory_store(json_store)

        store = get_memory_store()
        assert isinstance(store, JSONFileStore)


class TestMemoryStoreInterface:
    """Tests to verify MemoryStore interface compliance."""

    def test_inmemory_implements_interface(self):
        """Test that InMemoryStore implements MemoryStore."""
        store = InMemoryStore()
        assert hasattr(store, "save_session")
        assert hasattr(store, "load_session")
        assert hasattr(store, "save_insight")
        assert hasattr(store, "get_insights")

    def test_jsonfile_implements_interface(self, tmp_path):
        """Test that JSONFileStore implements MemoryStore."""
        store = JSONFileStore(str(tmp_path))
        assert hasattr(store, "save_session")
        assert hasattr(store, "load_session")
        assert hasattr(store, "save_insight")
        assert hasattr(store, "get_insights")
