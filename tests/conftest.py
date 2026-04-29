"""
Pytest configuration and fixtures
"""

import pytest
import os
from pathlib import Path


@pytest.fixture
def project_root():
    """Return the project root directory"""
    return Path(__file__).parent.parent


@pytest.fixture
def sample_requirement():
    """Sample requirement for testing"""
    return "Build a student management system with CRUD operations"


@pytest.fixture
def env_setup(monkeypatch):
    """Set up environment variables for tests"""
    monkeypatch.setenv("DEBUG", "False")
    monkeypatch.setenv("GEMINI_MODEL", "gemini-2.5-flash")
    return os.environ.copy()
