"""Tests for configuration management."""

import pytest
from chatcli.core.models import Profile
from chatcli.config import add_profile, get_profile, list_profiles


def test_add_and_get_profile(temp_app_dir, monkeypatch):
    """Test adding and retrieving a profile."""
    # Mock get_app_dir to use temp directory
    from chatcli import config
    monkeypatch.setattr(config, "get_app_dir", lambda: temp_app_dir)
    
    profile = Profile(
        name="test-profile",
        base_url="http://localhost:11434/v1",
        api_key="test-key",
        default_model="llama2"
    )
    
    add_profile(profile)
    retrieved = get_profile("test-profile")
    
    assert retrieved is not None
    assert retrieved.name == "test-profile"
    assert retrieved.base_url == "http://localhost:11434/v1"
    assert retrieved.default_model == "llama2"


def test_list_profiles(temp_app_dir, monkeypatch):
    """Test listing profiles."""
    from chatcli import config
    monkeypatch.setattr(config, "get_app_dir", lambda: temp_app_dir)
    
    # Add multiple profiles
    for i in range(3):
        profile = Profile(
            name=f"profile-{i}",
            base_url=f"http://api{i}.example.com",
            api_key=f"key-{i}"
        )
        add_profile(profile)
    
    profiles = list_profiles()
    assert len(profiles) == 3
    assert all(p.name.startswith("profile-") for p in profiles)


def test_profile_name_validation():
    """Test profile name validation."""
    from chatcli.commands.profile import add_profile_cmd
    import typer
    
    # This would need to be tested with proper CLI testing tools
    # For now, just document the validation rules
    pass
