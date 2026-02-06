"""Pytest configuration and fixtures."""

import os
import tempfile
from pathlib import Path
import pytest


@pytest.fixture
def temp_app_dir(monkeypatch):
    """Create a temporary application directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Mock the app directory to use temp directory
        monkeypatch.setenv("CHATCLI_CONFIG_DIR", tmpdir)
        yield Path(tmpdir)


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for testing."""
    from unittest.mock import Mock
    
    client = Mock()
    # Add mock methods as needed for specific tests
    return client
