"""Example test file."""

import pytest


def test_example():
    """Example test case."""
    assert 1 + 1 == 2


def test_version():
    """Test version import."""
    from agenticseller import __version__

    assert __version__ == "0.1.0"
